from PySimpleGUI.PySimpleGUI import T
import git
import PySimpleGUI as sg
import os
import sys
from datetime import date, datetime, timezone, timedelta
import threading

WORKSPACE_FOLDER = os.path.abspath(os.path.join(os.getcwd(), '..'))
WORKSPACE_REPOS = {}

print(WORKSPACE_FOLDER)

# see https://stackoverflow.com/a/39956572
# made changes to return repo object if exits


def is_git_repo(path):
    try:
        r = git.Repo(path)
        _ = r.git_dir
        return True, r
    except git.exc.InvalidGitRepositoryError:
        return False, None


def getRemoteIfExits(repo):
    try:
        return repo.remote()
    except ValueError as ve:
        return None


def getRemoteUrl(remote):
    if remote:
        return next(remote.urls)
    else:
        return None

# print('. is git repo -> ' + str(is_git_repo('.')))

# print('.. is git repo -> ' + str(is_git_repo('..')))


_limit = 25  # 0 for all

def commit_days_text(numdays):
    if numdays == 0:
        return "today"
    elif numdays == 1:
        return "yesterday"
    elif numdays > 1:
        return str(numdays) + " days ago"
    else:
        "invalid"

def getReposList(updateFunc=None):
    table_rows = []
    _now = datetime.now()
    _td_one_day = timedelta(days=1)
    _completion = 0

    if updateFunc:
        updateFunc(_completion)

    # Get all the subdirectories of the repo parent path (might call this workspace folder).
    _, all_subdirs, other_files = next(os.walk(WORKSPACE_FOLDER))

    # getting the dirs is 10% progress
    if updateFunc:
        _completion = 10
        updateFunc(_completion)

    # checking if the repos are git repos and populating repo object
    # is 80% of the progress
    _loading_total_progress = 90.0
    _count = 0
    _total = len(all_subdirs)
    _item_progress = _loading_total_progress / \
        (_limit if _total > _limit else _total)
    # print('total = ', str(_total), ' item progress = ', str(_item_progress))
    for dir in all_subdirs:
        if _limit > 0:
            _count += 1
        if _limit > 0 and _count >= _limit:
            if updateFunc:
                _completion += _item_progress
                updateFunc(_completion)
            break

        dir_abspath = os.path.abspath(os.path.join(WORKSPACE_FOLDER, dir))
        flag, repo = is_git_repo(dir_abspath)
        if flag:
            remote_url = str(getRemoteUrl(getRemoteIfExits(repo)))
            last_commit_datetime = str(repo.head.commit.committed_datetime)
            td_since_last_commit = _now - repo.head.commit.committed_datetime.replace(tzinfo=None)
            # print(td_since_last_commit)
            days_since_last_commit, _ = divmod(td_since_last_commit, _td_one_day)
            # print(days_since_last_commit)
            WORKSPACE_REPOS[dir] = (repo, remote_url, last_commit_datetime, commit_days_text(days_since_last_commit))
        if updateFunc:
            _completion += _item_progress
            updateFunc(_completion)

    # Create repository table
    for repo_dir, (repo, remote_url, last_commit_datetime, days_since_last_commit) in WORKSPACE_REPOS.items():
        table_rows.append([
            str(repo_dir), str(repo.working_dir), remote_url, days_since_last_commit
        ])

    # creating the repo table with details is 10% progress
    if updateFunc:
        _completion = 100
        updateFunc(_completion)

    return table_rows


def updateReposListWindow(window):
    window.write_event_value('-START-LOADING-PROGRESS-', None)
    table_rows = getReposList(lambda progress: window.write_event_value(
        '-UPDATE-LOADING-PROGRESS-', progress))
    window.write_event_value('-UPDATE-REPOS-LIST-', table_rows)
    window.write_event_value('-DONE-LOADING-PROGRESS-', None)


def longUpdateRepos():
    threading.Thread(target=updateReposListWindow,
                     args=(window,), daemon=True).start()

# print(WORKSPACE_REPOS)

# exit(0)

################# GUI Code ##################


sg.theme('DarkBlack')   # Add a touch of color
# All the stuff inside your window.

#tbBtnFont = 'Helvetica 13'
tbBtnFont = None

def createToolbarBtn(text, k=None, font=tbBtnFont, pad=((5, 0), (5, 0))):
    return sg.Button(text, k=k, font=font, p=pad)

repo_selection_bar = [
    sg.Text(text='Workspace Dir:'),
    sg.Input(default_text=WORKSPACE_FOLDER, k='workspace_folder', enable_events=True),
    sg.FolderBrowse('Select', initial_folder=WORKSPACE_FOLDER, enable_events=True, k='select_workspace')
]

toolbar = [
    createToolbarBtn('Open📂', k="open_dir"),
    createToolbarBtn('Terminal', k="terminal"),
    createToolbarBtn('Code✎', k="open_editor"),
    createToolbarBtn('Info🛈', k="repo_info"),
    createToolbarBtn('Gitk', k="gitk", pad=((30, 0), (5, 0))),
    createToolbarBtn('Git-gui', k="git-gui"),
    createToolbarBtn('Refresh🗘', k="refresh_repos", pad=((30, 0), (5, 0))),
]

layout = [
    repo_selection_bar,
    toolbar
    ]

repoTable = sg.Table(
    headings=['Name', 'Directory', 'Remote(Origin)', 'Last Commit'],
    values=[['Loading...', 'Loading...', 'Loading...', 'Loading...']],
    enable_events=True,
    justification='center',
    display_row_numbers=True,
    expand_x=True,
    expand_y=True,
    k='repo_table'
)

# Append table to the window layout
layout.append([repoTable])

statusbar = [
    sg.Text(
        text='',
        size=(25, 1),
        k='statusbar_text0'
    ),
    sg.ProgressBar(
        max_value=100,
        # bar_color='green',
        visible=False,
        size=(20, 20),
        k='repo_load_progress'
    )
]

layout.append(statusbar)

# Create the Window
window = sg.Window(
    'Repo Org UI', 
    layout,
    size=(800, 600)
)
window.finalize()

# run the update repos task for the first load
longUpdateRepos()

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    selected_rows = values['repo_table']
    for sr in selected_rows:
        selected_item = window['repo_table'].Values[sr][1]
        if event == 'open_dir':
            os.startfile(selected_item)
        elif event == 'open_editor':
            os.system('code ' + selected_item)
        elif event == 'gitk':
            currentdir = os.getcwd()
            os.chdir(selected_item)
            os.system('gitk ' + selected_item)
            os.chdir(currentdir)
        elif event == 'git-gui':
            currentdir = os.getcwd()
            os.chdir(selected_item)
            if sys.platform == 'win32':
                os.system('git-gui')
            else:
                os.system('git -gui')
            os.chdir(currentdir)
        elif event == 'terminal':
            currentdir = os.getcwd()
            os.chdir(selected_item)
            if sys.platform == 'win32':
                os.system('wt -d ' + selected_item)
            elif sys.platform == 'linux64':
                os.system('terminator')
            os.chdir(currentdir)

    if event == "refresh_repos":
        longUpdateRepos()
    elif event == '-UPDATE-REPOS-LIST-':
        print(values['-UPDATE-REPOS-LIST-'])
        # table selection can only be called after window.read or window.finalize
        window['repo_table'].update(
            values=values['-UPDATE-REPOS-LIST-'], select_rows=[0])
    elif event == '-START-LOADING-PROGRESS-':
        window['repo_load_progress'].update(current_count=0, visible=True)
        window['statusbar_text0'].update(value='Loading repo list...')
    elif event == '-DONE-LOADING-PROGRESS-':
        window['repo_load_progress'].update(current_count=100, visible=False)
        window['statusbar_text0'].update(value='Loaded repo list.')
    elif event == '-UPDATE-LOADING-PROGRESS-':
        window['repo_load_progress'].update(
            current_count=values['-UPDATE-LOADING-PROGRESS-'], visible=True)
    elif event == 'workspace_folder':
        WORKSPACE_FOLDER = values['workspace_folder']
        WORKSPACE_REPOS = {}
        longUpdateRepos()
    print('Event ', event)
    print('You entered ', values)

window.close()

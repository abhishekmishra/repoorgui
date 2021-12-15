import git
import PySimpleGUI as sg
import os
from datetime import date, datetime
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


_limit = 10  # 0 for all


def getReposList(updateFunc=None):
    completion = 0
    if updateFunc:
        updateFunc(completion)

    # Get all the subdirectories of the repo parent path (might call this workspace folder).
    _, all_subdirs, other_files = next(os.walk(WORKSPACE_FOLDER))

    # getting the dirs is 10% progress
    if updateFunc:
        completion = 10
        updateFunc(completion)

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
                completion += _item_progress
                updateFunc(completion)
            break

        dir_abspath = os.path.abspath(os.path.join(WORKSPACE_FOLDER, dir))
        flag, repo = is_git_repo(dir_abspath)
        if flag:
            remote_url = str(getRemoteUrl(getRemoteIfExits(repo)))
            last_commit_datetime = str(repo.head.commit.committed_datetime)
            WORKSPACE_REPOS[dir] = (repo, remote_url, last_commit_datetime)
        if updateFunc:
            completion += _item_progress
            updateFunc(completion)

    # Create repository table
    table_rows = []
    for repo_dir, (repo, remote_url, last_commit_datetime) in WORKSPACE_REPOS.items():
        table_rows.append([
            str(repo_dir), str(repo.working_dir), remote_url, last_commit_datetime
        ])

    # creating the repo table with details is 10% progress
    if updateFunc:
        completion = 100
        updateFunc(completion)

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


sg.theme('DarkBlack1')   # Add a touch of color
# All the stuff inside your window.

tbBtnFont = 'Helvetica 14'


def createToolbarBtn(text, k=None, font=tbBtnFont, pad=((0, 0), (0, 0))):
    return sg.Button(text, k=k, font=font, p=pad)


toolbar = [
    createToolbarBtn('📂', k="open_dir"),
    createToolbarBtn('✎', k="open_editor"),
    createToolbarBtn('🛈', k="repo_info"),
    createToolbarBtn('gitk', k="gitk", pad=((30, 0), (0, 0))),
    createToolbarBtn('git-gui', k="git-gui"),
    createToolbarBtn('🗘', k="refresh_repos", pad=((30, 0), (0, 0))),
]

layout = [toolbar]

repoTable = sg.Table(
    headings=['Name', 'Directory', 'Remote(Origin)', 'Last Commit'],
    values=[['Loading...', 'Loading...', 'Loading...', 'Loading...']],
    enable_events=True,
    justification='center',
    display_row_numbers=True,
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
window = sg.Window('Repo Org UI', layout)
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
            os.system('git-gui')
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
    # print('Event ', event)
    print('You entered ', values)

window.close()

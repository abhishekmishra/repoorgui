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


_limit = 5  # 0 for all


def getReposList():
    # Get all the subdirectories of the repo parent path (might call this workspace folder).
    _, all_subdirs, other_files = next(os.walk(WORKSPACE_FOLDER))

    _count = 0
    for dir in all_subdirs:
        if _limit > 0 and _count >= _limit:
            break

        dir_abspath = os.path.abspath(os.path.join(WORKSPACE_FOLDER, dir))
        flag, repo = is_git_repo(dir_abspath)
        if flag:
            WORKSPACE_REPOS[dir] = repo
            if _limit > 0:
                _count += 1

    # Create repository table
    table_rows = []
    for repo_dir, repo in WORKSPACE_REPOS.items():
        table_rows.append([
            str(repo_dir), str(repo.working_dir), str(getRemoteUrl(
                getRemoteIfExits(repo))), str(repo.head.commit.committed_datetime)
        ])
    return table_rows

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
    values=getReposList(),
    enable_events=True,
    justification='center',
    display_row_numbers=True,
    k='repo_table'
)

# Append table to the window layout
layout.append([repoTable])

# Create the Window
window = sg.Window('Repo Org UI', layout)
window.finalize()

# table selection can only be called after window.read or window.finalize
repoTable.update(select_rows=[0])

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
    print('You entered ', values)

window.close()

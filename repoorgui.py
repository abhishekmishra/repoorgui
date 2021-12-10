import git
import PySimpleGUI as sg
import os
from datetime import date, datetime

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

# print('. is git repo -> ' + str(is_git_repo('.')))

# print('.. is git repo -> ' + str(is_git_repo('..')))


# Get all the subdirectories of the repo parent path (might call this workspace folder).
_limit = 5  # 0 for all
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

# print(WORKSPACE_REPOS)

# exit(0)

################# GUI Code ##################


sg.theme('DarkBlack1')   # Add a touch of color
# All the stuff inside your window.

tbBtnFont = 'Helvetica 14'

toolbar = [
    sg.Button('🗘', k="refresh_repos", font=tbBtnFont),
    sg.Button('📂', k="open_dir", font=tbBtnFont),
    sg.Button('🛈', k="repo_info", font=tbBtnFont)
]

layout = [toolbar]

# Create repository table
table_rows = []
for repo_dir, repo in WORKSPACE_REPOS.items():
    table_rows.append([
        str(repo_dir), str(repo.working_dir), str(getRemoteUrl(
            getRemoteIfExits(repo))), str(repo.head.commit.committed_datetime)
    ])

repoTable = sg.Table(
    headings=['Name', 'Directory', 'Remote(Origin)', 'Last Commit'],
    values=table_rows,
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
    if event == 'open_dir':
        selected_rows = values['repo_table']
        for sr in selected_rows:
            # print(table_rows[sr])
            os.startfile(table_rows[sr][1])
    print('You entered ', values)

window.close()

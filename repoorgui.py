import git
import PySimpleGUI as sg
import os

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
_, all_subdirs, other_files = next(os.walk(WORKSPACE_FOLDER))

for dir in all_subdirs:
    dir_abspath = os.path.abspath(os.path.join(WORKSPACE_FOLDER, dir))
    flag, repo = is_git_repo(dir_abspath)
    if flag:
        WORKSPACE_REPOS[dir] = repo

# print(WORKSPACE_REPOS)

# exit(0)

################# GUI Code ##################

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('folder'), sg.Text('path')],
          ]

table_rows = []
for repo_dir, repo in WORKSPACE_REPOS.items():
    table_rows.append([
        str(repo_dir), str(repo.working_dir), str(repo.head.commit)
    ])

print(table_rows)
layout.append([sg.Table(headings=['name', 'folder', 'last_commit'], values=table_rows)])

# Create the Window
window = sg.Window('Repo Org UI', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()

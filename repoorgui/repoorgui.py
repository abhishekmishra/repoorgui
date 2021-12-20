# https://stackoverflow.com/a/55943328/9483968
from repoorgui.gitworkspace import *
from repoorgui.commands import *
import argparse
import platformdirs
import sys
import PySimpleGUI as sg
import git
from PySimpleGUI.PySimpleGUI import T
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

class AppState:
    def __init__(self) -> None:
        self.workspace_folder = os.path.abspath(
            os.path.join(os.getcwd(), '..')),
        self.workspace_repos = {}
        self.data_folder = os.path.join(
            platformdirs.user_data_dir(), 'repoorgui')
        self.gitignores_folder = os.path.join(
            self.data_folder, "gitignore")

_APP_STATE = AppState()

parser = argparse.ArgumentParser("repoorgui builder arguments")
parser.add_argument('workspace')
args = parser.parse_args()

if args.workspace:
    _APP_STATE.workspace_folder = args.workspace
else:
    print("Error no workspace provided.", file=sys.stderr)
print(_APP_STATE.workspace_folder)

@commandfn
def cmd_clone_gitignore(window, event, values, appstate):
    if os.path.isdir(appstate.gitignores_folder):
        pass
        # print(appstate.gitignores_folder, ' exists already. Will pull when needed.')
    else:
        # print(appstate.gitignores_folder, ' does not exist. Need to clone.')
        try:
            git.Repo.clone_from(
                "https://github.com/github/gitignore.git", appstate.gitignores_folder)
            print('https://github.com/github/gitignore.git cloned at ',
                  appstate.gitignores_folder)
        except git.GitCommandError as exception:
            print(exception)
            if exception.stdout:
                print(exception.stdout)
            if exception.stderr:
                print(exception.stderr)

run_command('clone_gitignore', None, None, None, appstate = _APP_STATE)

################# GUI Code ##################


sg.theme('DarkBlack')   # Add a touch of color
# All the stuff inside your window.

#tbBtnFont = 'Helvetica 13'
tbBtnFont = None

# TODO: can convert to partial
def createToolbarBtn(text, k=None, font=tbBtnFont, pad=((5, 0), (5, 0))):
    return sg.Button(text, k=k, font=font, p=pad)


repo_selection_bar = [
    sg.Text(text='Workspace Dir:'),
    sg.Input(default_text=_APP_STATE.workspace_folder,
             k='workspace_folder', enable_events=True),
    sg.FolderBrowse('Select', initial_folder=_APP_STATE.workspace_folder,
                    enable_events=True, k='select_workspace')
]

toolbar = [
    createToolbarBtn('New Repo', k="new_repo"),
    createToolbarBtn('Clone Repo', k="clone_repo"),
    createToolbarBtn('Repo Info', k="repo_info"),
    createToolbarBtn('Open Dir', k="open_dir"),
    createToolbarBtn('Open Terminal', k="terminal"),
    createToolbarBtn('VSCode', k="open_editor"),
    createToolbarBtn('Gitk', k="gitk", pad=((30, 0), (5, 0))),
    createToolbarBtn('Git-gui', k="git-gui"),
    createToolbarBtn('Refresh', k="refresh_repos", pad=((30, 0), (5, 0))),
    createToolbarBtn('About', k="tb_about_repoorgui"),
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

eventCommand = {
    'refresh_repos': 'long_update_repos',
    'workspace_folder': 'long_update_repos',
    'tb_about_repoorgui': 'about_repoorgui'
}

# run the update repos task for the first load
cmd_long_update_repos(window, None, None, _APP_STATE)

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

    if event == '-UPDATE-REPOS-LIST-':
        # print(values['-UPDATE-REPOS-LIST-'])
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
    elif event in eventCommand.keys():
        run_command(eventCommand[event], window,
                    event, values, appstate=_APP_STATE)
    # print('Event ', event)
    # print('You entered ', values)

window.close()

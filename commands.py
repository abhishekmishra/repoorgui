import PySimpleGUI as sg


def cmd_about_repoorgui(**kwargs):
    sg.popup_ok(
        'RepOrgUI v0.0.1',
        'A Git Repos Workspace Organizer',
        'Author: Abhishek Mishra <abhishekmishra3@gmail.com>',
        'Project: https://github.com/abhishekmishra/repoorgui',
        title="About RepOrgUI"
    )


def run_command(command_name, window, event, values):
    """
    Run command given by command_name(str) with arguments window, event, and values from the pysimplegui window

    Parameters:
        command_name (str): name of the command to run.
            program will look for method 'cmd_%command_name%' in global scope to run.

        window, event, values: the objects from pysimplegui window
            these will be passed as-is to the command function if found.

    Returns:
        Return value of executed command function.

    Throws:
        NameError if cmd_%command_name% not found.
    """
    cmd = globals()['cmd_' + command_name]
    if cmd != None:
        return cmd(window=window, event=event, values=values)
    else:
        NameError('cmd_' + command_name)

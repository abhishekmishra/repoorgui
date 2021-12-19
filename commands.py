import PySimpleGUI as sg

_ALL_COMMAND_FNS = {}

def commandfn(f):
    """
    Decorator to be used for every command function,
    so that the run_command function can find it when executing.
    """
    _ALL_COMMAND_FNS[f.__name__] = f
    return f

@commandfn
def cmd_about_repoorgui(**kwargs):
    sg.popup_ok(
        'RepOrgUI v0.0.1',
        'A Git Repos Workspace Organizer',
        'Author: Abhishek Mishra <abhishekmishra3@gmail.com>',
        'Project: https://github.com/abhishekmishra/repoorgui',
        title="About RepOrgUI"
    )

def run_command(command_name, window=None, event=None, values=None, **kwargs):
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
    cmdfn = _ALL_COMMAND_FNS['cmd_' + command_name]
    if cmdfn != None:
        return cmdfn(window=window, event=event, values=values, **kwargs)
    else:
        NameError('cmd_' + command_name)

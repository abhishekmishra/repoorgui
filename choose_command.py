import PySimpleGUI as sg


def choose_command_popup(title='Choose command'):
    command = None

    layout = [
        [
            sg.Input(
                enable_events=True,
                focus = True,
                pad = (0, 0),
                k='command_query'
            )
        ]
    ]

    window = sg.Window(
        title,
        layout,
        default_element_size=(120, 1),
        no_titlebar=True,
        grab_anywhere=True,
        use_default_focus = False,
        element_padding = (0, 0),
        margins = (0, 0),
        finalize=True
    )
    window.bind('<Return>', '-SUBMIT-')
    window.bind('<Escape>', '-EXIT-')
    window['command_query'].set_focus(force = True)

    while True:
        event, values = window.read()

        print(event)
        print(values)

        if event in ('-EXIT-', sg.WIN_CLOSED):
            break
        elif event == '-SUBMIT-':
            command = values['command_query']
            break

    window.close()
    # sg.popup('You entered', text_input)
    return command


if __name__ == "__main__":
    x = choose_command_popup()
    print(x)

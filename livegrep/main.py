import sys
from email._header_value_parser import get_invalid_parameter

from prompt_toolkit import Application
from prompt_toolkit.input import create_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Window

if sys.stdin.isatty():
    pass
else:  # We're part of a pipe
    # Start with hidden UI

    kb = KeyBindings()


    @kb.add('q')
    def exit_(event):
        event.app.exit()



    app = Application(layout=Layout(Window(height=0)),
                      full_screen=False,
                      # In order to work in a pipe, this input must be set this
                      # way; see https://github.com/prompt-toolkit/python-prompt-toolkit/issues/502  # noqa
                      input=create_input(sys.stdout),
                      key_bindings=kb)

    app.context

    app.run()
    for line in sys.stdin:
        print(line)

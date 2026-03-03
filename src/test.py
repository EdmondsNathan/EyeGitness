from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

kb = KeyBindings()
kb2 = KeyBindings()

sub_container = HSplit([
Window(height=10, content=FormattedTextControl(text='Hello world')),
Window(height=1, char='-'),
Window(content=FormattedTextControl(text='Hello world')),
])
root_container = VSplit([
    # One window that holds the BufferControl with the default buffer on
    # the left.
    # Window(content=BufferControl(buffer=buffer1)),
    Window(content=FormattedTextControl(text='this is some text\nandyeah')),

    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
    Window(width=1, char='|'),
    sub_container,
    # Display the text 'Hello world' on the right.
])

@kb.add('c-q')
def _(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()
@kb2.add('q')
def _(event):
    """
    Pressing Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

layout = Layout(root_container)

bindings = merge_key_bindings([
    kb,
    kb2,
    ])

app = Application(layout=layout, full_screen=True)
app.key_bindings = bindings
app.run() # You won't be able to Exit this app

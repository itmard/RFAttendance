from jnius import autoclass, cast
from android.runnable import run_on_ui_thread

Toast = autoclass('android.widget.Toast')
context = autoclass('org.renpy.android.PythonActivity').mActivity


@run_on_ui_thread
def toast(text, length_long=False):
    duration = Toast.LENGTH_LONG if length_long else Toast.LENGTH_SHORT
    string = autoclass('java.lang.String')
    c = cast('java.lang.CharSequence', string(text))
    t = Toast.makeText(context, c, duration)
    t.show()

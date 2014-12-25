from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.core.window import Window


class MainTab(TabbedPanelItem):
    def __init__(self, *args, **kwargs):
        super(MainTab, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_key_down(self, window, key, *args):
        if key == 27:
            exit(0)
            return True

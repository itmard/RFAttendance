from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.core.window import Window

from server import Server


class LoginTab(TabbedPanelItem):
    def __init__(self, *args, **kwargs):
        super(LoginTab, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_enter(self):
        # auth_data = Database().get_auth()
        # if auth_data:
        #     self.login(*auth_data)
        pass

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'main'
            return True

    def login(self, username=None, password=None):
        self.ids.status_label.text = 'Connecting to Server...'
        # Any better solution without callbacks?
        # Guess not, https://stackoverflow.com/a/22033066
        Clock.schedule_once(partial(
            Server,
            self.ids.username_box.text if not username else username,
            self.ids.password_box.text if not password else password,
            self.login_success,
            self.login_failed,
        ))

    def login_success(self):
        self.ids.status_label.text = 'Authentication Successful!'
        if self.ids.remember_me.active:
            # Default value of checkbox is false, so this block only executes if
            # auth data has entered via text input
            # Database().save_auth(
            #     self.username_box.text,
            #     self.password_box.text
            # )
            pass

    def login_failed(self):
        self.ids.status_label.text = 'Authentication Failed!'

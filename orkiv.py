from functools import partial

from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from server import Server, AuthError


class AccountDetailsForm(AnchorLayout):
    server_box = ObjectProperty()
    username_box = ObjectProperty()
    password_box = ObjectProperty()
    status_label = ObjectProperty()

    def login(self):
        app = Orkiv.get_running_app()
        self.status_label.text = "Connecting to Server.."
        # Any better solution without callbacks?
        # Guess not, https://stackoverflow.com/a/22033066
        Clock.schedule_once(partial(
            app.authenticate,
            self.username_box.text,
            self.password_box.text,
            self.login_success,
            self.login_failed,
        ))

    def login_success(self):
        self.status_label.text = "Authentication Successful!"

    def login_failed(self):
        self.status_label.text = 'Authentication Failed!'


class Orkiv(App):
    def __init__(self):
        super(Orkiv, self).__init__()
        self.server = None

    def authenticate(self, username, password, auth_success, auth_failed, *args):
        try:
            self.server = Server(username, password)
        except AuthError:
            auth_failed()
        else:
            auth_success()

    def on_stop(self):
        self.server = None

Orkiv().run()

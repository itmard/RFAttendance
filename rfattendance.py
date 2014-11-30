# coding: utf-8

from functools import partial

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button

from db import Database, DuplicationError
from server import Server, AuthError
from nfc import NFC


class RfAttendance(App):
    def __init__(self):
        super(RfAttendance, self).__init__()
        self.server = None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(NewSessionScreen(name='new_session'))
        self.sm.add_widget(RegisterNewMemberScreen(name='register_new_member'))
        self.sm.current = 'login'
        # self.server = Server('test', 'test')
        return self.sm

    def authenticate(self, username, password, auth_success, auth_failed, *args):
        try:
            self.server = Server(username, password)
        except AuthError:
            auth_failed()
        else:
            auth_success()

    def on_stop(self):
        self.server = None


class LoginScreen(Screen):
    username_box = ObjectProperty()
    password_box = ObjectProperty()
    remember_me = ObjectProperty()
    status_label = ObjectProperty()

    def on_enter(self):
        auth_data = Database.get_instance().get_auth()
        if auth_data:
            self.login(*auth_data)

    def login(self, username=None, password=None):
        app = RfAttendance.get_running_app()
        self.status_label.text = 'Connecting to Server...'
        # Any better solution without callbacks?
        # Guess not, https://stackoverflow.com/a/22033066
        Clock.schedule_once(partial(
            app.authenticate,
            self.username_box.text if not username else username,
            self.password_box.text if not password else password,
            self.login_success,
            self.login_failed,
        ))

    def login_success(self):
        app = RfAttendance.get_running_app()
        self.status_label.text = 'Authentication Successful!'
        if self.remember_me.active:
            # Default value of checkbox is false, so this block only executes if
            # auth data has entered via text input
            Database.get_instance().save_auth(
                self.username_box.text,
                self.password_box.text
            )
        app.sm.current = 'main'

    def login_failed(self):
        self.status_label.text = 'Authentication Failed!'


class MainScreen(Screen):
    pass


class NewSessionScreen(Screen):
    session_list = ObjectProperty()
    dropdown_button = ObjectProperty()
    status_label = ObjectProperty()

    def on_enter(self):
        app = RfAttendance.get_running_app()
        for session_id, session_info in app.server.get_session_list().items():
            button = Button(
                id=str(session_id), text=session_info['session_name'],
                size_hint_y=None, height=44
            )
            button.bind(
                on_release=lambda btn: self.session_list.select(btn.id)
            )
            self.session_list.add_widget(button)

    def session_selected(self, session_id):
        self.dropdown_button.text = 'Selected session {}'.format(session_id)
        self.status_label.text = 'Put RFID tag near the phone to recognize attendance'
        NFC(self.nfc_callback, session_id)

    def nfc_callback(self, tag_id, session_id, *args):
        try:
            english_name = Database.get_instance().get_member('tag_id', tag_id)[tag_id]['english_name']
            Database.get_instance().add_attendance(session_id, tag_id)
        except DuplicationError:
            self.status_label.text = '{} has already registered'.format(english_name)
        else:
            self.status_label.text = '{} successfully registered'.format(english_name)


class RegisterNewMemberScreen(Screen):
    tag_id = ObjectProperty()
    persian_name = ObjectProperty()
    english_name = ObjectProperty()
    status_label = ObjectProperty()

    def on_enter(self):
        NFC(self.update_tag_id)

    def update_tag_id(self, tag_id, *args):
        self.tag_id.text = str(tag_id * 10)

    def register(self):
        if not self.tag_id:
            self.status_label.text = 'You can\'t register without a Tag ID'
            return
        try:
            Database.get_instance().register_member(
                self.tag_id.text,
                self.english_name.text,
                self.persian_name.text
            )
        except DuplicationError:
            self.status_label.text = 'Member is already registered'
        else:
            self.status_label.text = '{} successfully registered'.format(
                self.english_name.text
            )
            app.sm.current = 'main'


RfAttendance().run()

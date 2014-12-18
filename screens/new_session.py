from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.core.window import Window

from db import Session


class NewSessionScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(NewSessionScreen, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_enter(self):
        self.new_session_checkbox()
        self.session_id = None
        for session in Session().select():
            button = Button(
                id=str(session.id), text=session.name,
                size_hint_y=None, height=44
            )

            button.bind(
                on_release=lambda btn: self.ids.session_list.select(btn.id)
            )
            self.ids.session_list.add_widget(button)

    def on_leave(self):
        self.session_id = None

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'main'
            return True

    def new_session_checkbox(self):
        self.ids.new_session_name.disabled = False
        self.ids.dropdown_button.disabled = True

    def added_session_checkbox(self):
        self.ids.new_session_name.disabled = True
        self.ids.dropdown_button.disabled = False

    def previously_added_session(self, session_id):
        self.session_id = session_id
        self.ids.dropdown_button.text = 'Session {}'.format(session_id)

    def register_attendance(self):
        if self.ids.new_session_checkbox.active and self.ids.new_session_name.text:
            self.session_id = self._create_new_session(self.ids.new_session_name.text)

        if self.session_id:
            self.manager.current = 'register_attendance'

    def _create_new_session(self, session_name):
        try:
            session = Session(name=session_name, date=datetime.now())
            session.save()
            return session.id
        except Exception as e:
            self.ids.status_label.text = 'Session already created'
            raise e               # FIXME

from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.utils import platform

from db import Member, IntegrityError
from nfc import nfc_instance

if platform == 'android':
    from android import activity


class RegisterNewMemberScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(RegisterNewMemberScreen, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_pre_enter(self):
        self.ids.status_label.text = 'Put an RFID tag near to phone'

    def on_enter(self):
        if nfc_instance:
            nfc_instance.register_action(self.update_tag_id)

    def on_leave(self):
        self.clean_widgets()
        if nfc_instance:
            nfc_instance.remove_action(self.update_tag_id)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'main'
            return True

    def clean_widgets(self):
        self.ids.tag_id.text = ''
        self.ids.name.text = ''

    def update_tag_id(self, tag_id, *args):
        self.ids.tag_id.text = str(tag_id)

    def register(self):
        if not self.ids.tag_id.text:
            self.ids.status_label.text = 'You can\'t register without a RFID tag'
            return

        if not self.ids.name.text:
            self.ids.status_label.text = 'Please enter your name'
            return

        try:
            Member(
                tag_id=self.ids.tag_id.text,
                name=self.ids.name.text
            ).save()
        except IntegrityError:
            self.ids.status_label.text = 'Member is already registered'
        else:
            self.ids.status_label.text = '{} successfully registered'.format(
                self.ids.name.text
            )

        self.clean_widgets()

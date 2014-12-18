from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.utils import platform

from db import Member, SessionAttendance, DoesNotExist, IntegrityError
from nfc import nfc_instance


if platform == 'android':
    from android import activity


class RegisterAttendanceScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(RegisterAttendanceScreen, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_pre_enter(self):
        self.ids.status_label.text = 'Put RFID tag near the phone to recognize attendance\n'

    def on_enter(self):
        self.session_id = self.manager.get_screen('new_session').session_id
        if not self.session_id:
            self.manager.current = 'new_session'
            return

        if nfc_instance:
            nfc_instance.register_action(self.attendance_registered)

    def on_leave(self):
        if nfc_instance:
            nfc_instance.remove_action(self.attendance_registered)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'new_session'
            return True

    def attendance_registered(self, tag_id, *args):
        try:
            member = Member.get(Member.tag_id == tag_id)
            print member, self.session_id
            SessionAttendance.create(session=self.session_id, member=member.id)
        except IntegrityError:
            self.ids.status_label.text += '{} has already registered\n'.format(member.name)
        except DoesNotExist:
            self.ids.status_label.text += 'There is no member with Tag ID {}\n'.format(tag_id)
        else:
            self.ids.status_label.text += '{} successfully registered\n'.format(member.name)

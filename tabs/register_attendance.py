from kivy.uix.tabbedpanel import TabbedPanelItem

from db import Member, SessionAttendance, DoesNotExist, IntegrityError
from nfc import nfc_instance
from toast import toast


class RegisterAttendanceTab(TabbedPanelItem):
    def __init__(self, *args, **kwargs):
        super(RegisterAttendanceTab, self).__init__(*args, **kwargs)

    def on_pre_enter(self):
        self.ids.status_label.text = 'Put RFID tag near the phone to recognize attendance\n'

    def on_enter(self):
        self.session_id = self.manager.get_screen('new_session').session_id

        if nfc_instance:
            nfc_instance.register_action(self.attendance_registered)

    def on_leave(self):
        if nfc_instance:
            nfc_instance.remove_action(self.attendance_registered)

    def attendance_registered(self, tag_id, *args):
        try:
            member = Member.get(Member.tag_id == tag_id)
            toast(member, self.session_id)
            SessionAttendance.create(session=self.session_id, member=member.id)
        except IntegrityError:
            toast('{} has already registered\n'.format(member.name))
        except DoesNotExist:
            toast('There is no member with Tag ID {}\n'.format(tag_id))
        else:
            toast('{} successfully registered\n'.format(member.name))

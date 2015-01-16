from datetime import datetime

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem
from kivy.uix.tabbedpanel import TabbedPanelItem

from db import Session, IntegrityError, SessionAttendance, Member, DoesNotExist
from nfc import nfc_instance
from toast import toast


class SessionsTab(TabbedPanelItem):
    def on_touch_down(self, *largs):
        self.content.current = 'list_sessions'
        super(TabbedPanelItem, self).on_touch_down(*largs)


class SessionsScreenManager(ScreenManager):
    pass


class ListSessions(Screen):
    def on_pre_enter(self):
        Clock.schedule_once(self.update_interface, -1)

    def update_interface(self, *args):
        self.ids.session_list.adapter = ListAdapter(
            data=Session.select(),
            args_converter=self.arg_converter,
            selection_mode='none',
            cls=CompositeListItem
        )
        self.ids.session_list.adapter.bind(data=self.session_data_changed)

    def session_data_changed(self, adapter, *args):
        self.ids.session_list.populate()
        self.ids.session_name.text = ''

    def arg_converter(self, index, session):
        return {
            'size_hint_y': 0.2,
            'height': '25dp',
            'cls_dicts': [{
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(session.name.encode('UTF-8')),
                }
            }, {
                'cls': ListItemLabel,
                'kwargs': {
                    'text': session.date.strftime('%d %b') if isinstance(session.date, datetime) else '',
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'View',
                    'on_press': lambda _: self.list_attendance(session.id)
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'Delete',
                    'on_press': lambda _: self.delete_session(session)
                }
            }]
        }

    def delete_session(self, session):
        session.delete_instance(recursive=True, delete_nullable=True)
        self.ids.session_list.adapter.data.remove(session)

    def list_attendance(self, session_id):
        self.selected_session_id = session_id
        self.manager.current = 'list_attendance'

    def create_new_session(self):
        try:
            if self.ids.session_name.text:
                session = Session.create(
                    name=self.ids.session_name.text,
                    date=datetime.now()
                )
                self.ids.session_list.adapter.data.append(session)
            else:
                toast('Session name can\'t be empty')
        except IntegrityError:
            toast('Session already created')


class ListAttendance(Screen):
    def on_pre_enter(self):
        self.session_id = self.manager.get_screen('list_sessions').selected_session_id
        nfc_instance.register_action(self.attendance_registered)
        Clock.schedule_once(self.update_interface, -1)
        Window.bind(on_keyboard=self.on_key_down)

    def on_enter(self, *args, **kwargs):
        super(ListAttendance, self).on_enter(*args, **kwargs)
        toast('Put RFID tag near to phone', True)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'list_sessions'
            return True

    def on_leave(self):
        Window.unbind(on_keyboard=self.on_key_down)
        nfc_instance.remove_action(self.attendance_registered)

    def update_interface(self, *args):
        self.ids.attendance_list.adapter = ListAdapter(
            data=Member.select(
                SessionAttendance, Member, Session
            ).join(SessionAttendance).join(Session).where(SessionAttendance.session == self.session_id),
            args_converter=self.arg_converter,
            selection_mode='none',
            cls=CompositeListItem
        )
        self.ids.attendance_list.adapter.bind(data=self.attendance_data_changed)

    def attendance_data_changed(self, adapter, *args):
        self.ids.attendance_list.populate()

    def arg_converter(self, index, attendace):
        return {
            'size_hint_y': 0.2,
            'cls_dicts': [{
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(attendace.name.encode('UTF-8')),
                    'is_representing_cls': True
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'Delete',
                    'on_press': lambda _: self.delete_attendace(attendace)
                }
            }]
        }

    def delete_attendace(self, attendance):
        try:
            SessionAttendance.select().where(
                SessionAttendance.member == attendance.id
            ).get().delete_instance()
        except DoesNotExist:
            toast('Member does not exist')
        self.ids.attendance_list.adapter.data.remove(attendance)

    def attendance_registered(self, tag_id, *args):
        try:
            attendance = Member.get(Member.tag_id == tag_id)
            SessionAttendance.create(session=self.session_id, member=attendance.id)
        except IntegrityError:
            toast('{} has already registered'.format(attendance.name))
        except DoesNotExist:
            toast('There is no member with Tag ID {}'.format(tag_id))
        else:
            self.ids.attendance_list.adapter.data.append(attendance)
            toast('{} successfully registered'.format(attendance.name))

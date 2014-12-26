from datetime import datetime

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem
from kivy.uix.tabbedpanel import TabbedPanelItem

from db import Member, IntegrityError, Session, SessionAttendance, DoesNotExist
from nfc import nfc_instance


class MembersTab(TabbedPanelItem):
    pass


class MembersScreenManager(ScreenManager):
    pass


class ListMembers(Screen):
    def on_pre_enter(self):
        Clock.schedule_once(self.update_interface, -1)

    def update_interface(self, *args):
        self.ids.member_list.adapter = ListAdapter(
            data=Member.select(),
            args_converter=self.arg_converter,
            selection_mode='none',
            cls=CompositeListItem
        )
        self.ids.member_list.adapter.bind(data=self.member_data_changed)

    def member_data_changed(self, adapter, *args):
        self.ids.member_list.populate()

    def arg_converter(self, index, member):
        return {
            'size_hint_y': 0.2,
            'cls_dicts': [{
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(member.tag_id),
                    'is_representing_cls': True
                }
            }, {
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(member.name.encode('UTF-8')),
                    'is_representing_cls': True
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'View',
                    'on_press': lambda _: self.view_member(member.id)
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'Delete',
                    'on_press': lambda _: self.delete_member(member)
                }
            }]
        }

    def delete_member(self, member):
        member.delete_instance(recursive=True, delete_nullable=True)
        self.ids.member_list.adapter.data.remove(member)

    def view_member(self, member_id):
        self.selected_member_id = member_id
        self.manager.current = 'view_member'


class NewMember(Screen):
    def on_enter(self):
        Window.bind(on_keyboard=self.on_key_down)
        if nfc_instance:
            nfc_instance.register_action(self.update_tag_id)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'list_members'
            return True

    def on_leave(self):
        Window.unbind(on_keyboard=self.on_key_down)
        self.clean_widgets()
        if nfc_instance:
            nfc_instance.remove_action(self.update_tag_id)

    def clean_widgets(self):
        self.ids.tag_id.text = ''
        self.ids.member_name.text = ''

    def update_tag_id(self, tag_id, *args):
        self.ids.tag_id.text = str(tag_id)

    def register(self):
        if not self.ids.tag_id.text:
            print 'You can\'t register without a RFID tag'
            return

        if not self.ids.member_name.text:
            print 'Please enter your name'
            return

        try:
            Member(
                tag_id=self.ids.tag_id.text,
                name=self.ids.member_name.text
            ).save()
        except IntegrityError:
            print 'Member is already registered'
        else:
            print '{} successfully registered'.format(
                self.ids.member_name.text
            )

        self.clean_widgets()
        self.manager.current = 'list_members'


class ViewMember(Screen):
    def on_pre_enter(self):
        self.member_id = self.manager.get_screen('list_members').selected_member_id
        Clock.schedule_once(self.update_interface, -1)
        Window.bind(on_keyboard=self.on_key_down)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'list_members'
            return True

    def on_leave(self):
        Window.unbind(on_keyboard=self.on_key_down)

    def update_interface(self, *args):
        self.ids.session_list.adapter = ListAdapter(
            data=Session.select(
                SessionAttendance, Member, Session
            ).join(SessionAttendance).join(Member).where(SessionAttendance.member == self.member_id),
            args_converter=self.arg_converter,
            selection_mode='none',
            cls=CompositeListItem
        )
        self.ids.session_list.adapter.bind(data=self.session_data_changed)

    def session_data_changed(self, adapter, *args):
        self.ids.session_list.populate()

    def arg_converter(self, index, session):
        return {
            'size_hint_y': 0.2,
            'cls_dicts': [{
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(session.name.encode('UTF-8')),
                    'is_representing_cls': True
                }
            }, {
                'cls': ListItemLabel,
                'kwargs': {
                    'text': session.date.strftime('%d %b') if isinstance(session.date, datetime) else ''
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
        try:
            SessionAttendance.select().where(
                SessionAttendance.session == session.id
            ).get().delete_instance()
        except DoesNotExist:
            print 'Session does not exist'
        self.ids.session_list.adapter.data.remove(session)

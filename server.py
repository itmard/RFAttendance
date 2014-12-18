# coding: utf-8

from time import sleep

from db import Database


class Server:
    def __init__(self, username, password, auth_success, auth_failed, *args):
        self.db = Database()
        # sleep(2)
        try:
            self._authenticate(username, password)
        except AuthError:
            auth_failed()
        else:
            auth_success()

    def _authenticate(self, username, password):
        if username == 'test' and password == 'test':
            pass
        else:
            raise AuthError()

    def get_session_list(self, force_refresh=False):
        sessions = Database.get_instance().get_sessions_list()
        if not sessions or force_refresh:
            sessions = {
                1: {'session_name': 'Session 1'},
                2: {'session_name': 'Session 2'},
                3: {'session_name': 'Session 3'},
                4: {'session_name': 'Session 4'},
                5: {'session_name': 'Session 5'}
            }
            Database.get_instance().save_sessions(sessions)

        return sessions

    def get_registered_members_list(self, force_refresh=False):
        members = Database.get_instance().get_members_list()
        if not members or force_refresh:
            members = {
                1: {'name': 'K1', 'persian_name': u'کیوان', 'tag_id': '1'},
                2: {'english_name': 'Nim4n', 'persian_name': u'نیما', 'tag_id': '2'},
                3: {'english_name': 'hapal', 'persian_name': u'هپل', 'tag_id': '3'},
                4: {'english_name': 'itmard', 'persian_name': u'مرد آی‌تی', 'tag_id': '4'},
                5: {'english_name': 'ftk', 'persian_name': u'حافظ', 'tag_id': '5'}
            }
            Database.get_instance().save_members(members)

        return members


class AuthError(Exception):
    pass

from datetime import datetime
from os import mkdir
from os.path import join

from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from db import Session, Member, SessionAttendance


class ExportScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(ExportScreen, self).__init__(*args, **kwargs)
        Window.bind(on_keyboard=self.on_key_down)

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.manager.current = 'main'
            return True

    def export(self):
        export_dir = join(
            self.manager.app.load_config().get('General', 'export_dir'),
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        try:
            mkdir(export_dir)
        except OSError:
            pass
        with open(join(export_dir, 'sessions.csv'), 'w') as sessions_file:
            sessions_file.write('session_name\n')
            for session in Session.select():
                sessions_file.write('{},\n'.format(session.name))
                with open(join(export_dir, 'session_{}.csv'.format(session.name.replace(' ', '_'))), 'w') as session_file:
                    query = SessionAttendance.select(
                        SessionAttendance, Member
                    ).join(Member).where(SessionAttendance.session==session.id)
                    for attendance in query:
                        session_file.write('{},{}\n'.format(attendance.member.tag_id, attendance.member.name))
                        print attendance.member.tag_id, attendance.member.name

        self.ids.status_label.text = 'Successfully exported to {}'.format(export_dir)

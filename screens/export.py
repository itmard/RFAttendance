from datetime import datetime
from os import mkdir
from os.path import join

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from playhouse.csv_loader import dump_csv

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

        dump_csv(Session.select(), join(export_dir, 'sessions.csv'))
        for session in Session.select():
            query = SessionAttendance.select(
                SessionAttendance, Member
            ).join(Member).where(SessionAttendance.session == session.id)
            dump_csv(query, join(export_dir, 'session_{}.csv'.format(session.name.replace(' ', '_'))))

        self.ids.status_label.text = 'Successfully exported to \n{}'.format(export_dir)

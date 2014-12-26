from datetime import datetime
from os import mkdir, listdir
from os.path import join, isdir, exists
from shutil import rmtree
from glob import glob

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem
from kivy.clock import Clock
from playhouse.csv_loader import dump_csv, load_csv

from db import Session, Member, SessionAttendance, IntegrityError


class ExportTab(TabbedPanelItem):
    def __init__(self, *args, **kwargs):
        super(ExportTab, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_interface, 0)

    def update_interface(self, *args):
        self.ids.exported_list.adapter = ListAdapter(
            data=self.get_exported(),
            args_converter=self.arg_converter,
            selection_mode='none',
            cls=CompositeListItem
        )

    def get_exported(self):
        self.export_base_dir = self.parent.tabbed_panel.app.load_config().get(
            'General', 'export_dir'
        )
        exported_dirs = filter(
            lambda file: isdir(join(self.export_base_dir, file)),
            listdir(self.export_base_dir)
        )
        return exported_dirs

    def arg_converter(self, index, directory_name):
        return {
            'size_hint_y': 0.2,
            'height': "25dp",
            'cls_dicts': [{
                'cls': ListItemLabel,
                'kwargs': {
                    'text': str(directory_name),
                    'is_representing_cls': True
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'Import',
                    'on_press': lambda _: self.import_(directory_name)
                }
            }, {
                'cls': ListItemButton,
                'kwargs': {
                    'text': 'Delete',
                    'on_press': lambda _: self.delete_export(directory_name)
                }
            }]
        }

    def delete_export(self, directory_name):
        rmtree(join(self.export_base_dir, directory_name))
        self.update_interface()

    def import_(self, directory_name):
        import_dir = join(self.export_base_dir, directory_name)

        if not (exists(join(import_dir, 'sessions.csv')) and
                exists(join(import_dir, 'members.csv'))):
            print 'Invalid backup'
            return

        try:
            load_csv(Session, join(import_dir, 'sessions.csv'), [
                Session.id,
                Session.name,
                Session.date
            ])
        except IntegrityError:
            print 'Sessions already imported'
        else:
            print 'Sessions Successfully imported'

        try:
            load_csv(Member, join(import_dir, 'members.csv'))
        except IntegrityError:
            print 'Member already imported'
        else:
            print 'Member Successfully imported'

        try:
            for session in glob(join(import_dir, 'session_*.csv')):
                load_csv(SessionAttendance, join(import_dir, session))
        except IntegrityError:
            print 'Sessions Attendance already imported'
        else:
            print 'Sessions Attendance Successfully imported'

    def export(self):
        export_dir = join(
            self.export_base_dir,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )

        try:
            mkdir(export_dir)
        except OSError:
            pass

        dump_csv(Session.select(Session.name, Session.date), join(export_dir, 'sessions.csv'))
        dump_csv(Member.select(Member.tag_id, Member.name), join(export_dir, 'members.csv'))
        for session in Session.select():
            dump_csv(
                SessionAttendance.select(
                    SessionAttendance.session,
                    SessionAttendance.member
                ).where(
                    SessionAttendance.session == session.id
                ), join(
                    export_dir,
                    'session_{}.csv'.format(session.name.replace(' ', '_'))
                )
            )

        print 'Successfully exported to \n{}'.format(export_dir)
        self.update_interface()

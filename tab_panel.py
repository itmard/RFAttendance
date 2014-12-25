from kivy.uix.tabbedpanel import TabbedPanel
from main import RfAttendance


class TabPannel(TabbedPanel):
    def __init__(self, *args, **kwargs):
        super(TabPannel, self).__init__(*args, **kwargs)
        self.app = RfAttendance.get_running_app()

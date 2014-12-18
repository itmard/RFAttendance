from kivy.uix.screenmanager import ScreenManager
from main import RfAttendance


class RfScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(RfScreenManager, self).__init__(*args, **kwargs)
        self.app = RfAttendance.get_running_app()

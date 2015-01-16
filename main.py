__version__ = '0.1'

from os import mkdir
from os.path import join

from kivy.config import Config
from kivy.app import App
from kivy.utils import platform
from kivy.core.window import Window

from nfc import nfc_instance, nfc_init
from db import create_tables, log_queries, create_instance


class RfAttendance(App):
    def build(self):
        if platform != 'android':
            Config.set('kivy', 'keyboard_mode', 'system')
            Config.write()
        else:
            Window.softinput_mode = 'resize'

    def build_config(self, config):
        config.adddefaultsection('General')
        config.write()
        config.set('General', 'database_file', join(self.user_data_dir, 'db.sqlite'))
        config.set('General', 'export_dir', join(self.user_data_dir, 'exports'))
        config.write()

        try:
            mkdir(config.get('General', 'export_dir'))
        except OSError:
            pass

        return config

    def on_pause(self):
        nfc_instance.nfc_disable_ndef_exchange()
        return True

    def on_resume(self):
        super(RfAttendance, self).on_resume()
        nfc_instance.nfc_enable_ndef_exchange()

if __name__ == '__main__':
    nfc_init()
    app = RfAttendance()

    create_instance(app.load_config().get('General', 'database_file'))
    app.run()

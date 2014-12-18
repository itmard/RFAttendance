__version__ = '0.1'

from os import mkdir, remove
from os.path import join

from kivy.app import App
from kivy.config import Config

from nfc import nfc_instance

class RfAttendance(App):
    def build_config(self, config):
        config.adddefaultsection('General')
        config.write()
        config.set('General', 'database_file', join(self.user_data_dir, 'db.sqlite'))
        config.set('General', 'export_dir', join(self.user_data_dir, 'exports'))
        config.write()
        try:
            mkdir(config.get('General', 'export_dir'))
            remove(config.get('General', 'database_file'))
        except OSError:
            pass
        print 1

        return config

    def on_pause(self):
        print 'Pause'
        if nfc_instance:
            nfc_instance.nfc_disable_ndef_exchange()
        return True

    def on_resume(self):
        super(RfAttendance, self).on_resume()
        if nfc_instance:
            nfc_instance.nfc_enable_ndef_exchange()

if __name__ == '__main__':
    RfAttendance().run()

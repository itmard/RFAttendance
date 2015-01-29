from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock
import webbrowser


class AboutTab(TabbedPanelItem):
    def __init__(self, *args, **kwargs):
        super(AboutTab, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_interface, 0)

    def update_interface(self, *args):
        self.ids.about.on_ref_press = on_ref_press
        self.ids.about.text ='''Version 1.0
Tehran Python Users Group [ref=tehpug][color=8888ff]tehpug.ir[/color][/ref]
Source available at [ref=github][color=8888ff]github.com/tehpug/RFAttendance[/color][/ref]
Report issues and bugs to [ref=mail][color=8888ff]rfattendance@tehpug.ir[/color][/ref] 
Keyvan Hedayati [ref=k1h][color=8888ff]k1h.ir[/color][/ref]
Copyright (C) 2014-2015
'''

        
def on_ref_press(ref):
    if ref == 'tehpug':
        webbrowser.open('http://tehpug.ir')
    elif ref == 'k1h':
        webbrowser.open('http://k1h.ir')
    elif ref == 'mail':
        webbrowser.open('mailto:rfattendance@tehpug.ir')
    elif ref == 'github':
        webbrowser.open('https://github.com/tehpug/RFAttendance')

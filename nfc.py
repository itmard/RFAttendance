from functools import partial
from random import randint


from kivy.clock import Clock


class NFC:
    def __init__(self, event_trigger_callback, *args):
        Clock.schedule_once(partial(
            event_trigger_callback,
            randint(1, 5),
            *args
        ))

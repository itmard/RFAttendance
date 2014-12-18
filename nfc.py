from time import sleep

from kivy.utils import platform

nfc_instance = None


class NFC:
    def __init__(self):
        self._action = None

        self.j_context = context = PythonActivity.mActivity
        self.nfc_adapter = NfcAdapter.getDefaultAdapter(context)

        self.nfc_pending_intent = PendingIntent.getActivity(
            context, 0,
            Intent(context, context.getClass()).addFlags(
                Intent.FLAG_ACTIVITY_SINGLE_TOP
            ),
            0
        )
        self.on_new_intenting = False
        self.resuming = False
        self.nfc_enable_ndef_exchange()
        activity.bind(on_new_intent=self.on_new_intent)

    def register_action(self, action):
        self._action = action

    def remove_action(self, action):
        if self._action == action:
            self._action = None
        else:
            raise ValueError('Action isn\' defined')

    def on_new_intent(self, intent):
        self.on_new_intenting = True
        sleep(0.25)
        while self.resuming:
            sleep(0.1)

        if intent.getAction() != NfcAdapter.ACTION_TAG_DISCOVERED:
            print 'unknow action, avoid.'
            return

        tag_id = ''
        for i in intent.getByteArrayExtra(NfcAdapter.EXTRA_ID).tolist():
            tag_id += hex(i & 0xff)[2:]

        if self._action:
            self._action(tag_id)

        self.on_new_intenting = False

    def nfc_enable_ndef_exchange(self):
        if self.on_new_intenting: # let it run, don't bother about initialising to saved
            return
        self.resuming = True
        print 'Resume'
        inten = Intent(self.j_context, self.j_context.getClass())
        inten.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)

        pen_in = PendingIntent.getActivity(self.j_context, 0, inten, 0)
        filt = []
        filt.append(IntentFilter())
        filt[0].addAction(NfcAdapter.ACTION_TAG_DISCOVERED)
        filt[0].addCategory(Intent.CATEGORY_DEFAULT)
        filt[0].addDataType("text/plain")

        self.nfc_adapter.enableForegroundDispatch(self.j_context, pen_in, filt, [[]])
        self.resuming = False

    def nfc_disable_ndef_exchange(self):
        self.nfc_adapter.disableForegroundDispatch(self.j_context)


if platform == 'android' and not nfc_instance:
    from jnius import autoclass
    from android import activity

    NfcAdapter = autoclass('android.nfc.NfcAdapter')
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    PendingIntent = autoclass('android.app.PendingIntent')

    nfc_instance = NFC()

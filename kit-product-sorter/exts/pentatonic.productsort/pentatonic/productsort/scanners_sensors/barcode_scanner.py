import omni.kit.app

class BarcodeScanners():
    def __init__(self, window):
        self._window = window
        
        self._barcode_scanner_1 = "/World/Barcode_Readers/Barcode_Scanner_01"
        self._barcode_scanner_2 = "/World/Barcode_Readers/Barcode_Scanner_02"

        self._update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_subscription = self._update_stream.create_subscription_to_pop(self.on_update)

        timeline_stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_subscription = timeline_stream.create_subscription_to_pop(self._on_timeline_event)

        self.initMessage = False
        self.captured = False
        
    def on_setup(self):
        stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_subscription = stream.create_subscription_to_pop(self._on_timeline_event)

    def on_update(self, e):
        if self.initMessage is False:
            self.initMessage = True
        #print("Barcode Scanner Updating")
        
    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self.captured = True
        elif e.type == int(omni.timeline.TimelineEventType.STOP):
            self.reset()
        elif e.type == int(omni.timeline.TimelineEventType.PAUSE):
            self.captured = False

    def reset(self):
        pass

    def on_shutdown(self):
        if self._timeline_subscription:
            self._timeline_subscription.unsubscribe()
        if self._update_stream:
            self._update_stream.unsubscribe()
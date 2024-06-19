import omni.kit.app

class ProximitySensors():
    def __init__(self, window):
        self._window = window

        self._slope2_start = "/World/Proximity_Sensors/Sensor_Slope2_Start/Camera_01"
        self._slope2_end = "/World/Proximity_Sensors/Sensor_Slope2_End/Camera_01"

        self._slope1_start = "/World/Proximity_Sensors/Sensor_Slope1_Start/Camera_01"
        self._slope1_end = "/World/Proximity_Sensors/Sensor_Slope1_End/Camera_01"

        self._curve_start = "/World/Proximity_Sensors/Sensor_Curve_Start/Camera_01"
        self._curve_end = "/World/Proximity_Sensors/Sensor_Slope2_End/Camera_01"

        self._station_1 = "/World/Proximity_Sensors/Sensor_Wait_01/Camera_01"
        self._station_2 = "/World/Proximity_Sensors/Sensor_Wait_02/Camera_01"
        self._station_3 = "/World/Proximity_Sensors/Sensor_Wait_03/Camera_01"
        self._station_4 = "/World/Proximity_Sensors/Sensor_Wait_04/Camera_01"
        self._station_5 = "/World/Proximity_Sensors/Sensor_Wait_05/Camera_01" 

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
        #print("Proximity Sensors Updating")
    
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
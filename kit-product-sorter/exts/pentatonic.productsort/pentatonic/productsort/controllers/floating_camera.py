import omni.kit.app
import omni.usd
import omni.ui as ui
import carb

import omni.kit.viewport.utility as vp_utils
from omni.physx import get_physx_scene_query_interface

class FloatingCamera():
    def __init__(self, window):
        self._window = window

        self._stage = omni.usd.get_context().get_stage()
        self._perspective_camera_path = "/OmniverseKit_Persp"
        self._perspective_prim = None

        self._update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_subscription = self._update_stream.create_subscription_to_pop(self.on_update)

        timeline_stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_subscription = timeline_stream.create_subscription_to_pop(self._on_timeline_event)

        self.captured = False
        self.floating_cam_enabled = False
        self._viewport_overlay_frame = None

    def on_update(self, e):
        
        is_playing = omni.timeline.get_timeline_interface().is_playing()

        if not is_playing:
            return

        if self.floating_cam_enabled is True:
            self._perspective_prim = self.get_default_perspective_camera()

            if self._perspective_prim is None:
                return
            
            #self.refresh_crosshair() 
            #self.get_floating_cam_info()
            #print("Floating Camera Update")
            
    def get_default_perspective_camera(self):
        # Get the current stage
        stage = omni.usd.get_context().get_stage()

        # Check if the default camera exists
        if stage.GetPrimAtPath(self._perspective_camera_path):
            return stage.GetPrimAtPath(self._perspective_camera_path)
        else:
            # If the default camera does not exist, look for any camera in the stage
            for prim in stage.Traverse():
                if prim.GetTypeName() == "Camera":
                    return prim
                
        return None
            
    def toggle_floating_camera(self, state):
        self.floating_cam_enabled = state
    
    # Call to retrive floating camera information
    def get_floating_cam_info(self):
        if self._perspective_prim is not None:
            hitInfo = self._calculate_ray(self._perspective_prim)
            if hitInfo is not None:
                print(hitInfo)
            else:
                return

            #return self._perspective_prim.GetAttribute('xformOp:translate').Get()
        
    def _calculate_ray(self, cam_prim):
        if cam_prim.GetAttribute("xformOp:transform").Get() is None:
            return None
        
        xform = cam_prim.GetAttribute("xformOp:transform").Get()

        if xform is None:
            return None

        cameraPos = xform.ExtractTranslation()

        if cameraPos is None:
            return None
   
        cameraForward = -xform.ExtractRotationMatrix().GetRow(2)

        origin = carb.Float3(cameraPos[0], cameraPos[1], cameraPos[2])

        rayDir = carb.Float3(cameraForward[0], cameraForward[1], cameraForward[2])

        hitInfo = get_physx_scene_query_interface().raycast_closest(origin, rayDir, 10000.0)
        return hitInfo
    
    # Sends Floating Camera Information From Update Method
    def set_floating_cam_info(self):
        return
    
    def _cleanup_overlay(self):
        if self._viewport_overlay_frame:
            self._viewport_overlay_frame.visible = False
            self._viewport_overlay_frame = None
        self._viewport_window = None

    # Update Crosshairs
    def refresh_crosshair(self):
        if self.captured is True:
            if not self._viewport_overlay_frame:
                self._viewport_window = vp_utils.get_active_viewport_window()
                self._viewport_overlay_frame = self._viewport_window.get_frame("omni.physx.cct.crosshair_frame")
                self._viewport_overlay_frame.visible = True
                with self._viewport_overlay_frame:
                    with ui.Placer(offset_x=ui.Percent(50), offset_y=ui.Percent(50)):
                        self._crosshair = ui.Circle(width=10, height=10, radius=10, style={"background_color": 4286548735})
        elif self._viewport_overlay_frame:
            self._cleanup_overlay()
    
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
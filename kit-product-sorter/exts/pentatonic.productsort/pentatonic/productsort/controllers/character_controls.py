import omni.ui as ui
import omni.kit.app
from pxr import Usd, UsdGeom, Gf, UsdPhysics, PhysxSchema, Vt, Sdf, UsdUtils, PhysicsSchemaTools
import json
import carb.events
import carb.input
import omni.physxcct.scripts.utils as cct_utils
import omni.kit.viewport.utility as vp_utils
from omni.kit.viewport.utility.camera_state import ViewportCameraState
import omni.timeline
import carb.windowing
from carb.input import MouseEventType, EVENT_TYPE_ALL, KeyboardInput
from omni.physx import get_physx_scene_query_interface
import omni.physx.scripts.utils as core_utils
import omni.kit.commands
from ..utilities.product_creation import initialize_objects
from ..utilities.product_creation import create_target
from ..utilities.assets import *

class CharacterController():
    def __init__(self, window):
        self._window = window
        self.target_pos = None

        update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_subscription = update_stream.create_subscription_to_pop(self.on_update)
        self._timeline_subscription = None
        self.captured = False

        # Input commands
        self.shoot = False  # Left Mouse
        self.place = False  # Right Mouse
        self.isShowing = False  # Showing Target
        self.click_count = 0

        self.cycle_up = False
        self.cycle_down = False
        self.key_1 = True
        self.key_2 = False

        self._rotation = None
        self._position = None
        self._rigidBody = None

        # Input Subscriptions
        self._mouse_sub = None
        self.input_iface = None
        self._keyboard_sub = None

        self._viewport_overlay_frame = None
        self._cct = None
        self.cct_prim = None
        self.cct_path = "/World/ThridPerson/capsuleActor"
        self.sphere_path = "/World/ThridPerson/Target"
        self.sphere = None
        self.radius = 2
        
        # Composure
        self.capsule_h = 100
        self.capsule_w = 50
        self.mouse_sensitivity = 15
        self.gamepad_sensitivity = 15
        self.capsule_spawn_x = 500
        self.capsule_spawn_y = 0
        self.capsule_spawn_z = 250
        self.cct_speed = 400

        self.rotate = 0
        self.live_preview = False

        self.target_object_prim = None
        self.container_type = None
        self.jsonData = None
        self.container_data = None
        
    def set_target(self, position, rotation, rigidBody, onPlace):
        self._window.set_target(position, rotation, rigidBody, onPlace)

    def set_key_command(self, event):
        self._window.set_key_command(event)

    def on_shutdown(self):
        self._cleanup_input_subscriptions()
        self._cleanup_overlay()

        if self._cct:
            self._cct.disable()
            self._cct.shutdown()
            self._cct = None
            self.cct_prim = None
            
    def _cleanup_input_subscriptions(self):
        if self.input_iface is None:
            self.input_iface = carb.input.acquire_input_interface()

        if self._mouse_sub:
            self.input_iface.unsubscribe_to_input_events(self._mouse_sub)
            self._mouse_sub = None

        if self._timeline_subscription:
            self._timeline_subscription.unsubscribe()

    def on_spawn(self, use_thrid_person_controller, using_isaac, live_preview, container_type):
        print("On Spawn Called")
        # Cleanup any previous subscriptions
        self._cleanup_input_subscriptions()

        if use_thrid_person_controller is True:
            print("Thrid Person: True")
        else:
            print("Thrid Person: False")

        #print("CCT Path: " + self.cct_prim)

        if use_thrid_person_controller and self.cct_prim is None:
            print("Passed Test 1")
            if using_isaac is True:
                self.mouse_sensitivity = 10
                self.gamepad_sensitivity = 10
                self.capsule_h = 1
                self.capsule_w = 0.5
                self.radius = 0.05
                self.capsule_spawn_x = -5
                self.capsule_spawn_y = -5
                self.capsule_spawn_z = 2
                self.cct_speed = 5
            
            self.live_preview = live_preview
            stage = omni.usd.get_context().get_stage()
        
            prim = cct_utils.spawn_capsule(stage, self.cct_path, Gf.Vec3f(self.capsule_spawn_x, self.capsule_spawn_y, self.capsule_spawn_z), self.capsule_h, self.capsule_w)
            
            camera_path = "/OmniverseKit_Persp"
            self._cct = cct_utils.CharacterController(self.cct_path, camera_path, True, 0.01)
            self._cct.activate(stage)
            
            stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
            self._timeline_subscription = stream.create_subscription_to_pop(self._on_timeline_event)
            self.appwindow = omni.appwindow.get_default_app_window()

            self._mouse = self.appwindow.get_mouse()

            self.input_iface = carb.input.acquire_input_interface()
            self._mouse_sub = self.input_iface.subscribe_to_input_events(self._mouse_info_event_cb, EVENT_TYPE_ALL, self._mouse, 0)

            print("Passed Test 2")
            rebind={
                "Forward": KeyboardInput.W,
                "Backward": KeyboardInput.S,
                "Right": KeyboardInput.D,
                "Left": KeyboardInput.A,
                "Up": KeyboardInput.E,
                "Down": KeyboardInput.Q,
                "Key1" : KeyboardInput.KEY_1,
                "Key2" : KeyboardInput.KEY_2,
                "CycleUp": KeyboardInput.UP,
                "PageCycleUp" : KeyboardInput.PAGE_UP,
                "CycleDown": KeyboardInput.DOWN,
                "PageCycleDown" : KeyboardInput.PAGE_DOWN,
            }

            # Setting Up Controls
            self._cct.setup_controls(self.cct_speed, cct_utils.ControlFlag.DEFAULT, rebind)

            # Registering New Keyboard Commands
            self._cct.control_state.register_keyboard_action("kbKey1", rebind["Key1"], 0, self._keyboard_key1_event_cb)
            self._cct.control_state.register_keyboard_action("kbKey2", rebind["Key2"], 0, self._keyboard_key2_event_cb)
            self._cct.control_state.register_keyboard_action("kbKeyUpArrow", rebind["CycleUp"], 0, self._keyboard_keyUp_event_cb)
            self._cct.control_state.register_keyboard_action("kbKeyUpArrow", rebind["PageCycleUp"], 0, self._keyboard_keyUp_event_cb)
            self._cct.control_state.register_keyboard_action("kbKey2DownArrow", rebind["CycleDown"], 0, self._keyboard_keyDown_event_cb)
            self._cct.control_state.register_keyboard_action("kbKey2DownArrow", rebind["PageCycleDown"], 0, self._keyboard_keyDown_event_cb)
            self._cct.control_state.mouse_sensitivity = self.mouse_sensitivity
            self._cct.control_state.gamepad_sensitivity = self.gamepad_sensitivity * 10

            self.cct_prim = stage.GetPrimAtPath(self.cct_path)
            omni.timeline.get_timeline_interface().play()
            # reset camera pos and view
            customLayerData = {
                "cameraSettings": {
                    "Perspective": {"position": Gf.Vec3d(2407, 2407, 2638), "radius": 500, "target": Gf.Vec3d(0, 0, 0)},
                    "boundCamera": "/OmniverseKit_Persp",
                }
            }
            stage.GetRootLayer().customLayerData = customLayerData
            
            print("Passed Test 3")
            self.container_type = container_type
            self.jsonData = json.loads(json.dumps(AssetPresets))
            self.container_data = self.jsonData['Containers'][self.container_type]

            if self.live_preview is True:
                self._create_target_object()

        elif use_thrid_person_controller and self.cct_prim is not None:
            omni.timeline.get_timeline_interface().play()
        
        else:
            pass

    # Creates object
    def _create_target_object(self):

        if self.target_object_prim is not None:
            print("Target Object Prim Is Not None")
            return
        
        else:
            print("Creating Target")
            self.target_object_prim = create_target()

    def _cleanup_overlay(self):
        if self._viewport_overlay_frame:
            self._viewport_overlay_frame.visible = False
            self._viewport_overlay_frame = None
        self._viewport_window = None

    # Update Crosshairs
    def refresh_crosshair(self, is_playing):
        if is_playing:
            if not self._viewport_overlay_frame:
                print("Refresh Crosshairs: Viewport Overlay Frames")
                self._viewport_window = vp_utils.get_active_viewport_window()
                self._viewport_overlay_frame = self._viewport_window.get_frame("omni.physx.cct.crosshair_frame")
                self._viewport_overlay_frame.visible = True
                with self._viewport_overlay_frame:
                    with ui.Placer(offset_x=ui.Percent(50), offset_y=ui.Percent(50)):
                        self._crosshair = ui.Circle(width=10, height=10, radius=10, style={"background_color": 4286548735})
        elif self._viewport_overlay_frame:
            self._cleanup_overlay()

    def on_update(self, e):
        is_playing = omni.timeline.get_timeline_interface().is_playing()

        if not is_playing:
            return

        # Add cross hairs
        self.refresh_crosshair(is_playing)
            
        stage = omni.usd.get_context().get_stage()

        # Ray Casting
        camera_prim = stage.GetPrimAtPath(vp_utils.get_active_viewport_camera_path())
        camera_th = core_utils.CameraTransformHelper(camera_prim)
        cameraPos = camera_th.get_pos()
        cameraForward = camera_th.get_forward()

        origin = carb.Float3(cameraPos[0], cameraPos[1], cameraPos[2])
        rayDir = carb.Float3(cameraForward[0], cameraForward[1], cameraForward[2])

        hitInfo = get_physx_scene_query_interface().raycast_closest(origin, rayDir, 10000.0)

        if hitInfo["hit"]:
            if self.live_preview is True:
                self.update_target_object(is_playing, hitInfo["position"], hitInfo["rigidBody"])
            else:
                return
        
    def create_sphere_target(self, is_playing, stage, position, rigidBody):
        if is_playing:
            if self.shoot:
                self.shoot = False
                if position is not None:
                    self._position = position
        
                if rigidBody is not None:
                    self._rigidBody = rigidBody

                if self.sphere is None:
                    sphere_geom = UsdGeom.Sphere.Define(stage, self.sphere_path)
                    sphere_geom.CreateRadiusAttr(self.radius)
                    self.targetTranslateOP = sphere_geom.AddTranslateOp()
                    self.sphere = sphere_geom

                if self.targetTranslateOP:
                    self.targetTranslateOP.Set(Gf.Vec3d(self._position[0], self._position[1], self._position[2]))

                # Shoot = Left Mouse Click. This will ether create/set the new target and send the new target info to the 
                # window class
                self.set_target(self._position, self._rotation, self._rigidBody, False)
            
            if self.place:
                self.place = False
                # Product Placement requires position value to be sent, Material requires rigid body for prim path
                if (self.key_1 and self._position is not None) or (self.key_2 and self._rigidBody is not None):
                    self.set_target(self._position, self._rotation, self._rigidBody, True)

    def update_target_object(self, is_playing, position, rigidBody):
        if is_playing:
            if self.target_object_prim is None or self.target_object_prim.GetAttribute('xformOp:translate') is None:
                return
            
            else:
                # Two Left Clicks = Show Sample and move with mouse controls
                if self.isShowing and position is not None:
                    # If user has Clicked Left once and Clicks Right then it cancels the action.
                    if self.place:
                        self.place = False
                        self.isShowing = False
                        self.shoot = False
                        
                        self.target_object_prim.GetAttribute("visibility").Set("invisible")
                        return

                    # If user has Clicked Left Click once and Position value is not None then update the target pos.
                    self._position = position
                    self._rigidBody = rigidBody

                    self._position = Gf.Vec3d(self._position[0], self._position[1], self._position[2])
                    self.target_object_prim.GetAttribute('xformOp:translate').Set(self._position)
                    
                    # Rotate Object With Mouse Wheel Rotate on Z Axis only
                    valU = self.input_iface.get_mouse_value(self._mouse, carb.input.MouseInput.SCROLL_UP)
                    if valU:
                        self.rotate = self.rotate + (valU * 4)

                    valD = self.input_iface.get_mouse_value(self._mouse, carb.input.MouseInput.SCROLL_DOWN)
                    if valD:
                        self.rotate = self.rotate - (valD * 4)
                    
                    self._rotation = Gf.Vec3d(0, 0, self.rotate)
                    self.target_object_prim.GetAttribute('xformOp:rotateXYZ').Set(self._rotation)

                    if self.shoot:
                        self.set_target(self._position, self._rotation, self._rigidBody, True)
                        self.shoot = False
                
    # Bug fix, currently gets called 3 times for every button press
    def _keyboard_key1_event_cb(self, event_in):
        if self.captured:
            self.key_1 = True
            self.key_2 = False
            self.set_key_command("KEY_1")
            print("key 1")
        return False  # Stop propagation

    def _keyboard_key2_event_cb(self, event_in):
        if self.captured:
            self.key_1 = False
            self.key_2 = True
            self.set_key_command("KEY_2")   
            print("Key 2")
        return False  # Stop propagation

    def _keyboard_keyUp_event_cb(self, event_in):
        if self.captured:
            self.set_key_command("CYCLE_UP")
            print("Cycle Up")
        return False  # Stop propagation

    def _keyboard_keyDown_event_cb(self, event_in):
        if self.captured:
            self.set_key_command("CYCLE_DOWN")
            print("Cycle Down")
        return False  # Stop propagation

    def _mouse_info_event_cb(self, event_in, *args, **kwargs):
        if self.captured:
            event = event_in.event
            if event.type == MouseEventType.SCROLL:
                print()

            if event.type == MouseEventType.LEFT_BUTTON_DOWN:
                print("Left Mouse Click")
                if self.isShowing is True:
                    self.shoot = True

                elif self.target_object_prim is not None:
                    self.target_object_prim.GetAttribute("visibility").Set("visible")
                    self.isShowing = True
            
            if event.type == MouseEventType.RIGHT_BUTTON_DOWN:
                print("Right Mouse Click")
                self.place = True
             
        return not self.captured

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self.captured = True
        elif e.type == int(omni.timeline.TimelineEventType.STOP):
            self.reset()
        elif e.type == int(omni.timeline.TimelineEventType.PAUSE):
            self.captured = False

    def reset(self):
        self.cct_prim = None
        self.captured = False
        self.shoot = False
        self.place = False
        self.key_1 = True
        self.key_2 = False
        self.isShowing = False  # Showing Target
        self.target_object_prim = None
        self.container_type = None
        self.jsonData = None
        self.container_data = None
        self._rotation = None
        self._position = None
        self._rigidBody = None

    def destroy(self):
        self.on_shutdown()

import omni.kit.app
import json
import random
import uuid
from pxr import  Gf, UsdGeom, Usd

from .assets import *
from .utils import set_transformTRS_attrs, add_usd_physics_if_needed

class ProductSpawner():
    def __init__(self, window):
        self._window = window
        stage = omni.usd.get_context().get_stage()

        self._hopper_spawning = False
        self._generation = None

        self._hopper_spawn_path = "/World/product_spawn"
        self._hopper_spawn_prim = None
        self._spawn_position = None

        self._update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_subscription = self._update_stream.create_subscription_to_pop(self.on_update)

        timeline_stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_subscription = timeline_stream.create_subscription_to_pop(self._on_timeline_event)

        self.initMessage = False
        self.captured = False
        self.frames = 0
        self.frame_rate = 320
        self.spawn_rate_per_sec = 320
        self._product_list = ['Plate_1x1', 'Block_1x2', 'Block_2x3', 'Degree_2x2_45', 'Plate_2x4', 'Plate_6x8']
        self._product_urls = ['omniverse://localhost/Projects/Medusa/Lego/Plate_1x1.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Block_1x2.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Degree_2x2_45.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Block_2x3.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Plate_2x4.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Plate_6x8.usdc']


    def on_setup(self):
        return
    
    def on_toggle(self, state):
        stage = omni.usd.get_context().get_stage()

        self._hopper_spawn_prim = stage.GetPrimAtPath(self._hopper_spawn_path)

        if self._hopper_spawn_prim is not None:
            self._spawn_position = self._hopper_spawn_prim.GetAttribute('xformOp:translate').Get()

        self._item_data = json.loads(json.dumps(AssetPresets))

        self._hopper_spawning = state 

    def on_update(self, e):
        is_playing = omni.timeline.get_timeline_interface().is_playing()

        if self._hopper_spawning is False or not is_playing:
            return
        
        self.frames += 1
        
        if self.frames == self.frame_rate/self.spawn_rate_per_sec:
            print("Hopper Spawning")
            self.frames = 0
            
            random_num = random.randint(0, 5)
            item_random = self._product_list[random_num]
            
            #item = self._item_data['Products'][self._generation['product_type']][item_random]
            unique_number = str(uuid.uuid4().int)[:5]
            object_path = '/World/Items/'

            path = object_path + item_random + "_" + unique_number
            prim = self.create_new_prim(path)

            references: Usd.references = prim.GetReferences()
            references.AddReference(assetPath=self._product_urls[random_num])

            set_transformTRS_attrs(prim, Gf.Vec3d(self._spawn_position[0], self._spawn_position[1], self._spawn_position[2] - 0.25), Gf.Vec3d(0, 0, 0), Gf.Vec3d(1.0,1.0,1.0))
            add_usd_physics_if_needed(prim)
            
    def create_new_prim(self, prim_path):
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        prim = stage.DefinePrim(prim_path) 
        xform = UsdGeom.Xform.Define(stage, prim_path)

        if not prim.GetAttribute('xformOp:transform'):
            xform.AddTransformOp()
        if not prim.GetAttribute('xformOp:translate'):
            xform.AddTranslateOp()
        if not prim.GetAttribute('xformOp:scale'):
            xform.AddScaleOp()
        if not prim.GetAttribute('xformOp:rotateXYZ'):
            xform.AddRotateXYZOp()

        return prim

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self.captured = True
        elif e.type == int(omni.timeline.TimelineEventType.STOP):
            self.reset()
        elif e.type == int(omni.timeline.TimelineEventType.PAUSE):
            self.captured = False

    def reset(self):
        self._hopper_spawning = False
        self._generation = None
        self._hopper_spawn_prim = None
        self._spawn_position = None

    def on_shutdown(self):
        self._hopper_spawning = False
        self._generation = None
        self._hopper_spawn_prim = None
        self._spawn_position = None

        if self._timeline_subscription:
            self._timeline_subscription.unsubscribe()
        if self._update_stream:
            self._update_stream.unsubscribe()
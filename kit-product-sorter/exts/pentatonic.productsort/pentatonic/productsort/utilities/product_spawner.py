import omni.kit.app
import json
import random
import uuid
from pxr import  Gf, UsdGeom, Usd
import asyncio
from omni.isaac.range_sensor import _range_sensor

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

        self._lidarInterface = _range_sensor.acquire_lidar_sensor_interface()

        self.initMessage = False
        self.captured = False
        self.frames = 0
        self.frame_rate = 320
        self.spawn_rate_per_sec = 320
        self._default_list = ['Plate_1x1', 'Block_1x2', 'Block_2x3', 'Degree_2x2_45', 'Plate_2x4', 'Plate_6x8']
        self._product_list = []
        self._product_urls = ['omniverse://localhost/Projects/Medusa/Lego/Plate_1x1.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Block_1x2.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Degree_2x2_45.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Block_2x3.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Plate_2x4.usdc', 'omniverse://localhost/Projects/Medusa/Lego/Plate_6x8.usdc']
        self._urls = []
        self._lego_colors = [
            "720E0F", "631314", "FEBABD", "FECCCF", "BD7D85", "FF879C", "D60026", "FC97AC", "FF0040", "FF698F", "F785B1", "DF6695", "FE78B0", "CD6298", "E4ADC8", "C870A0", "CE1D9B", "923978", "AA4D8E", "81007B", "845E84", 
            "8E5597", "96709F", "AC78BA", "8320B7", "4B0082", "E1D5ED", "5F27AA", "8D73B3", "4D4C52", "3F3691", "9391E4", "A5A5CB", "C9CAE2", "9195CA", "2032B0", "6874CA", "4C61DB", "0020A0", "4354A3", "AfB5C7", "0A1327", 
            "6074A1", "7988A1", "7396c8", "0055BF", "5A93DB", "0A3463", "B4D4F7", "CFE2F7", "61AFFF", "6e8aa6", "9FC3E9", "0057A6", "6C96BF", "0059A3", "B4D2E3", "C1DFF0", "3592C3", "5f7d8c", "078BC9", "1591cb", "0d4763", 
            "68AECE", "467083", "7DBFDD", "354e5a", "3E95B6", "009ECE", "039CBD", "5AC4DA", "36AEBF", "55A5AF", "68BCC5", "008F9B", "10929d", "AEEFEC", "27867E", "ADC3C0", "B3D7D1", "3FB69E", "a7dccf", "a3d1c0", "184632", 
            "3CB371", "73DCA1", "008E3C", "A0BCAC", "468A5F", "237841", "94E5AB", "60BA76", "84B68D", "006400", "1E601E", "78FC78", "627a62", "4B9F4A", "C2DAB8", "7DB538", "BDC6AD", "879867", "6C6E68", "7C9051", "C9E788", 
            "6A7944", "899B5F", "C0F500", "BBE90B", "DFEEA5", "D9E4A7", "C7D23C", "f5fab7", "BDC618", "b2b955", "6D6E5C", "9B9A5A", "FFF230", "F8F184", "EBD800", "FFF03A", "f9f1c7", "BBA53D", "FBE890", "DAB000", "F3C305", 
            "FFCF0B", "F5CD2F", "E4CD9E", "FFE371", "FBE696", "b4a774", "cdc298", "FED557", "DBAC34", "5C5030", "F8BB3D", "E4CD9E", "958A73", "AA7F2E", "DCBC81", "FFA70B", "DEC69C", "352100", "DD982E", "FFCB78", "F3C988", 
            "B46A00", "FA9C1C", "F9BA61", "AC8247", "F3CF9B", "645A4C", "bb771b", "907450", "F08F1C", "EF9121", "CCA373", "F6D7B3", "FCB76D", "A95500", "FE8A18", "F7AD63", "B48455", "737271", "FF800D", "FF8014", "AA7D55", 
            "B67B50", "755945", "AB673A", "D09168", "F45C40", "CA1F08", "F2705E", "945148", "C91A09", "B31004", "B52C20", "D67572", "8B0000", "330000", "FFFFFF", "FCFCFC", "F2F3F2", "c01111", "E6E3DA", "E6E3E0", "E0E0E0", 
            "D4D5C9", "A5ADB4", "A5A9B4", "ABADAC", "A0A5A9", "9CA3A8", "9BA19D", "898788", "d06262", "6D6E5C", "6C6E68", "635F52", "595D60", "575857", "3E3C39", "1B2A34", "6B5A5A", "05131D", "05131D", "05131D", "05131D", 
            "05131D", "FFFFFF", "FCFCFC", "F4F4F4", "D9D9D9", "9C9C9C", "9C9C9C", "616161", "5e5e5e"
        ]

    def on_setup(self):
        return
    
    def on_toggle(self, state, product_list):
        stage = omni.usd.get_context().get_stage()
        if state is False:
            self._product_list.clear()
            self._urls.clear()

        if len(product_list) > 0:
            self._product_list = product_list
            for name in self._product_list:
                for url in self._product_urls:
                    if name in url:
                        self._urls.append(url)
                        break
        else:
            self._product_list = self._default_list

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
            self.frames = 0
            
            random_num = random.randint(0, len(self._product_list) - 1)
            item_random = self._product_list[random_num] 
            
            #item = self._item_data['Products'][self._generation['product_type']][item_random]
            unique_number = str(uuid.uuid4().int)[:5]
            object_path = '/World/Items/'

            path = object_path + item_random + "_" + unique_number
            prim = self.create_new_prim(path)

            references: Usd.references = prim.GetReferences()
            references.AddReference(assetPath=self._urls[random_num])
            rand_x = random.uniform(self._spawn_position[0] - 0.15, self._spawn_position[0] + 0.15)
            rand_y = random.uniform(self._spawn_position[1] - 0.15, self._spawn_position[1] + 0.15)
            rand_rot = random.uniform(0, 359)

            set_transformTRS_attrs(prim, Gf.Vec3d(rand_x, rand_y, self._spawn_position[2] - 0.25), Gf.Vec3d(rand_rot, rand_rot, rand_rot), Gf.Vec3d(1.0,1.0,1.0))
            add_usd_physics_if_needed(prim)
            
    def create_new_prim(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        
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
    
    async def get_lidar_param(self):
        await omni.kit.app.get_app().next_update_async()
        omni.timeline.TimelineEventType.PAUSE
        depth = self._lidarInterface.get_linear_depth_data("/World/Lidar")
        zenith = self._lidarInterface.get_zenith_data("/World/Lidar")
        azimuth = self._lidarInterface.get_azimuth_data("/World/Lidar")
        print("depth", depth)
        print("zenith", zenith)
        print("azimuth", azimuth)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            asyncio.ensure_future(self.get_lidar_param())
            self.captured = True
        elif e.type == int(omni.timeline.TimelineEventType.STOP):
            stage = omni.usd.get_context().get_stage()
            if stage.GetPrimAtPath("/World/Items"):
                omni.kit.commands.execute('DeletePrimsCommand', paths=["/World/Items"])
            if stage.GetPrimAtPath("/World/Containers"):
                omni.kit.commands.execute('DeletePrimsCommand', paths=["/World/Containers"])

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
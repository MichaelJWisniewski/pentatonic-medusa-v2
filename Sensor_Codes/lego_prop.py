import omni
import asyncio
# importing the python bindings to interact with lidar sensor
from omni.isaac.range_sensor import _range_sensor
# pxr imports used to create cube
from pxr import UsdGeom, Gf, UsdPhysics, Sdf, Semantics
import omni.replicator.core as rep
from omni.isaac.core.utils.semantics import add_update_semantics

# ==== Stage Creation ====

stage = omni.usd.get_context().get_stage()

# ===== Communication with the LiDAR sensor (Sensor Creation) =====

lidarInterface = _range_sensor.acquire_lidar_sensor_interface()
timeline = omni.timeline.get_timeline_interface()
omni.kit.commands.execute('AddPhysicsSceneCommand',stage = stage, path='/World/PhysicsScene')
lidarPath = "/LidarName"
result, prim = omni.kit.commands.execute(
            "RangeSensorCreateLidar",
            path=lidarPath,
            parent="/World",
            min_range=0.4,
            max_range=100.0,
            draw_points=False,
            draw_lines=True,
            horizontal_fov=360.0,
            vertical_fov=30.0,
            horizontal_resolution=0.4,
            vertical_resolution=4.0,
            rotation_rate=0.0,
            high_lod=False,
            yaw_offset=0.0,
            enable_semantics=False
        )
print(prim)
print(result)


# ===== Ground Plane, Light Setup, Lego Generation and Adding Properties =====

with rep.new_layer():
    
    ground_plane_path = "C:\\Users\\ov-user\\Documents\\Neurologic\\Soulina\\Synthetic_data_generation\\ground_plane.usd"
    ground_plane = rep.create.from_usd(ground_plane_path, semantics=[("class", "ground_plane")], count=1)


    sphere_light = rep.create.light(
            light_type="Sphere",
            temperature=rep.distribution.normal(6500, 500),
            intensity=rep.distribution.normal(35000, 5000),
            position=(0,0,100),
            scale=rep.distribution.uniform(50, 100),
            count=1
            )


    usd_path = "C:\\Users\\ov-user\\Documents\\Neurologic\\Akash\\AK07_2.0\\Sensor_Codes\\Sensor_Codes\\Lego bricks\\lego_brick_2x4AK.usd"
    lego = rep.create.from_usd(usd_path, semantics=[("class", "lego")])
    

    def get_shapes():
        shapes = rep.get.prims(semantics=[("class", "lego")])
        with shapes:
            rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))
            rep.modify.pose(position=(2.3, 1, 0.4),
                            rotation=(0,0,0),
                            scale=(1, 1, 1))
            # rep.physics.rigid_body(velocity=(0, 0, 0))
        return shapes.node

    rep.randomizer.register(get_shapes)
    rep.randomizer.get_shapes()




# ===== Python Script Attach process ===== 

lego_path2 = "/Replicator/Ref_Xform_01/Ref/lego_brick_2x4"
prim = stage.GetPrimAtPath(lego_path2)
prim_paths = [prim.GetPath()]
omni.kit.commands.execute("ApplyScriptingAPICommand", paths=prim_paths)
omni.kit.commands.execute("RefreshScriptingPropertyWindowCommand")

# Add script
# Create and add script attribute
script_file_path = "C:\\Users\\ov-user\\Documents\\Neurologic\\Akash\\AK07_2.0\\Sensor_Codes\\Sensor_Codes\\ABS_material.py"
scripts = Sdf.AssetPathArray([script_file_path])
scriptAttr = prim.CreateAttribute("omni:scripting:scripts", Sdf.ValueTypeNames.AssetArray)
scriptAttr.Set(scripts)
    

# ==== Properties Extraction ====


def print_lego_properties():
    lego_path2 = "/Replicator/Ref_Xform_01/Ref/lego_brick_2x4"
    legoPrim = stage.GetPrimAtPath(lego_path2)
    if not legoPrim.IsValid():
        print("Lego object not found.")
        return

    print(f"Properties of the lego object at {lego_path2}:")
    for prop in legoPrim.GetAttributes():
        print(f"{prop.GetName()}: {prop.Get()}")
        
    # Run the ABS_material.py script
    print(f"Running script: {script_file_path}")
    with open(script_file_path, 'r') as file:
        script_content = file.read()
        exec(script_content, globals())

# print_lego_properties()


# ==== Adding Semantics Property ====

if lego:
    lego_path2 = "/Replicator/Ref_Xform_01/Ref/lego_brick_2x4"
    legoPrim = stage.GetPrimAtPath(lego_path2)
    add_update_semantics(legoPrim, "lego1")

    semantic_api = Semantics.SemanticsAPI.Get(legoPrim, "Semantics")
    type_attr = semantic_api.GetSemanticTypeAttr()
    data_attr = semantic_api.GetSemanticDataAttr()
    z1=data_attr.Get()

print(f"semantic type: {type_attr.Get()}, semantic data: {data_attr.Get()}")





# ===== Interaction with LiDAR Sensor =====

async def get_lidar_param(z1):
    await omni.kit.app.get_app().next_update_async()
    timeline.pause()
    depth = lidarInterface.get_linear_depth_data("/World"+lidarPath)
    zenith = lidarInterface.get_zenith_data("/World"+lidarPath)
    azimuth = lidarInterface.get_azimuth_data("/World"+lidarPath)
    semantics = lidarInterface.get_prim_data("/World"+lidarPath)
    if depth is not None:
        if z1 == "lego1" and lego:
            print("LIDAR Interaction Detected!")
            print_lego_properties()
        else:
            print("LIDAR Interaction Detected!")
            print("Different Object")
    print("Semantics:- ",semantics)
    # Depth: This typically refers to the distance measurements obtained by the LiDAR sensor.
    # print("Depth", depth)
    # Zenith: In LiDAR terminology, zenith usually refers to the vertical angle relative to the sensor's vertical axis.
    # print("Zenith", zenith)
    # Azimuth: This is the angle in the horizontal plane (parallel to the ground).
    # print("Azimuth", azimuth)
timeline.play()
asyncio.ensure_future(get_lidar_param(z1))
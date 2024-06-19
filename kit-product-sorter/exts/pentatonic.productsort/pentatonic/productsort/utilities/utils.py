from pxr import UsdGeom, Gf, UsdPhysics, PhysxSchema
import carb
import omni
from .assets import *
import omni.kit.commands

def create_prim(prim_path, prim_type='Xform'):
    print(prim_path)
    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    prim = stage.DefinePrim(prim_path)
    if prim_type == 'Xform':
        xform = UsdGeom.Xform.Define(stage, prim_path)
    else:
        xform = UsdGeom.Cube.Define(stage, prim_path)
    create_transformOps_for_xform(xform, prim)
    return prim

def create_transformOps_for_xform(xform, prim):
    if prim.GetAttribute('xformOp:translate') is None:
        xform.AddTranslateOp()
    if prim.GetAttribute('xformOp:rotateXYZ') is None:
        xform.AddRotateXYZOp()
    if prim.GetAttribute('xformOp:scale') is None:
        xform.AddScaleOp()

def set_transformTRS_attrs(prim, translate: Gf.Vec3d = Gf.Vec3d(0,0,0), rotate: Gf.Vec3d=Gf.Vec3d(0,0,0), scale: Gf.Vec3d=Gf.Vec3d(1,1,1)):
    prim.GetAttribute('xformOp:translate').Set(translate)
    prim.GetAttribute('xformOp:rotateXYZ').Set(rotate)
    prim.GetAttribute('xformOp:scale').Set(scale)

def get_bounding_box_dimensions(prim_path: str):
    min_coords, max_coords = get_coords_from_bbox(prim_path)

    #Min & Max Coords
    length = max_coords[0] - min_coords[0]
    width = max_coords[1] - min_coords[1]
    height = max_coords[2] - min_coords[2]
    return length, width, height

def get_coords_from_bbox(prim_path: str):
    ctx = omni.usd.get_context()
    bbox = ctx.compute_path_world_bounding_box(str(prim_path))
    min_coords, max_coords = bbox
    return min_coords, max_coords

def add_usd_physics_if_needed(prim):
    # Check if the prim already has a CollisionAPI
    collision_api = UsdPhysics.CollisionAPI(prim)
    rigid_body_api = UsdPhysics.RigidBodyAPI(prim)

    if not collision_api:
        # If it doesn't have a CollisionAPI, add one
        collision_api = UsdPhysics.CollisionAPI.Apply(prim)
    else:
        print("CollisionAPI already exists for", prim.GetPath()) 
    
    if not rigid_body_api:
        # If it doesn't have a RigidBodyAPI, add one
        physicsAPI = UsdPhysics.RigidBodyAPI.Apply(prim)
        PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
    else:
        print("RigidBodyAPI already exists for", prim.GetPath())
    
def scale_object_if_needed(prim):
    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    prim_path = prim.GetPath()

    length, width, height = get_bounding_box_dimensions(prim_path)
    largest_dimension = max(length, width, height)
    if largest_dimension < 10:
        # HACK: All Get Attribute Calls need to check if the attribute exists and add it if it doesn't
        if prim:
            scale_attr = prim.GetAttribute('xformOp:scale')
            
            if scale_attr:
                current_scale = scale_attr.Get()
                if current_scale is None:
                    scale_attr.Set(Gf.Vec3d(1,1,1))

                new_scale = (current_scale[0] * 100, current_scale[1] * 100, current_scale[2] * 100)

                scale_attr.Set(new_scale)

                carb.log_info(f"Scaled object by 100 times: {prim_path}")
            else:
                carb.log_info(f"Scale attribute not found for prim at path: {prim_path}")
        else:
            carb.log_info(f"Invalid prim at path: {prim_path}")
    else:
        carb.log_info(f"No scaling needed for object: {prim_path}")
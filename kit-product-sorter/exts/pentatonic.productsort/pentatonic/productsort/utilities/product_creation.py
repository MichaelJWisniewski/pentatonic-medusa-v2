from .assets import *
from .utils import set_transformTRS_attrs, add_usd_physics_if_needed

from pxr import  Gf, UsdGeom, Usd, UsdPhysics, PhysxSchema
import omni.kit.commands
import carb
import uuid
import json
import random
import time
import numpy as np
#Height = Depth
#Width = Height
#length = Width

def create_new_prim(prim_path):
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
            

#Height = Depth
#Width = Height
#length = Width
def create_target(position: Gf.Vec3d = Gf.Vec3d(0,0,0)):
    jsonData = json.loads(json.dumps(AssetPresets))
    target_data = jsonData['Containers']['Target']
    
    object_path = '/World/Target'
    prim = create_new_prim(object_path)
    prim.GetAttribute("visibility").Set("invisible")
    
    if target_data is not None:
        references: Usd.references = prim.GetReferences()
        references.AddReference(assetPath=target_data['url'])
        
    else:
        carb.log_warn("Product is not valid")
        return

    set_transformTRS_attrs(prim, position, Gf.Vec3d(0,0,0), Gf.Vec3d(1.0,1.0,1.0))

    return prim

# Requires Container Name, Container JSON, Position, Rotation, List of Products to reference, and product type
def spawn_container(generation, position: Gf.Vec3d = Gf.Vec3d(0,0,0), rotation: Gf.Vec3d = Gf.Vec3d(0,0,0)):
    item_data = json.loads(json.dumps(AssetPresets))
    if generation == 'None':
        container_data = item_data['Containers']['Cardboard_Box']
    else:
        container_data = item_data['Containers'][generation['container']]

    unique_number = str(uuid.uuid4().int)[:3]
    object_path = '/World/Containers/'
    path = object_path + generation['container'] + "_" + unique_number
    
    prim = create_new_prim(path)
    
    if container_data is not None:
        references: Usd.references = prim.GetReferences()
        references.AddReference(assetPath=container_data['url'])
        
    else:
        carb.log_warn("Product is not valid")
        return

    set_transformTRS_attrs(prim, position, rotation, Gf.Vec3d(1.0,1.0,1.0))
    #add_usd_physics_if_needed(prim)

    return prim, path
    
'''
data = {
    'container':self.current_container,
    'container_fill':self.current_container_fill,
    'product_type':self.current_product,
    'product_list':self.product_list
}
'''

def test(generation, container_prim, container_path):
    count = 100
    item_data = json.loads(json.dumps(AssetPresets))
    container_data = item_data['Containers'][generation['container']]

    for i in range(count):
        item_random = random.choice(generation['product_list'])
        item = item_data['Products'][generation['product_type']][item_random]

        unique_number = str(uuid.uuid4().int)[:5]

        object_path = '/World/Items/'

        path = object_path + item_random + "_" + unique_number
        print(path)
        prim = create_new_prim(path)

        if item is not None:
            references: Usd.references = prim.GetReferences()
            references.AddReference(assetPath=item['url'])

        position = container_prim.GetAttribute('xformOp:translate').Get()
        item_pos = Gf.Vec3d(position[0], position[1], position[2] + float(container_data['height']))

        set_transformTRS_attrs(prim, item_pos, Gf.Vec3d(random.randint(0, 359), random.randint(0, 359),random.randint(0, 359)), Gf.Vec3d(1.0,1.0,1.0))
        add_usd_physics_if_needed(prim)

def spawn_products_in_hopper(generation):
    stage = omni.usd.get_context().get_stage()

    hopper_spawn_path = "/World/product_spawn"
    hopper_spawn_prim = stage.GetPrimAtPath(hopper_spawn_path)
    
    spawn_pos = hopper_spawn_prim.GetAttribute('xformOp:translate').Get()

def spawn_products_in_container(generation, container_prim, container_path):
    count = 0
    
    item_data = json.loads(json.dumps(AssetPresets))
    container_data = item_data['Containers'][generation['container']]

    if count > 0:
        for i in range(count):
            item_random = random.choice(generation['product_list'])
            item = item_data['Products'][generation['product_type']][item_random]

            unique_number = str(uuid.uuid4().int)[:5]

            object_path = '/World/Items/'

            path = object_path + item_random + "_" + unique_number
            prim = create_new_prim(path)

            if item is not None:
                references: Usd.references = prim.GetReferences()
                references.AddReference(assetPath=item['url'])

            position = container_prim.GetAttribute('xformOp:translate').Get()
            rand_x = random.uniform(position[0] - (float(container_data['width'])/4), position[0] + (float(container_data['width'])/4))
            rand_y = random.uniform(position[1] - (float(container_data['length'])/4), position[1] + (float(container_data['length'])/4))
            rand_z = random.uniform(position[2] + float(container_data['height']) + 4, position[2] + float(container_data['height']) + 4.25)
            item_pos = Gf.Vec3d(rand_x, rand_y, rand_z)
            item_pos_old = Gf.Vec3d(position[0], position[1], position[2] + (float(container_data['height'])*10))

            set_transformTRS_attrs(prim, item_pos, Gf.Vec3d(random.randint(0, 359), random.randint(0, 359),random.randint(0, 359)), Gf.Vec3d(1.0,1.0,1.0))
            add_usd_physics_if_needed(prim)

'''

'''
def add_physics(prim):
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
        rigid_body_api = UsdPhysics.RigidBodyAPI.Apply(prim)
        PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
    else:
        print("RigidBodyAPI already exists for", prim.GetPath())
        
    # Set collision geometry type to Mesh if it’s not set correctly
    geom = UsdGeom.Mesh(prim)
    if geom:
        collision_api.GetCollisionGeometryTypeAttr().Set(UsdPhysics.Tokens.mesh)
    else:
        print("The geometry type of the prim is not a Mesh.")
        
    # Ensure that the container is set up as a static collider
    rigid_body_api.GetKinematicEnabledAttr().Set(False)
    rigid_body_api.GetRigidBodyEnabledAttr().Set(False)


def scale_legos(prim):
    h_scale = 0.004013
    w_scale = 0.001631
    l_scale = 0.006746

    scale_attr = prim.GetAttribute('xformOp:scale')
    current_scale = scale_attr.Get()
    new_scale = (current_scale[0] * l_scale * 100, current_scale[1] * w_scale * 100, current_scale[2] * h_scale * 100)
    scale_attr.Set(new_scale)

async def initialize_objects():
    item_data = json.loads(json.dumps(AssetPresets))
    parent_path = '/World/Sample_Products/'
    paths = []
    
    containers = item_data['Containers']
    legos = item_data['Products']['Legos']
    loreals = item_data['Products']['Loreal']

    for conatiner in containers:
        paths.append(create_samples(parent_path, 'Container', item_data, conatiner ,True))
    
    for lego in legos:
        paths.append(create_samples(parent_path, 'Legos', item_data, lego, False))
        
    for loreal in loreals:
        paths.append(create_samples(parent_path, 'Loreal', item_data, loreal, False))
    
    #omni.kit.commands.execute('DeletePrimsCommand', paths=paths)
    
async def create_samples(parent_path, product, item_data, item_name, isContainer):
    print(item_name + " Initialized")
    path = parent_path + item_name

    prim = create_new_prim(path)
    
    if isContainer == True:
        if item_data is not None:
            references: Usd.references = prim.GetReferences()
            references.AddReference(assetPath=item_data['Container'][item_name]['url'])
        else:
            carb.log_warn("Product is not valid")
            return
    else:
        if item_data is not None:
            references: Usd.references = prim.GetReferences()
            references.AddReference(assetPath=item_data['Products'][product][item_name]['url'])
        else:
            carb.log_warn("Product is not valid")
            return
        
    set_transformTRS_attrs(prim, Gf.Vec3d(0,0,0), Gf.Vec3d(0,0,0), Gf.Vec3d(1.0,1.0,1.0))
    add_usd_physics_if_needed(prim) 

    return path
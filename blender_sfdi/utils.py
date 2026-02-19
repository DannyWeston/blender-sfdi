import bpy
import random

from mathutils import Vector

def DeleteAllKeyframes(scene):
    for obj in scene.objects:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                fcurve.keyframe_points.clear()
                
    scene.animation_data_clear()

def AddDriver(to_drive, using, prop, data_path, index=-1, func=''):
    if index != -1: d = to_drive.driver_add(prop, index).driver
    else: d = to_drive.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = using
    v.targets[0].data_path = data_path

    d.expression = f"{func}({v.name})" if func else v.name

def ResetDeltaTransform(bl_obj):
    bl_obj.delta_location = (0.0, 0.0, 0.0)
    bl_obj.delta_rotation_euler = (0.0, 0.0, 0.0)

def RandomDeltaTransform(bl_obj, max_pos, max_rot, seed=0):
    random.seed(seed)

    for i in range(3):
        bl_obj.delta_location[i] = max_pos[i] * random.uniform(0.0, 1.0)
        bl_obj.delta_rotation_euler[i] = max_rot[i] * random.uniform(0.0, 1.0)

def HeightmapToMesh(heightmap, name="Heightmap"):
    height, width = heightmap.shape
    
    x_inc = 1.0 / (width - 1)
    y_inc = 1.0 / (height - 1)
    
    # Make main mesh object
    verts = []
    faces = []
    edges = []
    
    for i in range(height):
        for j in range(width):
            x = j * x_inc
            y = i * y_inc
            z = heightmap[i][j]
            verts.append(Vector((x, y, z)))
    
    for i in range(height - 1):
        for j in range(width - 1):
            faces.append([i * width + j, i * width + j + 1, (i + 1) * width + j])
            faces.append([i * width + j + 1, (i + 1) * width + j, (i + 1) * width + j + 1])

    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    
    return mesh

def HideObjects(bl_obj_ptrs, value):
    for bl_obj in bl_obj_ptrs:
        bl_obj.obj.hide_render = value
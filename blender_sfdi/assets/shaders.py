import bpy, mathutils

def make_shader_if_ne(name):
    mat = bpy.data.materials.get(name)
    if mat is not None: return mat

    # Doesn't exist so create
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
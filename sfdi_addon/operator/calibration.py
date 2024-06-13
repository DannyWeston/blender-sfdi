import bpy

from bpy.types import Operator
from mathutils import Vector

from sfdi_addon.blender import add_driver

def get_cb_pattern_mat():
    cb_name = "CheckerboardPattern"
    mat = bpy.data.materials.get(cb_name)
    if mat: return mat 
    
    mat = bpy.data.materials.new(name=cb_name)

    # Setup shader node for pattern part
    mat.use_nodes = True
    shader_nodes = mat.node_tree.nodes
    node_links = mat.node_tree.links

    # Create shader
    tex_node = shader_nodes.new(type="ShaderNodeTexCoord")
    tex_node.location = (0, 0)

    map_node = shader_nodes.new(type="ShaderNodeMapping")
    map_node.location = (200, 0)
    
    check_node = shader_nodes.new(type="ShaderNodeTexChecker")
    check_node.location = (400, 0)

    # White and black squares by default
    check_node.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0) 
    check_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    check_node.inputs[3].default_value = 1.0

    output_node = shader_nodes.get("Material Output")
    output_node.location = (600, 0)

    # Setup node Links
    node_links.new(tex_node.outputs[0], map_node.inputs[0])
    node_links.new(map_node.outputs[0], check_node.inputs[0])
    node_links.new(check_node.outputs[0], output_node.inputs[0])

    return mat

def get_cb_mat():
    cb_name = "Checkerboard"
    mat = bpy.data.materials.get(cb_name)
    if mat: return mat
    
    mat = bpy.data.materials.new(name=cb_name)

    # Setup shader node for pattern part
    mat.use_nodes = True
    # shader_nodes = mat.node_tree.nodes
    # node_links = mat.node_tree.links

    return mat

def create_checkerboard(location, rotation, size):
    # Make main mesh object
    # verts = [[9, 1, 0], [10, 3, 1], [4, 2, 3], [11, 0, 2], [3, 0, 1], [6, 9, 5], [8, 10, 6], [7, 4, 8], [5, 11, 7], [9, 10, 1], [10, 4, 3], [4, 11, 2], [11, 9, 0], [3, 2, 0], [6, 10, 9], [8, 4, 10], [7, 11, 4], [5, 9, 11]]
    verts = [Vector((-0.2199999988079071, -0.30699998140335083, -0.004999999888241291)), Vector((-0.2199999988079071, 0.30699998140335083, -0.004999999888241291)), Vector((0.2199999988079071, -0.30699998140335083, -0.004999999888241291)), Vector((0.2199999988079071, 0.30699998140335083, -0.004999999888241291)), Vector((0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((-0.20999999344348907, -0.296999990940094, 0.004999999888241291)), Vector((-0.20999999344348907, 0.296999990940094, 0.004999999888241291)), Vector((0.20999999344348907, -0.296999990940094, 0.004999999888241291)), Vector((0.20999999344348907, 0.296999990940094, 0.004999999888241291)), Vector((-0.2199999988079071, -0.30699998140335083, 0.004999999888241291)), Vector((-0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((0.2199999988079071, -0.30699998140335083, 0.004999999888241291))]
    faces = [[9, 1, 0], [10, 3, 1], [4, 2, 3], [11, 0, 2], [3, 0, 1], [6, 9, 5], [8, 10, 6], [7, 4, 8], [5, 11, 7], [9, 10, 1], [10, 4, 3], [4, 11, 2], [11, 9, 0], [3, 2, 0], [6, 10, 9], [8, 4, 10], [7, 11, 4], [5, 9, 11]]
    edges = []

    chb_mesh = bpy.data.meshes.new(name="Checkerboard")
    chb_mesh.from_pydata(verts, edges, faces)
    chb_mesh.update()

    # Add material to mesh
    mat = get_cb_mat()
    chb_mesh.materials.append(mat)

    # Make pattern mesh object
    verts = [Vector((-0.20999999344348907, -0.2969996929168701, 0.004999999888241291)), Vector((-0.20999999344348907, 0.29700028896331787, 0.004999999888241291)), Vector((0.20999997854232788, -0.2969996929168701, 0.004999999888241291)), Vector((0.20999997854232788, 0.29700028896331787, 0.004999999888241291))]
    faces = [[1, 2, 3], [1, 0, 2]]
    edges = []

    pattern_mesh = bpy.data.meshes.new(name="CheckerboardPattern")
    pattern_mesh.from_pydata(verts, edges, faces)
    pattern_mesh.update()

    # Add material to mesh
    mat = get_cb_pattern_mat()
    pattern_mesh.materials.append(mat)

    # TODO: Add width, height driver properties for checkerboard
    # Needs menu panel
    pattern_obj = bpy.data.objects.new('CheckerboardPattern', pattern_mesh)
    cb_obj = bpy.data.objects.new('Checkerboard', chb_mesh)

    # Transform created object if any supplied
    cb_obj.rotation_euler[0] = rotation[0]
    cb_obj.rotation_euler[1] = rotation[1]
    cb_obj.rotation_euler[2] = rotation[2]

    cb_obj.location[0] = location[0]
    cb_obj.location[1] = location[1]
    cb_obj.location[2] = location[2]

    bpy.context.collection.objects.link(pattern_obj)
    bpy.context.collection.objects.link(cb_obj)

    # Set pattern mesh parent to main object
    pattern_obj.parent = cb_obj

    # Setup property drivers for pattern width/height
    cb_obj["IsCheckerboard"] = True
    cb_obj["Size"] = size
    
    map_node = mat.node_tree.nodes["Mapping"]
    add_driver(map_node.inputs[3], cb_obj, 'default_value', '["Size"][0]', 0)
    add_driver(map_node.inputs[3], cb_obj, 'default_value', '["Size"][1]', 1)

    return cb_obj

class OP_AddCheckerboard(Operator):
    bl_idname = "menu.add_checkerboard"
    bl_label = "Checkerboard"

    bl_options = {'REGISTER', 'UNDO'}
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH')
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION')
    
    # Checkerboard square counts
    size: bpy.props.FloatVectorProperty(name="Size", default=(8.0, 6.0), size=2, min=0.0)

    def execute(self, context):
        chb = create_checkerboard(self.location, self.rotation, self.size)

        return {'FINISHED'}

classes = [
    OP_AddCheckerboard
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddCheckerboard.bl_idname))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
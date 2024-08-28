import bpy
from bpy.types import Operator

from opensfdi.io.std import stdout_redirected

from ..blender import add_driver
from ..definitions import MODELS_DIR

DEFAULT_CB_PATH =  str(MODELS_DIR / "checkerboard.obj")
CB_SHADER_NAME = "CheckerboardGenerator"

def get_cb_mat():
    mat = bpy.data.materials.get(CB_SHADER_NAME)
    
    if mat: return mat
    
    mat = bpy.data.materials.new(name=CB_SHADER_NAME)

    # Setup shader node for pattern part
    mat.use_nodes = True
    shader_nodes = mat.node_tree.nodes
    node_links = mat.node_tree.links

    shader_nodes.remove(shader_nodes["Principled BSDF"])

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

def create_checkerboard(location, rotation):
    # Load the checkerboard mesh from disk
    with stdout_redirected():
        bpy.ops.wm.obj_import(filepath=DEFAULT_CB_PATH, filter_obj=False, display_type='DEFAULT', forward_axis='NEGATIVE_Z', up_axis='Y')

    bl_obj = bpy.context.active_object

    # Add generating pattern material to mesh
    mat = get_cb_mat()
    if bl_obj.data.materials: bl_obj.data.materials[0] = mat
    else: bl_obj.data.materials.append(mat)

    # Transform created object if any supplied
    bl_obj.rotation_euler[0] = rotation[0]
    bl_obj.rotation_euler[1] = rotation[1]
    bl_obj.rotation_euler[2] = rotation[2]

    bl_obj.location[0] = location[0]
    bl_obj.location[1] = location[1]
    bl_obj.location[2] = location[2]

    # Setup property drivers for pattern width/height
    bl_obj["IsCheckerboard"] = True

    # Add driver for changing the size of the checkerboard
    map_node = mat.node_tree.nodes.get("Mapping")

    add_driver(map_node.inputs[3], bl_obj, 'default_value', 'settings.size[0]', 0)
    add_driver(map_node.inputs[3], bl_obj, 'default_value', 'settings.size[1]', 1)

    return bl_obj

class BL_Checkerboard:
    def __init__(self, name, width, height):
        self.__width = width
        self.__height = height

        # Retrieve object from Blender
        self.__cb_obj = bpy.data.objects[name]
            
    def get_pos(self):
        return self.__cb_obj.matrix_world.to_translation()

    def get_bl_obj(self):
        return self.__cb_obj

    @staticmethod
    def from_cb_obj(cb_obj):
        settings = cb_obj.cb_settings
        return BL_Checkerboard(name=cb_obj.name, width=settings.width, height=settings.height)

class OP_AddCheckerboard(Operator):
    bl_idname = "menu.add_checkerboard"
    bl_label = "Checkerboard"

    bl_options = {'REGISTER', 'UNDO'}
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        create_checkerboard(self.location, self.rotation)
        return {'FINISHED'}

classes = [
    OP_AddCheckerboard
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.append(lambda self, _: self.layout.operator(OP_AddCheckerboard.bl_idname))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
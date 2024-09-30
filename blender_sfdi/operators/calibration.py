import bpy
from bpy.types import Operator

from opensfdi.io.std import stdout_redirected

from ..blender import add_driver
from ..definitions import MODELS_DIR
from ..materials import replace_material

DEFAULT_CB_PATH =  str(MODELS_DIR / "checkerboard.obj")

CB_SHADER_NAME = "CB_Generator"
REPLACE_SLOT_NAME = "CB_Blank"
POSITION_NODES_NAME = "PositionRandomiser"

def get_cb_mat():
    # TODO: Investigate instance shaders Blender
    # Currently inefficient as recreating the same shader just with different params

    # Check if already loaded in Blender
    # mat = bpy.data.materials.get(CB_SHADER_NAME)
    # if mat: return mat

    # Need to make it as it doesn't exist
    mat = bpy.data.materials.new(name=CB_SHADER_NAME)

    # Setup shader node for pattern part
    mat.use_nodes = True
    shader_nodes = mat.node_tree.nodes
    node_links = mat.node_tree.links

    # Create shader
    tex_node = shader_nodes.new(type="ShaderNodeTexCoord")
    tex_node.location = (0, 0)

    map_node = shader_nodes.new(type="ShaderNodeMapping")
    map_node.location = (200, 0)
    map_node.vector_type = 'POINT'
    
    check_node = shader_nodes.new(type="ShaderNodeTexChecker")
    check_node.location = (400, 0)

    # White and black squares by default
    check_node.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0) 
    check_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    check_node.inputs[3].default_value = 1.0

    
    # Get BSDF node
    bsdf_node = shader_nodes["Principled BSDF"]
    bsdf_node.location = (600, 0)

    output_node = shader_nodes.get("Material Output")
    output_node.location = (800, 0)

    # Setup node Links
    node_links.new(tex_node.outputs[2], map_node.inputs[0])
    node_links.new(map_node.outputs[0], check_node.inputs[0])
    node_links.new(check_node.outputs[0], bsdf_node.inputs[0])

    return mat

def make_pos_rand_mod():
    # Don't make if already exists
    if POSITION_NODES_NAME in bpy.data.node_groups:
        return bpy.data.node_groups[POSITION_NODES_NAME]
    
    # Need to make it as doesn't exist
    node_group = bpy.data.node_groups.new(POSITION_NODES_NAME, 'GeometryNodeTree')
    
    input_node = node_group.nodes.new('NodeGroupInput')
    input_node.location = (0, 0)
    
    
    scale_pos_node = node_group.nodes.new('ShaderNodeVectorMath')
    scale_pos_node.location = (200, 200)
    scale_pos_node.operation = 'SCALE'
    scale_pos_node.inputs[3].default_value = -1.0
    
    scale_rot_node = node_group.nodes.new('ShaderNodeVectorMath')
    scale_rot_node.location = (200, -200)
    scale_rot_node.operation = 'SCALE'
    scale_rot_node.inputs[3].default_value = -1.0
    
    
    zero_node = node_group.nodes.new('FunctionNodeInputInt')
    zero_node.location = (400, 0)
    
    
    random_pos_node = node_group.nodes.new('FunctionNodeRandomValue')
    random_pos_node.location = (600, 200)
    random_pos_node.data_type = 'FLOAT_VECTOR'
    
    random_rot_node = node_group.nodes.new('FunctionNodeRandomValue')
    random_rot_node.location = (600, -200)
    random_rot_node.data_type = 'FLOAT_VECTOR'
    
    
    transform_node = node_group.nodes.new('GeometryNodeTransform')
    transform_node.location = (800, 0)


    realise_node = node_group.nodes.new('GeometryNodeRealizeInstances')
    realise_node.location = (1000, 0)
    
    
    output_node = node_group.nodes.new('NodeGroupOutput')
    output_node.location = (1200, 0)
    
    # Specify input and outputs of geometry nodes
    
    node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_group.interface.new_socket(name="Seed", in_out="INPUT", socket_type="NodeSocketInt")
    node_group.interface.new_socket(name="Max Position", in_out="INPUT", socket_type="NodeSocketVector")
    rot_socket = node_group.interface.new_socket(name="Max Rotation", in_out="INPUT", socket_type="NodeSocketVector")
    rot_socket.subtype = 'EULER'
    
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    
    # Setup links between nodes
    
    node_group.links.new(input_node.outputs['Geometry'], transform_node.inputs['Geometry'])
    
    node_group.links.new(input_node.outputs['Seed'], random_pos_node.inputs['Seed'])
    node_group.links.new(input_node.outputs['Seed'], random_rot_node.inputs['Seed'])
    
    node_group.links.new(input_node.outputs['Max Position'], scale_pos_node.inputs['Vector'])
    node_group.links.new(input_node.outputs['Max Rotation'], scale_rot_node.inputs['Vector'])
    node_group.links.new(input_node.outputs['Max Position'], random_pos_node.inputs['Max'])
    node_group.links.new(input_node.outputs['Max Rotation'], random_rot_node.inputs['Max'])
    
    node_group.links.new(scale_pos_node.outputs['Vector'], random_pos_node.inputs['Min'])
    node_group.links.new(scale_rot_node.outputs['Vector'], random_rot_node.inputs['Min'])
    
    node_group.links.new(zero_node.outputs['Integer'], random_pos_node.inputs['ID'])
    node_group.links.new(zero_node.outputs['Integer'], random_rot_node.inputs['ID'])
    
    node_group.links.new(random_pos_node.outputs['Value'], transform_node.inputs['Translation'])
    node_group.links.new(random_rot_node.outputs['Value'], transform_node.inputs['Rotation'])
    
    node_group.links.new(transform_node.outputs['Geometry'], realise_node.inputs['Geometry'])
    
    node_group.links.new(realise_node.outputs['Geometry'], output_node.inputs['Geometry'])
    
    return node_group

def create_checkerboard(location, rotation):
    # Load the checkerboard mesh from disk
    with stdout_redirected():
        bpy.ops.wm.obj_import(filepath=DEFAULT_CB_PATH, filter_obj=False, display_type='DEFAULT', forward_axis='Y', up_axis='Z')

    bl_obj = bpy.context.active_object

    # Fix error with texture space
    bl_obj.data.use_auto_texspace = False
    bl_obj.data.texspace_size[2] = 0

    # Transform created object if any supplied
    bl_obj.rotation_euler[0] = rotation[0]
    bl_obj.rotation_euler[1] = rotation[1]
    bl_obj.rotation_euler[2] = rotation[2]

    bl_obj.location[0] = location[0]
    bl_obj.location[1] = location[1]
    bl_obj.location[2] = location[2]

    # Setup property drivers for pattern width/height
    bl_obj.data["IsCheckerboard"] = True

    # Add a position randomising node with driver for changing the seed, min/max pos and rot
    pos_nodes = bl_obj.modifiers.new(POSITION_NODES_NAME, 'NODES')
    pos_nodes.node_group = make_pos_rand_mod()


    add_driver(pos_nodes, bl_obj, '["Socket_1"]', 'cb_settings.seed')
    for i in range(3):
        add_driver(pos_nodes, bl_obj, '["Socket_2"]', f'cb_settings.max_position[{i}]', i)
        add_driver(pos_nodes, bl_obj, '["Socket_3"]', f'cb_settings.max_rotation[{i}]', i)

    # Setup generator material with driver for changing the size of the checkerboard
    mat = get_cb_mat()
    replace_material(bl_obj, REPLACE_SLOT_NAME, mat)

    map_node = mat.node_tree.nodes["Mapping"]
    add_driver(map_node.inputs[3], bl_obj, 'default_value', 'cb_settings.size[0]', 0)
    add_driver(map_node.inputs[3], bl_obj, 'default_value', 'cb_settings.size[1]', 1)

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

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
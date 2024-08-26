import bpy
from bpy.types import Operator
from math import pi

from opensfdi.io.std import stdout_redirected

from ..blender import add_driver
from ..materials import make_fringe_intensity_map_group, make_pixelate_map_group
from ..definitions import MODELS_DIR

DEFAULT_PROJ_PATH = str(MODELS_DIR / "projector.obj")
PROJ_MASK_NAME = "ProjectorDefaultMask"

class OP_RegisterProj(Operator):
    bl_idname = "op.register_proj"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and ("IsProjector" in context.object.data) and (projs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        projs = context.scene.ExProjectors
        
        new_item = projs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterProj(Operator):
    bl_idname = "op.unregister_proj"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and (0 <= projs.find(context.object.name))
            
    def execute(self, context):        
        projs = context.scene.ExProjectors
        selected = context.object

        selected_id = projs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        projs.remove(selected_id)
            
        return {'FINISHED'}

class OP_AddProj(Operator):
    bl_idname = "menu.add_proj"
    bl_label = "Fringe Projector"
    bl_options = {'REGISTER', 'UNDO'}

    location : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        ProjectorFactory.MakeBL_FringeProjector(self.location, self.rotation)
        return {'FINISHED'}

class ProjectorFactory:
    @staticmethod
    def MakeBL_FringeProjector(location, rotation):

        # Create new light for the projector
        light_data = bpy.data.lights.new(name="ProjectorLight", type='SPOT')
        light_data.energy = 10              # 10 Watts
        light_data.shadow_soft_size = 0.0   # No blurring over whole image
        light_data.spot_blend = 0.0         # No blurring around the edge
        light_data.spot_size = pi           # Full 180 deg vision
        light_data.cycles.max_bounces = 16  # Max light bounces of 16 for performance
        light_data.cycles.use_multiple_importance_sampling = False

        # Setup light shader nodes for light emission
        light_data.use_nodes = True
        light_nodes = light_data.node_tree.nodes
        node_links = light_data.node_tree.links

        # Check if Fringe Intensity Map group exists, create if not
        if light_nodes.get("Fringe Intensity Map", None) is None: 
            make_fringe_intensity_map_group()
            
        if light_nodes.get("Vector Pixelate", None) is None: 
            make_pixelate_map_group()

        tex_node = light_nodes.new(type="ShaderNodeTexCoord")
        tex_node.location = (0, 0)

        divide_node = light_nodes.new(type="ShaderNodeVectorMath")
        divide_node.operation = 'DIVIDE'
        divide_node.location = (200, 100)
        
        sep_node = light_nodes.new(type="ShaderNodeSeparateXYZ")
        sep_node.location = (200, -100)

        
        # > Allow for configurable resolution

        pixelate_node = light_nodes.new(type="ShaderNodeGroup")
        pixelate_node.node_tree = bpy.data.node_groups['Vector Pixelate']
        pixelate_node.location = (400, 0)
        
        fringe_node = light_nodes.new(type="ShaderNodeGroup")
        fringe_node.node_tree = bpy.data.node_groups['Fringe Intensity Map']
        fringe_node.location = (600, 0)


        # > Set the projector to use a rectangular pattern using a grid

        mapping_node = light_nodes.new(type="ShaderNodeMapping")
        mapping_node.location = (400, -400)
        mapping_node.inputs[1].default_value[0] = 0.5
        mapping_node.inputs[1].default_value[1] = 0.5

        mask_node = light_nodes.new(type="ShaderNodeTexImage")
        mask_node.location = (600, -400)

        mask_node.interpolation = "Linear"
        mask_node.extension = "CLIP"
        if (img := bpy.data.images.get(PROJ_MASK_NAME, None)) is None:
            bpy.ops.image.new(name=PROJ_MASK_NAME, width=4096, height=4096, color=(1.0, 1.0, 1.0, 1.0), alpha=True, generated_type="BLANK")
            img = bpy.data.images.get(PROJ_MASK_NAME)

        mask_node.image = img

        # <

        emission_node = light_nodes.get('Emission')
        emission_node.location = (800, 0)
        
        output_node = light_nodes.get("Light Output")
        output_node.location = (1000, 0)
        
        # Setup node Links
        node_links.new(tex_node.outputs[1], divide_node.inputs[0])
        node_links.new(tex_node.outputs[1], sep_node.inputs[0])
        node_links.new(sep_node.outputs[2], divide_node.inputs[1])
        
        node_links.new(divide_node.outputs[0], pixelate_node.inputs[0])
        node_links.new(divide_node.outputs[0], mapping_node.inputs[0])
        
        node_links.new(pixelate_node.outputs[0], fringe_node.inputs[0])
        node_links.new(mapping_node.outputs[0], mask_node.inputs[0])
        
        node_links.new(fringe_node.outputs[0], emission_node.inputs[0])
        node_links.new(mask_node.outputs[0], emission_node.inputs[1])
        
        node_links.new(emission_node.outputs[0], output_node.inputs[0])
        
        light_obj = bpy.data.objects.new(name="Projector", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)

        # Set translation of object
        light_obj.rotation_euler[0] = rotation[0]
        light_obj.rotation_euler[1] = rotation[1]
        light_obj.rotation_euler[2] = rotation[2]

        light_obj.location[0] = location[0]
        light_obj.location[1] = location[1]
        light_obj.location[2] = location[2]

        # Setup property drivers for fringe projector
        light_data["IsProjector"] = True

        add_driver(fringe_node.inputs[1], light_obj, 'default_value', 'proj_settings.fringe_rotation')
        add_driver(fringe_node.inputs[2], light_obj, 'default_value', 'proj_settings.fringe_frequency')
        add_driver(fringe_node.inputs[3], light_obj, 'default_value', 'proj_settings.fringe_phase')
        
        add_driver(pixelate_node.inputs[1], light_obj, 'default_value', 'proj_settings.resolution[0]')
        add_driver(pixelate_node.inputs[2], light_obj, 'default_value', 'proj_settings.resolution[1]')

        add_driver(mapping_node.inputs[3], light_obj, 'default_value', 'proj_settings.aspect_ratio', index=0)
        add_driver(light_obj, light_obj, 'scale', 'proj_settings.throw_ratio', index=2)

        # Add a mesh to the light obj
        with stdout_redirected():
            bpy.ops.wm.obj_import(filepath=DEFAULT_PROJ_PATH, filter_obj=False, display_type='DEFAULT', forward_axis='NEGATIVE_Z', up_axis='Y')

        active = bpy.context.active_object
        active.parent = light_obj
        active.hide_select = True # Disallow selecting as can cause issues with users

        # Limit Z movement on object (so throw ratio can apply correctly)
        constraint = active.constraints.new(type='LIMIT_SCALE')
        constraint.use_min_x = constraint.use_min_y = constraint.use_min_z = True
        constraint.min_x = constraint.min_y = constraint.min_z = 1.0
        

        constraint.use_max_x = constraint.use_max_y = constraint.use_max_z = True
        constraint.max_x = constraint.max_y = constraint.max_z = 1.0
        
        return light_obj

classes = [
    OP_RegisterProj,
    OP_UnregisterProj,
    OP_AddProj
]

def add_proj_func(self, _):
    self.layout.operator(OP_AddProj.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(add_proj_func)

def unregister():
    # TODO: Remove from VIEW3D
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

        bpy.types.VIEW3D_MT_add.remove(add_proj_func)
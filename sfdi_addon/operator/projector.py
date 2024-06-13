import bpy
from bpy.types import Operator
from mathutils import Vector

from sfdi_addon.blender import add_driver
from sfdi_addon.materials import make_fringe_intensity_map_group, make_pixelate_map_group

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
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH')
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION')
    
    f_type: bpy.props.EnumProperty(
        name="Type",
        description="TODO: Some description",
        items=[
            ("OP1", "Sinusoidal",   "TODO: Fill tooltip", 1),
            ("OP2", "Binary",       "TODO: Fill tooltip", 2),
        ])
    
    f_sf: bpy.props.FloatProperty(name="Fringe Frequency", default=32.0, min=0.0)
    
    f_phase: bpy.props.FloatProperty(name="Fringe Phase", default=0.0, unit='ROTATION')
    
    f_rotation: bpy.props.FloatProperty(name="Fringe Rotation", default=0.0, unit='ROTATION')
    
    resolution: bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1024, 768), min=1)

    def execute(self, context):
        ProjectorFactory.MakeBL_FringeProjector(self.location, self.rotation, self.f_type, self.f_sf, self.f_phase, self.f_rotation, self.resolution)

        return {'FINISHED'}

class ProjectorFactory:
    @staticmethod
    def MakeBL_FringeProjector(location, rotation, f_type, f_sf, f_phase, f_rotation, resolution):
        # Create new light for the projector
        light_data = bpy.data.lights.new(name="ProjectorLight", type='SPOT')
        light_data.energy = 5               # 5 Watts
        light_data.shadow_soft_size = 0.005 # Slight blurring over whole image
        light_data.spot_blend = 0.1         # Slight blurring around the edge
        light_data.spot_size = 1.2309807    # Cone size 70.3 deg for Throw Ratio 1:1 # TODO: Improve calculation for throw ratio
        light_data.cycles.max_bounces = 16  # Max light bounces of 16 for performance

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
        
        pixelate_node = light_nodes.new(type="ShaderNodeGroup")
        pixelate_node.node_tree = bpy.data.node_groups['Vector Pixelate']
        pixelate_node.location = (400, 0)
        
        fringe_node = light_nodes.new(type="ShaderNodeGroup")
        fringe_node.node_tree = bpy.data.node_groups['Fringe Intensity Map']
        fringe_node.location = (600, 0)
        
        emission_node = light_nodes.get('Emission')
        emission_node.location = (800, 0)
        
        output_node = light_nodes.get("Light Output")
        output_node.location = (1000, 0)
        
        # Setup node Links
        node_links.new(tex_node.outputs[1], divide_node.inputs[0])
        node_links.new(tex_node.outputs[1], sep_node.inputs[0])
        node_links.new(sep_node.outputs[2], divide_node.inputs[1])
        
        node_links.new(divide_node.outputs[0], pixelate_node.inputs[0])
        
        node_links.new(pixelate_node.outputs[0], fringe_node.inputs[0])
        
        node_links.new(fringe_node.outputs[0], emission_node.inputs[1])
        
        node_links.new(emission_node.outputs[0], output_node.inputs[0])
        
        light_obj = bpy.data.objects.new(name="Projector", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)

        # Make main mesh object
        verts = [Vector((-0.05000000074505806, -0.05000000074505806, -0.05000000074505806)), Vector((0.0, 0.10000000894069672, 0.02500000037252903)), Vector((-0.05000000074505806, -0.05000000074505806, 0.05000000074505806)), Vector((0.004877258092164993, 0.10000000894069672, 0.024519631639122963)), Vector((-0.05000000074505806, 0.05000000074505806, -0.05000000074505806)), Vector((0.009567086584866047, 0.10000000894069672, 0.02309698797762394)), Vector((-0.05000000074505806, 0.05000000074505806, 0.05000000074505806)), Vector((0.013889255933463573, 0.10000000894069672, 0.020786739885807037)), Vector((0.05000000074505806, -0.05000000074505806, -0.05000000074505806)), Vector((0.01767767034471035, 0.10000000894069672, 0.01767767034471035)), Vector((0.05000000074505806, -0.05000000074505806, 0.05000000074505806)), Vector((0.020786739885807037, 0.10000000894069672, 0.013889255933463573)), Vector((0.05000000074505806, 0.05000000074505806, -0.05000000074505806)), Vector((0.02309698797762394, 0.10000000894069672, 0.009567086584866047)), Vector((0.05000000074505806, 0.05000000074505806, 0.05000000074505806)), Vector((0.024519631639122963, 0.10000000894069672, 0.004877258092164993)), Vector((0.02500000037252903, 0.10000000894069672, 0.0)), Vector((0.024519631639122963, 0.10000000894069672, -0.004877258092164993)), Vector((0.02309698797762394, 0.10000000894069672, -0.009567086584866047)), Vector((0.020786739885807037, 0.10000000894069672, -0.013889255933463573)), Vector((0.01767767034471035, 0.10000000894069672, -0.01767767034471035)), Vector((0.013889255933463573, 0.10000000894069672, -0.020786739885807037)), Vector((0.009567086584866047, 0.10000000894069672, -0.02309698797762394)), Vector((0.004877258092164993, 0.10000000894069672, -0.024519631639122963)), Vector((0.0, 0.10000000894069672, -0.02500000037252903)), Vector((-0.004877258092164993, 0.10000000894069672, -0.024519631639122963)), Vector((-0.009567086584866047, 0.10000000894069672, -0.02309698797762394)), Vector((-0.013889255933463573, 0.10000000894069672, -0.020786739885807037)), Vector((-0.01767767034471035, 0.10000000894069672, -0.01767767034471035)), Vector((-0.020786739885807037, 0.10000000894069672, -0.013889255933463573)), Vector((-0.02309698797762394, 0.10000000894069672, -0.009567086584866047)), Vector((-0.024519631639122963, 0.10000000894069672, -0.004877258092164993)), Vector((-0.02500000037252903, 0.10000000894069672, 0.0)), Vector((-0.024519631639122963, 0.10000000894069672, 0.004877258092164993)), Vector((-0.02309698797762394, 0.10000000894069672, 0.009567086584866047)), Vector((-0.020786739885807037, 0.10000000894069672, 0.013889255933463573)), Vector((-0.01767767034471035, 0.10000000894069672, 0.01767767034471035)), Vector((-0.013889255933463573, 0.10000000894069672, 0.020786739885807037)), Vector((-0.009567086584866047, 0.10000000894069672, 0.02309698797762394)), Vector((-0.004877258092164993, 0.10000000894069672, 0.024519631639122963)), Vector((-0.012499997392296791, 0.05000000074505806, 0.0)), Vector((-0.012259813956916332, 0.05000000074505806, -0.0024386285804212093)), Vector((-0.012259813956916332, 0.05000000074505806, 0.0024386285804212093)), Vector((-0.008838833309710026, 0.05000000074505806, -0.008838833309710026)), Vector((-0.01039336808025837, 0.05000000074505806, -0.006944626569747925)), Vector((-0.01154849212616682, 0.05000000074505806, -0.004783542361110449)), Vector((-0.01039336808025837, 0.05000000074505806, 0.006944626569747925)), Vector((-0.01154849212616682, 0.05000000074505806, 0.004783542361110449)), Vector((-0.0024386285804212093, 0.05000000074505806, 0.012259813956916332)), Vector((-0.004783542361110449, 0.05000000074505806, 0.01154849212616682)), Vector((-0.006944626569747925, 0.05000000074505806, 0.01039336808025837)), Vector((0.006944626569747925, 0.05000000074505806, 0.01039336808025837)), Vector((0.008838833309710026, 0.05000000074505806, 0.008838833309710026)), Vector((0.004783542361110449, 0.05000000074505806, 0.01154849212616682)), Vector((0.0024386285804212093, 0.05000000074505806, 0.012259813956916332)), Vector((0.0, 0.05000000074505806, 0.012499997392296791)), Vector((-0.008838833309710026, 0.05000000074505806, 0.008838833309710026)), Vector((-0.006944626569747925, 0.05000000074505806, -0.01039336808025837)), Vector((-0.004783542361110449, 0.05000000074505806, -0.01154849212616682)), Vector((-0.0024386285804212093, 0.05000000074505806, -0.012259813956916332)), Vector((0.004783542361110449, 0.05000000074505806, -0.01154849212616682)), Vector((0.006944626569747925, 0.05000000074505806, -0.01039336808025837)), Vector((0.0024386285804212093, 0.05000000074505806, -0.012259813956916332)), Vector((0.0, 0.05000000074505806, -0.012499997392296791)), Vector((0.012499997392296791, 0.05000000074505806, 0.0)), Vector((0.012259813956916332, 0.05000000074505806, -0.0024386285804212093)), Vector((0.012259813956916332, 0.05000000074505806, 0.0024386285804212093)), Vector((0.01154849212616682, 0.05000000074505806, -0.004783542361110449)), Vector((0.01039336808025837, 0.05000000074505806, -0.006944626569747925)), Vector((0.01154849212616682, 0.05000000074505806, 0.004783542361110449)), Vector((0.01039336808025837, 0.05000000074505806, 0.006944626569747925)), Vector((0.008838833309710026, 0.05000000074505806, -0.008838833309710026))]
        faces = [[0, 2, 6, 4], [56, 6, 14, 12, 71, 68, 67, 65, 64, 66, 69, 70, 52, 51, 53, 54, 55, 48, 49, 50], [71, 12, 4, 6, 56, 46, 47, 42, 40, 41, 45, 44, 43, 57, 58, 59, 63, 62, 60, 61], [12, 14, 10, 8], [8, 10, 2, 0], [4, 12, 8, 0], [14, 6, 2, 10], [1, 55, 54, 3], [3, 54, 53, 5], [5, 53, 51, 7], [7, 51, 52, 9], [11, 9, 52, 70], [13, 11, 70, 69], [15, 13, 69, 66], [16, 15, 66, 64], [17, 16, 64, 65], [18, 17, 65, 67], [19, 18, 67, 68], [20, 19, 68, 71], [71, 61, 21, 20], [61, 60, 22, 21], [60, 62, 23, 22], [62, 63, 24, 23], [25, 24, 63, 59], [25, 59, 58, 26], [26, 58, 57, 27], [27, 57, 43, 28], [29, 28, 43, 44], [30, 29, 44, 45], [31, 30, 45, 41], [32, 31, 41, 40], [42, 33, 32, 40], [47, 34, 33, 42], [46, 35, 34, 47], [56, 36, 35, 46], [56, 50, 37, 36], [50, 49, 38, 37], [39, 1, 3, 5, 7, 9, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], [49, 48, 39, 38], [55, 1, 39, 48]]
        edges = []

        proj_mesh = bpy.data.meshes.new(name="ProjectorMesh")
        proj_mesh.from_pydata(verts, edges, faces)
        proj_mesh.update()

        proj_obj = bpy.data.objects.new('ProjectorMesh', proj_mesh)
        # proj_obj.visible_shadow = False # Make mesh ignore projector light

        proj_obj.location[2] = 0.10001
        proj_obj.rotation_euler[0] = -1.5708

        bpy.context.collection.objects.link(proj_obj)
        
        # Set translation of object
        light_obj.rotation_euler[0] = rotation[0]
        light_obj.rotation_euler[1] = rotation[1]
        light_obj.rotation_euler[2] = rotation[2]

        light_obj.location[0] = location[0]
        light_obj.location[1] = location[1]
        light_obj.location[2] = location[2]

        # Set mesh parent to light
        proj_obj.parent = light_obj
        
        # Setup property drivers for fringe projector
        light_data["IsProjector"] = True
        
        light_data["Fringe Type"]        = f_type
        light_data["Spatial Frequency"]  = f_sf
        light_data["Phase"]              = f_phase
        light_data["Rotation"]           = f_rotation
        light_data["Resolution"]         = resolution
        
        add_driver(fringe_node.inputs[1], light_obj, 'default_value', 'data["Rotation"]')
        add_driver(fringe_node.inputs[2], light_obj, 'default_value', 'data["Spatial Frequency"]')
        add_driver(fringe_node.inputs[3], light_obj, 'default_value', 'data["Phase"]')
        
        add_driver(pixelate_node.inputs[1], light_obj, 'default_value', 'data["Resolution"][0]')
        add_driver(pixelate_node.inputs[2], light_obj, 'default_value', 'data["Resolution"][1]')

        return light_obj

classes = [
    OP_RegisterProj,
    OP_UnregisterProj,
    OP_AddProj
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddProj.bl_idname))

def unregister():
    # TODO: Remove from VIEW3D
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
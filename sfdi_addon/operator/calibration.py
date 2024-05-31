import bpy
from bpy.types import Operator

from mathutils import Vector

def create_checkerboard(location, rotation, width, height):
    # Make main mesh object
    verts = [Vector((-0.2199999988079071, -0.30699998140335083, -0.004999999888241291)), Vector((-0.2199999988079071, -0.30699998140335083, 0.004999999888241291)), Vector((-0.2199999988079071, 0.30699998140335083, -0.004999999888241291)), Vector((-0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((0.2199999988079071, -0.30699998140335083, -0.004999999888241291)), Vector((0.2199999988079071, -0.30699998140335083, 0.004999999888241291)), Vector((0.2199999988079071, 0.30699998140335083, -0.004999999888241291)), Vector((0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((-0.20999999344348907, -0.296999990940094, 0.004999999888241291)), Vector((-0.20999999344348907, 0.296999990940094, 0.004999999888241291)), Vector((0.20999999344348907, -0.296999990940094, 0.004999999888241291)), Vector((0.20999999344348907, 0.296999990940094, 0.004999999888241291)), Vector((-0.2199999988079071, -0.30699998140335083, 0.004999999888241291)), Vector((-0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((0.2199999988079071, 0.30699998140335083, 0.004999999888241291)), Vector((0.2199999988079071, -0.30699998140335083, 0.004999999888241291))]
    faces = [[0, 9, 10, 1], [1, 10, 4, 3], [3, 4, 11, 2], [2, 11, 9, 0], [1, 3, 2, 0], [5, 6, 10, 9], [6, 8, 4, 10], [8, 7, 11, 4], [7, 5, 9, 11]]
    edges = []
    
    chb_mesh = bpy.data.meshes.new(name="Checkerboard")
    chb_mesh.from_pydata(verts, edges, faces)
    chb_mesh.update()
    
    

    
    # Make pattern mesh object
    verts = [Vector((-0.006039813160896301, -2.534384250640869, 0.018381403759121895)), Vector((-0.006039813160896301, -1.9403842687606812, 0.018381403759121895)), Vector((0.41396015882492065, -2.534384250640869, 0.018381403759121895)), Vector((0.41396015882492065, -1.9403842687606812, 0.018381403759121895))]
    faces = [[0, 1, 2, 3]]
    edges = []
    
    pattern_mesh = bpy.data.meshes.new(name="CheckerboardPattern")
    pattern_mesh.from_pydata(verts, edges, faces)
    pattern_mesh.update()
    
    proj_obj = bpy.data.objects.new('ProjectorMesh', proj_mesh)

    # Setup shader node for pattern part
    # pattern_mesh.use_nodes = True
    # shader_nodes = light_data.node_tree.nodes
    # node_links = light_data.node_tree.links

    # Create shader

    # tex_node = shader_nodes.new(type="ShaderNodeTexCoord")
    # tex_node.location = (0, 0)
    
    # sep_node = light_nodes.new(type="ShaderNodeSeparateXYZ")
    # sep_node.location = (200, -100)
    
    # emission_node = light_nodes.get('Emission')
    # emission_node.location = (800, 0)
    
    # output_node = light_nodes.get("Light Output")
    # output_node.location = (1000, 0)
    
    # # Setup node Links
    # node_links.new(tex_node.outputs[1], divide_node.inputs[0])
    # node_links.new(tex_node.outputs[1], sep_node.inputs[0])
    # node_links.new(sep_node.outputs[2], divide_node.inputs[1])
    
    # node_links.new(divide_node.outputs[0], pixelate_node.inputs[0])
    
    # node_links.new(pixelate_node.outputs[0], fringe_node.inputs[0])
    
    # node_links.new(fringe_node.outputs[0], emission_node.inputs[1])
    
    # node_links.new(emission_node.outputs[0], output_node.inputs[0])
    
    # light_obj = bpy.data.objects.new(name="Projector", object_data=light_data)
    # bpy.context.collection.objects.link(light_obj)

    

    # proj_mesh = bpy.data.meshes.new(name="ProjectorMesh")
    # proj_mesh.from_pydata(verts, edges, faces)
    # proj_mesh.update()

    # proj_obj = bpy.data.objects.new('ProjectorMesh', proj_mesh)
    # # proj_obj.visible_shadow = False # Make mesh ignore projector light

    # proj_obj.location[2] = 0.10001
    # proj_obj.rotation_euler[0] = -1.5708

    # bpy.context.collection.objects.link(proj_obj)
    
    if rotation:
        pattern_mesh.rotation_euler[0] += rotation[0]
        pattern_mesh.rotation_euler[1] += rotation[1]
        pattern_mesh.rotation_euler[2] += rotation[2]

    if location:
        pattern_mesh.location[0] += location[0]
        pattern_mesh.location[1] += location[1]
        pattern_mesh.location[2] += location[2]

    # Set pattern mesh parent to main object
    # proj_obj.parent = light_obj
    
    # Setup property drivers for pattern width/height
    
    # add_driver(pixelate_node.inputs[1], light_obj, 'default_value', 'CheckerboardSettings.width')
    # add_driver(pixelate_node.inputs[2], light_obj, 'default_value', 'CheckerboardSettings.height')

    # return light_obj

class OP_AddCheckerboard(Operator):
    bl_idname = "menu.add_checkerboard"
    bl_label = "Checkerboard"

    bl_options = {'REGISTER', 'UNDO'}
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH')
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION')
    
    # Checkerboard square counts
    width: bpy.props.FloatProperty(name="Width", default=6)
    height: bpy.props.FloatProperty(name="Height", default=8)

    # TODO: Implement custom draw function to make menu look a bit nicer

    def execute(self, context):
        chb = create_checkerboard(self.location, self.rotation, self.width, self.height)

        chb_settings = chb.CheckerboardSettings
        
        chb_settings.width = self.width
        chb_settings.height = self.height

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
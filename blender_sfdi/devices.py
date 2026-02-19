import bpy
import numpy as np

from opensfdi import devices, characterisation as ch
from .utils import AddDriver


# Camera

TEMPLATE_CAMERAS = [
    ("Pi Camera v1.0", (2592, 1944)),
]

class BL_Camera(devices.BaseCamera):
    def __init__(self, bl_obj, char: ch.ZhangChar=None):
        super().__init__(char=char)

        if not BL_Camera.is_camera(bl_obj):
            raise Exception("Provided Blender object is not a camera")

        self._bl_obj = bl_obj

    @staticmethod
    def is_camera(data):
        if data is None: return False
        if data.type is None: return False

        return data.type == "CAMERA"

    @staticmethod
    def create_bl_obj(location=None, rotation=None, name="Camera"):
        bl_obj = bpy.data.objects.new(name, bpy.data.cameras.new(name))

        if location is not None: bl_obj.location = location
        if rotation is not None: bl_obj.rotation_euler = rotation

        bpy.context.collection.objects.link(bl_obj)

        return bl_obj

    @staticmethod
    def from_bl_obj(bl_obj):
        if not BL_Camera.is_camera(bl_obj):
            raise Exception("Provided Blender object is not a camera")

        return BL_Camera(bl_obj)

    def capture(self):
        pass
    
    @property
    def resolution(self):
        return self.settings.resolution
    
    @property
    def refresh_rate(self):
        return self.settings.refresh_rate
    
    @property
    def channels(self):
        if self.settings.channels == "RGB": 
            return 3

        return 1

    @property
    def shape(self):
        w, h = self.resolution

        if self.channels == 1: return (h, w)
        
        return (h, w, self.channels)


    # Blender specific properties

    @property
    def bl_obj(self):
        return self._bl_obj

    @property
    def world_matrix(self):
        return self.bl_obj.matrix_world
    
    @property
    def render_samples(self):
        return self.settings.render_samples

    @property
    def settings(self):
        return self.bl_obj.data.sfdi


# Projector

class BL_Projector(devices.BaseProjector):
    IS_PROJECTOR_STR = "is_projector"

    FRINGE_NODE = "Fringe Intensity Map"

    MASK_NAME = "ProjectorImage"

    def __init__(self, bl_obj, char:ch.ZhangChar=None):
        super().__init__(char=char)

        self._bl_obj = bl_obj

    @staticmethod
    def is_projector(bl_obj):
        if bl_obj is None: return False
        if bl_obj.type is None: return False

        return (bl_obj.type == "LIGHT") and (BL_Projector.IS_PROJECTOR_STR in bl_obj.data)

    @staticmethod
    def __fringe_shader():
        # Check if exists already, and return
        if BL_Projector.FRINGE_NODE in bpy.data.node_groups:
            return bpy.data.node_groups[BL_Projector.FRINGE_NODE]

        node_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=BL_Projector.FRINGE_NODE)
        node_tree.default_group_node_width = 140

        # Input values
        input_vector = node_tree.interface.new_socket(name="Vector", in_out='INPUT', socket_type='NodeSocketVector')
        input_vector.default_value = (0.0, 0.0, 0.0)
        input_vector.subtype = 'NONE'

        input_intensity = node_tree.interface.new_socket(name="Intensity", in_out='INPUT', socket_type='NodeSocketFloat')
        input_intensity.default_value = 0.0
        input_intensity.min_value = 0.0
        input_intensity.max_value = 1.0
        input_intensity.subtype = 'FACTOR'

        input_stripe_count = node_tree.interface.new_socket(name="Stripe Count", in_out='INPUT', socket_type='NodeSocketFloat')
        input_stripe_count.default_value = 0.0
        input_stripe_count.min_value = 0.0
        input_stripe_count.max_value = 10000.0

        input_phase = node_tree.interface.new_socket(name="Phase", in_out='INPUT', socket_type='NodeSocketFloat')
        input_phase.default_value = 0.0
        input_phase.min_value = -2 * np.pi
        input_phase.max_value = 2 * np.pi
        input_phase.subtype = 'ANGLE'

        input_rotation = node_tree.interface.new_socket(name="Rotation", in_out='INPUT', socket_type='NodeSocketFloat')
        input_rotation.default_value = 0.0
        input_rotation.min_value = -2 * np.pi
        input_rotation.max_value = 2 * np.pi
        input_rotation.subtype = 'ANGLE'

        input_noise = node_tree.interface.new_socket(name="Noise", in_out='INPUT', socket_type='NodeSocketFloat')
        input_noise.default_value = 0.0
        input_noise.min_value = 0.0
        input_noise.max_value = 1.0
        input_noise.subtype = 'FACTOR'

        input_fringes_type = node_tree.interface.new_socket(name="Fringes Type", in_out='INPUT', socket_type='NodeSocketMenu')
        
        # Rotation
        frame_rotation = node_tree.nodes.new("NodeFrame")
        frame_rotation.label = "Rotation"
        frame_rotation.name = "Frame Rotation"
        frame_rotation.label_size = 20
        frame_rotation.shrink = True

        input_group_rotation = node_tree.nodes.new("NodeGroupInput")
        input_group_rotation.name = "Group Input"

        node_rotation_separate = node_tree.nodes.new("ShaderNodeSeparateXYZ")
        node_rotation_separate.name = "Separate XYZ"

        node_rotation_sin = node_tree.nodes.new("ShaderNodeMath")
        node_rotation_sin.name = "Rotation Sin"
        node_rotation_sin.operation = 'SINE'
        node_rotation_sin.use_clamp = False

        node_rotation_cos = node_tree.nodes.new("ShaderNodeMath")
        node_rotation_cos.name = "Rotation Cos"
        node_rotation_cos.operation = 'COSINE'
        node_rotation_cos.use_clamp = False

        node_rotation_x = node_tree.nodes.new("ShaderNodeMath")
        node_rotation_x.name = "Rotation X"
        node_rotation_x.hide = True
        node_rotation_x.operation = 'MULTIPLY'
        node_rotation_x.use_clamp = False

        node_rotation_y = node_tree.nodes.new("ShaderNodeMath")
        node_rotation_y.name = "Rotation Y"
        node_rotation_y.hide = True
        node_rotation_y.operation = 'MULTIPLY'
        node_rotation_y.use_clamp = False

        node_rotation_subtract = node_tree.nodes.new("ShaderNodeMath")
        node_rotation_subtract.name = "Rotation Subtract"
        node_rotation_subtract.hide = True
        node_rotation_subtract.operation = 'SUBTRACT'
        node_rotation_subtract.use_clamp = False

        # Noise
        frame_noise = node_tree.nodes.new("NodeFrame")
        frame_noise.label = "Noise"
        frame_noise.name = "Noise Frame"
        frame_noise.label_size = 20
        frame_noise.shrink = True

        input_group_noise = node_tree.nodes.new("NodeGroupInput")
        input_group_noise.name = "Noise Input Group"

        node_white_noise = node_tree.nodes.new("ShaderNodeTexWhiteNoise")
        node_white_noise.name = "White Noise Texture"
        node_white_noise.hide = True
        node_white_noise.noise_dimensions = '2D'

        node_noise_subtract = node_tree.nodes.new("ShaderNodeMath")
        node_noise_subtract.name = "Noise Subtract"
        node_noise_subtract.hide = True
        node_noise_subtract.operation = 'SUBTRACT'
        node_noise_subtract.use_clamp = False
        node_noise_subtract.inputs[1].default_value = 0.5

        node_noise_divide = node_tree.nodes.new("ShaderNodeMath")
        node_noise_divide.name = "Noise Divide"
        node_noise_divide.hide = True
        node_noise_divide.operation = 'DIVIDE'
        node_noise_divide.use_clamp = False
        node_noise_divide.inputs[1].default_value = 2.0

        node_noise_multiply = node_tree.nodes.new("ShaderNodeMath")
        node_noise_multiply.name = "Noise Multiply"
        node_noise_multiply.operation = 'MULTIPLY'
        node_noise_multiply.use_clamp = False

        # Fringe Generator
        frame_fringes = node_tree.nodes.new("NodeFrame")
        frame_fringes.label = "Fringes Generator"
        frame_fringes.name = "Fringes Generator Frame"
        frame_fringes.label_size = 20
        frame_fringes.shrink = True

        input_group_fringes = node_tree.nodes.new("NodeGroupInput")
        input_group_fringes.name = "Fringes Input Group"

        node_fringes_twopi = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_twopi.name = "Fringes Twopi"
        node_fringes_twopi.hide = True
        node_fringes_twopi.operation = 'MULTIPLY'
        node_fringes_twopi.use_clamp = False
        node_fringes_twopi.inputs[1].default_value = 2 * np.pi

        node_fringes_x = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_x.name = "Fringes X"
        node_fringes_x.hide = True
        node_fringes_x.operation = 'MULTIPLY'
        node_fringes_x.use_clamp = False

        node_fringes_phase = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_phase.name = "Fringes Phase"
        node_fringes_phase.operation = 'ADD'
        node_fringes_phase.use_clamp = False

        node_fringes_cos = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_cos.name = "Fringes Cos"
        node_fringes_cos.operation = 'COSINE'
        node_fringes_cos.use_clamp = False

        node_fringes_add = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_add.name = "Fringes Add"
        node_fringes_add.operation = 'ADD'
        node_fringes_add.use_clamp = False
        node_fringes_add.inputs[1].default_value = 1.0

        node_fringes_divide = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_divide.name = "Fringes Divide"
        node_fringes_divide.operation = 'DIVIDE'
        node_fringes_divide.use_clamp = True
        node_fringes_divide.inputs[1].default_value = 2.0

        node_fringes_binary = node_tree.nodes.new("ShaderNodeMath")
        node_fringes_binary.name = "Fringes Binary"
        node_fringes_binary.operation = 'GREATER_THAN'
        node_fringes_binary.inputs[1].default_value = 0.5
        node_fringes_binary.use_clamp = False

        
        # Output values
        node_switch_fringes_type = node_tree.nodes.new("GeometryNodeMenuSwitch")
        node_switch_fringes_type.name = "Fringes Type Switch"
        node_switch_fringes_type.label = "Fringes Type Switch"
        node_switch_fringes_type.data_type = 'FLOAT'
        node_switch_fringes_type.enum_items.clear()
        node_switch_fringes_type.enum_items.new("Sinusoidal")
        node_switch_fringes_type.enum_items.new("Binary")
        node_switch_fringes_type.active_index = 1
        node_switch_fringes_type.inputs[0].default_value = "Sinusoidal"

        input_group_intensity = node_tree.nodes.new("NodeGroupInput")
        input_group_intensity.name = "Intensity Input Group"

        node_intensity_multiply = node_tree.nodes.new("ShaderNodeMath")
        node_intensity_multiply.name = "Intensity Multiply"
        node_intensity_multiply.operation = 'MULTIPLY'
        node_intensity_multiply.use_clamp = False

        node_output_add = node_tree.nodes.new("ShaderNodeMath")
        node_output_add.name = "Output Add"
        node_output_add.hide = True
        node_output_add.operation = 'ADD'
        node_output_add.use_clamp = True

        output_group = node_tree.nodes.new("NodeGroupOutput")
        output_group.name = "Group Output"
        output_group.hide = True
        output_group.is_active_output = True

        output_value = node_tree.interface.new_socket(name="Value", in_out='OUTPUT', socket_type='NodeSocketFloat')
        output_value.default_value = 0.0
        output_value.min_value = 0.0
        output_value.max_value = 1.0

        # Setup links
        # Rotation
        input_group_rotation.parent = frame_rotation
        node_rotation_separate.parent = frame_rotation
        node_rotation_sin.parent = frame_rotation
        node_rotation_cos.parent = frame_rotation
        node_rotation_x.parent = frame_rotation
        node_rotation_y.parent = frame_rotation
        node_rotation_subtract.parent = frame_rotation

        # Noise
        input_group_noise.parent = frame_noise
        node_white_noise.parent = frame_noise
        node_noise_subtract.parent = frame_noise
        node_noise_divide.parent = frame_noise
        node_noise_multiply.parent = frame_noise

        # Fringes Generator
        input_group_fringes.parent = frame_fringes
        node_fringes_twopi.parent = frame_fringes
        node_fringes_x.parent = frame_fringes
        node_fringes_phase.parent = frame_fringes
        node_fringes_cos.parent = frame_fringes
    
        # Output
        node_fringes_add.parent = frame_fringes
        node_fringes_divide.parent = frame_fringes
        node_fringes_binary.parent = frame_fringes
        node_switch_fringes_type.parent = frame_fringes
        input_group_intensity.parent = frame_fringes
        node_intensity_multiply.parent = frame_fringes


        # Set Node Locations
        # Rotation
        frame_rotation.location = (-393.6666564941406, 560.4666748046875)
        input_group_rotation.location = (28.91339111328125, -220.88174438476562)
        node_rotation_separate.location = (257.91339111328125, -35.88177490234375)
        node_rotation_sin.location = (259.91339111328125, -211.88174438476562)
        node_rotation_cos.location = (260.91339111328125, -359.8817138671875)
        node_rotation_x.location = (493.9134216308594, -162.88174438476562)
        node_rotation_y.location = (494.9134216308594, -331.88177490234375)
        node_rotation_subtract.location = (686.9133911132812, -248.8817138671875)

        # White Noise
        frame_noise.location = (679.6666870117188, 555.7999877929688)
        input_group_noise.location = (29.30810546875, -35.53314208984375)
        node_white_noise.location = (242.30810546875, -56.53314208984375)
        node_noise_subtract.location = (498.30804443359375, -56.53314208984375)
        node_noise_divide.location = (689.3080444335938, -56.53314208984375)
        node_noise_multiply.location = (867.3080444335938, -56.53314208984375)

        # Fringes generator
        frame_fringes.location = (211.0, 21.80000114440918)
        input_group_fringes.location = (29.218399047851562, -445.08843994140625)
        node_fringes_twopi.location = (206.8765869140625, -391.4837341308594)
        node_fringes_x.location = (412.84967041015625, -269.51153564453125)
        node_fringes_phase.location = (634.0, -297.79998779296875)
        node_fringes_cos.location = (832.0, -295.79998779296875)
        node_fringes_add.location = (1017.0, -230.8000030517578)
        node_fringes_divide.location = (1184.0, -247.8000030517578)
        node_fringes_binary.location = (1384.0, -347.79998779296875)
        node_switch_fringes_type.location = (1600.8984375, -198.72764587402344)

        # Intensity
        input_group_intensity.location = (1380.0693359375, -43.666629791259766)
        node_intensity_multiply.location = (1790.1973876953125, -35.68275833129883)
        node_output_add.location = (2198.2353515625, 99.14217376708984)
        output_group.location = (2367.741455078125, 104.7054443359375)


        # Rotation
        # SeparateXYZ -> Sin(rot) + Cos(rot)
        node_tree.links.new(input_group_rotation.outputs[0], node_rotation_separate.inputs[0])
        node_tree.links.new(input_group_rotation.outputs[4], node_rotation_sin.inputs[0])
        node_tree.links.new(input_group_rotation.outputs[4], node_rotation_cos.inputs[0])
        
        # Sin / Cos -> Multiply
        node_tree.links.new(node_rotation_separate.outputs[0], node_rotation_x.inputs[0])
        node_tree.links.new(node_rotation_separate.outputs[1], node_rotation_y.inputs[0])
        node_tree.links.new(node_rotation_cos.outputs[0], node_rotation_x.inputs[1])
        node_tree.links.new(node_rotation_sin.outputs[0], node_rotation_y.inputs[1])

        # X / Y -> Subtract -> Fringes Generator
        node_tree.links.new(node_rotation_x.outputs[0], node_rotation_subtract.inputs[0])
        node_tree.links.new(node_rotation_y.outputs[0], node_rotation_subtract.inputs[1])
        node_tree.links.new(node_rotation_subtract.outputs[0], node_fringes_x.inputs[0])

        # Noise
        node_tree.links.new(input_group_noise.outputs[0], node_white_noise.inputs[0])
        node_tree.links.new(node_white_noise.outputs[0], node_noise_subtract.inputs[0])
        node_tree.links.new(node_noise_subtract.outputs[0], node_noise_divide.inputs[0])
        node_tree.links.new(node_noise_divide.outputs[0], node_noise_multiply.inputs[0])
        node_tree.links.new(input_group_noise.outputs[5], node_noise_multiply.inputs[1])

        node_tree.links.new(node_noise_multiply.outputs[0], node_output_add.inputs[0])

        # Fringes Generator
        node_tree.links.new(input_group_fringes.outputs[2], node_fringes_twopi.inputs[0])
        node_tree.links.new(input_group_fringes.outputs[3], node_fringes_phase.inputs[1])
        node_tree.links.new(node_fringes_twopi.outputs[0], node_fringes_x.inputs[1])
        node_tree.links.new(node_fringes_x.outputs[0], node_fringes_phase.inputs[0])
        node_tree.links.new(node_fringes_phase.outputs[0], node_fringes_cos.inputs[0])
        node_tree.links.new(node_fringes_cos.outputs[0], node_fringes_add.inputs[0])
        node_tree.links.new(node_fringes_add.outputs[0], node_fringes_divide.inputs[0])
        node_tree.links.new(node_fringes_divide.outputs[0], node_intensity_multiply.inputs[1])
        node_tree.links.new(node_fringes_divide.outputs[0], node_fringes_binary.inputs[0])

        # Output
        node_tree.links.new(input_group_intensity.outputs[6], node_switch_fringes_type.inputs[0])
        node_tree.links.new(node_fringes_divide.outputs[0], node_switch_fringes_type.inputs[1])
        node_tree.links.new(node_fringes_binary.outputs[0], node_switch_fringes_type.inputs[2])

        node_tree.links.new(input_group_intensity.outputs[1], node_intensity_multiply.inputs[0])
        node_tree.links.new(node_switch_fringes_type.outputs[0], node_intensity_multiply.inputs[1])
        node_tree.links.new(node_intensity_multiply.outputs[0], node_output_add.inputs[1])
        node_tree.links.new(node_output_add.outputs[0], output_group.inputs[0])

        return node_tree

    @staticmethod
    def __generate_shader(bl_light_data):
        bl_light_data.use_nodes = True

        node_tree = bl_light_data.node_tree
        node_tree.nodes.clear()

        node_tree = bl_light_data.node_tree
        node_tree.color_tag = 'NONE'
        node_tree.description = ""
        node_tree.default_group_node_width = 140

        node_links = node_tree.links

        # Node Texture Coordinate
        node_texture_coord = node_tree.nodes.new("ShaderNodeTexCoord")
        node_texture_coord.from_instancer = False

        # Divide Coordinates
        node_divide_xz = node_tree.nodes.new("ShaderNodeMath")
        node_divide_xz.operation = 'DIVIDE'
        node_divide_xz.use_clamp = False

        node_divide_yz = node_tree.nodes.new("ShaderNodeMath")
        node_divide_yz.operation = 'DIVIDE'
        node_divide_yz.use_clamp = False

        # Node Combine XYZ
        node_combine_xyz = node_tree.nodes.new("ShaderNodeCombineXYZ")
        node_combine_xyz.inputs[2].default_value = 0.0

        # Node Separate XYZ
        node_separate_xyz = node_tree.nodes.new("ShaderNodeSeparateXYZ")

        # First Channel
        node_channel_1 = node_tree.nodes.new("ShaderNodeGroup")
        node_channel_1.name = "Channel 1"
        node_channel_1.node_tree = BL_Projector.__fringe_shader()

        node_channel_1.inputs[1].default_value = 1.0 	        # Intensity
        node_channel_1.inputs[2].default_value = 16.0 	        # Stripe Count
        node_channel_1.inputs[3].default_value = 0.0 	        # Phase
        node_channel_1.inputs[4].default_value = 0.0	        # Rotation
        node_channel_1.inputs[5].default_value = 0.0	        # Noise
        node_channel_1.inputs[6].default_value = "Sinusoidal"   # Fringe Type


        # First Channel
        node_channel_2 = node_tree.nodes.new("ShaderNodeGroup")
        node_channel_2.name = "Channel 2"
        node_channel_2.node_tree = BL_Projector.__fringe_shader()
        node_channel_2.inputs[1].default_value = 1.0 	        # Intensity
        node_channel_2.inputs[2].default_value = 16.0 	        # Stripe Count
        node_channel_2.inputs[3].default_value = 0.0 	        # Phase
        node_channel_2.inputs[4].default_value = 0.0	        # Rotation
        node_channel_2.inputs[5].default_value = 0.0	        # Noise
        node_channel_2.inputs[6].default_value = "Sinusoidal"   # Fringe Type


        # First Channel
        node_channel_3 = node_tree.nodes.new("ShaderNodeGroup")
        node_channel_3.name = "Channel 3"
        node_channel_3.node_tree = BL_Projector.__fringe_shader()
        node_channel_3.inputs[1].default_value = 1.0 	        # Intensity
        node_channel_3.inputs[2].default_value = 16.0 	        # Stripe Count
        node_channel_3.inputs[3].default_value = 0.0 	        # Phase
        node_channel_3.inputs[4].default_value = 0.0	        # Rotation
        node_channel_3.inputs[5].default_value = 0.0	        # Noise
        node_channel_3.inputs[6].default_value = "Sinusoidal"   # Fringe Type

        # Node Mapping
        node_mapping = node_tree.nodes.new("ShaderNodeMapping")
        node_mapping.vector_type = 'POINT'
        node_mapping.inputs[1].default_value = (0.5, 0.5, 0.0)		# Location
        node_mapping.inputs[2].default_value = (0.0, 0.0, 0.0) 		# Rotation
        node_mapping.inputs[3].default_value = (1.0, 16.0/9.0, 1.0)	# Scale

        # Node Image Texture
        node_image_texture = node_tree.nodes.new("ShaderNodeTexImage")
        node_image_texture.name = "Image Mask"
        node_image_texture.extension = 'CLIP'
        node_image_texture.interpolation = 'Closest'

        # TODO: Add configurable resolution
        if bpy.data.images.get(BL_Projector.MASK_NAME, None) is None:
            bpy.ops.image.new(name=BL_Projector.MASK_NAME, width=4096, height=4096, color=(1.0, 1.0, 1.0, 1.0), alpha=False, generated_type="BLANK")

        node_image_texture.image = bpy.data.images.get(BL_Projector.MASK_NAME)

        # Node Reroute
        node_mapping_reroute = node_tree.nodes.new("NodeReroute")
        node_mapping_reroute.socket_idname = "NodeSocketVector"

        # Node Light Falloff
        node_falloff = node_tree.nodes.new("ShaderNodeLightFalloff")
        node_falloff.inputs[0].default_value = 1.0 # Strength
        node_falloff.inputs[1].default_value = 0.0 # Smooth

        # Node Mix
        node_mix_colour = node_tree.nodes.new("ShaderNodeMix")
        node_mix_colour.blend_type = 'MULTIPLY'
        node_mix_colour.clamp_factor = True
        node_mix_colour.clamp_result = True
        node_mix_colour.data_type = 'RGBA'
        node_mix_colour.factor_mode = 'UNIFORM'
        node_mix_colour.inputs[0].default_value = 1.0
        node_combine_colour = node_tree.nodes.new("ShaderNodeCombineXYZ")

        # Node Channels
        node_switch_channels = node_tree.nodes.new("GeometryNodeMenuSwitch")
        node_switch_channels.name = "Channels Switch"
        node_switch_channels.label = "Channels"
        node_switch_channels.data_type = 'RGBA'
        node_switch_channels.enum_items.clear()
        node_switch_channels.enum_items.new("Monochrome")
        node_switch_channels.enum_items.new("RGB")
        node_switch_channels.active_index = 1
        node_switch_channels.inputs[0].default_value = 'Monochrome'

        # Node Falloff
        node_switch_falloff = node_tree.nodes.new("GeometryNodeMenuSwitch")
        node_switch_falloff.name = "Light Falloff Switch"
        node_switch_falloff.label = "Falloff"
        node_switch_falloff.data_type = 'RGBA'
        node_switch_falloff.enum_items.clear()
        node_switch_falloff.enum_items.new("Quadratic")
        node_switch_falloff.enum_items.new("Linear")
        node_switch_falloff.enum_items.new("Constant")
        node_switch_falloff.active_index = 2
        node_switch_falloff.inputs[0].default_value = 'Quadratic'

        # Node Emission
        node_emission = node_tree.nodes.new("ShaderNodeEmission")
        node_emission.name = "Emission"

        # Node Light Output
        output_light = node_tree.nodes.new("ShaderNodeOutputLight")
        output_light.is_active_output = True
        output_light.target = 'ALL'


        # Set locations
        node_texture_coord.location = (-672, -14)

        node_separate_xyz.location = (-467, -12)
        node_divide_xz.location = (-231, 108)
        node_divide_yz.location = (-231, -68)
        node_combine_xyz.location = (0, 0)

        node_mapping.location = (235, 0)

        node_image_texture.location = (483, 373)
        node_mapping_reroute.location = (432, -31)

        node_channel_1.location = (482, 85)
        node_channel_2.location = (482, -156)
        node_channel_3.location = (482, -349)

        node_combine_colour.location = (774, -112)

        node_switch_channels.location = (1003, 49)

        node_mix_colour.location = (1209, 248)

        node_falloff.location = (1004, -141)
        node_switch_falloff.location = (1210, -31)

        node_emission.location = (1391, 49)
        output_light.location = (1580, 42)


        # Setup links
        # Texture Coordinate Normal Output
        node_links.new(node_texture_coord.outputs[1], node_separate_xyz.inputs[0])

        # SeparateXYZ -> X / Z
        node_links.new(node_separate_xyz.outputs[0], node_divide_xz.inputs[0])
        node_links.new(node_separate_xyz.outputs[2], node_divide_xz.inputs[1])

        # SeparateXYZ -> Y / Z
        node_links.new(node_separate_xyz.outputs[1], node_divide_yz.inputs[0])
        node_links.new(node_separate_xyz.outputs[2], node_divide_yz.inputs[1])

        # Mapping
        node_links.new(node_divide_yz.outputs[0], node_combine_xyz.inputs[1])
        node_links.new(node_divide_xz.outputs[0], node_combine_xyz.inputs[0])

        node_links.new(node_combine_xyz.outputs[0], node_mapping.inputs[0])
        node_links.new(node_mapping.outputs[0], node_image_texture.inputs[0])

        # Vector Input -> Channels
        node_links.new(node_mapping.outputs[0], node_mapping_reroute.inputs[0])
        node_links.new(node_mapping_reroute.outputs[0], node_channel_1.inputs[0])
        node_links.new(node_mapping_reroute.outputs[0], node_channel_2.inputs[0])
        node_links.new(node_mapping_reroute.outputs[0], node_channel_3.inputs[0])

        # Combine RGB Colour
        node_links.new(node_channel_1.outputs[0], node_combine_colour.inputs[0])
        node_links.new(node_channel_2.outputs[0], node_combine_colour.inputs[1])
        node_links.new(node_channel_3.outputs[0], node_combine_colour.inputs[2])
        node_links.new(node_combine_colour.outputs[0], node_switch_channels.inputs[2])

        # Monocrhome Colour
        node_links.new(node_channel_1.outputs[0], node_switch_channels.inputs[1])

        # Apply ImageTexture to chosen colour
        node_links.new(node_image_texture.outputs[0], node_mix_colour.inputs[6])
        node_links.new(node_switch_channels.outputs[0], node_mix_colour.inputs[7])
        node_links.new(node_mix_colour.outputs[2], node_emission.inputs[0])

        # Switch Light Falloff
        node_links.new(node_falloff.outputs[0], node_switch_falloff.inputs[1])
        node_links.new(node_falloff.outputs[1], node_switch_falloff.inputs[2])
        node_links.new(node_falloff.outputs[2], node_switch_falloff.inputs[3])
        node_links.new(node_switch_falloff.outputs[0], node_emission.inputs[1])

        # Emission output
        node_links.new(node_emission.outputs[0], output_light.inputs[0])

        return node_tree

    @staticmethod
    def create_bl_obj(location=None, rotation=None, name="Projector", channels=1, fringes_stripe_count=16.0, fringes_phase=0.0, fringes_rot=0.0):
        # Create new light for the projector
        bl_light_data = bpy.data.lights.new(name=f"{name}Light", type='SPOT')

        bl_light_data.energy = 5
        bl_light_data.exposure = 0.0
        bl_light_data.normalize = False
        bl_light_data.use_temperature = False
        bl_light_data.color = (1.0, 1.0, 1.0)
        bl_light_data.shadow_soft_size = 0.0
        bl_light_data.spot_blend = 0.0
        bl_light_data.spot_size = np.pi
        # bl_light_data.cycles.max_bounces = 16  # Max light bounces of 16 for performance

        # Create a shader for this projector
        BL_Projector.__generate_shader(bl_light_data)
        
        # Link data to bl_obj
        bl_light_obj = bpy.data.objects.new(name=name, object_data=bl_light_data)
        bpy.context.collection.objects.link(bl_light_obj)

        # Set default property values
        bl_light_data.sfdi.channels = "RGB" if channels == 3 else "Monochrome"
        for _ in range(max(3, channels)): bl_light_data.sfdi.channels_list.add()

        # Setup property drivers for fringe projector
        bl_light_data[BL_Projector.IS_PROJECTOR_STR] = True

        # Add drivers for props to shader
        node_tree = bl_light_data.node_tree

        # Aspect Ratio
        AddDriver(node_tree.nodes["Mapping"].inputs[3], bl_light_obj, 'default_value', 'data.sfdi.aspect_ratio', index=1)

        # Throw Ratio: TODO: Currently inverse relationship, need to flip in driver
        AddDriver(bl_light_obj, bl_light_obj, 'scale', 'data.sfdi.throw_ratio', index=2)

        # Channels (Currently Not Supported as of Blender 5.0)
        # AddDriver(node_tree.nodes["Channels Switch"].inputs[0], bl_light_obj, 'default_value', 'data.sfdi.channels')
        
        # Light Falloff (Currently Not Supported as of Blender 5.0)
        # AddDriver(node_tree.nodes["Light Falloff Switch"].inputs[0], bl_light_obj, 'default_value', f'data.sfdi.light_falloff')

        for i in range(3):
            node = node_tree.nodes[f"Channel {i+1}"]

            AddDriver(node.inputs["Intensity"], bl_light_obj, 'default_value', f'data.sfdi.channels_list[{i}].intensity')
            AddDriver(node.inputs["Stripe Count"], bl_light_obj, 'default_value', f'data.sfdi.channels_list[{i}].stripe_count')
            AddDriver(node.inputs["Phase"], bl_light_obj, 'default_value', f'data.sfdi.channels_list[{i}].phase')
            AddDriver(node.inputs["Rotation"], bl_light_obj, 'default_value', f'data.sfdi.channels_list[{i}].rotation')
            AddDriver(node.inputs["Noise"], bl_light_obj, 'default_value', f'data.sfdi.channels_list[{i}].noise')
            
        
        # TODO: Figure out resolution


        # AddDriver(fringe_node.inputs[3], bl_light_obj, 'default_value', 'data.sfdi.phase')
        # AddDriver(fringe_node.inputs[1], bl_light_obj, 'default_value', 'data.sfdi.rotation')
        
        # AddDriver(pixelate_node.inputs[1], bl_light_obj, 'default_value', 'data.sfdi.resolution[0]')
        # AddDriver(pixelate_node.inputs[2], bl_light_obj, 'default_value', 'data.sfdi.resolution[1]')

        # AddDriver(mapping_node.inputs[3], bl_light_obj, 'default_value', 'data.sfdi.aspect_ratio', index=0)
        # AddDriver(bl_light_obj, bl_light_obj, 'scale', 'data.sfdi.throw_ratio', index=2)
        
        if rotation is not None:
            bl_light_obj.rotation_euler[0] = rotation[0]
            bl_light_obj.rotation_euler[1] = rotation[1]
            bl_light_obj.rotation_euler[2] = rotation[2]

        if location is not None:
            bl_light_obj.location[0] = location[0]
            bl_light_obj.location[1] = location[1]
            bl_light_obj.location[2] = location[2]

        return bl_light_obj

    @staticmethod
    def from_bl_obj(bl_obj):
        if not BL_Projector.is_projector(bl_obj):
            raise Exception("Provided Blender object is not a projector")

        return BL_Projector(bl_obj)

    def display(self):
        pass

    @property
    def resolution(self):
        return self.settings.resolution
    
    @property
    def refresh_rate(self):
        return -1
    
    @property
    def channels(self):
        if self.settings.channels == "RGB": 
            return 3

        return 1

    @property
    def aspect_ratio(self):
        return self.settings.aspect_ratio

    @property
    def throw_ratio(self):
        return self.settings.throw_ratio

    @property
    def shape(self):
        w, h = self.resolution

        if self.channels == 1: return (h, w)
        
        return (h, w, self.channels)

    # Blender specific properties

    @property
    def light_falloff(self):
        return self.settings.light_falloff

    @property
    def bl_obj(self):
        return self._bl_obj

    @property
    def world_matrix(self):
        return self.bl_obj.matrix_world

    @property
    def settings(self):
        return self.bl_obj.data.sfdi


# Characterisation Board
# TODO: Add support for creating CircleBoard and Checkerboard

class BL_CharBoard:
    IS_BOARD_STR = "is_char_board"

    def __init__(self, bl_obj):
        if not BL_CharBoard.is_char_board(bl_obj):
            raise ValueError(f"{bl_obj.name} is not a characterisation board")

        self._bl_obj = bl_obj

    @property
    def settings(self):
        return self.bl_obj.sfdi
    
    @property
    def bl_obj(self):
        return self._bl_obj
    
    @property
    def world_matrix(self):
        return self.bl_obj.matrix_world

    @staticmethod
    def create_bl_obj(location, rotation):
        # Get active object
        bl_obj = bpy.context.active_object

        bl_obj.location = location
        bl_obj.rotation_euler = rotation

        # Set property flag
        bl_obj.data[BL_CharBoard.IS_BOARD_STR] = True

        return bl_obj
    
    @staticmethod
    def _checkerboard_shader(material):
        node_tree = material.node_tree

        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        material.alpha_threshold = 0.5
        material.line_priority = 0
        material.max_vertex_displacement = 0.0
        material.metallic = 0.0
        material.paint_active_slot = 0
        material.paint_clone_slot = 0
        material.pass_index = 0
        material.refraction_depth = 0.0
        material.roughness = 0.4000000059604645
        material.show_transparent_back = True
        material.specular_intensity = 0.5
        material.use_backface_culling = False
        material.use_backface_culling_lightprobe_volume = True
        material.use_backface_culling_shadow = False
        material.use_preview_world = False
        material.use_raytrace_refraction = False
        material.use_screen_refraction = False
        material.use_sss_translucency = False
        material.use_thickness_from_shadow = False
        material.use_transparency_overlap = True
        material.use_transparent_shadow = True
        material.blend_method = 'HASHED'
        material.displacement_method = 'BUMP'
        material.preview_render_type = 'SPHERE'
        material.surface_render_method = 'DITHERED'
        material.thickness_mode = 'SPHERE'
        material.volume_intersection_method = 'FAST'
        material.specular_color = (1.0, 1.0, 1.0)
        material.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        material.line_color = (0.0, 0.0, 0.0, 0.0)

        principled_bsdf = node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'MULTI_GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK'

        principled_bsdf.inputs[1].default_value = 0.0
        principled_bsdf.inputs[2].default_value = 0.5
        principled_bsdf.inputs[3].default_value = 1.5
        principled_bsdf.inputs[4].default_value = 1.0
        principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[7].default_value = 0.0
        principled_bsdf.inputs[8].default_value = 0.0
        principled_bsdf.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
        principled_bsdf.inputs[10].default_value = 0.05000000074505806
        principled_bsdf.inputs[12].default_value = 0.0
        principled_bsdf.inputs[13].default_value = 0.5
        principled_bsdf.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[15].default_value = 0.0
        principled_bsdf.inputs[16].default_value = 0.0
        principled_bsdf.inputs[17].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[18].default_value = 0.0
        principled_bsdf.inputs[19].default_value = 0.0
        principled_bsdf.inputs[20].default_value = 0.029999999329447746
        principled_bsdf.inputs[21].default_value = 1.5
        principled_bsdf.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[23].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[24].default_value = 0.0
        principled_bsdf.inputs[25].default_value = 0.5
        principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[28].default_value = 0.0
        principled_bsdf.inputs[29].default_value = 0.0
        principled_bsdf.inputs[30].default_value = 1.3300000429153442

        # Node Material Output
        material_output = node_tree.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        material_output.inputs[3].default_value = 0.0

        checker_texture = node_tree.nodes.new("ShaderNodeTexChecker")
        checker_texture.name = "Checker Texture"
        checker_texture.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        checker_texture.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
        checker_texture.inputs[3].default_value = 1.0

        mapping = node_tree.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'TEXTURE'
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)

        texture_coordinate = node_tree.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        value = node_tree.nodes.new("ShaderNodeValue")
        value.label = "POI Count X"
        value.name = "Value"

        value.outputs[0].default_value = 15.0
        value_001 = node_tree.nodes.new("ShaderNodeValue")
        value_001.label = "POI Count Y"
        value_001.name = "Value.001"
        value_001.outputs[0].default_value = 15.0

        math = node_tree.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.hide = True
        math.operation = 'DIVIDE'
        math.use_clamp = False
        math.inputs[0].default_value = 1.0

        math_001 = node_tree.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.hide = True
        math_001.operation = 'DIVIDE'
        math_001.use_clamp = False
        math_001.inputs[0].default_value = 1.0

        combine_xyz = node_tree.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz.name = "Combine XYZ"
        combine_xyz.inputs[2].default_value = 0.0

        math_002 = node_tree.nodes.new("ShaderNodeMath")
        math_002.name = "Math.002"
        math_002.hide = True
        math_002.operation = 'ADD'
        math_002.use_clamp = False
        math_002.inputs[1].default_value = 1.0

        math_003 = node_tree.nodes.new("ShaderNodeMath")
        math_003.name = "Math.003"
        math_003.hide = True
        math_003.operation = 'ADD'
        math_003.use_clamp = False
        math_003.inputs[1].default_value = 1.0

        # Set locations
        node_tree.nodes["Principled BSDF"].location = (-98.1971206665039, 135.6539306640625)
        node_tree.nodes["Material Output"].location = (200.0984649658203, 134.7980499267578)
        node_tree.nodes["Checker Texture"].location = (-299.76995849609375, 134.21649169921875)
        node_tree.nodes["Mapping"].location = (-497.7911682128906, 134.1084747314453)
        node_tree.nodes["Texture Coordinate"].location = (-704.7914428710938, 132.6710662841797)
        node_tree.nodes["Value"].location = (-1354.1865234375, -132.7310333251953)
        node_tree.nodes["Value.001"].location = (-1353.65283203125, -222.9019012451172)
        node_tree.nodes["Math"].location = (-938.5772094726562, -135.8905487060547)
        node_tree.nodes["Math.001"].location = (-940.7443237304688, -227.1855010986328)
        node_tree.nodes["Combine XYZ"].location = (-703.8069458007812, -137.7341766357422)
        node_tree.nodes["Math.002"].location = (-1140.0966796875, -136.25839233398438)
        node_tree.nodes["Math.003"].location = (-1141.5823974609375, -226.9690399169922)

        node_tree.links.new(node_tree.nodes["Principled BSDF"].outputs[0], node_tree.nodes["Material Output"].inputs[0])
        node_tree.links.new(node_tree.nodes["Mapping"].outputs[0], node_tree.nodes["Checker Texture"].inputs[0])
        node_tree.links.new(node_tree.nodes["Checker Texture"].outputs[0], node_tree.nodes["Principled BSDF"].inputs[0])
        node_tree.links.new(node_tree.nodes["Texture Coordinate"].outputs[2], node_tree.nodes["Mapping"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.002"].outputs[0], node_tree.nodes["Math"].inputs[1])
        node_tree.links.new(node_tree.nodes["Math"].outputs[0], node_tree.nodes["Combine XYZ"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.001"].outputs[0], node_tree.nodes["Combine XYZ"].inputs[1])
        node_tree.links.new(node_tree.nodes["Combine XYZ"].outputs[0], node_tree.nodes["Mapping"].inputs[3])
        node_tree.links.new(node_tree.nodes["Math.003"].outputs[0], node_tree.nodes["Math.001"].inputs[1])
        node_tree.links.new(node_tree.nodes["Value"].outputs[0], node_tree.nodes["Math.002"].inputs[0])
        node_tree.links.new(node_tree.nodes["Value.001"].outputs[0], node_tree.nodes["Math.003"].inputs[0])

    @staticmethod
    def _circleboard_shader(material):
        node_tree = material.node_tree

        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        material.alpha_threshold = 0.5
        material.line_priority = 0
        material.max_vertex_displacement = 0.0
        material.metallic = 0.0
        material.paint_active_slot = 0
        material.paint_clone_slot = 0
        material.pass_index = 0
        material.refraction_depth = 0.0
        material.roughness = 0.4000000059604645
        material.show_transparent_back = True
        material.specular_intensity = 0.5
        material.use_backface_culling = False
        material.use_backface_culling_lightprobe_volume = True
        material.use_backface_culling_shadow = False
        material.use_preview_world = False
        material.use_raytrace_refraction = False
        material.use_screen_refraction = False
        material.use_sss_translucency = False
        material.use_thickness_from_shadow = False
        material.use_transparency_overlap = True
        material.use_transparent_shadow = True
        material.blend_method = 'HASHED'
        material.displacement_method = 'BUMP'
        material.preview_render_type = 'SPHERE'
        material.surface_render_method = 'DITHERED'
        material.thickness_mode = 'SPHERE'
        material.volume_intersection_method = 'FAST'
        material.specular_color = (1.0, 1.0, 1.0)
        material.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        material.line_color = (0.0, 0.0, 0.0, 0.0)

        # Node Principled BSDF
        principled_bsdf = node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'MULTI_GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK'
        principled_bsdf.inputs[1].default_value = 0.0
        principled_bsdf.inputs[2].default_value = 0.5
        principled_bsdf.inputs[3].default_value = 1.5
        principled_bsdf.inputs[4].default_value = 1.0
        principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[7].default_value = 0.0
        principled_bsdf.inputs[8].default_value = 0.0
        principled_bsdf.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
        principled_bsdf.inputs[10].default_value = 0.05000000074505806
        principled_bsdf.inputs[12].default_value = 0.0
        principled_bsdf.inputs[13].default_value = 0.5
        principled_bsdf.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[15].default_value = 0.0
        principled_bsdf.inputs[16].default_value = 0.0
        principled_bsdf.inputs[17].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[18].default_value = 0.0
        principled_bsdf.inputs[19].default_value = 0.0
        principled_bsdf.inputs[20].default_value = 0.029999999329447746
        principled_bsdf.inputs[21].default_value = 1.5
        principled_bsdf.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[23].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[24].default_value = 0.0
        principled_bsdf.inputs[25].default_value = 0.5
        principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[28].default_value = 0.0
        principled_bsdf.inputs[29].default_value = 0.0
        principled_bsdf.inputs[30].default_value = 1.3300000429153442

        # Node Material Output
        material_output = node_tree.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        material_output.inputs[3].default_value = 0.0

        # Node Mapping
        mapping = node_tree.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'TEXTURE'
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
        mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

        texture_coordinate = node_tree.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        separate_xyz = node_tree.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz.name = "Separate XYZ"

        math = node_tree.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.operation = 'MULTIPLY'
        math.use_clamp = False

        math_001 = node_tree.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.operation = 'MULTIPLY'
        math_001.use_clamp = False

        math_002 = node_tree.nodes.new("ShaderNodeMath")
        math_002.name = "Math.002"
        math_002.operation = 'FRACT'
        math_002.use_clamp = False

        math_003 = node_tree.nodes.new("ShaderNodeMath")
        math_003.name = "Math.003"
        math_003.operation = 'FRACT'
        math_003.use_clamp = False

        math_004 = node_tree.nodes.new("ShaderNodeMath")
        math_004.name = "Math.004"
        math_004.operation = 'SUBTRACT'
        math_004.use_clamp = False
        math_004.inputs[1].default_value = 0.5

        math_005 = node_tree.nodes.new("ShaderNodeMath")
        math_005.name = "Math.005"
        math_005.operation = 'SUBTRACT'
        math_005.use_clamp = False
        math_005.inputs[1].default_value = 0.5

        math_006 = node_tree.nodes.new("ShaderNodeMath")
        math_006.name = "Math.006"
        math_006.operation = 'POWER'
        math_006.use_clamp = False
        math_006.inputs[1].default_value = 2.0

        # Node Math.007
        math_007 = node_tree.nodes.new("ShaderNodeMath")
        math_007.name = "Math.007"
        math_007.operation = 'POWER'
        math_007.use_clamp = False
        math_007.inputs[1].default_value = 2.0

        math_008 = node_tree.nodes.new("ShaderNodeMath")
        math_008.name = "Math.008"
        math_008.operation = 'ADD'
        math_008.use_clamp = False

        math_009 = node_tree.nodes.new("ShaderNodeMath")
        math_009.name = "Math.009"
        math_009.operation = 'SQRT'
        math_009.use_clamp = False

        math_010 = node_tree.nodes.new("ShaderNodeMath")
        math_010.name = "Math.010"
        math_010.operation = 'LESS_THAN'
        math_010.use_clamp = True
        math_010.inputs[1].default_value = 0.5

        value = node_tree.nodes.new("ShaderNodeValue")
        value.label = "Spacing X"
        value.name = "Value"

        value.outputs[0].default_value = 1.0
        math_011 = node_tree.nodes.new("ShaderNodeMath")
        math_011.name = "Math.011"
        math_011.operation = 'MULTIPLY'
        math_011.use_clamp = False

        math_012 = node_tree.nodes.new("ShaderNodeMath")
        math_012.name = "Math.012"
        math_012.operation = 'MULTIPLY'
        math_012.use_clamp = False

        value_001 = node_tree.nodes.new("ShaderNodeValue")
        value_001.label = "Spacing Y"
        value_001.name = "Value.001"

        value_001.outputs[0].default_value = 1.0
        math_013 = node_tree.nodes.new("ShaderNodeMath")
        math_013.name = "Math.013"
        math_013.operation = 'ADD'
        math_013.use_clamp = False
        math_013.inputs[1].default_value = 1.0

        math_014 = node_tree.nodes.new("ShaderNodeMath")
        math_014.name = "Math.014"
        math_014.operation = 'ADD'
        math_014.use_clamp = False
        math_014.inputs[1].default_value = 1.0

        value_002 = node_tree.nodes.new("ShaderNodeValue")
        value_002.label = "POI Count Y"
        value_002.name = "Value.002"

        value_002.outputs[0].default_value = 13.0
        value_003 = node_tree.nodes.new("ShaderNodeValue")
        value_003.label = "POI Count X"
        value_003.name = "Value.003"

        value_003.outputs[0].default_value = 13.0
        node_tree.nodes["Principled BSDF"].location = (1481.1448974609375, 172.7858428955078)
        node_tree.nodes["Material Output"].location = (1822.4039306640625, 172.61354064941406)
        node_tree.nodes["Mapping"].location = (-1056.72705078125, 141.2757110595703)
        node_tree.nodes["Texture Coordinate"].location = (-1263.7271728515625, 139.83827209472656)
        node_tree.nodes["Separate XYZ"].location = (-861.0908203125, 174.92811584472656)
        node_tree.nodes["Math"].location = (-573.0879516601562, 253.6879425048828)
        node_tree.nodes["Math.001"].location = (-576.3865356445312, 80.12899017333984)
        node_tree.nodes["Math.002"].location = (-262.76092529296875, 253.8677520751953)
        node_tree.nodes["Math.003"].location = (-263.62066650390625, 80.00749969482422)
        node_tree.nodes["Math.004"].location = (55.75461959838867, 255.3138427734375)
        node_tree.nodes["Math.005"].location = (58.914306640625, 81.32154083251953)
        node_tree.nodes["Math.006"].location = (574.0513916015625, 255.2118377685547)
        node_tree.nodes["Math.007"].location = (572.1910400390625, 80.54219818115234)
        node_tree.nodes["Math.008"].location = (841.5757446289062, 170.29054260253906)
        node_tree.nodes["Math.009"].location = (1043.65380859375, 173.7025909423828)
        node_tree.nodes["Math.010"].location = (1256.6651611328125, 173.0057830810547)
        node_tree.nodes["Value"].location = (-109.07379913330078, 325.8116149902344)
        node_tree.nodes["Math.011"].location = (299.3882141113281, 281.4593200683594)
        node_tree.nodes["Math.012"].location = (296.0896301269531, 107.900390625)
        node_tree.nodes["Value.001"].location = (-109.20208740234375, -88.8041000366211)
        node_tree.nodes["Math.013"].location = (57.47953414916992, -73.3337631225586)
        node_tree.nodes["Math.014"].location = (56.58627700805664, 420.9566955566406)
        node_tree.nodes["Value.002"].location = (-754.9849243164062, -73.02371215820312)
        node_tree.nodes["Value.003"].location = (-766.064697265625, 309.53759765625)

        node_tree.links.new(node_tree.nodes["Principled BSDF"].outputs[0], node_tree.nodes["Material Output"].inputs[0])
        node_tree.links.new(node_tree.nodes["Texture Coordinate"].outputs[2], node_tree.nodes["Mapping"].inputs[0])
        node_tree.links.new(node_tree.nodes["Mapping"].outputs[0], node_tree.nodes["Separate XYZ"].inputs[0])
        node_tree.links.new(node_tree.nodes["Separate XYZ"].outputs[1], node_tree.nodes["Math.001"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math"].outputs[0], node_tree.nodes["Math.002"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.001"].outputs[0], node_tree.nodes["Math.003"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.002"].outputs[0], node_tree.nodes["Math.004"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.003"].outputs[0], node_tree.nodes["Math.005"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.006"].outputs[0], node_tree.nodes["Math.008"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.007"].outputs[0], node_tree.nodes["Math.008"].inputs[1])
        node_tree.links.new(node_tree.nodes["Math.008"].outputs[0], node_tree.nodes["Math.009"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.010"].outputs[0], node_tree.nodes["Principled BSDF"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.009"].outputs[0], node_tree.nodes["Math.010"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.011"].outputs[0], node_tree.nodes["Math.006"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.005"].outputs[0], node_tree.nodes["Math.012"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.012"].outputs[0], node_tree.nodes["Math.007"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.013"].outputs[0], node_tree.nodes["Math.012"].inputs[1])
        node_tree.links.new(node_tree.nodes["Value"].outputs[0], node_tree.nodes["Math.014"].inputs[0])
        node_tree.links.new(node_tree.nodes["Value.001"].outputs[0], node_tree.nodes["Math.013"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.014"].outputs[0], node_tree.nodes["Math.011"].inputs[0])
        node_tree.links.new(node_tree.nodes["Math.004"].outputs[0], node_tree.nodes["Math.011"].inputs[1])
        node_tree.links.new(node_tree.nodes["Value.003"].outputs[0], node_tree.nodes["Math"].inputs[0])
        node_tree.links.new(node_tree.nodes["Separate XYZ"].outputs[0], node_tree.nodes["Math"].inputs[1])
        node_tree.links.new(node_tree.nodes["Value.002"].outputs[0], node_tree.nodes["Math.001"].inputs[1])

        return node_tree

    @staticmethod
    def _imageboard_shader(material):
        node_tree = material.node_tree

        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        material.alpha_threshold = 0.5
        material.line_priority = 0
        material.max_vertex_displacement = 0.0
        material.metallic = 0.0
        material.paint_active_slot = 0
        material.paint_clone_slot = 0
        material.pass_index = 0
        material.refraction_depth = 0.0
        material.roughness = 0.4000000059604645
        material.show_transparent_back = True
        material.specular_intensity = 0.5
        material.use_backface_culling = False
        material.use_backface_culling_lightprobe_volume = True
        material.use_backface_culling_shadow = False
        material.use_preview_world = False
        material.use_raytrace_refraction = False
        material.use_screen_refraction = False
        material.use_sss_translucency = False
        material.use_thickness_from_shadow = False
        material.use_transparency_overlap = True
        material.use_transparent_shadow = True
        material.blend_method = 'HASHED'
        material.displacement_method = 'BUMP'
        material.preview_render_type = 'SPHERE'
        material.surface_render_method = 'DITHERED'
        material.thickness_mode = 'SPHERE'
        material.volume_intersection_method = 'FAST'
        material.specular_color = (1.0, 1.0, 1.0)
        material.diffuse_color = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        material.line_color = (0.0, 0.0, 0.0, 0.0)

        principled_bsdf = node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'MULTI_GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK'
        principled_bsdf.inputs[1].default_value = 0.0
        principled_bsdf.inputs[2].default_value = 0.5
        principled_bsdf.inputs[3].default_value = 1.5
        principled_bsdf.inputs[4].default_value = 1.0
        principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[7].default_value = 0.0
        principled_bsdf.inputs[8].default_value = 0.0
        principled_bsdf.inputs[9].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
        principled_bsdf.inputs[10].default_value = 0.05000000074505806
        principled_bsdf.inputs[12].default_value = 0.0
        principled_bsdf.inputs[13].default_value = 0.5
        principled_bsdf.inputs[14].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[15].default_value = 0.0
        principled_bsdf.inputs[16].default_value = 0.0
        principled_bsdf.inputs[17].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[18].default_value = 0.0
        principled_bsdf.inputs[19].default_value = 0.0
        principled_bsdf.inputs[20].default_value = 0.029999999329447746
        principled_bsdf.inputs[21].default_value = 1.5
        principled_bsdf.inputs[22].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[23].default_value = (0.0, 0.0, 0.0)
        principled_bsdf.inputs[24].default_value = 0.0
        principled_bsdf.inputs[25].default_value = 0.5
        principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0)
        principled_bsdf.inputs[28].default_value = 0.0
        principled_bsdf.inputs[29].default_value = 0.0
        principled_bsdf.inputs[30].default_value = 1.3300000429153442

        material_output = node_tree.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        material_output.inputs[3].default_value = 0.0

        mapping = node_tree.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'TEXTURE'
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
        mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

        texture_coordinate = node_tree.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        image_texture = node_tree.nodes.new("ShaderNodeTexImage")
        image_texture.name = "Image Texture"
        image_texture.extension = 'CLIP'
        image_texture.image_user.frame_current = 1
        image_texture.image_user.frame_duration = 1
        image_texture.image_user.frame_offset = 299
        image_texture.image_user.frame_start = 1
        image_texture.image_user.tile = 0
        image_texture.image_user.use_auto_refresh = False
        image_texture.image_user.use_cyclic = False
        image_texture.interpolation = 'Closest'
        image_texture.projection = 'FLAT'
        image_texture.projection_blend = 0.0

        # Set locations
        node_tree.nodes["Principled BSDF"].location = (-553.6383666992188, 168.35658264160156)
        node_tree.nodes["Material Output"].location = (-249.2390899658203, 173.330322265625)
        node_tree.nodes["Mapping"].location = (-1056.72705078125, 141.2757110595703)
        node_tree.nodes["Texture Coordinate"].location = (-1263.7271728515625, 139.83827209472656)
        node_tree.nodes["Image Texture"].location = (-861.617919921875, 164.5237579345703)

        # Initialize shader_nodetree links
        node_tree.links.new(node_tree.nodes["Principled BSDF"].outputs[0], node_tree.nodes["Material Output"].inputs[0])
        node_tree.links.new(node_tree.nodes["Texture Coordinate"].outputs[2], node_tree.nodes["Mapping"].inputs[0])
        node_tree.links.new(node_tree.nodes["Mapping"].outputs[0], node_tree.nodes["Image Texture"].inputs[0])
        node_tree.links.new(node_tree.nodes["Image Texture"].outputs[0], node_tree.nodes["Principled BSDF"].inputs[0])

        return node_tree

    @staticmethod
    def is_char_board(bl_obj):
        if bl_obj is None: return False
        if bl_obj.data is None: return False
        if BL_CharBoard.IS_BOARD_STR not in bl_obj.data: return False

        return bl_obj.data[BL_CharBoard.IS_BOARD_STR]

    @staticmethod
    def from_bl_obj(bl_obj):
        if not BL_CharBoard.is_char_board(bl_obj):
            raise Exception("Provided Blender object is not a calibration board")

        return BL_CharBoard(bl_obj)


# Blender register functions

def register():
    pass

def unregister():
    pass
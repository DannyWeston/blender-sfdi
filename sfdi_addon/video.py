import numpy as np
import cv2
import bpy

import os

from time import perf_counter

from sfdi.video import FringeProjector, Camera
from sfdi.definitions import ROOT_DIR
from sfdi.io.std import stdout_redirected

from mathutils import Vector
from math import pi

def add_driver(
        source, target, prop, dataPath,
        index = -1, func = ''
    ):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1: d = source.driver_add(prop, index).driver
    else: d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name                 = prop
    v.targets[0].id        = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name

def make_fringe_intensity_map_group():
    test_group = bpy.data.node_groups.new('Fringe Intensity Map', 'ShaderNodeTree')

    # Create NodeGroup Inputs

    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200, 0)
    test_group.inputs.new('NodeSocketVector','Vector')
    test_group.inputs.new('NodeSocketFloat','Rotation')
    test_group.inputs.new('NodeSocketFloat','Frequency')
    test_group.inputs.new('NodeSocketFloat','Phase')

    # Create intermediate nodes
    
    vector_rotate_0 = test_group.nodes.new('ShaderNodeVectorRotate')
    vector_rotate_0.location = (0, 100)
    vector_rotate_0.rotation_type = "Z_AXIS"

    mapping_sep_1 = test_group.nodes.new('ShaderNodeSeparateXYZ')
    mapping_sep_1.location = (200, -200)


    mult_node_1 = test_group.nodes.new('ShaderNodeMath')
    mult_node_1.operation = 'MULTIPLY'
    mult_node_1.location = (200, 0)
    mult_node_1.inputs[0].default_value = pi * 2.0



    mult_node_2 = test_group.nodes.new('ShaderNodeMath')
    mult_node_2.operation = 'MULTIPLY'
    mult_node_2.location = (400, 0)



    add_node_3 = test_group.nodes.new('ShaderNodeMath')
    add_node_3.operation = 'ADD'
    add_node_3.location = (600, 0)



    sin_node_4 = test_group.nodes.new('ShaderNodeMath')
    sin_node_4.operation = 'SINE'
    sin_node_4.location = (800, 0)



    add_node_5 = test_group.nodes.new('ShaderNodeMath')
    add_node_5.operation = 'ADD'
    add_node_5.location = (1000, 0)
    add_node_5.inputs[0].default_value = 1.0
    
    
    
    divide_node_6 = test_group.nodes.new('ShaderNodeMath')
    divide_node_6.operation = 'DIVIDE'
    divide_node_6.location = (1200, 0)
    divide_node_6.use_clamp = True
    divide_node_6.inputs[1].default_value = 2.0
    
    # Create output nodes
    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (1400, 0)
    test_group.outputs.new('NodeSocketFloat','Intensity')

    # Link Nodes Together
    
    test_group.links.new(vector_rotate_0.inputs[0], group_inputs.outputs['Vector']) # Vector -> VectorRotate
    test_group.links.new(vector_rotate_0.inputs[2], group_inputs.outputs['Rotation']) # Rotation -> VectorRotate
    
    test_group.links.new(mapping_sep_1.inputs[0], vector_rotate_0.outputs[0]) # Vector Rotate -> SeparateXYZ
    test_group.links.new(mult_node_1.inputs[1], group_inputs.outputs['Frequency']) # Frequency -> Multiply 1 [1]

    test_group.links.new(mult_node_2.inputs[0], mapping_sep_1.outputs[1]) # SeparateXYZ Y -> Multiply 2 [0]
    test_group.links.new(mult_node_2.inputs[1], mult_node_1.outputs[0]) # Multiply 1 -> Multiply 2 [1]

    test_group.links.new(add_node_3.inputs[0], mult_node_2.outputs[0]) # Multiply 2 -> Add 3 [0]
    test_group.links.new(add_node_3.inputs[1], group_inputs.outputs['Phase']) # Phase -> Add 3 [1]

    test_group.links.new(sin_node_4.inputs[0], add_node_3.outputs[0]) # Add 3 -> Sin [0]

    test_group.links.new(add_node_5.inputs[0], sin_node_4.outputs[0]) # Sin -> Add 5 [0]
    
    test_group.links.new(divide_node_6.inputs[0], add_node_5.outputs[0]) # Add -> Divide 6 [0]

    test_group.links.new(group_outputs.inputs["Intensity"], divide_node_6.outputs[0]) # Cos -> Add 4 [0]

def make_pixelate_map_group():
    test_group = bpy.data.node_groups.new('Vector Pixelate', 'ShaderNodeTree')
    
    
    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (0, 0)
    test_group.inputs.new('NodeSocketVector','Vector')
    test_group.inputs.new('NodeSocketInt','Width')
    test_group.inputs.new('NodeSocketInt','Height')

    
    # Define Intermediate Nodes
    
    width_divide = test_group.nodes.new('ShaderNodeMath')
    width_divide.operation = 'DIVIDE'
    width_divide.location = (200, 100)
    width_divide.inputs[0].default_value = 1.0
    
    height_divide = test_group.nodes.new('ShaderNodeMath')
    height_divide.operation = 'DIVIDE'
    height_divide.location = (200, -100)
    height_divide.inputs[0].default_value = 1.0
    
    combine_xyz = test_group.nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (400, 0)
    
    snap = test_group.nodes.new('ShaderNodeVectorMath')
    snap.operation = 'SNAP'
    snap.location = (600, 0)
    
    # Create NodeGroup outputs

    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (800, 0)
    
    test_group.outputs.new('NodeSocketVector','Vector')
    
    # Link Nodes Together
    
    test_group.links.new(group_inputs.outputs['Vector'], snap.inputs[0])
    test_group.links.new(group_inputs.outputs['Width'], width_divide.inputs[1])
    test_group.links.new(group_inputs.outputs['Height'], height_divide.inputs[1])
    
    test_group.links.new(width_divide.outputs[0], combine_xyz.inputs[0])
    test_group.links.new(height_divide.outputs[0], combine_xyz.inputs[1])
    
    test_group.links.new(combine_xyz.outputs[0], snap.inputs[1])
    
    test_group.links.new(snap.outputs[0], group_outputs.inputs['Vector'])

class BL_FringeProjector(FringeProjector):
    def __init__(self, name, frequency, orientation, resolution, phases=[]):
        super().__init__(name, frequency, orientation, resolution, phases)
        
        self.light_obj = bpy.data.objects[name]
        self.settings = self.light_obj.ProjectorSettings

    def display(self):
        # Don't actually need to do anything because the Blender Renderer handles the image projection for us
        # When changing the phase
        self.logger.debug("Projecting image")
        
        # Set the phase angle in ProjectorSettings for next image
        self.settings.phase = self.get_phase()
        
        # Set the projector image to img
        # b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA) # Blender needs alpha channel
        # img = img.astype(np.float16) # Blender needs images as float16s between 0 and 1
        
        # b_image.pixels = img.ravel()
        
        # self.img_node.image = b_image
        
    def get_pos(self):
        return self.light_obj.matrix_world.to_translation()

class BL_Camera(Camera):
    def __init__(self, name='Camera1', resolution=(1920, 1080), cam_mat=None, dist_mat=None, optimal_mat=None, samples=16):
        super().__init__(resolution=resolution, name='Camera1', cam_mat=cam_mat, dist_mat=dist_mat, optimal_mat=optimal_mat)

        self.camera = bpy.data.objects[name]
        
        self.samples = samples
        
        # Set the number of samples for the active scene
        bpy.data.scenes[0].cycles.samples = samples

    def capture(self):
        scene = bpy.context.scene
        
        # Need to set this camera as the renderer to be safe
        scene.camera = self.camera

        # Set scene render resolution to this camera's resolution
        scene.render.resolution_x = self.resolution[0]
        scene.render.resolution_y = self.resolution[1]

        # Render scene to temporary file
        old_filetype = scene.render.image_settings.file_format
        old_quality = scene.render.image_settings.quality
        
        # JPEG with max quality (no compression)
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.quality = 100
        
        # TODO: Change to addon_dir
        temp_path = os.path.join(ROOT_DIR, f'{self.name}_temp.jpg')
        #temp_path = os.path.join('C:\\Users\\danie\\Desktop', f'{self.name}_temp.jpg')
        scene.render.filepath = temp_path
        
        self.logger.debug("Rendering camera image")
        
        calc_time = perf_counter()
        with stdout_redirected():
            bpy.ops.render.render(write_still=True)
        
        # Reset old parameters
        scene.render.image_settings.file_format = old_filetype
        scene.render.image_settings.quality = old_quality

        self.logger.debug(f"Rendered in {(perf_counter() - calc_time):.2f} seconds")
        
        # Load rendered image from disk and convert to correct range (delete old image)
        img = cv2.imread(temp_path)
        img = img.astype(np.float32) / 255.0

        # try:
        #     os.remove(temp_path)
        # except:
        #     self.logger.error("Could not delete temporary render image file")

        return img
    
    def get_pos(self):
        return self.camera.matrix_world.to_translation()

    def set_resolution(self, width, height):
        self.resolution = width, height

        return self
 
class CameraFactory:
    @staticmethod
    def DefaultCamera():
        return None

class ProjectorFactory:
    @staticmethod
    def MakeDefault(location=None, rotation=None):
        # Create new light for the projector
        light_data = bpy.data.lights.new(name="ProjectorLight", type='SPOT')
        light_data.energy = 5               # 5 Watts
        light_data.shadow_soft_size = 0.005 # Slight Blurring over whole image
        light_data.spot_blend = 0.1         # Slight blending around the edge 
        light_data.spot_size = 1.2309807    # Cone size 70.3 deg for Throw Ratio 1:1
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
        
        if rotation:
            light_obj.rotation_euler[0] += rotation[0]
            light_obj.rotation_euler[1] += rotation[1]
            light_obj.rotation_euler[2] += rotation[2]

        if location:
            light_obj.location[0] += location[0]
            light_obj.location[1] += location[1]
            light_obj.location[2] += location[2]

        # Set mesh parent to light
        proj_obj.parent = light_obj
        
        # Setup property drivers for shader
        add_driver(fringe_node.inputs[1], light_obj, 'default_value', 'ProjectorSettings.rotation')
        add_driver(fringe_node.inputs[2], light_obj, 'default_value', 'ProjectorSettings.frequency')
        add_driver(fringe_node.inputs[3], light_obj, 'default_value', 'ProjectorSettings.phase')
        
        add_driver(pixelate_node.inputs[1], light_obj, 'default_value', 'ProjectorSettings.width')
        add_driver(pixelate_node.inputs[2], light_obj, 'default_value', 'ProjectorSettings.height')

        return light_obj
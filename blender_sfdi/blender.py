import logging
import bpy
import random
import numpy as np
import cv2
import tempfile

from mathutils import Vector
from time import perf_counter

from opensfdi.video import FringeProjector, Camera
from opensfdi.utils import stdout_redirected
from opensfdi.services import ExperimentService, FileProfRepo

from pathlib import Path

from . import materials
from .definitions import MODELS_DIR

BL_EX_SERVICE = ExperimentService(FileProfRepo(Path(bpy.utils.extension_path_user(__package__, create=True))))

def add_driver(source, target, prop, dataPath, index=-1, func=''):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1: d = source.driver_add(prop, index).driver
    else: d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = target
    v.targets[0].data_path = dataPath

    d.expression = f"{func}({v.name})" if func else v.name

def reset_delta_transform(bl_obj):
    bl_obj.delta_location = (0.0, 0.0, 0.0)
    bl_obj.delta_rotation_euler = (0.0, 0.0, 0.0)

def random_delta_transform(bl_obj, max_pos, max_rot, seed=0):
    random.seed(seed)

    for i in range(3):
        bl_obj.delta_location[i] = max_pos[i] * random.uniform(-1.0, 1.0)
        bl_obj.delta_rotation_euler[i] = max_rot[i] * random.uniform(-1.0, 1.0)

def heightmap_to_mesh(heightmap, name="Heightmap"):
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


# # # # # # # # # # # # # # # # # # # # # 
# Projector

DEFAULT_PROJ_PATH = str(MODELS_DIR / "projector_mesh.obj")
PROJ_MASK_NAME = "ProjectorDefaultMask"

class BL_FringeProjector(FringeProjector):
    def __init__(self, bl_obj):
        if not BL_FringeProjector.is_fringe_proj(bl_obj):
            raise ValueError(f"{bl_obj.name} is not a fringe projector")
        
        self.__bl_obj = bl_obj

    @property
    def frequency(self):
        return self.settings.fringe_frequency
    
    @frequency.setter
    def frequency(self, value):
        self.settings.fringe_frequency = value

    @property
    def resolution(self):
        return self.settings.resolution
            
    @resolution.setter
    def resolution(self, value):
        if (any(value <= 0)):
            raise ValueError("Cannot have non-positive resolution values")
        
        self.settings.resolution = value
    
    @property
    def rotation(self):
        return self.settings.fringe_rotation
    
    @rotation.setter
    def rotation(self, value):
        self.settings.fringe_rotation = value

    @property
    def phase(self):
        return self.settings.fringe_phase

    @phase.setter
    def phase(self, value):
        self.settings.fringe_phase = value

    def display(self):
        # Don't actually need to do anything because the Blender Renderer handles the image projection for us
        # When changing the phase
        pass

        #self.logger.debug(f"{self.bl_obj.name} - projecting fringes")
        
        # Set the projector image to img
        # b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA) # Blender needs alpha channel
        # img = img.astype(np.float16) # Blender needs images as float16s between 0 and 1
        
        # b_image.pixels = img.ravel()
        
        # self.img_node.image = b_image
    
    @property
    def bl_obj(self):
        return self.__bl_obj

    @property
    def position(self):
        return self.bl_obj.matrix_world.to_translation()

    @property
    def settings(self):
        return self.bl_obj.proj_settings

    @staticmethod
    def is_fringe_proj(bl_obj):
        return bl_obj and ("IsProjector" in bl_obj.data)

    @staticmethod
    def from_name(proj_obj):
        data = proj_obj.data
        return BL_FringeProjector(name=proj_obj.name,
                                    frequency=data["Spatial Frequency"], 
                                    orientation=data["Rotation"],
                                    resolution=tuple(data["Resolution"]))

    # TODO: Reduce size of function
    @staticmethod
    def create_bl_obj(location, rotation):
        # Create new light for the projector
        light_data = bpy.data.lights.new(name="ProjectorLight", type='SPOT')
        light_data.energy = 10              # 10 Watts
        light_data.shadow_soft_size = 0.0   # No blurring over whole image
        light_data.spot_blend = 0.0         # No blurring around the edge
        light_data.spot_size = np.pi        # Full 180 deg vision
        light_data.cycles.max_bounces = 16  # Max light bounces of 16 for performance
        light_data.cycles.use_multiple_importance_sampling = False

        # Setup light shader nodes for light emission
        light_data.use_nodes = True
        light_nodes = light_data.node_tree.nodes
        node_links = light_data.node_tree.links

        # Check if Fringe Intensity Map group exists, create if not
        if light_nodes.get("Fringe Intensity Map", None) is None: 
            materials.fringe_intensity_map_group()
            
        if light_nodes.get("Vector Pixelate", None) is None: 
            materials.pixelate_map_group()

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
            bpy.ops.wm.obj_import(filepath=DEFAULT_PROJ_PATH, filter_obj=False, display_type='DEFAULT', forward_axis='Y', up_axis='Z')

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


# # # # # # # # # # # # # # # # # # # # # 
# Camera

class BL_Camera(Camera):
    def __init__(self, bl_obj, samples=16):
        if not BL_Camera.is_camera(bl_obj):
            raise ValueError(f"{bl_obj.name} is not a camera")
        
        self.__bl_obj = bl_obj
        self.__samples = samples

    @property
    def resolution(self):
        return (self.settings.resolution[0], self.settings.resolution[1])

    @resolution.setter
    def resolution(self, value):
        self.settings.resolution = value

    @property
    def samples(self):
        return self.__samples
    
    @samples.setter
    def samples(self, value):
        self.__samples = value

    @property
    def bl_obj(self):
        return self.__bl_obj
    
    @property
    def position(self):
        return self.bl_obj.matrix_world.to_translation()

    @property
    def settings(self):
        return self.bl_obj.camera_settings

    def capture(self):
        # Change scene render target to this camera (including settings)
        scene = bpy.context.scene
        scene.camera = self.bl_obj
    
        scene.render.resolution_x = self.resolution[0]
        scene.render.resolution_y = self.resolution[1]

        scene.cycles.samples = self.samples
        
        # JPEG with max quality (no compression)
        # TODO: Maybe remove this and rely upon user to set scene's filetype using normal UI
        old_filetype = scene.render.image_settings.file_format
        old_quality = scene.render.image_settings.quality
        old_filepath = scene.render.filepath

        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.compression = 0

        # Use a temporary filename to write the render output
        with tempfile.NamedTemporaryFile(dir=bpy.path.abspath("//"), suffix=".png") as temp_file:
            temp_path = temp_file.name
            scene.render.filepath = temp_path

            logger = logging.getLogger(__name__)
            logger.debug(f"Rendering camera image ({temp_path})")
            
            calc_time = perf_counter()
            with stdout_redirected():
                bpy.ops.render.render(write_still=True)
            
            # Reset old parameters
            scene.render.image_settings.file_format = old_filetype
            scene.render.image_settings.quality = old_quality
            scene.render.filepath = old_filepath

            time_took = perf_counter() - calc_time
            logger.debug(f"Rendered in {time_took:.2f} seconds")

            # Load rendered image from disk and convert to correct range (delete old image)
            return cv2.imread(temp_path).astype(np.float32) / 255.0

    @staticmethod
    def create_bl_obj(location, rotation):
        bl_camera_obj = bpy.data.cameras.new("Camera")

        bl_obj = bpy.data.objects.new("Camera", bl_camera_obj)

        bl_obj.location = location
        bl_obj.rotation_euler = rotation

        bpy.context.collection.objects.link(bl_obj)

        return BL_Camera(bl_obj)

    @staticmethod
    def is_camera(bl_obj):
        return bl_obj and (bl_obj.type == "CAMERA")

    @staticmethod
    def from_name(name):
        return BL_Checkerboard(bpy.data.objects[name])

# class BlenderCameraCalibration(CameraCalibration):
#     def __init__(self, camera, img_count=10, cb_size=(8, 6), cb_name='Checkerboard'):
#         super().__init__(camera, img_count, cb_size)
        
#         self._cb_name = cb_name
        
#         self._cb_obj = bpy.data.objects[cb_name]
        
#         self._set_cb_orientation(0)
        
#     def calibrate(self):
#         self._cb_obj.hide_render = False
#         result = super().calibrate()
#         self._cb_obj.hide_render = True
        
#         return result

#     def on_checkerboard_change(self, i):
#         self._set_cb_orientation(i + 1)

#     def _set_cb_orientation(self, seed):
#         self.logger.debug("Generating new checkerboard orientation")
#         self._cb_obj.modifiers["GeometryNodes"]["Input_5"] = seed
#         self._cb_obj.data.update()

# class BlenderGammaCalibration(GammaCalibration):
#     def __init__(self, camera, projector, delta, crop_size=0.25, order=5, intensity_count=32):
#         super().__init__(camera, projector, delta, crop_size, order, intensity_count)
    
#     def calibrate(self):
#         self.projector.enabled(True)
#         result = super().calibrate()
#         self.projector.enabled(False)
        
#         return result


# # # # # # # # # # # # # # # # # # # # #
# Checkerboard

DEFAULT_CB_PATH =  str(MODELS_DIR / "checkerboard.obj")
CB_SLOT_NAME = "CB_Blank"

class BL_Checkerboard:
    def __init__(self, bl_obj):
        if not BL_Checkerboard.is_checkerboard(bl_obj):
            raise ValueError(f"{bl_obj.name} is not a checkerboard")

        self.__bl_obj = bl_obj

    @property
    def settings(self):
        return self.bl_obj.cb_settings
    
    @property
    def bl_obj(self):
        return self.__bl_obj
    
    @property
    def position(self):
        return self.bl_obj.matrix_world.to_translation()

    def random_transform(self, max_pos, max_rot, seed):
        random_delta_transform(self.bl_obj, max_pos, max_rot, seed)

    def restore_transform(self):
        reset_delta_transform(self.bl_obj)

    @staticmethod
    def create_bl_obj(location, rotation):
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

        # Setup generator material with driver for changing the size of the checkerboard
        mat = materials.checkerboard_mat()
        materials.replace_material(bl_obj, CB_SLOT_NAME, mat)

        map_node = mat.node_tree.nodes["Mapping"]
        add_driver(map_node.inputs[3], bl_obj, 'default_value', 'cb_settings.size[0]', 0)
        add_driver(map_node.inputs[3], bl_obj, 'default_value', 'cb_settings.size[1]', 1)

        return BL_Checkerboard(bl_obj)

    @staticmethod
    def is_checkerboard(bl_obj):
        return bl_obj and ("IsCheckerboard" in bl_obj.data)

    @staticmethod
    def from_name(name):
        return BL_Checkerboard(bpy.data.objects[name])
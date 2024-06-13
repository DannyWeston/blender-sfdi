import bpy
import logging

from sfdi.experiment import Experiment
from sfdi.calibration import CameraCalibration, GammaCalibration
from sfdi.io.std import stdout_redirected

from mathutils import Vector

def add_driver(source, target, prop, dataPath, index = -1, func = ''):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1: d = source.driver_add(prop, index).driver
    else: d = source.driver_add(prop).driver

    v = d.variables.new()
    v.name = prop
    v.targets[0].id = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name

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

def mesh_to_heightmap(mesh):
    pass

class BlenderGammaCalibration(GammaCalibration):
    def __init__(self, camera, projector, delta, crop_size=0.25, order=5, intensity_count=32):
        super().__init__(camera, projector, delta, crop_size, order, intensity_count)
    
    def calibrate(self):
        self.projector.enabled(True)
        result = super().calibrate()
        self.projector.enabled(False)
        
        return result

class BlenderCameraCalibration(CameraCalibration):
    def __init__(self, camera, img_count=10, cb_size=(8, 6), cb_name='Checkerboard'):
        super().__init__(camera, img_count, cb_size)
        
        self._cb_name = cb_name
        
        self._cb_obj = bpy.data.objects[cb_name]
        
        self._set_cb_orientation(0)
        
    def calibrate(self):
        self._cb_obj.hide_render = False
        result = super().calibrate()
        self._cb_obj.hide_render = True
        
        return result

    def on_checkerboard_change(self, i):
        self._set_cb_orientation(i + 1)

    def _set_cb_orientation(self, seed):
        self.logger.debug("Generating new checkerboard orientation")
        self._cb_obj.modifiers["GeometryNodes"]["Input_5"] = seed
        self._cb_obj.data.update()
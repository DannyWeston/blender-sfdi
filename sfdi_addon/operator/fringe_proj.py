import bpy
from bpy.types import Operator

from sfdi_addon.blender import heightmap_to_mesh
from sfdi_addon.video import BL_FringeProjector, BL_Camera
from sfdi_addon.operator.object import hide_objects

from sfdi.experiment import NStepFPExperiment, FringeProjection

from math import pi

def make_bl_projector(bl_proj, phases):
    settings = bl_proj.ProjectorSettings
    return BL_FringeProjector(name=bl_proj.name,
                                frequency=settings.frequency, 
                                orientation=settings.rotation,
                                resolution=(settings.width, settings.height),
                                phases=phases)

class OP_FPNStep(Operator):
    bl_idname = "op.run_experiment"
    bl_label = "TODO"

    def execute(self, context):
        # TODO: Gather all the experiment settings, create correct objects, and run the experiment
        # TODO: Need to gather the results and present them in a pretty way
        # TODO: Make into a modal operator so Blender doesn't have a fit
        
        # Setup projectors
        bl_projectors = context.scene.ExProjectors
        if len(bl_projectors) < 1:
            self.report({'ERROR'}, "You need at least 1 projector")
            return {'CANCELLED'}

        ex = context.scene.ExProperties
        phases = [2.0 * pi * (i / ex.phase_count) for i in range(ex.phase_count)]
        projector = make_bl_projector(bl_projectors[0].obj, phases=phases)

        # Setup cameras
        bl_cameras = context.scene.ExCameras
        if len(bl_cameras) < 1:
            self.report({'ERROR'}, "You need at least 1 camera")
            return {'CANCELLED'}

        cameras = [BL_Camera(name=c.obj.name, resolution=(1920, 1080), cam_mat=None, dist_mat=None, optimal_mat=None, samples=8) for c in bl_cameras]
        
        # Fetch/calculate experiment parameters
        n_step = ex.fp_n_step
        sf = n_step.sf
        cam_ref_dists = [0.5 for _ in cameras] # Set to 1 metre for now
        cam_proj_dists = [(c.get_pos() - projector.get_pos()).length for c in cameras]
        
        test = FringeProjection(cameras, projector)
        experiment = NStepFPExperiment(test, steps=ex.phase_count)
        
        experiment.add_pre_ref_callback(lambda: hide_objects(True))
        experiment.add_post_ref_callback(lambda: hide_objects(False))
        
        ref_imgs, imgs = experiment.run()

        # Save to disk
    
        heightmaps = experiment.classic_ph(ref_imgs, imgs, sf, cam_ref_dists, cam_proj_dists)

        for i, heightmap in enumerate(heightmaps):
            masked = self.mask_heightmap(heightmap)

            # Convert the heightmap to a blender mesh/object
            h_name = f'FPNStep_{cameras[i].name}_heightmap'
            h_mesh = heightmap_to_mesh(masked, h_name)
            
            h_obj = bpy.data.objects.new(h_name, h_mesh)
            bpy.context.collection.objects.link(h_obj)
        
        # TODO: Revert properties to original settings before running experiment 

        return {'FINISHED'}
    
    def mask_heightmap(self, heightmap):
        import cv2

        # Smooth over the heightmap with median filter
        smoothed = cv2.medianBlur(heightmap, 3)

        smoothed = cv2.normalize(smoothed, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)

        # Find Canny edges
        edged = cv2.Canny(smoothed, 30, 200) 
        cv2.imshow('Canny Edges After Contouring', edged)
        cv2.waitKey(0)

        # Finding Contours
        # Use a copy of the image e.g. edged.copy() 
        # since findContours alters the image 
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        print("Number of Contours found = " + str(len(contours))) 
        
        # Draw all contours 
        # -1 signifies drawing all contours 
        cv2.drawContours(smoothed, contours, -1, (0, 255, 0), 3) 
        
        cv2.imshow('Contours', smoothed) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return smoothed

classes = [
    OP_FPNStep,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
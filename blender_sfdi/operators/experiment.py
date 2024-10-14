import bpy
import os
import cv2
from bpy.types import Operator

from opensfdi.experiment import NStepFPExperiment

from ..blender import BL_FringeProjector, BL_Camera

def hide_objects(bl_obj_ptrs, value):
    for ptr in bl_obj_ptrs:
        ptr.obj.hide_render = value

class OP_RegisterObject(Operator):
    bl_idname = "op.register_object"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        bl_objs = context.scene.ex_settings.bl_objs

        # Check if valid object and not already registered
        return context.object and (bl_objs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        bl_objs = context.scene.ex_settings.bl_objs
        
        new_item = bl_objs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterObject(Operator):
    bl_idname = "op.unregister_object"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        bl_objs = context.scene.ex_settings.bl_objs

        return context.object and (0 <= bl_objs.find(context.object.name))
            
    def execute(self, context):
        bl_objs = context.scene.ex_settings.bl_objs
        selected = context.object

        selected_id = bl_objs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        bl_objs.remove(selected_id)
            
        return {'FINISHED'}

class OP_FPNStep(Operator):
    bl_idname = "op.run_experiment"
    bl_label = "TODO"

    def execute(self, context):
        scene = context.scene
        settings = scene.ex_nstepclassic
        ex_settings = scene.ex_settings

        # TODO: Need to gather the results and present them in a pretty way
        # TODO: Make into a modal operator so Blender doesn't have a fit

        # Setup peripherals
        projector = BL_FringeProjector(settings.projector)
        cameras = [BL_Camera(settings.camera)]
        
        # Check if supplied output dir was valid
        output_dir = bpy.path.abspath(ex_settings.output_dir)
        if output_dir == '' or (not os.path.exists(output_dir)):
            self.report({"ERROR"}, f"Invalid output directory given")
            return {'CANCELLED'}
        
        self.report({"INFO"}, f"Results will be saved in {output_dir}")

        needs_calibrate = settings.calibrate
        phases = settings.phases
        bl_objs = ex_settings.bl_objs

        experiment = NStepFPExperiment(cameras, projector, phases)

        # cam_ref_dists = [0.5 for _ in cameras] # Set to 1 metre for now
        # cam_proj_dists = [(c.get_pos() - projector.get_pos()).length for c in cameras]

        experiment.add_pre_ref_callback(lambda: hide_objects(bl_objs, True))
        experiment.add_post_ref_callback(lambda: hide_objects(bl_objs, False))

        ref_imgs, imgs = experiment.run()

        # Write results to file
        for i, cam in enumerate(ref_imgs): # Reference images
            for j, img in enumerate(cam):
                filename = os.path.join(output_dir, f"ref_{j}.jpg")
                cv2.imwrite(filename, 255*img) #TODO : Fix properly
        
        for i, cam in enumerate(imgs): # Measurement images
            for j, img in enumerate(cam):
                filename = os.path.join(output_dir, f"measurement_{j}.jpg")
                cv2.imwrite(filename, 255*img) #TODO: FIx properly
        
        # Run profilometry
        sf = settings.sf
    
        # heightmaps = experiment.classic_ph(ref_imgs, imgs, sf, cam_ref_dists, cam_proj_dists)

        # for i, heightmap in enumerate(heightmaps):
        #     #masked = self.mask_heightmap(heightmap)

        #     # Convert the heightmap to a blender mesh/object
        #     h_name = f'FPNStep_{cameras[i].name}_heightmap'
        #     h_mesh = heightmap_to_mesh(heightmap, h_name)
            
        #     h_obj = bpy.data.objects.new(h_name, h_mesh)
        #     bpy.context.collection.objects.link(h_obj)
        
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
    OP_RegisterObject,
    OP_UnregisterObject,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
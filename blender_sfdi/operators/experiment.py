import bpy
import numpy as np

from bpy.types import Operator

from opensfdi.experiment import Experiment
from opensfdi.utils import show_heightmap, show_surface

from ..properties import PG_Experiment
from .. import blender

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

class OP_Experiment(Operator):
    bl_idname = "op.run_experiment"
    bl_label = "TODO"

    def execute(self, context):
        scene = context.scene
        settings = scene.ex_settings

        # TODO: Need to gather the results and present them in a pretty way
        # TODO: Make into a modal operator so Blender doesn't have a fit

        # Setup peripherals
        projector = blender.BL_FringeProjector(settings.projector)
        camera = blender.BL_Camera(settings.camera)

        # TODO: Allow for changing phase-shift / unwrapping methods after loading calibration

        # Load profilometry calibration method
        exp = blender.BL_EX_SERVICE.load_experiment(settings.calibration_files) # Get profilometry from name
        
        # Add callbacks to hide the object
        exp.add_post_phasemap_cbs(lambda: hide_objects(settings.bl_objs, False))

        # Hide the objects ready for reference measurement
        hide_objects(settings.bl_objs, True)

        # Run the experiment and show results
        imgs = exp.get_imgs(camera, projector) # TODO: Allow for image generation only

        # Save the images to disk
        for phasemap in range(imgs.shape[0]):
            for phase in range(imgs.shape[1]):
                blender.BL_EX_SERVICE.save_img(imgs[phasemap, phase], f'img{phasemap}_phase{phase}')

        # Check if we are only generating images
        if settings.only_images: 
            return {'FINISHED'}
        
        # These images are currently in RGB format
        # TODO: Add way to choose between keep channel or take mean
        imgs = np.mean(imgs, axis=5)

        heightmap = exp.heightmap(imgs)

        show_heightmap(heightmap)
        show_surface(heightmap)

        # ref_imgs, imgs = experiment.run()

        # for i, heightmap in enumerate(heightmaps):
        #     #masked = self.mask_heightmap(heightmap)

        #     # Convert the heightmap to a blender mesh/object
        #     h_name = f'FPNStep_{cameras[i].name}_heightmap'
        #     h_mesh = heightmap_to_mesh(heightmap, h_name)
            
        #     h_obj = bpy.data.objects.new(h_name, h_mesh)
        #     bpy.context.collection.objects.link(h_obj)
        
        # TODO: Revert properties to original settings before running experiment 

        return {'FINISHED'}

class OP_CalibrateProf(Operator):
    # TODO: Add support for moving a stage

    bl_idname = "op.run_calibration"
    bl_label = "TODO"

    def execute(self, context):
        scene = context.scene
        settings: PG_Experiment = scene.ex_settings

        # Setup peripherals
        projector = blender.BL_FringeProjector(settings.projector)
        camera = blender.BL_Camera(settings.camera)
        
        # Check if supplied output name was valid
        if blender.BL_EX_SERVICE.exp_exists(settings.output_name):
            self.report({"ERROR"}, f"Calibration with name \"{settings.output_name}\" already exists")
            return {'CANCELLED'}
        
        # Create objects from scenes 
        shift_prop = settings.phase_shift.methods
        ph_shift = getattr(scene, shift_prop).make_instance()

        unwrap_prop = settings.phase_unwrap.methods
        ph_unwrap = getattr(scene, unwrap_prop).make_instance()

        prof_prop = settings.profilometry.methods
        prof = getattr(scene, prof_prop).make_instance(name=settings.output_name)

        
        # Hide all of the objects-to-be-hidden (ready for calibration)
        hide_objects(settings.bl_objs, True)

        # Check if a motor stage is needed by the calibration method
        if not prof.needs_motor_stage:
            print("Not supported yet")
            return {'FINISHED'}

        motor_stage = blender.BL_MotorStage(settings.motor_stage)
        
        exp = Experiment(settings.output_name, prof, ph_shift, ph_unwrap)

        heights = np.linspace(motor_stage.min_height, motor_stage.max_height, motor_stage.steps)

        height_imgs = []
        for height in heights:
            motor_stage.bl_obj.delta_location[2] = height
            imgs = exp.get_imgs(camera, projector)
            height_imgs.append(imgs)

        # Reset motor stage back to 0
        motor_stage.bl_obj.delta_location[2] = 0.0

        height_imgs = np.array(height_imgs)

        # Height Phasemap Phase 

        # Save the images to disk
        for h in range(motor_stage.steps):
            for ph in range(height_imgs.shape[1]):
                for p in range(height_imgs.shape[2]):
                    temp = height_imgs[h, ph, p]
                    img_name = f'{settings.output_name}_calib{h}_{ph}_phase{p}'
                    print(temp.shape)
                    blender.BL_EX_SERVICE.save_img(temp, img_name)

        # Check if we are only generating images
        if settings.only_images: 
            return {'FINISHED'}
        
        # These images are currently in RGB format
        # TODO: Add way to choose between keep channel or take mean
        height_imgs = np.mean(height_imgs, axis=5)
    
        exp.calibrate(height_imgs, heights)

        # Save the calibration
        blender.BL_EX_SERVICE.save_experiment(exp)

        return {'FINISHED'}
        


classes = [
    OP_RegisterObject,
    OP_UnregisterObject,

    OP_Experiment,
    OP_CalibrateProf,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
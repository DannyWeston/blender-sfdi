import bpy
import numpy as np

from bpy.types import Operator

from opensfdi.experiment import Experiment
from opensfdi.utils import show_heightmap, show_surface

from ..properties import PG_Experiment
from ..definitions import get_storage_path

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

        # Run the reconstruction
        imgs = exp.reconstruct_imgs(camera, projector)

        P, phases, *_ = imgs.shape

        # Setup animation settings
        scene.frame_start = 0
        scene.frame_step = 1
        scene.frame_end = (phases * P) - 1

        # Generate keyframes for devices
        camera.bl_obj.animation_data_clear()
        projector.bl_obj.animation_data_clear()

        for i in range(P):
            for j in range(phases):
                frame_num = j + (i * phases)

                # Camera frames
                camera.bl_obj.keyframe_insert(data_path="location", frame=frame_num)

                # Set scene samples rate
                scene.cycles.samples = camera.bl_settings.scene_samples
                scene.keyframe_insert(data_path="cycles.samples", frame=frame_num)

                # Projector frames
                projector.settings.fringe_phase = phases[j]
                projector.settings.keyframe_insert(data_path="fringe_phase", frame=frame_num)

                # projector.settings.keyframe_insert(data_path="fringe_frequency", frame=frame_num)
                # projector.settings.keyframe_insert(data_path="fringe_rotation", frame=frame_num)
                # projector.settings.keyframe_insert(data_path="fringe_type", frame=frame_num)
        
        # Render the animation
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)

        # Check if it was successful
        for i in range(P):
            for j in range(phases): 
                frame_num = j + (i * phases)

        # Save the images to disk
        name = f'{settings.output_name}_img{i}_phase{j}'
        blender.BL_EX_SERVICE.save_img(imgs[i, j], name)

        # Check if only generating images
        if settings.only_images:
            # TODO: Remove on_height_measurement motorstage cb
            return {'FINISHED'}

        # Run calibration
        heightmap = exp.reconstruct(imgs)

        # Apply some filtering to heightmap
        # TODO: Move this into opensfdi
        # masked = self.mask_heightmap(heightmap)

        # Convert the heightmap to a blender mesh/object
        h_name = f'{settings.output_name}_heightmap'
        h_mesh = blender.heightmap_to_mesh(heightmap, h_name)
        
        h_obj = bpy.data.objects.new(h_name, h_mesh)
        bpy.context.collection.objects.link(h_obj)

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
        # TODO: Move to startup cb
        hide_objects(settings.bl_objs, True)

        # Check if a motor stage is needed by the calibration method
        if not prof.needs_motor_stage:
            print("Not supported yet")
            return {'FINISHED'}

        motor_stage = blender.BL_MotorStage(settings.motor_stage)
        
        # Create experiment
        exp = Experiment(settings.output_name, prof, ph_shift, ph_unwrap)
        exp.on_height_measurement(motor_stage.set_height) # Update motor stage at each height

        # Linear interp heights
        # TODO: Support different interp, e.g polynomial granular, bell curve, etc.
        n_count = np.linspace(motor_stage.min_height, motor_stage.max_height, motor_stage.steps)
        
        # Get calibration images
        height_imgs = exp.calibrate_imgs(camera, projector, n_count)
        n_count, phase_count, *_ = height_imgs.shape

        # Generate keyframes for devices
        camera.bl_obj.animation_data_clear()
        projector.bl_obj.animation_data_clear()

        # Save the images to disk
        for i in range(n_count):
            for j in range(phase_count):
                name = f'{settings.output_name}_calib{i}_phase{j}'
                blender.BL_EX_SERVICE.save_img(height_imgs[i, j], name)


        # Setup animation settings
        scene.frame_start = 0
        scene.frame_step = 1
        scene.frame_end = (phases * P) - 1

        for i in range(P):
            for j in range(phases):
                frame_num = j + (i * phases)

                # Camera frames
                camera.bl_obj.keyframe_insert(data_path="location", frame=frame_num)

                # Set scene samples rate
                scene.cycles.samples = camera.bl_settings.scene_samples
                scene.keyframe_insert(data_path="cycles.samples", frame=frame_num)

                # Projector frames
                projector.settings.fringe_phase = phases[j]
                projector.settings.keyframe_insert(data_path="fringe_phase", frame=frame_num)

                # projector.settings.keyframe_insert(data_path="fringe_frequency", frame=frame_num)
                # projector.settings.keyframe_insert(data_path="fringe_rotation", frame=frame_num)
                # projector.settings.keyframe_insert(data_path="fringe_type", frame=frame_num)

        # Check if only generating images
        if settings.only_images:
            # TODO: Remove on_height_measurement motorstage cb
            return {'FINISHED'}

        # Run calibration
        exp.calibrate(height_imgs, n_count)

        # Save the calibration
        blender.BL_EX_SERVICE.save_experiment(exp)

        # TODO: Remove on_height_measurement motorstage cb
        return {'FINISHED'}

    @classmethod
    def description(cls, context, event):
        return f"Directory: {str(get_storage_path())}"      


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
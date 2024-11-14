import bpy

from bpy.types import Operator

from opensfdi.experiment import FPExperiment
from opensfdi.utils import show_heightmap, show_surface

from ..properties import profilometry
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
        ex_settings = scene.ex_settings

        # TODO: Need to gather the results and present them in a pretty way
        # TODO: Make into a modal operator so Blender doesn't have a fit

        # Setup peripherals
        projector = blender.BL_FringeProjector(ex_settings.projector)
        camera =  blender.BL_Camera(ex_settings.camera)

        # Check if supplied output dir was valid
        # output_dir = Path(bpy.path.abspath(ex_settings.output_dir))
        # if not output_dir.exists():
        #     self.report({"ERROR"}, f"Invalid output directory given")
        #     return {'CANCELLED'}

        # Create phase shifting obj
        ph_shift = [x for x in profilometry.REGISTERED_PHASE_SHIFTS if x.has_name(ex_settings.phase_shift)][0].make_clazz_inst()

        # Create phase unwrapping obj
        ph_unwrap = [x for x in profilometry.REGISTERED_PHASE_UNWRAPS if x.has_name(ex_settings.phase_unwrap)][0].make_clazz_inst()

        # Load profilometry calibration method

        prof = ex_service.load_calib(ex_settings.profilometry)
        
        # Add callbacks to hide the object
        bl_objs = ex_settings.bl_objs
        prof.add_post_ref_cb(lambda: hide_objects(bl_objs, False)) # Hide objects after
        hide_objects(bl_objs, True)


        # Run the experiment and show results
        experiment = FPExperiment(camera, projector, ph_shift, ph_unwrap, prof)
        heightmap = experiment.run()

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
        calib_settings = scene.calib_settings
        ex_settings = scene.ex_settings

        # Setup peripherals
        projector =  blender.BL_FringeProjector(ex_settings.projector)
        camera =  blender.BL_Camera(ex_settings.camera)
        
        # Check if supplied output name was valid
        if self.ex_service.calib_exists(calib_settings.output_name):
            self.report({"ERROR"}, f"Calibration with name \"{calib_settings.output_name}\" already exists")
            return {'CANCELLED'}
        
        # Create phase shifting obj
        ph_shift = [x for x in profilometry.REGISTERED_PHASE_SHIFTS if x.has_name(ex_settings.phase_shift)][0].make_clazz_inst()

        # Create phase unwrapping obj
        ph_unwrap = [x for x in profilometry.REGISTERED_PHASE_UNWRAPS if x.has_name(ex_settings.phase_unwrap)][0].make_clazz_inst()

        # Create profilometry object
        prof = [x for x in profilometry.REGISTERED_PROFS if x.has_name(calib_settings.profilometry)][0] # Create profilometry object
        prof = prof.make_clazz_inst(calib_settings.output_name)

        # Hide all of the objects-to-be-hidden (ready for calibration)
        hide_objects(ex_settings.bl_objs, True)

        # Run the calibration and save the results
        def f(height): print(f"Moving stage to {height}")
        
        experiment = FPExperiment(camera, projector, ph_shift, ph_unwrap, prof)
        experiment.on_height_measurement(f)
        experiment.calibrate([0.0, 1.0, 2.0]) # TODO: Fetch heights from provided list
        
        ex_service.save_calib(experiment)

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
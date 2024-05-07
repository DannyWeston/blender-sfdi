import bpy
import bpy_extras

from sfdi import display_image, show_surface
from sfdi.experiment import NStepFPExperiment, FringeProjection

from sfdi_addon.video import BL_FringeProjector, BL_Camera, ProjectorFactory, CameraFactory

from bpy_extras.object_utils import AddObjectHelper, object_data_add

from mathutils import Vector

def make_bl_projector(bl_proj, phase_count):
    # TODO: Take resolution from Blender

    settings = bl_proj.ProjectorSettings
    return BL_FringeProjector(name=bl_proj.name, 
                                phase_count=phase_count, 
                                frequency=settings.frequency, 
                                orientation=settings.rotation,
                                resolution=(1024, 1024)
)
        
def hide_objects(value):
    objs = bpy.context.scene.ExProperties.objects
    
    for obj in objs:
        obj.obj.hide_render = value

class OP_RegisterProj(bpy.types.Operator):
    bl_idname = "op.register_proj"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and (context.object.type == "LIGHT") and (projs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        projs = context.scene.ExProjectors
        
        new_item = projs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterProj(bpy.types.Operator):
    bl_idname = "op.unregister_proj"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and (0 <= projs.find(context.object.name))
            
    def execute(self, context):        
        projs = context.scene.ExProjectors
        selected = context.object

        selected_id = projs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        projs.remove(selected_id)
            
        return {'FINISHED'}

class OP_RegisterCamera(bpy.types.Operator):
    bl_idname = "op.register_camera"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        cameras = context.scene.ExCameras

        return context.object and (context.object.type == "CAMERA") and (cameras.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        cameras = context.scene.ExCameras
        
        new_item = cameras.add()
        new_item.name = selected.name
        new_item.obj = selected
            
        return {'FINISHED'}

class OP_UnregisterCamera(bpy.types.Operator):
    bl_idname = "op.unregister_camera"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        cameras = context.scene.ExCameras

        return context.object and (0 <= cameras.find(context.object.name))

    def execute(self, context):
        cameras = context.scene.ExCameras
        selected = context.object

        selected_id = cameras.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        cameras.remove(selected_id)
            
        return {'FINISHED'}

class OP_RegisterObject(bpy.types.Operator):
    bl_idname = "op.register_object"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        objs = context.scene.ExProperties.objects

        return context.object and (objs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        objs = context.scene.ExProperties.objects
        
        new_item = objs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterObject(bpy.types.Operator):
    bl_idname = "op.unregister_object"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        objs = context.scene.ExProperties.objects

        return context.object and (0 <= objs.find(context.object.name))
            
    def execute(self, context):
        objs = context.scene.ExProperties.objects
        selected = context.object

        selected_id = objs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        objs.remove(selected_id)
            
        return {'FINISHED'}

class OP_AddProj(bpy.types.Operator):
    bl_idname = "menu.add_proj"
    bl_label = "Fringe Projector"

    bl_options = {'REGISTER', 'UNDO'}
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH')
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION')
    
    # Projector resolution
    width: bpy.props.IntProperty(name="Width", default=1024, min=1)
    height: bpy.props.IntProperty(name="Height", default=768, min=1)
    
    fringe_type: bpy.props.EnumProperty(
        name="Type",
        description="TODO: Some description",
        items=[
            ("OP1", "Sinusoidal",   "TODO: Fill tooltip", 1),
            ("OP2", "Binary",       "TODO: Fill tooltip", 2),
        ]
    )
    
    fringe_frequency: bpy.props.FloatProperty(name="Fringe Frequency", default=32.0, min=0.0)
    
    fringe_phase: bpy.props.FloatProperty(name="Fringe Phase", default=0.0, unit='ROTATION')
    
    fringe_rotation: bpy.props.FloatProperty(name="Fringe Rotation", default=0.0, unit='ROTATION')

    # TODO: Implement custom draw function to make menu look a bit nicer

    def execute(self, context):
        # Make a projector using factory
        projector = ProjectorFactory.MakeDefault(self.location, self.rotation)

        proj_settings = projector.ProjectorSettings

        proj_settings.frequency = self.fringe_frequency
        proj_settings.phase = self.fringe_phase
        proj_settings.rotation = self.fringe_rotation
        proj_settings.fringe_type = self.fringe_type
        
        proj_settings.width = self.width
        proj_settings.height = self.height

        return {'FINISHED'}

class OP_AddCamera(bpy.types.Operator):
    bl_idname = "op.add_camera"
    bl_label = "SFDI Camera"

    def execute(self, context):
        # Add the stuff
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# FringeProjection Operators

class OP_FPNStep(bpy.types.Operator):
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
        phase_count = ex.phase_count
        projector = make_bl_projector(bl_projectors[0].obj, phase_count)
        
        # Setup cameras
        bl_cameras = context.scene.ExCameras
        if len(bl_cameras) < 1:
            self.report({'ERROR'}, "You need at least 1 camera")
            return {'CANCELLED'}
        
        cameras = [BL_Camera(name=c.obj.name, resolution=(1920, 1080), cam_mat=None, dist_mat=None, optimal_mat=None, samples=16) for c in bl_cameras]
        
        # Fetch/calculate experiment parameters
        n_step = ex.fp_n_step
        sf = n_step.sf
        cam_ref_dists = [0.5 for c in cameras] # Set to 1 metre for now
        cam_proj_dists = [(c.get_pos() - projector.get_pos()).length for c in cameras]
        
        test = FringeProjection(cameras, projector)
        experiment = NStepFPExperiment(test)
        
        experiment.add_pre_ref_callback(lambda: hide_objects(True))
        experiment.add_post_ref_callback(lambda: hide_objects(False))
        
        ref_imgs, imgs = experiment.run()
    
        heightmaps = experiment.classic_ph(ref_imgs, imgs, sf, cam_ref_dists, cam_proj_dists)

        for i, heightmap in enumerate(heightmaps):
            h_name = f'FPNStep_{cameras[i].name}_heightmap'
            h_mesh = self.heightmap_to_mesh(heightmap, h_name)
            
            h_obj = bpy.data.objects.new(h_name, h_mesh)
            bpy.context.collection.objects.link(h_obj)
            
            # Add mesh to environment
        
        # TODO: Revert properties to original settings before running experiment 
        
        return {'FINISHED'}
    
    def heightmap_to_mesh(self, heightmap, name="Heightmap"):
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


classes = [
    OP_RegisterProj,
    OP_UnregisterProj,
    OP_AddProj,
    
    OP_RegisterCamera,
    OP_UnregisterCamera,
    OP_AddCamera,
    
    OP_RegisterObject,
    OP_UnregisterObject,
    
    OP_FPNStep,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddProj.bl_idname))
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddCamera.bl_idname))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
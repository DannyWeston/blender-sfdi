import bpy

from bpy.app.handlers import persistent

from . import devices


# Projector

def update_fringes_type_switch(self, context):
    bl_obj = context.object

    if devices.BL_Projector.is_projector(bl_obj):
        projector = devices.BL_Projector(bl_obj)

        # Find property in parent container and set channel node value
        for i, prop in enumerate(projector.settings.channels_list.values()):
            if self == prop:
                bl_obj.data.node_tree.nodes[f"Channel {i+1}"].inputs[6].default_value = self.fringes_type

def update_channels_switch(self, context):
    bl_obj = context.object

    if devices.BL_Projector.is_projector(bl_obj):
        node_tree = bl_obj.data.node_tree
        
        node_tree.nodes["Channels Switch"].inputs[0].default_value = self.channels

def update_falloff_switch(self, context):
    bl_obj = context.object

    if devices.BL_Projector.is_projector(bl_obj):
        node_tree = bl_obj.data.node_tree
        
        node_tree.nodes["Light Falloff Switch"].inputs[0].default_value = self.light_falloff

class PG_ProjectorChannel(bpy.types.PropertyGroup):
    intensity : bpy.props.FloatProperty(name="Intensity", default=1.0, min=0.0, max=1.0) # type: ignore

    stripe_count : bpy.props.FloatProperty(name="Stripe Count", default=16.0, min=0.0, max=10000.0) # type: ignore
    
    phase : bpy.props.FloatProperty(name="Phase", default=0.0, unit='ROTATION') # type: ignore
    
    rotation : bpy.props.FloatProperty(name="Rotation", default=0.0, unit='ROTATION') # type: ignore

    noise : bpy.props.FloatProperty(name="Noise", default=0.0, min=0.0, max=1.0) # type: ignore

    fringes_type : bpy.props.EnumProperty(name="Fringes Type", description="Type", 
        items=[
            ("Sinusoidal", "Sinusoidal",   "TODO: Fill tooltip"),
            ("Binary", "Binary",   "TODO: Fill tooltip"),
        ],
        update=update_fringes_type_switch
    ) # type: ignore

class PG_ProjectorSettings(bpy.types.PropertyGroup):
    channels : bpy.props.EnumProperty(
        name="Channels",
        description="TODO",
        items=[
            ("Monochrome", "Monochrome", "Black and white"),
            ("RGB", "RGB", "Red, blue, and green channels"),
        ],
        update=update_channels_switch
    ) # type: ignore

    light_falloff : bpy.props.EnumProperty(
        name="Light Falloff",
        description="How much light falloff",
        items=[
            ("Quadratic", "Quadratic", "TODO"),
            ("Linear", "Linear", "TODO"),
            ("Constant", "Constant", "TODO"),
        ],
        update=update_falloff_switch
    ) # type: ignore

    channels_list : bpy.props.CollectionProperty(type=PG_ProjectorChannel) # type: ignore

    throw_ratio : bpy.props.FloatProperty(name="Throw Ratio", default=1.0, min=0.01, max=5.0, subtype='NONE') # type: ignore

    aspect_ratio : bpy.props.FloatProperty(name="Aspect Ratio", default=16.0/9.0, min=0.01, max=5.0, subtype='NONE') # type: ignore
    
    resolution : bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1920, 1080), min=100) # type: ignore


# Camera

class PG_CameraSettings(bpy.types.PropertyGroup):
    resolution : bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1920, 1080)) # type: ignore

    refresh_rate: bpy.props.IntProperty(name="Refresh Rate", min=1, default=30) # type: ignore

    bit_depth : bpy.props.EnumProperty(
        name="Bit Depth",
        description="How many bits per channel",
        items=[
            ("8", "8-bit", "Normal for cameras"),
            ("16", "16-bit", "TODO"),
    ]) # type: ignore

    channels : bpy.props.EnumProperty(
        name="Colour Channels",
        description="Camera colour channels which it will use when rendering",
        items=[
            ("BW", "Monochrome", "Black and white"),
            ("RGB", "RGB", "3 channels"),
    ]) # type: ignore

    render_samples : bpy.props.IntProperty(name="Render Samples", default=64) # type: ignore

    file_format : bpy.props.EnumProperty(
        name="File Format",
        description="What should the type of output files be?",
        items=[
            ("TIFF", ".tif", "Description"),
    ]) # type: ignore


# Fringes Manager

def update_projector(self, context):
    bl_obj = context.object

    if devices.BL_Projector.is_projector(bl_obj):
        projector = devices.BL_Projector(bl_obj)

        context.fp_stereo.fringes_manager.multiplexing = 1 < projector.channels

class PG_FringesStripeCount(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="Fringes Stripe Count", default=32.0, min=0.0, max=10000.0) # type: ignore

class PG_FringesRotation(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="Fringes Rotation", default=0.0, unit='ROTATION') # type: ignore

class PG_FringesPhase(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="Fringes Phase", default=0.0, unit='ROTATION') # type: ignore

class PG_FringesManager(bpy.types.PropertyGroup):        
    multiplexing : bpy.props.BoolProperty(name="Fringes Multiplexing", description="TODO", default=False) # type: ignore

    stripe_counts: bpy.props.CollectionProperty(type=PG_FringesStripeCount) # type: ignore

    phases : bpy.props.CollectionProperty(type=PG_FringesPhase) # type: ignore

    rotations : bpy.props.CollectionProperty(type=PG_FringesRotation) # type: ignore

class PG_StereoFP(bpy.types.PropertyGroup):
    # Devices
    camera : bpy.props.PointerProperty(name="FPStereoCamera", type=bpy.types.Object, poll=lambda _, o: devices.BL_Camera.is_camera(o)) # type: ignore
    char_board : bpy.props.PointerProperty(name="FPStereoBoard", type=bpy.types.Object, poll=lambda _, o: devices.BL_CharBoard.is_char_board(o)) # type: ignore
    projector : bpy.props.PointerProperty(name="FPStereoProjector", type=bpy.types.Object, poll=lambda _, o: devices.BL_Projector.is_projector(o), update=update_projector) # type: ignore

    fringes_manager : bpy.props.PointerProperty(name="FPStereoFringesManager", type=PG_FringesManager) # type: ignore

    # Output
    output_dir : bpy.props.StringProperty(name="FPStereoDir", default="", subtype='DIR_PATH', description="Leave blank for default in-built directory") # type: ignore
    output_name : bpy.props.StringProperty(name="FPStereoFilename", description="Choose an output filename:") # type: ignore

    metadata : bpy.props.BoolProperty(name="FPStereoMetadata", description="TODO", default=False) # type: ignore


# Characterisation Board

class PG_CharBoardPose(bpy.types.PropertyGroup):
    translation: bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype='TRANSLATION') # type: ignore
    rotation: bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0, 0.0), size=4, subtype='QUATERNION') # type: ignore

class PG_CharBoardSettings(bpy.types.PropertyGroup):
    poses : bpy.props.CollectionProperty(name="CharBoardPoses", type=PG_CharBoardPose) # type: ignore


# Blender register

@persistent
def initialise_fp_stereo(dummy1, dummy2):
    for scene in bpy.data.scenes:
        if hasattr(scene, "fp_stereo"):
            fp_stereo = scene.fp_stereo

            fringes_manager = fp_stereo.fringes_manager

            if len(fringes_manager.stripe_counts) == 0:
                fringes_manager.stripe_counts.add()

            if len(fringes_manager.phases) == 0:
                fringes_manager.phases.add()

            if len(fringes_manager.rotations) == 0:
                fringes_manager.rotations.add()

classes = [
    # Projector
    PG_ProjectorChannel,
    PG_ProjectorSettings,
    
    # Camera
    PG_CameraSettings,

    # Characterisation Board
    PG_CharBoardPose,
    PG_CharBoardSettings,

    # Fringes Manager
    PG_FringesStripeCount,
    PG_FringesRotation,
    PG_FringesPhase,
    PG_FringesManager,

    # Stereo Fringe Projection
    PG_StereoFP,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # SFDI Object Properties
    bpy.types.Light.sfdi = bpy.props.PointerProperty(type=PG_ProjectorSettings)
    bpy.types.Camera.sfdi = bpy.props.PointerProperty(type=PG_CameraSettings)
    bpy.types.Object.sfdi = bpy.props.PointerProperty(type=PG_CharBoardSettings)

    # Experiment settings
    bpy.types.Scene.fp_stereo = bpy.props.PointerProperty(type=PG_StereoFP)

    bpy.app.handlers.load_post.append(initialise_fp_stereo)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(initialise_fp_stereo)

    del bpy.types.Scene.fp_stereo

    del bpy.types.Light.sfdi
    del bpy.types.Camera.sfdi
    del bpy.types.Object.sfdi
import bpy

from pathlib import Path
from opensfdi.utils import stdout_redirected

def load_fbx(filepath: Path):
    with stdout_redirected():
        bpy.ops.import_scene.fbx(filepath=str(filepath.resolve()))

def load_obj(filepath: Path):
    with stdout_redirected():
        bpy.ops.wm.obj_import(filepath=str(filepath.resolve()), filter_obj=False, display_type='DEFAULT', forward_axis='Y', up_axis='Z')
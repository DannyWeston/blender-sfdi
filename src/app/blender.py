import bpy

from tkinter import filedialog as fd

def load_scene():
    try:
        filepath = fd.askopenfilename()
        bpy.ops.wm.open_mainfile(filepath=filepath)
    except Exception as e:
        print(e)
        return False
    
    return True
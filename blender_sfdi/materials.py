import bpy
import numpy as np

def replace_material(bl_obj, target_name, new_mat, append_fallback=True):
    if 0 <= (slot := bl_obj.material_slots.find(target_name)):
        # Delete the placeholder material
        temp = bl_obj.material_slots[slot].material
        bpy.data.materials.remove(temp)
        
        # Assign new material
        bl_obj.material_slots[slot].material = new_mat
    
    elif append_fallback:
        print("Could not load material slots correctly, falling back to just append")
        bl_obj.data.materials.append(new_mat)

# Specific materials

def proj_mesh_mat():
    mat = bpy.data.materials.get("ProjectorMeshMat")
    if mat is not None: return mat

    # Doesn't exist so create
    mat = bpy.data.materials.new(name="ProjectorMeshMat")
    mat.use_nodes = True
    nt = mat.node_tree

    nt.nodes["Principled BSDF"].inputs[0].default_value = (0.25, 0.55, 1.0, 1.0)

    return mat

def ringboard_mat():
    mat = bpy.data.materials.new(name="RingboardMat")
    mat.use_nodes = True

    ringboard = mat.node_tree

	# Start with a clean node tree
    for node in ringboard.nodes: ringboard.nodes.remove(node)

    material_output = ringboard.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"

    texture_coordinate = ringboard.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    principled_bsdf = ringboard.nodes.new("ShaderNodeBsdfPrincipled")

    mapping = ringboard.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
        
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    #node Voronoi Texture
    voronoi_texture = ringboard.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture.name = "Voronoi Texture"
    voronoi_texture.distance = 'EUCLIDEAN'
    voronoi_texture.feature = 'F1'
    voronoi_texture.normalize = False
    voronoi_texture.voronoi_dimensions = '3D'
        
    voronoi_texture.inputs[2].default_value = 20.0
    voronoi_texture.inputs[3].default_value = 1.0
    voronoi_texture.inputs[4].default_value = 1.0
    voronoi_texture.inputs[5].default_value = 0.0
    voronoi_texture.inputs[8].default_value = 0.0

    math = ringboard.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'LESS_THAN'
    math.use_clamp = True
    math.inputs[1].default_value = 0.2

    # Set locations
    material_output.location = (500, 255)
    texture_coordinate.location = (-656, 239)
    principled_bsdf.location = (203, 251)
    mapping.location = (-414.7839660644531, 242)
    voronoi_texture.location = (-207, 231)
    math.location = (10, 236)

    ringboard.links.new(principled_bsdf.outputs[0], material_output.inputs[0])
    ringboard.links.new(mapping.outputs[0], voronoi_texture.inputs[0])
    ringboard.links.new(math.outputs[0], principled_bsdf.inputs[0])
    ringboard.links.new(voronoi_texture.outputs[0], math.inputs[0])
    ringboard.links.new(texture_coordinate.outputs[3], mapping.inputs[0])

    return mat

def checkerboard_mat():
    # TODO: Investigate instance shaders Blender
    # Currently inefficient as recreating the same shader just with different params

    # Check if already loaded in Blender
    # mat = bpy.data.materials.get(CB_SHADER_NAME)
    # if mat: return mat

    # Need to make it as it doesn't exist
    mat = bpy.data.materials.new(name="CB_Generator")

    # Setup shader node for pattern part
    mat.use_nodes = True
    shader_nodes = mat.node_tree.nodes
    node_links = mat.node_tree.links

    # Create shader
    tex_node = shader_nodes.new(type="ShaderNodeTexCoord")
    tex_node.location = (0, 0)

    map_node = shader_nodes.new(type="ShaderNodeMapping")
    map_node.location = (200, 0)
    map_node.vector_type = 'POINT'
    
    check_node = shader_nodes.new(type="ShaderNodeTexChecker")
    check_node.location = (400, 0)

    # White and black squares by default
    check_node.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0) 
    check_node.inputs[2].default_value = (0.0, 0.0, 0.0, 1.0)
    check_node.inputs[3].default_value = 1.0

    
    # Get BSDF node
    bsdf_node = shader_nodes["Principled BSDF"]
    bsdf_node.location = (600, 0)

    output_node = shader_nodes.get("Material Output")
    output_node.location = (800, 0)

    # Setup node Links
    node_links.new(tex_node.outputs[2], map_node.inputs[0])
    node_links.new(map_node.outputs[0], check_node.inputs[0])
    node_links.new(check_node.outputs[0], bsdf_node.inputs[0])

    return mat

# Material groups

def pixelate_map_group():
    test_group = bpy.data.node_groups.new('Vector Pixelate', 'ShaderNodeTree')
    
    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (0, 0)
    
    test_group.interface.new_socket('Vector', socket_type='NodeSocketVector', in_out='INPUT')
    test_group.interface.new_socket('Width', socket_type='NodeSocketInt', in_out='INPUT')
    test_group.interface.new_socket('Height', socket_type='NodeSocketInt', in_out='INPUT')
    
    # Define Intermediate Nodes
    
    width_divide = test_group.nodes.new('ShaderNodeMath')
    width_divide.operation = 'DIVIDE'
    width_divide.location = (200, 100)
    width_divide.inputs[0].default_value = 1.0
    
    height_divide = test_group.nodes.new('ShaderNodeMath')
    height_divide.operation = 'DIVIDE'
    height_divide.location = (200, -100)
    height_divide.inputs[0].default_value = 1.0
    
    combine_xyz = test_group.nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (400, 0)
    
    snap = test_group.nodes.new('ShaderNodeVectorMath')
    snap.operation = 'SNAP'
    snap.location = (600, 0)
    
    # Create NodeGroup outputs

    group_output = test_group.nodes.new('NodeGroupOutput')
    group_output.location = (800, 0)

    test_group.interface.new_socket('Vector', socket_type='NodeSocketVector', in_out='OUTPUT')
    
    # Link Nodes Together
    
    test_group.links.new(group_inputs.outputs[0], snap.inputs[0])
    test_group.links.new(group_inputs.outputs[1], width_divide.inputs[1])
    test_group.links.new(group_inputs.outputs[2], height_divide.inputs[1])
    
    test_group.links.new(width_divide.outputs[0], combine_xyz.inputs[0])
    test_group.links.new(height_divide.outputs[0], combine_xyz.inputs[1])
    
    test_group.links.new(combine_xyz.outputs[0], snap.inputs[1])
    
    test_group.links.new(snap.outputs[0], group_output.inputs[0])

def fringe_intensity_map_group():
    test_group = bpy.data.node_groups.new('Fringe Intensity Map', 'ShaderNodeTree')

    # Create NodeGroup Inputs

    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200, 0)

    test_group.interface.new_socket('Vector', socket_type='NodeSocketVector', in_out='INPUT')
    test_group.interface.new_socket('Rotation', socket_type='NodeSocketFloat', in_out='INPUT')
    test_group.interface.new_socket('Frequency', socket_type='NodeSocketFloat', in_out='INPUT')
    test_group.interface.new_socket('Phase', socket_type='NodeSocketFloat', in_out='INPUT')

    # Create intermediate nodes
    
    vector_rotate_0 = test_group.nodes.new('ShaderNodeVectorRotate')
    vector_rotate_0.location = (0, 100)
    vector_rotate_0.rotation_type = "Z_AXIS"

    mapping_sep_1 = test_group.nodes.new('ShaderNodeSeparateXYZ')
    mapping_sep_1.location = (200, -200)


    mult_node_1 = test_group.nodes.new('ShaderNodeMath')
    mult_node_1.operation = 'MULTIPLY'
    mult_node_1.location = (200, 0)
    mult_node_1.inputs[0].default_value = np.pi * 2.0



    mult_node_2 = test_group.nodes.new('ShaderNodeMath')
    mult_node_2.operation = 'MULTIPLY'
    mult_node_2.location = (400, 0)



    add_node_3 = test_group.nodes.new('ShaderNodeMath')
    add_node_3.operation = 'ADD'
    add_node_3.location = (600, 0)



    sin_node_4 = test_group.nodes.new('ShaderNodeMath')
    sin_node_4.operation = 'SINE'
    sin_node_4.location = (800, 0)



    add_node_5 = test_group.nodes.new('ShaderNodeMath')
    add_node_5.operation = 'ADD'
    add_node_5.location = (1000, 0)
    add_node_5.inputs[0].default_value = 1.0
    
    
    
    divide_node_6 = test_group.nodes.new('ShaderNodeMath')
    divide_node_6.operation = 'DIVIDE'
    divide_node_6.location = (1200, 0)
    divide_node_6.use_clamp = True
    divide_node_6.inputs[1].default_value = 2.0
    
    # Create output nodes
    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (1400, 0)
    
    test_group.interface.new_socket('Intensity', socket_type='NodeSocketFloat', in_out='OUTPUT')

    # Link Nodes Together
    
    test_group.links.new(group_inputs.outputs[0], vector_rotate_0.inputs[0]) # Vector -> VectorRotate
    test_group.links.new(group_inputs.outputs[1], vector_rotate_0.inputs[3]) # Rotation -> VectorRotate
    test_group.links.new(vector_rotate_0.outputs[0], mapping_sep_1.inputs[0]) # VectorRotate -> SeparateXYZ

    test_group.links.new(group_inputs.outputs[2], mult_node_1.inputs[1]) # Frequency -> Multiply 1 [1]

    test_group.links.new(mapping_sep_1.outputs[1], mult_node_2.inputs[0]) # SeparateXYZ Y -> Multiply 2 [0]
    test_group.links.new(mult_node_1.outputs[0], mult_node_2.inputs[1]) # Multiply 1 -> Multiply 2 [1]

    test_group.links.new(mult_node_2.outputs[0], add_node_3.inputs[0]) # Multiply 2 -> Add 3 [0]
    test_group.links.new(group_inputs.outputs[3], add_node_3.inputs[1]) # Phase -> Add 3 [1]

    test_group.links.new(add_node_3.outputs[0], sin_node_4.inputs[0]) # Add 3 -> Sin [0]

    test_group.links.new(sin_node_4.outputs[0], add_node_5.inputs[0]) # Sin -> Add 5 [0]
    
    test_group.links.new(add_node_5.outputs[0], divide_node_6.inputs[0]) # Add -> Divide 6 [0]

    test_group.links.new(divide_node_6.outputs[0], group_outputs.inputs["Intensity"]) # Cos -> Add 4 [0]
import bpy
from math import pi

def make_pixelate_map_group():
    test_group = bpy.data.node_groups.new('Vector Pixelate', 'ShaderNodeTree')
    
    
    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (0, 0)
    test_group.inputs.new('NodeSocketVector','Vector')
    test_group.inputs.new('NodeSocketInt','Width')
    test_group.inputs.new('NodeSocketInt','Height')

    
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

    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (800, 0)
    
    test_group.outputs.new('NodeSocketVector','Vector')
    
    # Link Nodes Together
    
    test_group.links.new(group_inputs.outputs['Vector'], snap.inputs[0])
    test_group.links.new(group_inputs.outputs['Width'], width_divide.inputs[1])
    test_group.links.new(group_inputs.outputs['Height'], height_divide.inputs[1])
    
    test_group.links.new(width_divide.outputs[0], combine_xyz.inputs[0])
    test_group.links.new(height_divide.outputs[0], combine_xyz.inputs[1])
    
    test_group.links.new(combine_xyz.outputs[0], snap.inputs[1])
    
    test_group.links.new(snap.outputs[0], group_outputs.inputs['Vector'])

def make_fringe_intensity_map_group():
    test_group = bpy.data.node_groups.new('Fringe Intensity Map', 'ShaderNodeTree')

    # Create NodeGroup Inputs

    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200, 0)
    test_group.inputs.new('NodeSocketVector','Vector')
    test_group.inputs.new('NodeSocketFloat','Rotation')
    test_group.inputs.new('NodeSocketFloat','Frequency')
    test_group.inputs.new('NodeSocketFloat','Phase')

    # Create intermediate nodes
    
    vector_rotate_0 = test_group.nodes.new('ShaderNodeVectorRotate')
    vector_rotate_0.location = (0, 100)
    vector_rotate_0.rotation_type = "Z_AXIS"

    mapping_sep_1 = test_group.nodes.new('ShaderNodeSeparateXYZ')
    mapping_sep_1.location = (200, -200)


    mult_node_1 = test_group.nodes.new('ShaderNodeMath')
    mult_node_1.operation = 'MULTIPLY'
    mult_node_1.location = (200, 0)
    mult_node_1.inputs[0].default_value = pi * 2.0



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
    test_group.outputs.new('NodeSocketFloat','Intensity')

    # Link Nodes Together
    
    test_group.links.new(vector_rotate_0.inputs[0], group_inputs.outputs['Vector']) # Vector -> VectorRotate
    test_group.links.new(vector_rotate_0.inputs[3], group_inputs.outputs['Rotation']) # Rotation -> VectorRotate
    
    test_group.links.new(mapping_sep_1.inputs[0], vector_rotate_0.outputs[0]) # Vector Rotate -> SeparateXYZ
    test_group.links.new(mult_node_1.inputs[1], group_inputs.outputs['Frequency']) # Frequency -> Multiply 1 [1]

    test_group.links.new(mult_node_2.inputs[0], mapping_sep_1.outputs[1]) # SeparateXYZ Y -> Multiply 2 [0]
    test_group.links.new(mult_node_2.inputs[1], mult_node_1.outputs[0]) # Multiply 1 -> Multiply 2 [1]

    test_group.links.new(add_node_3.inputs[0], mult_node_2.outputs[0]) # Multiply 2 -> Add 3 [0]
    test_group.links.new(add_node_3.inputs[1], group_inputs.outputs['Phase']) # Phase -> Add 3 [1]

    test_group.links.new(sin_node_4.inputs[0], add_node_3.outputs[0]) # Add 3 -> Sin [0]

    test_group.links.new(add_node_5.inputs[0], sin_node_4.outputs[0]) # Sin -> Add 5 [0]
    
    test_group.links.new(divide_node_6.inputs[0], add_node_5.outputs[0]) # Add -> Divide 6 [0]

    test_group.links.new(group_outputs.inputs["Intensity"], divide_node_6.outputs[0]) # Cos -> Add 4 [0]
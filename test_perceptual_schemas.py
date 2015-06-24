# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language schemas defined in perceptual_schemas.py
"""
def test():
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    import saliency_matlab as smat
    import schema_theory as st
    import perceptual_schemas as ps
    
    ###############################
    ### percepaul schema system ###
    ###############################
    # Instantiating all the necessary procedural schemas
    visualWM = ps.VISUAL_WM()
    perceptualLTM = ps.PERCEPTUAL_LTM()
    saliency_map = ps.SALIENCY_MAP()
    saccade_system = ps.SACCADE_SYSTEM()
    fixation = ps.FIXATION()
    
    # Defining schema to brain mappings.
    perception_mapping = {'Visual_WM':['ITG'], 
                        'Perceptual_LTM':[], 
                        'Saliency_map':['IPS'], 
                        'Saccade_system':['Basal Ganglia', 'FEF', 'Superior Colliculus'],
                        'Fixation':['Visual cortex']}
                        
    perceptual_schemas = [fixation, saliency_map, saccade_system, visualWM, perceptualLTM]
    
    # Creating schema system and adding procedural schemas
    perceptual_system = st.SCHEMA_SYSTEM('Perceptual_system')
    perceptual_system.add_schemas(perceptual_schemas)
    
    # Defining connections
    perceptual_system.add_connection(visualWM, 'to_saliency_map', saliency_map, 'from_visual_WM')
    perceptual_system.add_connection(perceptualLTM, 'to_visual_WM', visualWM, 'from_perceptual_LTM')
    perceptual_system.add_connection(fixation, 'to_visual_WM', visualWM, 'from_fixation')
    perceptual_system.add_connection(saliency_map, 'to_saccade_system', saccade_system , 'from_saliency_map')
    perceptual_system.add_connection(saccade_system, 'to_saliency_map', saliency_map, 'from_saccade_system')
    perceptual_system.add_connection(saccade_system, 'to_fixation', fixation, 'from_saccade_system')
    perceptual_system.add_connection(fixation, 'to_saccade_system', saccade_system, 'from_fixation', )
    
    # Defining input and output ports 
    perceptual_system.set_input_ports([fixation._find_port('from_input'), saliency_map._find_port('from_input')])
    perceptual_system.set_output_ports([visualWM._find_port('to_conceptualizer')])
    
    # Setting up schema to brain mappings
    perception_brain_mapping = st.BRAIN_MAPPING()
    perception_brain_mapping.schema_mapping = perception_mapping
    perceptual_system.brain_mapping = perception_brain_mapping
    
    # Generating schema system graph visualization
    perceptual_system.system2dot()
    
    # Setting up BU saliency data
    saliency_data = smat.SALIENCY_DATA()
    saliency_data.load("./data/scenes/cholitas")
    saliency_map.BU_saliency_map = saliency_data.saliency_map.data
    
    # Display and run    
    plt.figure(1)
    plt.subplot(2,2,1)
    plt.axis('off')
    plt.title('Input scene')
    plt.imshow(saliency_data.orig_image.data)
    
    r = 2**(saliency_data.params.levelParams['mapLevel']-1) # ONly works if pyramidtype = dyadic!
    
    plt.subplot(2,2,2)
    plt.axis('off')
    plt.title('Bottom-up saliency map')
    plt.imshow(saliency_map.BU_saliency_map, cmap = cm.Greys_r)
    
    # Running the schema system
    fixation = plt.subplot(2,2,3)
    plt.axis('off')
    plt.title('Fixation')
    plt.imshow(saliency_data.orig_image.data)
    fix = plt.Circle((0,0), saliency_data.params.foaSize, color='r', alpha=0.3)
    fixation.add_patch(fix)
    
    ior_fig = plt.subplot(2,2,4)
    plt.axis('off')
    plt.title('IOR')
    time = 200
    for t in range(time):    
        perceptual_system.update()
        map = saliency_map.IOR_mask
        if map != None:
            plt.sca(ior_fig)
            ior_fig.cla()
            plt.imshow(map, cmap = cm.Greys_r)
        if saccade_system.eye_pos:
            fix.remove()
            fix.center = (saccade_system.eye_pos[1]*r,saccade_system.eye_pos[0]*r)
            plt.sca(fixation)
            fixation.add_patch(fix)
        plt.pause(0.01)
    
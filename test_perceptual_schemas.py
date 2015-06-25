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
    import language_schemas as ls 
    import loader as ld
    
    
    ###############################
    ### percepaul schema system ###
    ###############################
    # Instantiating all the necessary procedural schemas
    visualWM = ps.VISUAL_WM()
    perceptualLTM = ps.PERCEPTUAL_LTM()
    saliency_map = ps.SALIENCY_MAP()
    saccade_system = ps.SACCADE_SYSTEM()
    fixation = ps.FIXATION()
    conceptualizer = ls.CONCEPTUALIZER()
    conceptLTM = ls.CONCEPT_LTM()
    
    # Defining schema to brain mappings.
    perception_mapping = {'Visual_WM':['ITG'], 
                        'Perceptual_LTM':[], 
                        'Saliency_map':['IPS'], 
                        'Saccade_system':['Basal Ganglia', 'FEF', 'Superior Colliculus'],
                        'Fixation':['Visual cortex'], 'Conceptualizer':['aTP'], 'Concept_LTM':['']}
                        
    perceptual_schemas = [fixation, saliency_map, saccade_system, visualWM, perceptualLTM, conceptualizer, conceptLTM]
    
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
    perceptual_system.add_connection(fixation, 'to_saccade_system', saccade_system, 'from_fixation')
    perceptual_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
    perceptual_system.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
    
    # Defining input and output ports 
    perceptual_system.set_input_ports([fixation._find_port('from_input'), saliency_map._find_port('from_input')])
    perceptual_system.set_output_ports([conceptualizer._find_port('to_semantic_WM')])
    
    # Setting up schema to brain mappings
    perception_brain_mapping = st.BRAIN_MAPPING()
    perception_brain_mapping.schema_mapping = perception_mapping
    perceptual_system.brain_mapping = perception_brain_mapping
    
    # Generating schema system graph visualization
#    perceptual_system.system2dot(image_type='png', disp=True)
    
    # Parameters   
    visualWM.dyn_params['tau'] = 300
    visualWM.dyn_params['act_inf'] = 0.0
    visualWM.dyn_params['L'] = 1.0
    visualWM.dyn_params['k'] = 10.0
    visualWM.dyn_params['x0'] = 0.5
    visualWM.dyn_params['noise_mean'] = 0
    visualWM.dyn_params['noise_std'] = 0.2
    
    visualWM.C2_params['confidence_threshold'] = 0
    visualWM.C2_params['prune_threshold'] = 0.01
    visualWM.C2_params['coop_weight'] = 0
    visualWM.C2_params['comp_weight'] = 0
    
    perceptualLTM.init_act = 1
    conceptLTM.init_act = 1
    
    # Loading data
    my_perceptual_knowledge = ld.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    
    # Initialize perceptual LTM content
    perceptualLTM.initialize(my_perceptual_knowledge)
        
    # Initialize conceptuual  LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
#    # Setting up BU saliency data
#    saliency_data = smat.SALIENCY_DATA()
#    saliency_data.load("./data/scenes/cholitas")
#    saliency_map.BU_saliency_map = saliency_data.saliency_map.data
#    
#    # Display and run    
#    plt.figure()
#    plt.subplot(2,2,1)
#    plt.axis('off')
#    plt.title('Input scene')
#    plt.imshow(saliency_data.orig_image.data)
#    
#    r = 2**(saliency_data.params.levelParams['mapLevel']-1) # ONly works if pyramidtype = dyadic!
#    
#    plt.subplot(2,2,2)
#    plt.axis('off')
#    plt.title('Bottom-up saliency map')
#    plt.imshow(saliency_map.BU_saliency_map, cmap = cm.Greys_r)
#    
#    # Running the schema system
#    fixation = plt.subplot(2,2,3)
#    plt.axis('off')
#    plt.title('Fixation')
#    plt.imshow(saliency_data.orig_image.data)
#    fix = plt.Circle((0,0), saliency_data.params.foaSize, color='r', alpha=0.3)
#    fixation.add_patch(fix)
#    
#    ior_fig = plt.subplot(2,2,4)
#    plt.axis('off')
#    plt.title('IOR')
#    time = 200
#    for t in range(time):    
#        perceptual_system.update()
#        map = saliency_map.IOR_mask
#        if map != None:
#            plt.sca(ior_fig)
#            ior_fig.cla()
#            plt.imshow(map, cmap = cm.Greys_r)
#        if saccade_system.eye_pos:
#            fix.remove()
#            fix.center = (saccade_system.eye_pos[1]*r,saccade_system.eye_pos[0]*r)
#            plt.sca(fixation)
#            fixation.add_patch(fix)
#        plt.pause(0.01)

if __name__=='__main__':
    test()
    

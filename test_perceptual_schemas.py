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
    perceptLTM = ps.PERCEPT_LTM()
    saliency_map = ps.SALIENCY_MAP()
    saccade_system = ps.SACCADE_SYSTEM()
    fixation = ps.FIXATION()
    subscene_rec = ps.SUBSCENE_RECOGNITION()
    conceptualizer = ls.CONCEPTUALIZER()
    conceptLTM = ls.CONCEPT_LTM()
    
    # Defining schema to brain mappings.
    perception_mapping = {'Visual_WM':['ITG'], 
                        'Percept_LTM':[''], 
                        'Saliency_map':['IPS'], 
                        'Saccade_system':[''],
                        'Subscene_recognition':['Ventral stream'], 'Conceptualizer':['aTP'], 'Concept_LTM':[''], 'Fixation':['']}
                        
    perceptual_schemas = [subscene_rec, saliency_map, saccade_system, visualWM, perceptLTM, conceptualizer, conceptLTM, fixation]
    
    # Creating schema system and adding procedural schemas
    perceptual_system = st.SCHEMA_SYSTEM('Perceptual_system')
    perceptual_system.add_schemas(perceptual_schemas)
    
    # Defining connections
    perceptual_system.add_connection(visualWM, 'to_saliency_map', saliency_map, 'from_visual_WM')
    perceptual_system.add_connection(perceptLTM, 'to_subscene_rec', subscene_rec, 'from_percept_LTM')
    perceptual_system.add_connection(subscene_rec, 'to_visual_WM', visualWM, 'from_subscene_rec')
    perceptual_system.add_connection(saliency_map, 'to_saccade_system', saccade_system , 'from_saliency_map')
    perceptual_system.add_connection(saccade_system, 'to_saliency_map', saliency_map, 'from_saccade_system')
    perceptual_system.add_connection(saccade_system, 'to_fixation', fixation, 'from_saccade_system')
    perceptual_system.add_connection(fixation, 'to_subscene_rec', subscene_rec, 'from_fixation')
    perceptual_system.add_connection(subscene_rec, 'to_saccade_system', saccade_system, 'from_subscene_rec')
    perceptual_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
    perceptual_system.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
    
    # Defining input and output ports 
    perceptual_system.set_input_ports([subscene_rec._find_port('from_input'), saliency_map._find_port('from_input')])
    perceptual_system.set_output_ports([conceptualizer._find_port('to_semantic_WM')])
    
    # Setting up schema to brain mappings
    perception_brain_mapping = st.BRAIN_MAPPING()
    perception_brain_mapping.schema_mapping = perception_mapping
    perceptual_system.brain_mapping = perception_brain_mapping
    
    # Generating schema system graph visualization
#    perceptual_system.system2dot(image_type='png', disp=True)
    
    # Parameters   
    saliency_map.IOR_params = {'IOR_radius': 5, 'IOR_decay': 0.99, 'IOR_max': 100}
    visualWM.dyn_params['tau'] = 300
    visualWM.dyn_params['act_inf'] = 0.0
    visualWM.dyn_params['L'] = 1.0
    visualWM.dyn_params['k'] = 10.0
    visualWM.dyn_params['x0'] = 0.5
    visualWM.dyn_params['noise_mean'] = 0
    visualWM.dyn_params['noise_std'] = 1
    
    visualWM.C2_params['confidence_threshold'] = 0
    visualWM.C2_params['prune_threshold'] = 0.3
    visualWM.C2_params['coop_weight'] = 0
    visualWM.C2_params['comp_weight'] = 0
    
    perceptLTM.init_act = 1
    conceptLTM.init_act = 1
    
    # Loading data
    my_perceptual_knowledge = ld.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptualization = ld.load_conceptualization("TCG_semantics.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
    my_scene = ld.load_scene("TCG_scene.json", "./data/scenes/cholitas/")
    
    # Initialize perceptual LTM content
    perceptLTM.initialize(my_perceptual_knowledge)
        
    # Initialize concept LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize conceptualizer
    conceptualizer.initialize(my_conceptualization)
    
    # Setting up BU saliency data
    saliency_data = smat.SALIENCY_DATA()
    saliency_data.load("./data/scenes/cholitas")
    saliency_map.BU_saliency_map = saliency_data.saliency_map.data
    
    # Test schema rec intialization
    perceptual_system.set_input(my_scene)
    for step in range(1000):
        perceptual_system.update()
    perceptual_system.update()
    
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
#    time = 1000
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

    visualWM.show_dynamics(c2_levels=False)
    perceptual_system.save_sim('./tmp/test_perception_output.json')
if __name__=='__main__':
    test()
    

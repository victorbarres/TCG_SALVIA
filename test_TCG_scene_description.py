# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG description
"""
import random

import schema_theory as st
import perceptual_schemas as ps
import language_schemas as ls 
import loader as ld


def TCG_description_system():
    """
    Creates and returns the TCG production schema system.
    """
    # Instantiating all the necessary procedural schemas
    subscene_rec = ps.SUBSCENE_RECOGNITION()
    perceptLTM = ps.PERCEPT_LTM()
    visualWM = ps.VISUAL_WM()
    
    conceptualizer = ls.CONCEPTUALIZER()
    conceptLTM = ls.CONCEPT_LTM()
    
    semanticWM = ls.SEMANTIC_WM()
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    phonWM_P = ls.PHON_WM_P()
    control = ls.CONTROL()
    utter = ls.UTTER()
    
    # Defining schema to brain mappings.
    brain_mappings = {'Visual_WM':['ITG'], 
                        'Percept_LTM':[''],
                        'Subscene_recognition':['Ventral stream'], 
                        'Conceptualizer':['aTP'], 
                        'Concept_LTM':[''],
                        'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                        'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                        'Grammatical_LTM':['left_STG', 'left_MTG'],
                        'Cxn_retrieval_P':[], 
                        'Phonological_WM_P':['left_BA6'],
                        'Utter':[''],
                        'Control':['DLPFC'], 
                        'Concept_LTM':['']}
                        
    schemas = [subscene_rec, visualWM, perceptLTM, conceptualizer, conceptLTM, grammaticalLTM, cxn_retrieval_P, semanticWM, grammaticalWM_P, phonWM_P, utter, control] 
    # Creating schema system and adding procedural schemas
    description_system = st.SCHEMA_SYSTEM('Description_system')
    description_system.add_schemas(schemas)
    
    # Defining connections
    description_system.add_connection(perceptLTM, 'to_subscene_rec', subscene_rec, 'from_percept_LTM')
    description_system.add_connection(subscene_rec, 'to_visual_WM', visualWM, 'from_subscene_rec')
    
    description_system.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
    description_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
    description_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
    
    description_system.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    description_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    description_system.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    description_system.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    description_system.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    description_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    description_system.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    description_system.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    description_system.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    description_system.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    
    
    # Defining input and output ports 
    description_system.set_input_ports([subscene_rec.find_port('from_input')])
    description_system.set_output_ports([utter.find_port('to_output')])
    
    # Setting up schema to brain mappings
    description_brain_mapping = st.BRAIN_MAPPING()
    description_brain_mapping.schema_mapping = brain_mappings
    description_system.brain_mapping = description_brain_mapping
    
    # Parameters   
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
    
    semanticWM.dyn_params['tau'] = 300
    semanticWM.dyn_params['act_inf'] = 0.0
    semanticWM.dyn_params['L'] = 1.0
    semanticWM.dyn_params['k'] = 10.0
    semanticWM.dyn_params['x0'] = 0.5
    semanticWM.dyn_params['noise_mean'] = 0
    semanticWM.dyn_params['noise_std'] = 0.2
    semanticWM.C2_params['confidence_threshold'] = 0
    semanticWM.C2_params['prune_threshold'] = 0.01
    semanticWM.C2_params['coop_weight'] = 0
    semanticWM.C2_params['comp_weight'] = 0
    
    conceptLTM.init_act = 1
    
    grammaticalWM_P.dyn_params['tau'] = 100
    grammaticalWM_P.dyn_params['act_inf'] = 0.0
    grammaticalWM_P.dyn_params['L'] = 1.0
    grammaticalWM_P.dyn_params['k'] = 10.0
    grammaticalWM_P.dyn_params['x0'] = 0.5
    grammaticalWM_P.dyn_params['noise_mean'] = 0
    grammaticalWM_P.dyn_params['noise_std'] = 0.2
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.2
    grammaticalWM_P.C2_params['prune_threshold'] = 0.1
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -1
    
    grammaticalLTM.init_act = grammaticalWM_P.C2_params['confidence_threshold']
    
    control.task_params['mode'] = 'produce'
    control.task_params['time_pressure'] = 800
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
    
    my_perceptual_knowledge = ld.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptualization = ld.load_conceptualization("TCG_semantics.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
    
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize perceptual LTM content
    perceptLTM.initialize(my_perceptual_knowledge)
        
    # Initialize concept LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize conceptualizer
    conceptualizer.initialize(my_conceptualization)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return description_system

def test(seed=None):
    """
    """
    random.seed(seed)
    
    description_system = TCG_description_system()

    # Generating schema system graph visualization
    description_system.system2dot(image_type='png', disp=True)
    
    # Setting up BU saliency data
    scene_name = 'KC06_1_1'
    scene_folder = "./data/scenes/%s/" %scene_name
    my_scene = ld.load_scene("TCG_scene.json", scene_folder)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    # Running the schema system
    time = 1000
    for t in range(time):
        description_system.update()
        output = description_system.get_output()
        if output:
            print output
    
#    description_system.schemas['Visual_WM'].show_SceneRep()
#    description_system.schemas['Semantic_WM'].show_SemRep()
    description_system.schemas['Grammatical_WM_P'].show_dynamics()
    description_system.schemas['Grammatical_WM_P'].show_state()
    
    #description_system.save_sim('./tmp/test_description_output.json')

if __name__ == '__main__':
    test(seed=None)
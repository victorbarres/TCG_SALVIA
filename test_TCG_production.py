# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG Production
"""
import random

import saliency_matlab as smat
import schema_theory as st
import perceptual_schemas as ps
import language_schemas as ls 
import loader as ld

random.seed(seed)


####################################
### TCG production schema system ###
####################################
# Instantiating all the necessary procedural schemas
visualWM = ps.VISUAL_WM()
perceptLTM = ps.PERCEPT_LTM()
saliency_map = ps.SALIENCY_MAP()
saccade_system = ps.SACCADE_SYSTEM()
fixation = ps.FIXATION()
subscene_rec = ps.SUBSCENE_RECOGNITION()
conceptualizer = ls.CONCEPTUALIZER()
conceptLTM = ls.CONCEPT_LTM()
semanticWM = ls.SEMANTIC_WM()
grammaticalWM = ls.GRAMMATICAL_WM()
grammaticalLTM = ls.GRAMMATICAL_LTM()
cxn_retrieval = ls.CXN_RETRIEVAL()
phonWM = ls.PHON_WM()
control = ls.CONTROL()

# Defining schema to brain mappings.
brain_mappings = {'Fixation':[''],
                    'Visual_WM':['ITG'], 
                    'Percept_LTM':[''], 
                    'Saliency_map':['IPS'], 
                    'Saccade_system':[''],
                    'Subscene_recognition':['Ventral stream'], 
                    'Conceptualizer':['aTP'], 
                    'Concept_LTM':[''],
                    'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval':[], 
                    'Phonological_WM':['left_BA6'],
                    'Control':['DLPFC'], 'Concept_LTM':['']}
                    
schemas = [fixation, subscene_rec, saliency_map, saccade_system, visualWM, perceptLTM, conceptualizer, conceptLTM, grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM, control] 

# Creating schema system and adding procedural schemas
production_system = st.SCHEMA_SYSTEM('Production_system')
production_system.add_schemas(schemas)

# Defining connections
production_system.add_connection(visualWM, 'to_saliency_map', saliency_map, 'from_visual_WM')
production_system.add_connection(perceptLTM, 'to_subscene_rec', subscene_rec, 'from_percept_LTM')
production_system.add_connection(subscene_rec, 'to_visual_WM', visualWM, 'from_subscene_rec')
production_system.add_connection(saliency_map, 'to_saccade_system', saccade_system , 'from_saliency_map')
production_system.add_connection(saccade_system, 'to_saliency_map', saliency_map, 'from_saccade_system')
production_system.add_connection(saccade_system, 'to_fixation', fixation, 'from_saccade_system')
production_system.add_connection(fixation, 'to_subscene_rec', subscene_rec, 'from_fixation')
production_system.add_connection(subscene_rec, 'to_saccade_system', saccade_system, 'from_subscene_rec')
production_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
production_system.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
production_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
production_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
production_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
production_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
production_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
production_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
production_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
production_system.add_connection(phonWM, 'to_control', control, 'from_phonological_WM')
production_system.add_connection(control, 'to_grammatical_WM', grammaticalWM, 'from_control')


# Defining input and output ports 
production_system.set_input_ports([subscene_rec._find_port('from_input'), saliency_map._find_port('from_input')])
production_system.set_output_ports([phonWM._find_port('to_output')])

# Setting up schema to brain mappings
production_brain_mapping = st.BRAIN_MAPPING()
production_brain_mapping.schema_mapping = brain_mappings
production_system.brain_mapping = production_brain_mapping

# Generating schema system graph visualization
#production_system.system2dot(image_type='png', disp=True)

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

grammaticalWM.dyn_params['tau'] = 30
grammaticalWM.dyn_params['act_inf'] = 0.0
grammaticalWM.dyn_params['L'] = 1.0
grammaticalWM.dyn_params['k'] = 10.0
grammaticalWM.dyn_params['x0'] = 0.5
grammaticalWM.dyn_params['noise_mean'] = 0
grammaticalWM.dyn_params['noise_std'] = 0.2
grammaticalWM.C2_params['confidence_threshold'] = 0.2
grammaticalWM.C2_params['prune_threshold'] = 0.01
grammaticalWM.C2_params['coop_weight'] = 1
grammaticalWM.C2_params['comp_weight'] = -1

grammaticalLTM.init_act = grammaticalWM.C2_params['confidence_threshold']

control.task_params['time_pressure'] = 50

# Loading data
my_scene = ld.load_scene("TCG_scene.json", "./data/scenes/cholitas/")

my_perceptual_knowledge = ld.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
my_conceptualization = ld.load_conceptualization("TCG_semantics.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
my_grammar = ld.load_grammar("TCG_grammar_VB.json", "./data/grammars/", my_conceptual_knowledge)

# Initialize perceptual LTM content
perceptLTM.initialize(my_perceptual_knowledge)
    
# Initialize concept LTM content
conceptLTM.initialize(my_conceptual_knowledge)

# Initialize conceptualizer
conceptualizer.initialize(my_conceptualization)

# Initialize grammatical LTM content
grammaticalLTM.initialize(my_grammar)

# Setting up BU saliency data
saliency_data = smat.SALIENCY_DATA()
saliency_data.load("./data/scenes/cholitas") # This needs to eb better integrated with the scene data.
saliency_map.BU_saliency_map = saliency_data.saliency_map.data

# Test schema rec intialization
production_system.set_input(my_scene)
production_system.verbose = False
for step in range(100):
    production_system.update()        
production_system.update()

visualWM.show_dynamics(c2_levels=False)
semanticWM.show_dynamics(c2_levels=False)
grammaticalWM.show_dynamics()
grammaticalWM.show_state()

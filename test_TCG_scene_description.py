# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG Production
"""
import random

import schema_theory as st
import perceptual_schemas as ps
import language_schemas as ls 
import loader as ld

random.seed(3)


####################################
### TCG production schema system ###
####################################
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
                    'Control':['DLPFC'], 'Concept_LTM':['']}
                    
schemas = [subscene_rec, visualWM, perceptLTM, conceptualizer, conceptLTM, grammaticalLTM, cxn_retrieval_P, semanticWM, grammaticalWM_P, phonWM_P, control] 

# Creating schema system and adding procedural schemas
production_system = st.SCHEMA_SYSTEM('Production_system')
production_system.add_schemas(schemas)

# Defining connections
production_system.add_connection(perceptLTM, 'to_subscene_rec', subscene_rec, 'from_percept_LTM')
production_system.add_connection(subscene_rec, 'to_visual_WM', visualWM, 'from_subscene_rec')

production_system.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
production_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
production_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')

production_system.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
production_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
production_system.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
production_system.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
production_system.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
production_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
production_system.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
production_system.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')


# Defining input and output ports 
production_system.set_input_ports([subscene_rec.find_port('from_input')])
production_system.set_output_ports([phonWM_P.find_port('to_output')])

# Setting up schema to brain mappings
production_brain_mapping = st.BRAIN_MAPPING()
production_brain_mapping.schema_mapping = brain_mappings
production_system.brain_mapping = production_brain_mapping

# Generating schema system graph visualization
production_system.system2dot(image_type='png', disp=True)

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

control.task_params['time_pressure'] = 800

# Loading data
scene_name = 'KC06_1_1'
grammar_name = 'TCG_grammar_VB'

scene_folder = "./data/scenes/%s/" %scene_name
my_scene = ld.load_scene("TCG_scene.json", scene_folder)
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

# Setting up BU saliency data
saliency_data = ld.load_BU_saliency(scene_name, scene_folder)
r = 2**(saliency_data.params.levelParams['mapLevel']-1) # ONly works if pyramidtype = dyadic!

# Schema rec intialization
production_system.set_input(my_scene)
production_system.verbose = False

# Running the schema system
time = 1000
for t in range(time):
    production_system.update()
    output = production_system.get_output()
    if output[0]:
        print output[0]

#visualWM.show_SceneRep()
#semanticWM.show_SemRep()
grammaticalWM_P.show_dynamics()
grammaticalWM_P.show_state()

#production_system.save_sim('./tmp/test_production_output.json')f
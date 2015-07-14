# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Contains functions that can instantiate various TCG models and submodels.
"""
import schema_theory as st
import language_schemas as ls
import perceptual_schemas as ps
from loader import TCG_LOADER

def TCG_production_system(name='language_system_P'):
    """
    Creates and returns the TCG production schema system.
    """
    # Instantiating all the necessary procedural schemas
    semanticWM = ls.SEMANTIC_WM()
    conceptLTM = ls.CONCEPT_LTM()
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    phonWM_P = ls.PHON_WM_P()
    utter = ls.UTTER()
    control = ls.CONTROL()
    
    # Defining schema to brain mappings.
    language_mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'],
                        'Concept_LTM':[''],
                        'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                        'Grammatical_LTM':['left_STG', 'left_MTG'],
                        'Cxn_retrieval_P':[], 
                        'Phonological_WM_P':['left_BA6'],
                        'Control':['DLPFC'],
                        'Utter':['']
                        }
   
   # Initializing schema system
    language_system_P = st.SCHEMA_SYSTEM(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system_P.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [conceptLTM, semanticWM, grammaticalLTM, cxn_retrieval_P, grammaticalWM_P, phonWM_P, utter, control]

    language_system_P.add_schemas(language_schemas)
    language_system_P.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    language_system_P.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    language_system_P.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    language_system_P.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    language_system_P.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    language_system_P.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    language_system_P.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system_P.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    language_system_P.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    language_system_P.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    language_system_P.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system_P.set_input_ports([semanticWM.find_port('from_conceptualizer')])
    language_system_P.set_output_ports([utter.find_port('to_output')])
    
    # Parameters   
    semanticWM.dyn_params['tau'] = 1000
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
    
    grammaticalWM_P.dyn_params['tau'] = 30
    grammaticalWM_P.dyn_params['act_inf'] = 0.0
    grammaticalWM_P.dyn_params['L'] = 1.0
    grammaticalWM_P.dyn_params['k'] = 10.0
    grammaticalWM_P.dyn_params['x0'] = 0.5
    grammaticalWM_P.dyn_params['noise_mean'] = 0
    grammaticalWM_P.dyn_params['noise_std'] = 0.2
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.7
    grammaticalWM_P.C2_params['prune_threshold'] = 0.05
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -4
    grammaticalWM_P.style_params['activation']=0.8
    grammaticalWM_P.style_params['sem_length']=0.2
    grammaticalWM_P.style_params['form_length']=0
    
    phonWM_P.dyn_params['tau'] = 100
    phonWM_P.dyn_params['act_inf'] = 0.0
    phonWM_P.dyn_params['L'] = 1.0
    phonWM_P.dyn_params['k'] = 10.0
    phonWM_P.dyn_params['x0'] = 0.5
    phonWM_P.dyn_params['noise_mean'] = 0
    phonWM_P.dyn_params['noise_std'] = 0.2
    phonWM_P.C2_params['confidence_threshold'] = 0
    phonWM_P.C2_params['prune_threshold'] = 0.01
    phonWM_P.C2_params['coop_weight'] = 0
    phonWM_P.C2_params['comp_weight'] = 0
    
    utter.params['speech_rate'] = 1
    
    control.set_mode('produce')
    control.task_params['time_pressure'] = 500
    control.task_params['start_produce'] = 500
    
    conceptLTM.init_act = 1
    grammaticalLTM.init_act = 0.3
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
#    grammar_name = 'TCG_grammar_VB_naming'

   
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return language_system_P


def TCG_comprehension_system(name='language_system_C'):
    """
    Creates and returns the TCG comprehension schema system.
    """
    # Instantiating all the necessary procedural schemas
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_C = ls.CXN_RETRIEVAL_C()
    phonWM_C = ls.PHON_WM_C()
    grammaticalWM_C = ls.GRAMMATICAL_WM_C()
    semanticWM = ls.SEMANTIC_WM()
    conceptLTM = ls.CONCEPT_LTM()
    control = ls.CONTROL()
    
    # Defining schema to brain mappings.
    language_mapping = {'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_C':[], 
                    'Phonological_WM_C':['Wernicke'],
                    'Grammatical_WM_C':['lBA44, lBA45'],
                    'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'],
                    'Concept_LTM':[''],
                    'Control':['DLPFC']}
    
    # Initializing schema system
    language_system_C = st.SCHEMA_SYSTEM(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system_C.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [grammaticalLTM, cxn_retrieval_C, phonWM_C,  grammaticalWM_C, semanticWM, conceptLTM, control]

    language_system_C.add_schemas(language_schemas)
    language_system_C.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    language_system_C.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    language_system_C.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    language_system_C.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    language_system_C.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    language_system_C.add_connection(conceptLTM, 'to_semantic_WM', semanticWM, 'from_concept_LTM')
    language_system_C.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system_C.add_connection(control, 'to_grammatical_WM_C', grammaticalWM_C, 'from_control')
    language_system_C.set_input_ports([phonWM_C.find_port('from_input')])
    language_system_C.set_output_ports([phonWM_C.find_port('to_grammatical_WM_C')])
    
    
    # Parameters
    phonWM_C.dyn_params['tau'] = 100
    phonWM_C.dyn_params['act_inf'] = 0.0
    phonWM_C.dyn_params['L'] = 1.0
    phonWM_C.dyn_params['k'] = 10.0
    phonWM_C.dyn_params['x0'] = 0.5
    phonWM_C.dyn_params['noise_mean'] = 0
    phonWM_C.dyn_params['noise_std'] = 0.2
    phonWM_C.C2_params['confidence_threshold'] = 0
    phonWM_C.C2_params['prune_threshold'] = 0.01
    phonWM_C.C2_params['coop_weight'] = 0
    phonWM_C.C2_params['comp_weight'] = 0
    
    grammaticalWM_C.dyn_params['tau'] = 100
    grammaticalWM_C.dyn_params['act_inf'] = 0.0
    grammaticalWM_C.dyn_params['L'] = 1.0
    grammaticalWM_C.dyn_params['k'] = 10.0
    grammaticalWM_C.dyn_params['x0'] = 0.5
    grammaticalWM_C.dyn_params['noise_mean'] = 0
    grammaticalWM_C.dyn_params['noise_std'] = 0.2
    grammaticalWM_C.C2_params['confidence_threshold'] = 0.5
    grammaticalWM_C.C2_params['prune_threshold'] = 0.1
    grammaticalWM_C.C2_params['coop_weight'] = 1
    grammaticalWM_C.C2_params['comp_weight'] = -1
    
    grammaticalLTM.init_act = grammaticalWM_C.C2_params['confidence_threshold']*0.5
    
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
    
    conceptLTM.init_act = 0.8
    control.task_params['time_pressure'] = 500
    control.task_params['start_produce'] = 500
    control.set_mode('listen')
    
    # Loading data
    grammar_name = 'TCG_grammar_VB_singlehead'
    
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    return language_system_C

def TCG_language_system(name='language_system'):
    """
    Creates and returns the TCG language schema system, including both production and comprehension.
    """
    # Instantiating all the necessary procedural schemas
    semanticWM = ls.SEMANTIC_WM()
    conceptLTM = ls.CONCEPT_LTM()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    grammaticalWM_C = ls.GRAMMATICAL_WM_C()
    cxn_retrieval_C = ls.CXN_RETRIEVAL_C()
    phonWM_P = ls.PHON_WM_P()
    utter = ls.UTTER()
    phonWM_C = ls.PHON_WM_C()
    control = ls.CONTROL()
    
    
    # Defining schema to brain mappings.
    language_mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_P':[], 
                    'Phonological_WM_P':['left_BA6'],
                    'Utter':[''],
                    'Cxn_retrieval_C':[], 
                    'Phonological_WM_C':['Wernicke'],
                    'Grammatical_WM_C':['lBA44, lBA45'],
                    'Control':['DLPFC'],
                    'Concept_LTM':['']}
   
   # Initializing schema system
    language_system = st.SCHEMA_SYSTEM(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [semanticWM, conceptLTM, grammaticalLTM, cxn_retrieval_P, grammaticalWM_P, phonWM_P, utter, phonWM_C, grammaticalWM_C, cxn_retrieval_C, control]

    language_system.add_schemas(language_schemas)
    language_system.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    language_system.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    language_system.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    language_system.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    language_system.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    language_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    language_system.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    language_system.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    language_system.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    language_system.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    language_system.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    language_system.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system.add_connection(control, 'to_grammatical_WM_C', grammaticalWM_C, 'from_control')
    language_system.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    language_system.add_connection(conceptLTM, 'to_semantic_WM', semanticWM, 'from_concept_LTM')
    language_system.set_input_ports([phonWM_C.find_port('from_input')])
    language_system.set_output_ports([utter.find_port('to_output')])
    
     # Parameters
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
    
    grammaticalWM_P.dyn_params['tau'] = 30
    grammaticalWM_P.dyn_params['act_inf'] = 0.0
    grammaticalWM_P.dyn_params['L'] = 1.0
    grammaticalWM_P.dyn_params['k'] = 10.0
    grammaticalWM_P.dyn_params['x0'] = 0.5
    grammaticalWM_P.dyn_params['noise_mean'] = 0
    grammaticalWM_P.dyn_params['noise_std'] = 0.2
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.7
    grammaticalWM_P.C2_params['prune_threshold'] = 0.01
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -1
    grammaticalWM_P.style_params['activation']=0.8
    grammaticalWM_P.style_params['sem_length']=0.2
    grammaticalWM_P.style_params['form_length']=0
    
    phonWM_P.dyn_params['tau'] = 100
    phonWM_P.dyn_params['act_inf'] = 0.0
    phonWM_P.dyn_params['L'] = 1.0
    phonWM_P.dyn_params['k'] = 10.0
    phonWM_P.dyn_params['x0'] = 0.5
    phonWM_P.dyn_params['noise_mean'] = 0
    phonWM_P.dyn_params['noise_std'] = 0.2
    phonWM_P.C2_params['confidence_threshold'] = 0
    phonWM_P.C2_params['prune_threshold'] = 0.01
    phonWM_P.C2_params['coop_weight'] = 0
    phonWM_P.C2_params['comp_weight'] = 0
    
    conceptLTM.init_act = 1
    grammaticalLTM.init_act = grammaticalWM_P.C2_params['confidence_threshold']*0.5
    
    utter.params['speech_rate'] = 10
    
    control.task_params['time_pressure'] = 200
    control.task_params['start_produce'] = 300
    
    phonWM_C.dyn_params['tau'] = 100
    phonWM_C.dyn_params['act_inf'] = 0.0
    phonWM_C.dyn_params['L'] = 1.0
    phonWM_C.dyn_params['k'] = 10.0
    phonWM_C.dyn_params['x0'] = 0.5
    phonWM_C.dyn_params['noise_mean'] = 0
    phonWM_C.dyn_params['noise_std'] = 0.2
    phonWM_C.C2_params['confidence_threshold'] = 0
    phonWM_C.C2_params['prune_threshold'] = 0.01
    phonWM_C.C2_params['coop_weight'] = 0
    phonWM_C.C2_params['comp_weight'] = 0
    
    grammaticalWM_C.dyn_params['tau'] = 100
    grammaticalWM_C.dyn_params['act_inf'] = 0.0
    grammaticalWM_C.dyn_params['L'] = 1.0
    grammaticalWM_C.dyn_params['k'] = 10.0
    grammaticalWM_C.dyn_params['x0'] = 0.5
    grammaticalWM_C.dyn_params['noise_mean'] = 0
    grammaticalWM_C.dyn_params['noise_std'] = 0.2
    grammaticalWM_C.C2_params['confidence_threshold'] = 0.5
    grammaticalWM_C.C2_params['prune_threshold'] = 0.1
    grammaticalWM_C.C2_params['coop_weight'] = 1
    grammaticalWM_C.C2_params['comp_weight'] = -1
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
   
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return language_system
    
def TCG_description_system(name='description_system'):
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
    description_system = st.SCHEMA_SYSTEM(name)
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
    description_system.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
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
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.7
    grammaticalWM_P.C2_params['prune_threshold'] = 0.1
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -1
    grammaticalWM_P.style_params['activation']=0.8
    grammaticalWM_P.style_params['sem_length']=0.2
    grammaticalWM_P.style_params['form_length']=0
    
    grammaticalLTM.init_act = grammaticalWM_P.C2_params['confidence_threshold']
    
    control.task_params['mode'] = 'produce'
    control.task_params['time_pressure'] = 500
    control.task_params['start_produce'] = 500
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
    
    my_perceptual_knowledge = TCG_LOADER.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptualization = TCG_LOADER.load_conceptualization("TCG_semantics.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
    
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize perceptual LTM content
    perceptLTM.initialize(my_perceptual_knowledge)
        
    # Initialize concept LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize conceptualizer
    conceptualizer.initialize(my_conceptualization)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return description_system

if __name__ == '__main__':
    production_system_1 = TCG_production_system()
    production_system_2 = TCG_production_system()
    
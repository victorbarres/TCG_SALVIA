# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Contains functions that can instantiate various TCG models and submodels.
"""
import schema_theory as st
import language_schemas as ls
import perceptual_schemas as ps
from loader import TCG_LOADER
    
    
def TCG_production_system(name='language_system_P', 
                          grammar_name='TCG_grammar_VB', 
                          semantics_name = 'TCG_semantics',
                          grammar_path = './data/grammars/',
                          semantics_path = './data/semantics/'):
    """
    Creates and returns the TCG production schema system.
    """
    # Instantiating all the necessary modules schemas
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
    language_system_P.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    language_system_P.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system_P.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    language_system_P.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    language_system_P.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    language_system_P.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system_P.set_input_ports([semanticWM.find_port('from_conceptualizer')])
    language_system_P.set_output_ports([utter.find_port('to_output'), grammaticalWM_P.find_port('to_output')])
    
    # Parameters
    semanticWM.params['dyn']['tau'] = 5000.0
    semanticWM.params['dyn']['act_rest'] = 0.001
    semanticWM.params['dyn']['k'] = 10.0
    semanticWM.params['dyn']['noise_mean'] = 0.0
    semanticWM.params['dyn']['noise_std'] = 0.2
    semanticWM.params['C2']['confidence_threshold'] = 0.0
    semanticWM.params['C2']['prune_threshold'] = 0.01
    semanticWM.params['C2']['coop_weight'] = 0.0
    semanticWM.params['C2']['comp_weight'] = 0.0
    
    grammaticalWM_P.params['dyn']['tau'] = 100 # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    grammaticalWM_P.params['dyn']['act_rest'] = 0.001
    grammaticalWM_P.params['dyn']['k'] = 10.0 # Need to analyze the impact of that factor.
    grammaticalWM_P.params['dyn']['noise_mean'] = 0.0
    grammaticalWM_P.params['dyn']['noise_std'] = 0.2
    grammaticalWM_P.params['C2']['confidence_threshold'] = 0.3 #0.7
    grammaticalWM_P.params['C2']['prune_threshold'] = 0.01 #0.01 # Manipulations can yield "broca's aphasia" (0.3)
    grammaticalWM_P.params['C2']['coop_weight'] = 0.1
    grammaticalWM_P.params['C2']['comp_weight'] = -0.1 #-4.0 # Needs to compensate for the dominance of cooperation link.
    grammaticalWM_P.params['C2']['sub_threshold_r'] = 0.8
    grammaticalWM_P.params['C2']['deact_weight'] = 0.0 # When set at 1, the output act as if the start_produce always occured right after new sem elements are introduced.
    
    phonWM_P.params['dyn']['tau'] = 100.0
    phonWM_P.params['dyn']['act_rest'] = 0.001
    phonWM_P.params['dyn']['k'] = 10.0
    phonWM_P.params['dyn']['noise_mean'] = 0.0
    phonWM_P.params['dyn']['noise_std'] = 0.2
    phonWM_P.params['C2']['confidence_threshold'] = 0.0
    phonWM_P.params['C2']['prune_threshold'] = 0.01
    phonWM_P.params['C2']['coop_weight'] = 0.0
    phonWM_P.params['C2']['comp_weight'] = 0.0
    
    utter.params['speech_rate'] = 1.0
    
    control.set_mode('produce')
    control.params['task']['time_pressure'] = 200.0
    control.params['task']['start_produce'] = 400.0
    control.params['style']['activation'] = 0.3 #0.7
    control.params['style']['sem_length'] = 0.7 #0.5
    control.params['style']['form_length'] = 0.0 #0.0
    control.params['style']['continuity'] = 0.0  #0.0
    
    conceptLTM.init_act = 1.0
    grammaticalLTM.init_act = 0.3
    
    # Loading data
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return language_system_P


def TCG_comprehension_system(name='language_system_C',
                             grammar_name='TCG_grammar_VB', 
                             semantics_name = 'TCG_semantics',
                             grammar_path = './data/grammars/',
                             semantics_path = './data/semantics/'):
    """
    Creates and returns the TCG comprehension schema system.
    """
    # Instantiating all the necessary modules schemas
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
    language_system_C.set_output_ports([semanticWM.find_port('to_visual_WM')])
    
    
    # Parameters
    phonWM_C.params['dyn']['tau'] = 100.0
    phonWM_C.params['dyn']['act_rest'] = 0.001
    phonWM_C.params['dyn']['k'] = 10.0
    phonWM_C.params['dyn']['noise_mean'] = 0.0
    phonWM_C.params['dyn']['noise_std'] = 0.2
    phonWM_C.params['C2']['confidence_threshold'] = 0.0
    phonWM_C.params['C2']['prune_threshold'] = 0.01
    phonWM_C.params['C2']['coop_weight'] = 0.0
    phonWM_C.params['C2']['comp_weight'] = 0.0
    
    grammaticalWM_C.params['dyn']['tau'] = 100.0
    grammaticalWM_C.params['dyn']['act_rest'] = 0.001
    grammaticalWM_C.params['dyn']['k'] = 10.0
    grammaticalWM_C.params['dyn']['noise_mean'] = 0.0
    grammaticalWM_C.params['dyn']['noise_std'] = 0.2
    grammaticalWM_C.params['C2']['confidence_threshold'] = 0.5
    grammaticalWM_C.params['C2']['prune_threshold'] = 0.1
    grammaticalWM_C.params['C2']['coop_weight'] = 1.0
    grammaticalWM_C.params['C2']['comp_weight'] = -1.0
    grammaticalWM_C.params['C2']['sub_threshold_r'] = 0.8
    grammaticalWM_C.params['C2']['deact_weight'] = 0.0
    
    grammaticalLTM.init_act = grammaticalWM_C.params['C2']['confidence_threshold']*0.5
    
    semanticWM.params['dyn']['tau'] = 300.0
    semanticWM.params['dyn']['act_rest'] = 0.001
    semanticWM.params['dyn']['k'] = 10.0
    semanticWM.params['dyn']['noise_mean'] = 0.0
    semanticWM.params['dyn']['noise_std'] = 0.2
    semanticWM.params['C2']['confidence_threshold'] = 0.0
    semanticWM.params['C2']['prune_threshold'] = 0.01
    semanticWM.params['C2']['coop_weight'] = 0.0
    semanticWM.params['C2']['comp_weight'] = 0.0
    
    conceptLTM.init_act = 0.8
    control.params['task']['time_pressure'] = 500.0
    control.params['task']['start_produce'] = 500.0
    control.set_mode('listen')
    
    # Loading data
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    return language_system_C

def TCG_language_system(name='language_system',
                        grammar_name='TCG_grammar_VB', 
                        semantics_name = 'TCG_semantics',
                        grammar_path = './data/grammars/',
                        semantics_path = './data/semantics/'):
    """
    Creates and returns the TCG language schema system, including both production and comprehension.
    """
    # Instantiating all the necessary modules schemas
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
    language_system.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
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
    semanticWM.params['dyn']['tau'] = 1000.0
    semanticWM.params['dyn']['act_rest'] = 0.001
    semanticWM.params['dyn']['k'] = 10.0
    semanticWM.params['dyn']['noise_mean'] = 0.0
    semanticWM.params['dyn']['noise_std'] = 0.2
    semanticWM.params['C2']['confidence_threshold'] = 0.0
    semanticWM.params['C2']['prune_threshold'] = 0.01
    semanticWM.params['C2']['coop_weight'] = 0.0
    semanticWM.params['C2']['comp_weight'] = 0.0
    
    grammaticalWM_P.params['dyn']['tau'] = 30.0
    grammaticalWM_P.params['dyn']['act_rest'] = 0.001
    grammaticalWM_P.params['dyn']['k'] = 10.0
    grammaticalWM_P.params['dyn']['noise_mean'] = 0.0
    grammaticalWM_P.params['dyn']['noise_std'] = 0.2
    grammaticalWM_P.params['C2']['confidence_threshold'] = 0.7
    grammaticalWM_P.params['C2']['prune_threshold'] = 0.01
    grammaticalWM_P.params['C2']['coop_weight'] = 1.0
    grammaticalWM_P.params['C2']['comp_weight'] = -1.0
    grammaticalWM_P.params['C2']['sub_threshold_r'] = 0.8
    grammaticalWM_P.params['C2']['deact_weight'] = 0.0
    
    phonWM_P.params['dyn']['tau'] = 100.0
    phonWM_P.params['dyn']['act_rest'] = 0.001
    phonWM_P.params['dyn']['k'] = 10.0
    phonWM_P.params['dyn']['noise_mean'] = 0
    phonWM_P.params['dyn']['noise_std'] = 0.2
    phonWM_P.params['C2']['confidence_threshold'] = 0
    phonWM_P.params['C2']['prune_threshold'] = 0.01
    phonWM_P.params['C2']['coop_weight'] = 0
    phonWM_P.params['C2']['comp_weight'] = 0
    
    conceptLTM.init_act = 1.0
    grammaticalLTM.init_act = grammaticalWM_P.params['C2']['confidence_threshold']*0.5
    
    utter.params['speech_rate'] = 10.0
    
    control.params['task']['mode'] = 'produce'
    control.params['task']['time_pressure'] = 200.0
    control.params['task']['start_produce'] = 200.0
    control.params['style']['activation'] = 0.7
    control.params['style']['sem_length'] = 0.2
    control.params['style']['form_length'] = 0.0
    control.params['style']['continuity'] = 0.1
    
    phonWM_C.params['dyn']['tau'] = 100.0
    phonWM_C.params['dyn']['act_rest'] = 0.001
    phonWM_C.params['dyn']['k'] = 10.0
    phonWM_C.params['dyn']['noise_mean'] = 0.0
    phonWM_C.params['dyn']['noise_std'] = 0.2
    phonWM_C.params['C2']['confidence_threshold'] = 0.0
    phonWM_C.params['C2']['prune_threshold'] = 0.01
    phonWM_C.params['C2']['coop_weight'] = 0.0
    phonWM_C.params['C2']['comp_weight'] = 0.0
    
    grammaticalWM_C.params['dyn']['tau'] = 100.0
    grammaticalWM_C.params['dyn']['act_rest'] = 0.001
    grammaticalWM_C.params['dyn']['k'] = 10.0
    grammaticalWM_C.params['dyn']['noise_mean'] = 0.0
    grammaticalWM_C.params['dyn']['noise_std'] = 0.2
    grammaticalWM_C.params['C2']['confidence_threshold'] = 0.5
    grammaticalWM_C.params['C2']['prune_threshold'] = 0.1
    grammaticalWM_C.params['C2']['coop_weight'] = 1.0
    grammaticalWM_C.params['C2']['comp_weight'] = -1.0
    grammaticalWM_C.params['C2']['sub_threshold_r'] = 0.8
    grammaticalWM_C.params['C2']['deact_weight'] = 0.0
    
    
    # Loading data
    
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return language_system
    
def TCG_description_system(name='description_system',
                           grammar_name='TCG_grammar_VB', 
                           semantics_name = 'TCG_semantics',
                           grammar_path = './data/grammars/',
                           semantics_path = './data/semantics/'):
    """
    Creates and returns the TCG production schema system.
    """
    # Instantiating all the necessary modules schemas
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
    # Creating schema system and adding modules schemas
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
    description_system.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    description_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    description_system.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    description_system.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    description_system.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    description_system.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    
    
    # Defining input and output ports 
    description_system.set_input_ports([subscene_rec.find_port('from_input')])
    description_system.set_output_ports([utter.find_port('to_output'), subscene_rec.find_port('to_output')])
    
    # Setting up schema to brain mappings
    description_brain_mapping = st.BRAIN_MAPPING()
    description_brain_mapping.schema_mapping = brain_mappings
    description_system.brain_mapping = description_brain_mapping
    
    # Parameters
    subscene_rec.params['recognition_time'] = 50
    
    visualWM.params['dyn']['tau'] = 300.0
    visualWM.params['dyn']['act_rest'] = 0.001
    visualWM.params['dyn']['k'] = 10.0
    visualWM.params['dyn']['noise_mean'] = 0.0
    visualWM.params['dyn']['noise_std'] = 1.0
    visualWM.params['C2']['confidence_threshold'] = 0.0
    visualWM.params['C2']['prune_threshold'] = 0.01
    visualWM.params['C2']['coop_weight'] = 0.0
    visualWM.params['C2']['comp_weight'] = 0.0
    
    perceptLTM.init_act = 1.0
    
    semanticWM.params['dyn']['tau'] = 300.0
    semanticWM.params['dyn']['act_rest'] = 0.001
    semanticWM.params['dyn']['k'] = 10.0
    semanticWM.params['dyn']['noise_mean'] = 0.0
    semanticWM.params['dyn']['noise_std'] = 0.2
    semanticWM.params['C2']['confidence_threshold'] = 0.0
    semanticWM.params['C2']['prune_threshold'] = 0.01
    semanticWM.params['C2']['coop_weight'] = 0.0
    semanticWM.params['C2']['comp_weight'] = 0.0
    
    conceptLTM.init_act = 1.0
    
    grammaticalWM_P.params['dyn']['tau'] = 30 # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    grammaticalWM_P.params['dyn']['act_rest'] = 0.001
    grammaticalWM_P.params['dyn']['k'] = 10.0 # Need to analyze the impact of that factor.
    grammaticalWM_P.params['dyn']['noise_mean'] = 0.0
    grammaticalWM_P.params['dyn']['noise_std'] = 0.2
    grammaticalWM_P.params['C2']['confidence_threshold'] = 0.7
    grammaticalWM_P.params['C2']['prune_threshold'] = 0.01 # Manipulations can yield "broca's aphasia" (0.3)
    grammaticalWM_P.params['C2']['coop_weight'] = 1.0
    grammaticalWM_P.params['C2']['comp_weight'] = -4.0 # Needs to compensate for the dominance of cooperation link.
    grammaticalWM_P.params['C2']['sub_threshold_r'] = 0.8
    grammaticalWM_P.params['C2']['deact_weight'] = 0.0 # When set at 1, the output act as if the start_produce always occured right after new sem elements are introduced.
    
    grammaticalLTM.init_act = grammaticalWM_P.params['C2']['confidence_threshold']
    
    phonWM_P.params['dyn']['tau'] = 100.0
    phonWM_P.params['dyn']['act_rest'] = 0.001
    phonWM_P.params['dyn']['k'] = 10.0
    phonWM_P.params['dyn']['noise_mean'] = 0
    phonWM_P.params['dyn']['noise_std'] = 0.2
    phonWM_P.params['C2']['confidence_threshold'] = 0
    phonWM_P.params['C2']['prune_threshold'] = 0.01
    phonWM_P.params['C2']['coop_weight'] = 0
    phonWM_P.params['C2']['comp_weight'] = 0
    
    control.params['task']['mode'] = 'produce'
    control.params['task']['time_pressure'] = 100.0
    control.params['task']['start_produce'] = 500.0
    control.params['style']['activation'] = 1.0
    control.params['style']['sem_length'] = 0.0
    control.params['style']['form_length'] = 0
    control.params['style']['continuity'] = 0
    
    # Loading data
    
    semantics_file = "%s.json" % semantics_name
    my_perceptual_knowledge = TCG_LOADER.load_perceptual_knowledge(semantics_file, semantics_path)
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    
    my_conceptualization = TCG_LOADER.load_conceptualization(semantics_file, semantics_path, my_conceptual_knowledge, my_perceptual_knowledge)
    
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    # Initialize perceptual LTM content
    perceptLTM.initialize(my_perceptual_knowledge)
        
    # Initialize concept LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize conceptualizer
    conceptualizer.initialize(my_conceptualization)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return description_system
    
def TCG_description_system_verbal_guidance(name='description_system_verbal_guidance',
                                           grammar_name='TCG_grammar_VB', 
                                           semantics_name = 'TCG_semantics',
                                           grammar_path = './data/grammars/',
                                           semantics_path = './data/semantics/'):
    """
    Creates and returns the TCG production schema system with verbal guidance.
    """
    
    description_system = TCG_description_system(name, grammar_name, semantics_name, grammar_path, semantics_path)
    semanticWM = description_system.schemas['Semantic_WM']
    visualWM = description_system.schemas['Visual_WM']
    subscene_rec = description_system.schemas['Subscene_recognition']
    description_system.add_connection(semanticWM, 'to_visual_WM', visualWM, 'from_semantic_WM')
    description_system.add_connection(visualWM, 'to_subscene_rec', subscene_rec, 'from_visual_WM')
    
    return description_system
    
def TCG_description_system_saliency(name='description_system_saliency'):
    """
    Creates and returns the TCG production schema system that include a simple saliency map
    """
    description_system = TCG_description_system(name)
    
    # Instantiating all the necessary modules schemas
    simpleSM = ps.SIMPLE_SALIENCY_MAP()
    
    # Defining schema to brain mappings.
    description_system.brain_mapping['Saliency_map'] = ['Dorsal_stream', 'IPS']
    
    # Adding modules schemas
    schemas = [simpleSM] 
    description_system.add_schemas(schemas)
    
    # Defining connections
    visualWM = description_system.schemas['Visual_WM']
    subscene_rec = description_system.schemas['Subscene_recognition']

    description_system.add_connection(simpleSM, 'to_visual_WM', visualWM, 'from_saliency_map')
    description_system.add_connection(visualWM, 'to_saliency_map', simpleSM, 'from_visual_WM')
    description_system.add_connection(simpleSM, 'to_subscene_rec', subscene_rec, 'from_saliency_map')
    
    # Defining input and output ports 
    description_system.input_ports.append(simpleSM.find_port('from_input'))
    
    return description_system

def TCG_SemWM(name='Semantic_WM', 
              semantics_name = 'TCG_semantics',
              semantics_path = './data/semantics/'):
    """
    Test model that only includes the Semantic WM. 
    Note that Control is required to send the "produce" signal.
    """
    
    # Instantiating all the necessary modules schemas
    semanticWM = ls.SEMANTIC_WM()
    conceptLTM = ls.CONCEPT_LTM()
    control = ls.CONTROL()
    
    # Defining schema to brain mappings.    
    mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus']}
    
    # Initializing schema system
    language_system_sem = st.SCHEMA_SYSTEM('Semantic_WM')
    language_schemas = [conceptLTM, semanticWM, control]
    language_system_sem.add_schemas(language_schemas)
    
    # Setting up schema to brain mappings
    brain_mapping = st.BRAIN_MAPPING()
    brain_mapping.schema_mapping = mapping
    language_system_sem.brain_mapping = brain_mapping
    
    # Setting up language schema system.
    language_system_sem.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system_sem.set_input_ports([semanticWM.find_port('from_conceptualizer')])
    language_system_sem.set_output_ports([semanticWM.find_port('to_cxn_retrieval_P')])
        
    # Loading data
    semantics_file = "%s.json" %semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    return language_system_sem

def create_model(model_name):
    """
    """
    possibles = globals().copy()
    function = possibles.get(model_name)
    if not function:
        raise NotImplementedError("model %s not implemented" % model_name)
    model = function()
    return model
        

if __name__ == '__main__':
    production_system = TCG_production_system()
    st.save(production_system)
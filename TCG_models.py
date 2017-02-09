# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Contains functions that can instantiate various TCG models and submodels.
"""
from __future__ import division
import schema_theory as st
import language_schemas as ls
import perceptual_schemas as ps
from loader import TCG_LOADER

GRAMMAR_PATH = './data/grammars/'
GRAMMAR_NAME = 'TCG_grammar_VB_main'
SEMANTICS_PATH = './data/semantics/'
SEMANTICS_NAME = 'TCG_semantics_main'


def parameters(system_names):
    """
    Returns a parameter dictionary containing the path and values for the parameters associated with each system whose name is given in system_names
    Args:
        - system_names ([STR])
    """
    params = {
    'Percept_LTM':{
        'init_act':1.0
        },
        
    'Concept_LTM':{
        'init_act':1.0
        },
        
    'Grammatical_LTM':{
        'init_act':0.3
        },
        
    'Semantic_WM':{
        'dyn.tau':10000.0,
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0,
        'dyn.noise_mean':0.0,
        'dyn.noise_std':1.0,
        'C2.confidence_threshold':0.0,
        'C2.prune_threshold':0.01,
        'C2.coop_weight':0.0,
        'C2.comp_weight':0.0,
        'C2.max_capacity':None
        },
        
    'Conceptualizer':{},
    
    'Cxn_retrieval_P':{},
        
    'Grammatical_WM_P':{
        'dyn.tau':100.0, # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0, # Need to analyze the impact of that factor.
        'dyn.noise_mean':0.0,
        'dyn.noise_std':0.1,
        'C2.confidence_threshold':0.3, #0.7
        'C2.prune_threshold':0.01, #0.01 # Manipulations can yield "broca's aphasia" (0.3)
        'C2.coop_weight':1.0,
        'C2.comp_weight':-10.0, # Needs to compensate for the dominance of cooperation link.
        'C2.coop_asymmetry':1.0,
        'C2.comp_asymmetry':0.0,
        'C2.max_capacity':None,
        'C2.sub_threshold_r':0.8,
        'C2.deact_weight':0.0, # When set at 1, the output act as if the start_produce always occured right after new sem elements are introduced.
        'C2.refractory_period':10
        },
        
    'Phonological_WM_P':{
        'dyn.tau':300.0,
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0,
        'dyn.noise_mean':0.0,
        'dyn.noise_std':1.0,
        'C2.confidence_threshold':0.0,
        'C2.prune_threshold':0.01,
        'C2.coop_weight':0.0,
        'C2.comp_weight':0.0,
        'C2.max_capacity':None
        },
        
    'Utter':{
        'speech_rate':1.0
        },
        
    'Control':{
        'task.mode':'produce',
        'task.time_pressure': 200, #200.0,
        'task.start_produce': 400.0, #400.0,
        'style.activation':0.7, #0.7
        'style.sem_length':0.0, #0.5
        'style.form_length':0.0, #0.0
        'style.continuity':0.3  #0.0
        },
    
    'Phonological_WM_C':{
        'dyn.tau':100.0,
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0,
        'dyn.noise_mean':0.0,
        'dyn.noise_std':1.0,    
        'C2.confidence_threshold':0.0,
        'C2.prune_threshold':0.01,
        'C2.coop_weight':0.0,
        'C2.comp_weight':0.0,
        'C2.max_capacity':None,
        },
    
    'Cxn_retrieval_C':{},
        
    'Grammatical_WM_C':{
        'dyn.tau':100.0, 
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0, 
        'dyn.noise_mean':0.0,
        'dyn.noise_std':1.0, 
        'C2.confidence_threshold':0.6, 
        'C2.prune_threshold':0.01, 
        'C2.coop_weight':1.0,
        'C2.comp_weight':-10.0, 
        'C2.coop_asymmetry':0.0,
        'C2.comp_asymmetry':0.0,
        'C2.max_capacity':None,
        'C2.sub_threshold_r':0.8,
        'C2.deact_weight':0.0,
        'parser.pred_init':['S'],
        'parser.parser_type':'Left-Corner'
        },
        
    'Visual_WM':{
        'dyn.tau':10000.0,
        'dyn.int_weight':1.0,
        'dyn.ext_weight':1.0,
        'dyn.act_rest':0.001,
        'dyn.k':10.0,
        'dyn.noise_mean':0.0,
        'dyn.noise_std':1.0,    
        'C2.confidence_threshold':0.0,
        'C2.prune_threshold':0.01,
        'C2.coop_weight':0.0,
        'C2.comp_weight':0.0,
        'C2.max_capacity':None
        },
        
    'Subscene_recognition':{
        'recognition_time':50
        },
        
    'Scene_perception':{
        'recognition_time':50
        }
    }
    
    system_params = {}
    for system_name in system_names:
        for k,v in params[system_name].iteritems():
            path = '%s.%s' %(system_name, k)
            system_params[path] = v
    return system_params
    
def TCG_production_system(name = 'language_system_P', 
                          grammar_name = GRAMMAR_NAME, 
                          semantics_name = SEMANTICS_NAME,
                          grammar_path = GRAMMAR_PATH,
                          semantics_path = SEMANTICS_PATH):
    """
    Creates and returns the TCG production model.
    """
    # Instantiating all the necessary sysem schemas
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
   
    # Initializing model
    model = st.MODEL(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    model.brain_mapping = language_brain_mapping
    
    # Setting up language model.
    language_schemas = [conceptLTM, semanticWM, grammaticalLTM, cxn_retrieval_P, grammaticalWM_P, phonWM_P, utter, control]

    model.add_schemas(language_schemas)
    
    model.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    model.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    model.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    model.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    model.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    model.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    model.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    model.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    model.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    model.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    
    model.set_input_ports([semanticWM.find_port('from_conceptualizer')])
    model.set_output_ports([utter.find_port('to_output'),phonWM_P.find_port('to_output'), grammaticalWM_P.find_port('to_output'), semanticWM.find_port('to_output')])
    
    # Parameters
    system_names = model.schemas.keys()
    model_params = parameters(system_names)
    model.update_params(model_params)
    
    control.set_mode('produce')
    
    # Loading data
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return model


def TCG_comprehension_system(name = 'language_system_C',
                             grammar_name = GRAMMAR_NAME, 
                             semantics_name = SEMANTICS_NAME,
                             grammar_path = GRAMMAR_PATH,
                             semantics_path = SEMANTICS_PATH):
    """
    Creates and returns the TCG comprehension model.
    """
    # Instantiating all the necessary system schemas
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
    
    # Initializing model
    model = st.MODEL(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    model.brain_mapping = language_brain_mapping
    
    # Setting up language model.
    language_schemas = [grammaticalLTM, cxn_retrieval_C, phonWM_C,  grammaticalWM_C, semanticWM, conceptLTM, control]

    model.add_schemas(language_schemas)
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    model.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    model.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    model.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    model.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    model.add_connection(conceptLTM, 'to_semantic_WM', semanticWM, 'from_concept_LTM')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    model.add_connection(control, 'to_grammatical_WM_C', grammaticalWM_C, 'from_control')
    
    model.set_input_ports([phonWM_C.find_port('from_input')])
    model.set_output_ports([semanticWM.find_port('to_visual_WM')])
    
    # Parameters
    system_names = model.schemas.keys()
    model_params = parameters(system_names)
    model.update_params(model_params)
    
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
    
    return model

def TCG_language_system(name = 'language_system',
                        grammar_name = GRAMMAR_NAME, 
                        semantics_name = SEMANTICS_NAME,
                        grammar_path = GRAMMAR_PATH,
                        semantics_path = SEMANTICS_PATH):
    """
    Creates and returns the TCG language model, including both production and comprehension.
    """
    # Instantiating all the necessary system schemas
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
   
    # Initializing model
    model = st.MODEL(name)
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    model.brain_mapping = language_brain_mapping
    
    # Setting up language model.
    language_schemas = [semanticWM, conceptLTM, grammaticalLTM, cxn_retrieval_P, grammaticalWM_P, phonWM_P, utter, phonWM_C, grammaticalWM_C, cxn_retrieval_C, control]

    model.add_schemas(language_schemas)
    model.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    model.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    model.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    model.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    model.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    model.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    model.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    model.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    model.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    model.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    model.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    model.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    model.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    model.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    model.add_connection(conceptLTM, 'to_semantic_WM', semanticWM, 'from_concept_LTM')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    model.add_connection(control, 'to_grammatical_WM_C', grammaticalWM_C, 'from_control')
    
    model.set_input_ports([phonWM_C.find_port('from_input')])
    model.set_output_ports([utter.find_port('to_output')])
    
    # Parameters
    system_names = model.schemas.keys()
    model_params = parameters(system_names)
    model.update_params(model_params)
    
    # Loading data
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
    
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return model
    
def SALVIA_P(name='SALVIA_P',
           grammar_name = GRAMMAR_NAME, 
           semantics_name = SEMANTICS_NAME,
           grammar_path = GRAMMAR_PATH,
           semantics_path = SEMANTICS_PATH):
    """
    Creates and returns the SALVIA production model.
    """
    # Instantiating all the necessary system schemas
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
                        'Control':['DLPFC']}
                        
    schemas = [subscene_rec, visualWM, perceptLTM, conceptualizer, conceptLTM, grammaticalLTM, cxn_retrieval_P, semanticWM, grammaticalWM_P, phonWM_P, utter, control] 
   
   # Creating model and adding system schemas
    model = st.MODEL(name)
    model.add_schemas(schemas)
    
    # Defining connections
    model.add_connection(subscene_rec, 'to_visual_WM', visualWM, 'from_subscene_rec')
    
    model.add_connection(visualWM, 'to_conceptualizer', conceptualizer, 'from_visual_WM')
    model.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
    model.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
    
    model.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    model.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    model.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    model.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    model.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    model.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    model.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    model.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    model.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    model.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    

    model.set_input_ports([subscene_rec.find_port('from_input')])
    model.set_output_ports([utter.find_port('to_output'), subscene_rec.find_port('to_output')])
    
    # Setting up schema to brain mappings
    description_brain_mapping = st.BRAIN_MAPPING()
    description_brain_mapping.schema_mapping = brain_mappings
    model.brain_mapping = description_brain_mapping
    
    # Parameters
    system_names = model.schemas.keys()
    model_params = parameters(system_names)
    model.update_params(model_params)
    
    grammaticalLTM.init_act = grammaticalWM_P.params['C2']['confidence_threshold']
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
    
    return model
    
def SALVIA_P_verbal_guidance(name='SALVIA_P_verbal_guidance',
                             grammar_name = GRAMMAR_NAME, 
                             semantics_name = SEMANTICS_NAME,
                             grammar_path = GRAMMAR_PATH,
                             semantics_path = SEMANTICS_PATH):
    """
    Creates and returns the SALVIA model with verbal guidance.
    """
    
    model = SALVIA_P(name, grammar_name, semantics_name, grammar_path, semantics_path)
    semanticWM = model.schemas['Semantic_WM']
    visualWM = model.schemas['Visual_WM']
    subscene_rec = model.schemas['Subscene_recognition']
    model.add_connection(semanticWM, 'to_visual_WM', visualWM, 'from_semantic_WM')
    model.add_connection(visualWM, 'to_subscene_rec', subscene_rec, 'from_visual_WM')
    
    return model
    
def SALVIA_P_light(name='SALVIA_P_verbal_guidance',
                   grammar_name = GRAMMAR_NAME, 
                   semantics_name = SEMANTICS_NAME,
                   grammar_path = GRAMMAR_PATH,
                   semantics_path = SEMANTICS_PATH):
    """
    Creates and returns a light version of the SALVIA production model.
    It bypasses the VisualWM and the Conceptualizer
    """
    # Instantiating all the necessary system schemas
    scene_perception = ps.SCENE_PERCEPTION()

    conceptLTM = ls.CONCEPT_LTM()
    
    semanticWM = ls.SEMANTIC_WM()
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    phonWM_P = ls.PHON_WM_P()
    control = ls.CONTROL()
    utter = ls.UTTER()
    
    # Defining schema to brain mappings.
    brain_mappings = {'Scene_perception':['Ventral stream'],
                        'Concept_LTM':[''],
                        'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                        'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                        'Grammatical_LTM':['left_STG', 'left_MTG'],
                        'Cxn_retrieval_P':[], 
                        'Phonological_WM_P':['left_BA6'],
                        'Utter':[''],
                        'Control':['DLPFC']}
                        
    schemas = [scene_perception, conceptLTM, grammaticalLTM, cxn_retrieval_P, semanticWM, grammaticalWM_P, phonWM_P, utter, control] 
   
   # Creating model and adding system schemas
    model = st.MODEL(name)
    model.add_schemas(schemas)
    
    # Defining connections
    model.add_connection(scene_perception, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
    model.add_connection(semanticWM, 'to_visual_WM', scene_perception, 'from_semantic_WM')
    
    model.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    model.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    model.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    model.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    model.add_connection(grammaticalWM_P, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_P')
    model.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    model.add_connection(phonWM_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_phonological_WM_P')
    model.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    model.add_connection(phonWM_P, 'to_utter', utter, 'from_phonological_WM_P')
    model.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    model.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    model.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    

    model.set_input_ports([scene_perception.find_port('from_input')])
    model.set_output_ports([utter.find_port('to_output'), scene_perception.find_port('to_output')])
    
    # Setting up schema to brain mappings
    description_brain_mapping = st.BRAIN_MAPPING()
    description_brain_mapping.schema_mapping = brain_mappings
    model.brain_mapping = description_brain_mapping
    
    # Parameters
    system_names = model.schemas.keys()
    model_params = parameters(system_names)
    model.update_params(model_params)
    
    grammaticalLTM.init_act = grammaticalWM_P.params['C2']['confidence_threshold']
    # Loading data
    
    semantics_file = "%s.json" % semantics_name
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge(semantics_file, semantics_path)
    
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, grammar_path, my_conceptual_knowledge)
        
    # Initialize concept LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
    
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    return model
    
#def SALVIA_P_saliency(name='SALVIA_P_saliency'):
#    """
#    Creates and returns the SALVIA production model that include a simple saliency map
#    """
#    model = SALVIA_P(name)
#    
#    # Instantiating all the necessary system schemas
#    simpleSM = ps.SIMPLE_SALIENCY_MAP()
#    
#    # Defining schema to brain mappings.
#    model.brain_mapping['Saliency_map'] = ['Dorsal_stream', 'IPS']
#    
#    # Adding system schemas
#    schemas = [simpleSM] 
#    model.add_schemas(schemas)
#    
#    # Defining connections
#    visualWM = model.schemas['Visual_WM']
#    subscene_rec = model.schemas['Subscene_recognition']
#
#    model.add_connection(simpleSM, 'to_visual_WM', visualWM, 'from_saliency_map')
#    model.add_connection(visualWM, 'to_saliency_map', simpleSM, 'from_visual_WM')
#    model.add_connection(simpleSM, 'to_subscene_rec', subscene_rec, 'from_saliency_map')
#    
#    # Defining input and output ports 
#    model.input_ports.append(simpleSM.find_port('from_input'))
#    
#    return model


#def create_model(model_name):
#    """
#    For now does not handle inputs... not used
#    """
#    possibles = globals().copy()
#    function = possibles.get(model_name)
#    if not function:
#        raise NotImplementedError("model %s not implemented" % model_name)
#    model = function()
#    return model
        

if __name__ == '__main__':
    model = TCG_language_system()
    model.system2dot(image_type='png', disp=True)
#    st.save(production_system)
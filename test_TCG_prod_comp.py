# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for a system that incoporates production and comprehension
"""
def test(seed=None):
    import random
    import numpy as np
    import schema_theory as st
    import language_schemas as ls
    import loader as ld
    
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    # Instantiating all the necessary procedural schemas
    semanticWM = ls.SEMANTIC_WM()
    conceptLTM = ls.CONCEPT_LTM()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    grammaticalWM_C = ls.GRAMMATICAL_WM_C()
    cxn_retrieval_C = ls.CXN_RETRIEVAL_C()
    phonWM_P = ls.PHON_WM_P()
    phonWM_C = ls.PHON_WM_C()
    control = ls.CONTROL()
    
    
    # Defining schema to brain mappings.
    language_mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_P':[], 
                    'Phonological_WM_P':['left_BA6'],
                    'Cxn_retrieval_C':[], 
                    'Phonological_WM_C':['Wernicke'],
                    'Grammatical_WM_C':['lBA44, lBA45'],
                    'Control':['DLPFC'],
                    'Concept_LTM':['']}
   
   # Initializing schema system
    language_system = st.SCHEMA_SYSTEM('language_system')
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [semanticWM, conceptLTM, grammaticalLTM, cxn_retrieval_P, grammaticalWM_P, phonWM_P, phonWM_C, grammaticalWM_C, cxn_retrieval_C, control]

    language_system.add_schemas(language_schemas)
    language_system.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    language_system.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    language_system.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    language_system.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    language_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    language_system.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    language_system.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    language_system.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    language_system.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    language_system.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    language_system.add_connection(conceptLTM, 'to_semantic_WM', semanticWM, 'from_concept_LTM')
    language_system.set_input_ports([phonWM_C.find_port('from_input')])
    language_system.set_output_ports([phonWM_P.find_port('to_output')])
    
    # Display schema system
    language_system.system2dot(image_type='png', disp=True)
    
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
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.5
    grammaticalWM_P.C2_params['prune_threshold'] = 0.01
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -1
    
    conceptLTM.init_act = 1
    grammaticalLTM.init_act = grammaticalWM_P.C2_params['confidence_threshold']*0.5
    
    control.task_params['time_pressure'] = 600
    
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
   
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    option = 3
    control.set_mode('listen')
    
    prod_rate = 10
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    
    lang_input = lang_inputs[option]
    lang_input.reverse()
    max_time = 1000
    flag = True
    
    for t in range(max_time):
        if t>10 and np.mod(t, prod_rate) == 0 and lang_input: # Need some time to have the system set up before it receives the first input.
            word_form = lang_input.pop()
            print 't: %i, receive: %s' %(t, word_form)
            language_system.set_input(word_form)
        language_system.update()
        if semanticWM.schema_insts and flag: #Switching from comprehension to production
            semanticWM.show_SemRep()
            control.set_mode('produce')
            flag = False
        output = language_system.get_output()
        if output[0]:
            print output[0]     
    
    grammaticalWM_P.show_dynamics()
    grammaticalWM_C.show_dynamics()

if __name__=='__main__':
    test(seed=None)
        




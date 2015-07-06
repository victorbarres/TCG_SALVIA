# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the comprehensoin language schemas defined in language_schemas.py
"""
def test(seed=None):
    import random
    import schema_theory as st
    import language_schemas as ls
    import loader as ld
    
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    # Instantiating all the necessary procedural schemas
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_C = ls.CXN_RETRIEVAL_C()
    phonWM_C = ls.PHON_WM_C()
    
    # Defining schema to brain mappings.
    language_mapping = {'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_C':[], 
                    'Phonological_WM_C':['Wernicke'],}
   
   # Initializing schema system
    language_system = st.SCHEMA_SYSTEM('Language_system')
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [grammaticalLTM, cxn_retrieval_C, phonWM_C]

    language_system.add_schemas(language_schemas)
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    language_system.add_connection(phonWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_phonological_WM_C')
    language_system.set_input_ports([phonWM_C._find_port('from_input')])
    language_system.set_output_ports([phonWM_C._find_port('to_grammatical_WM_C')])
    
    # Display schema system
#    language_system.system2dot(image_type='png', disp=True)
    
    # Parameters
    phonWM_C.dyn_params['tau'] = 2
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
    grammaticalLTM.init_act = 1
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
   
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    lang_input = {1:'a', 2:'woman', 3:'kick', 4:'a', 5:'man'}
#    
    max_time = 10
    for step in range(max_time):
        if step in lang_input:
            word_form = lang_input[step]
            print 't: %i, receive: %s' %(step, word_form)
            language_system.set_input(word_form)
        language_system.update()
    
    print phonWM_C.show_dynamics()


if __name__=='__main__':
    test(seed=None)
        




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
    import viewer
    
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    # Instantiating all the necessary procedural schemas
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_C = ls.CXN_RETRIEVAL_C()
    phonWM_C = ls.PHON_WM_C()
    grammaticalWM_C = ls.GRAMMATICAL_WM_C()
    semanticWM = ls.SEMANTIC_WM()
    
    # Defining schema to brain mappings.
    language_mapping = {'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_C':[], 
                    'Phonological_WM_C':['Wernicke'],
                    'Grammatical_WM_C':['lBA44, lBA45'],
                    'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus']}
   
   # Initializing schema system
    language_system_C = st.SCHEMA_SYSTEM('language_system_C')
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system_C.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [grammaticalLTM, cxn_retrieval_C, phonWM_C,  grammaticalWM_C, semanticWM]

    language_system_C.add_schemas(language_schemas)
    language_system_C.add_connection(grammaticalLTM, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_LTM')
    language_system_C.add_connection(phonWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_phonological_WM_C')
    language_system_C.add_connection(phonWM_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_phonological_WM_C')
    language_system_C.add_connection(grammaticalWM_C, 'to_cxn_retrieval_C', cxn_retrieval_C, 'from_grammatical_WM_C')
    language_system_C.add_connection(cxn_retrieval_C, 'to_grammatical_WM_C', grammaticalWM_C, 'from_cxn_retrieval_C')
    language_system_C.add_connection(grammaticalWM_C, 'to_semantic_WM', semanticWM, 'from_grammatical_WM_C')
    language_system_C.set_input_ports([phonWM_C.find_port('from_input')])
    language_system_C.set_output_ports([phonWM_C.find_port('to_grammatical_WM_C')])
    
    # Display schema system
    language_system_C.system2dot(image_type='png', disp=True)
    
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
    grammaticalWM_C.C2_params['confidence_threshold'] = 0.2
    grammaticalWM_C.C2_params['prune_threshold'] = 0.1
    grammaticalWM_C.C2_params['coop_weight'] = 1
    grammaticalWM_C.C2_params['comp_weight'] = -1
    
    grammaticalLTM.init_act = grammaticalWM_C.C2_params['confidence_threshold']

    
    # Loading data
    grammar_name = 'TCG_grammar_VB_singlehead'
   
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    option = 2
    
    lang_inputs = {}
    lang_inputs[1] = {1:'a', 10:'woman', 20:'kick', 30:'a', 50:'man', 60:'in', 70:'blue'}
    lang_inputs[2] = {1:'a', 10:'woman', 20:'kick', 30:'a', 50:'man', 60:'in', 65: 'a', 70:'blue', 80:'boxing ring'}
    lang_inputs[3] = {1:'a', 10:'woman', 13:'who', 14:'is', 15:'pretty', 20:'kick', 30:'a', 50:'man', 60:'in', 70:'blue'}
    lang_inputs[4] = {1:'a', 10:'woman', 20:'laugh', 60:'kick', 70:'a', 75:'man', 80:'in', 85:'blue'}
    
    lang_input = lang_inputs[option]
    max_time = 500
    for step in range(max_time):
        if step in lang_input:
            word_form = lang_input[step]
            print 't: %i, receive: %s' %(step, word_form)
            language_system_C.set_input(word_form)
        language_system_C.update()
    
#    phonWM_C.show_dynamics()
#    grammaticalWM_C.show_dynamics()
#    grammaticalWM_C.show_state()
    
    assemblages = grammaticalWM_C.assemble()
    assemblage = assemblages[0]
    inst  = ls.GRAMMATICAL_WM_C.assemblage2inst(assemblage)
    viewer.TCG_VIEWER.display_cxn(inst.content)

if __name__=='__main__':
    test(seed=None)
        




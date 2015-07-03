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
    language_system.set_output_ports([cxn_retrieval_C._find_port('to_grammatical_WM_C')])
    
    # Display schema system
#    language_system.system2dot(image_type='png', disp=True)
    
    # Parameters   
    grammaticalLTM.init_act = 1
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
   
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    lang_input = ['a', 'woman', 'kick', 'a', 'man']
    language_system.set_input(lang_input)
    
    max_time = 2
    for step in range(max_time):
        language_system.update()


if __name__=='__main__':
    test(seed=None)
        




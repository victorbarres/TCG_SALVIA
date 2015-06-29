# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language schemas defined in language_schemas.py
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
    conceptualizer = ls.CONCEPTUALIZER()
    grammaticalWM = ls.GRAMMATICAL_WM()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval = ls.CXN_RETRIEVAL()
    semanticWM = ls.SEMANTIC_WM()
    phonWM = ls.PHON_WM()
    control = ls.CONTROL()
    conceptLTM = ls.CONCEPT_LTM()
    
    # Defining schema to brain mappings.
    language_mapping = {'Conceptualizer':['aTP'], 
                    'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval':[], 
                    'Phonological_WM':['left_BA6'],
                    'Control':['DLPFC'], 'Concept_LTM':['']}
   
   # Initializing schema system
    language_system = st.SCHEMA_SYSTEM('Language_system')
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [conceptualizer, grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM, control, conceptLTM]

    language_system.add_schemas(language_schemas)
    language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
    language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
    language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
    language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
    language_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system.add_connection(phonWM, 'to_control', control, 'from_phonological_WM')
    language_system.add_connection(control, 'to_grammatical_WM', grammaticalWM, 'from_control')
    language_system.add_connection(conceptLTM, 'to_conceptualizer', conceptualizer, 'from_concept_LTM')
    language_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
    
    language_system.set_input_ports([conceptualizer._find_port('from_visual_WM')])
    language_system.set_output_ports([phonWM._find_port('to_output')])
    
#    language_system.system2dot(image_type='png', disp=True)
    
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
    
    control.task_params['time_pressure'] = 150
    
    conceptLTM.init_act = 1
    grammaticalLTM.init_act = grammaticalWM.C2_params['confidence_threshold']
    
    # Loading data
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_grammar = ld.load_grammar("TCG_grammar_VB.json", "./data/grammars/", my_conceptual_knowledge)
    
    # Initialize conceptual LTM content
    conceptLTM.initialize(my_conceptual_knowledge)
        
    # Initialize grammatical LTM content
    grammaticalLTM.initialize(my_grammar)
    
    # Semantic WM content using predefined cpt_schema_instances.
    man_cpt_schema = conceptLTM.find_schema(name='MAN')
    woman_cpt_schema = conceptLTM.find_schema(name='WOMAN')
    kick_cpt_schema = conceptLTM.find_schema(name='KICK')
    pretty_cpt_schema = conceptLTM.find_schema(name='PRETTY')
    big_cpt_schema = conceptLTM.find_schema(name='BIG')
    agent_cpt_schema = conceptLTM.find_schema(name='AGENT')
    patient_cpt_schema = conceptLTM.find_schema(name='PATIENT')
    modify_cpt_schema = conceptLTM.find_schema(name='MODIFY')
    
    man1 = ls.CPT_SCHEMA_INST(man_cpt_schema, trace={'per_inst':None, 'cpt_schema':man_cpt_schema})
    woman1 = ls.CPT_SCHEMA_INST(woman_cpt_schema, trace={'per_inst':None, 'cpt_schema':woman_cpt_schema})
    kick1 = ls.CPT_SCHEMA_INST(kick_cpt_schema, trace={'per_inst':None, 'cpt_schema':kick_cpt_schema})
    pretty1 = ls.CPT_SCHEMA_INST(pretty_cpt_schema, trace={'per_inst':None, 'cpt_schema':pretty_cpt_schema})
    big1 = ls.CPT_SCHEMA_INST(big_cpt_schema, trace={'per_inst':None, 'cpt_schema':big_cpt_schema})
    
    agent1 = ls.CPT_SCHEMA_INST(agent_cpt_schema, trace={'per_inst':None, 'cpt_schema':agent_cpt_schema})
    agent1.content['pFrom'] = kick1
    agent1.content['pTo'] = woman1
    patient1 = ls.CPT_SCHEMA_INST(patient_cpt_schema, trace={'per_inst':None, 'cpt_schema':patient_cpt_schema})
    patient1.content['pFrom'] = kick1
    patient1.content['pTo'] = man1
    modify1 = ls.CPT_SCHEMA_INST(modify_cpt_schema, trace={'per_inst':None, 'cpt_schema':modify_cpt_schema})
    modify1.content['pFrom'] = pretty1
    modify1.content['pTo'] = woman1
    modify2 = ls.CPT_SCHEMA_INST(modify_cpt_schema, trace={'per_inst':None, 'cpt_schema':modify_cpt_schema})
    modify2.content['pFrom'] = big1
    modify2.content['pTo'] = man1

    # Timing options:
    # Define at which time the schema instances should be invoked in semantic working memory
    # Bypasses the conceptualizer bv directly setting it's output to semantic_WM.
    sem_timing_1 = {100:[woman1]}
    sem_timing_2 = {100:[woman1, modify1, pretty1]}
    sem_timing_3 = {100:[woman1, kick1, man1, agent1, patient1]}
    sem_timing_4 = {100:[woman1, modify1, pretty1, kick1, agent1, patient1, man1, big1, modify2]}
    sem_timing_5 = {100:[woman1, modify1, pretty1, man1, big1, modify2]} # SemRep contains to unconnected subgraphs.
    
    sem_timing_6 = {100:[woman1], 200:[modify1, pretty1]}
    
    sem_timing_7 = {100:[woman1], 200:[modify1, pretty1], 300: [kick1],  400:[agent1, patient1, man1], 500:[big1, modify2]}
    sem_timing_8 = {100:[man1], 200:[kick1, woman1, agent1, patient1], 300:[modify1, pretty1], 400:[big1, modify2]}
    sem_timing_9 = {100:[man1], 200:[kick1, woman1, agent1, patient1], 300:[big1, modify2], 400:[modify1, pretty1]} # NOTE HOW THE FACT THAT 'big' + 'mod2' are introduced right after the TRA tends to favor man first utterances compared to the previous case.
    
    sem_timing_10 = {10:[woman1], 300:[modify1, pretty1], 500: [kick1],  700:[agent1, patient1, man1], 900:[big1, modify2]}    
    
    sem_timing_11 = {100:[woman1, modify1, pretty1], 200:[man1, big1, modify2], 300:[kick1], 400:[agent1, patient1]}
    
    sem_timing = sem_timing_2
    
    end_delay = 500
    max_time = max([time for time in sem_timing.keys()])
    max_time += end_delay
    for step in range(max_time):
        if step in sem_timing:
            for inst in sem_timing[step]:
                print "time:%i, sem:%s" %(step, inst.name)
            conceptualizer.set_output('to_semantic_WM', sem_timing[step])
            semanticWM.set_output('to_control', True)
        language_system.update()
    
    semanticWM.show_dynamics(c2_levels=False)
    grammaticalWM.show_dynamics()
    grammaticalWM.show_state()

if __name__=='__main__':
    test(seed=None)
        




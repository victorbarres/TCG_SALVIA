# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language production schemas defined in language_schemas.py
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
    grammaticalWM_P = ls.GRAMMATICAL_WM_P()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval_P = ls.CXN_RETRIEVAL_P()
    semanticWM = ls.SEMANTIC_WM()
    phonWM_P = ls.PHON_WM_P()
    control = ls.CONTROL()
    conceptLTM = ls.CONCEPT_LTM()
    
    # Defining schema to brain mappings.
    language_mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM_P':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval_P':[], 
                    'Phonological_WM_P':['left_BA6'],
                    'Control':['DLPFC'], 'Concept_LTM':['']}
   
   # Initializing schema system
    language_system_P = st.SCHEMA_SYSTEM('language_system_P')
    
    # Setting up schema to brain mappings
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system_P.brain_mapping = language_brain_mapping
    
    # Setting up language schema system.
    language_schemas = [grammaticalLTM, cxn_retrieval_P, semanticWM, grammaticalWM_P, phonWM_P, control]

    language_system_P.add_schemas(language_schemas)
    language_system_P.add_connection(semanticWM,'to_cxn_retrieval_P', cxn_retrieval_P, 'from_semantic_WM')
    language_system_P.add_connection(grammaticalLTM, 'to_cxn_retrieval_P', cxn_retrieval_P, 'from_grammatical_LTM')
    language_system_P.add_connection(cxn_retrieval_P, 'to_grammatical_WM_P', grammaticalWM_P, 'from_cxn_retrieval_P')
    language_system_P.add_connection(semanticWM, 'to_grammatical_WM_P', grammaticalWM_P, 'from_semantic_WM')
    language_system_P.add_connection(grammaticalWM_P, 'to_phonological_WM_P', phonWM_P, 'from_grammatical_WM_P')
    language_system_P.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
    language_system_P.add_connection(phonWM_P, 'to_control', control, 'from_phonological_WM_P')
    language_system_P.add_connection(control, 'to_grammatical_WM_P', grammaticalWM_P, 'from_control')
    language_system_P.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
    language_system_P.set_input_ports([semanticWM.find_port('from_conceptualizer')])
    language_system_P.set_output_ports([phonWM_P.find_port('to_output')])
    
    # Display schema system
    language_system_P.system2dot(image_type='png', disp=True)
    
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
    
    grammaticalWM_P.C2_params['confidence_threshold'] = 0.2
    grammaticalWM_P.C2_params['prune_threshold'] = 0.1
    grammaticalWM_P.C2_params['coop_weight'] = 1
    grammaticalWM_P.C2_params['comp_weight'] = -1
    
    control.task_params['mode'] = 'produce'
    control.task_params['time_pressure'] = 500
    
    conceptLTM.init_act = 1
    grammaticalLTM.init_act = grammaticalWM_P.C2_params['confidence_threshold']
    
    # Loading data
    grammar_name = 'TCG_grammar_VB'
   
    my_conceptual_knowledge = ld.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = ld.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
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
    blue_cpt_schema = conceptLTM.find_schema(name='BLUE')
    wear_cpt_schema = conceptLTM.find_schema(name='WEAR')
    dress_cpt_schema = conceptLTM.find_schema(name='DRESS')
    
    man1 = ls.CPT_SCHEMA_INST(man_cpt_schema, trace={'per_inst':None, 'cpt_schema':man_cpt_schema})
    woman1 = ls.CPT_SCHEMA_INST(woman_cpt_schema, trace={'per_inst':None, 'cpt_schema':woman_cpt_schema})
    kick1 = ls.CPT_SCHEMA_INST(kick_cpt_schema, trace={'per_inst':None, 'cpt_schema':kick_cpt_schema})
    pretty1 = ls.CPT_SCHEMA_INST(pretty_cpt_schema, trace={'per_inst':None, 'cpt_schema':pretty_cpt_schema})
    big1 = ls.CPT_SCHEMA_INST(big_cpt_schema, trace={'per_inst':None, 'cpt_schema':big_cpt_schema})
    blue1 = ls.CPT_SCHEMA_INST(blue_cpt_schema, trace={'per_inst':None, 'cpt_schema':blue_cpt_schema})
    wear1 = ls.CPT_SCHEMA_INST(wear_cpt_schema, trace={'per_inst':None, 'cpt_schema':blue_cpt_schema})
    dress1 = ls.CPT_SCHEMA_INST(dress_cpt_schema, trace={'per_inst':None, 'cpt_schema':blue_cpt_schema})
    
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
    
    agent2 = ls.CPT_SCHEMA_INST(agent_cpt_schema, trace={'per_inst':None, 'cpt_schema':agent_cpt_schema})
    agent2.content['pFrom'] = wear1
    agent2.content['pTo'] = woman1
    patient2 = ls.CPT_SCHEMA_INST(patient_cpt_schema, trace={'per_inst':None, 'cpt_schema':patient_cpt_schema})
    patient2.content['pFrom'] = wear1
    patient2.content['pTo'] = dress1
    
    modify3 = ls.CPT_SCHEMA_INST(modify_cpt_schema, trace={'per_inst':None, 'cpt_schema':modify_cpt_schema})
    modify3.content['pFrom'] = blue1
    modify3.content['pTo'] = dress1

    # Timing options:
    # Define at which time the schema instances should be invoked in semantic working memory
    # Bypasses the conceptualizer bv directly setting it's output to semantic_WM.

    sem_option = 11
    end_delay = 500
    
    sem_timings = {}
    sem_timings[1] = {100:[woman1]}
    sem_timings[2] = {100:[woman1, modify1, pretty1]}
    sem_timings[3] = {100:[woman1, kick1, man1, agent1, patient1]}
    sem_timings[4] = {100:[woman1, modify1, pretty1, kick1, agent1, patient1, man1, big1, modify2]}
    sem_timings[5] = {100:[woman1, modify1, pretty1, man1, big1, modify2]} # SemRep contains two unconnected subgraphs.
    
    sem_timings[6] = {100:[woman1], 200:[modify1, pretty1]}
    
    sem_timings[7] = {100:[woman1], 200:[modify1, pretty1], 300: [kick1],  400:[agent1, patient1, man1], 500:[big1, modify2]}
    sem_timings[8] = {100:[man1], 200:[kick1, woman1, agent1, patient1], 300:[modify1, pretty1], 400:[big1, modify2]}
    sem_timings[9] = {100:[man1], 200:[kick1, woman1, agent1, patient1], 300:[big1, modify2], 400:[modify1, pretty1]} # NOTE HOW THE FACT THAT 'big' + 'mod2' are introduced right after the TRA tends to favor man first utterances compared to the previous case.(without time pressure)
    
    sem_timings[10] = {10:[woman1], 300:[modify1, pretty1], 500: [kick1],  700:[agent1, patient1, man1], 900:[big1, modify2]}    
    
    sem_timings[11] = {100:[woman1, modify1, pretty1], 200:[man1, big1, modify2], 300:[kick1], 400:[agent1, patient1]}
    
    sem_timings[12] = {100:[woman1, wear1, agent2, patient2, dress1, blue1, modify3, kick1, agent1, patient1, man1]} # Test IN_COLOR
    
    sem_timing = sem_timings[sem_option]
    
    max_time = max([time for time in sem_timing.keys()])
    max_time += end_delay
    for step in range(max_time):
        if step in sem_timing:
            for inst in sem_timing[step]:
                print "time:%i, sem:%s" %(step, inst.name)
            language_system_P.set_input(sem_timing[step])
            semanticWM.set_output('to_control', True)
        language_system_P.update()
        output = language_system_P.get_output()
        if output[0]:
            print output[0]
    
#    semanticWM.show_dynamics(c2_levels=False)
    grammaticalWM_P.show_dynamics(c2_levels=False)
    grammaticalWM_P.show_state()
#    language_system_P.save_sim('./tmp/test_language_output.json')

if __name__=='__main__':
    test(seed=None)
        




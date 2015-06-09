# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language schemas defined in language_schemas.py
"""
def test(seed=None):
    import random
    import schema_theory as st
    import language_schemas as ls
    import concept as cpt
    import loader as ld
    import viewer
    
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    conceptualizer = ls.CONCEPTUALIZER()
    grammaticalWM = ls.GRAMMATICAL_WM()
    grammaticalLTM = ls.GRAMMATICAL_LTM()
    cxn_retrieval = ls.CXN_RETRIEVAL()
    semanticWM = ls.SEMANTIC_WM()
    phonWM = ls.PHON_WM()
    control = ls.CONTROL()
    
    language_mapping = {'Conceptualizer':[], 
                    'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                    'Grammatical_WM':['left_BA45', 'leftBA44'], 
                    'Grammatical_LTM':['left_STG', 'left_MTG'],
                    'Cxn_retrieval':[], 
                    'Phonological_WM':['left_BA6'],
                    'Control':['DLPFC']}
    
    language_system = st.SCHEMA_SYSTEM('Language_system')
    
    language_brain_mapping = st.BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    prompt =  "1: TEST BUILD LANGUAGE SYSTEM; 2: TEST GRAMMATICAL WM; 3: TEST CXN RETRIEVAL; 4: TEST STATIC SEMREP; 5: TEST STATIC SEMREP (FULL GRAMMAR + TEXT2SPEECH); 6: TEST INCREMENTAL SEMREP; 7: TEST INCREMENTAL + CONTROL"
    print prompt
    case = raw_input("ENTER CASE #: ")
    while case not in ['1','2','3','4','5', '6', '7']:
        print "INVALID CHOICE"
        print prompt
        case = raw_input("ENTER CASE #: ")
        
    if case == '1':
        ###########################################################################
        ### TEST BUILD LANGUAGE SYSTEM ###
        language_schemas = [conceptualizer, grammaticalWM, grammaticalLTM, cxn_retrieval, semanticWM, phonWM]
        
        language_system.add_schemas(language_schemas)
        
        language_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([conceptualizer._find_port('from_visual_WM')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
        language_system.system2dot()
    
    elif case == '2':
        ###########################################################################
        ### TEST GRAMMATICAL WM 1 ###
        
        # Load grammar
        my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
        
        # Set up grammatical LTM content
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, random.random())
            grammaticalLTM.add_schema(new_cxn_schema)
            
        # Select random cxn
        WM_size = 10
        idx = [random.randint(0,len(grammaticalLTM.schemas)-1) for i in range(WM_size)]
        
        # Instaniate constructions in WM
        for i in idx:
            cxn_inst = ls.CXN_SCHEMA_INST(grammaticalLTM.schemas[i], trace=None, mapping=None)
            grammaticalWM.add_instance(cxn_inst, act0=grammaticalLTM.schemas[i].init_act)
        
        # Run WM
        max_step = 1000
        for step in range(max_step):
            grammaticalWM.update_activations()
        
        grammaticalWM.show_dynamics()
    
    elif case == '3': 
        ###########################################################################
        ### TEST CXN RETRIEVAL ###
        
        my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        # Set up grammatical LTM content
        act0 = 1
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, act0)
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        
        entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
        
    
        # Set up Semantic WM content
        semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt, new=True)
        semanticWM.SemRep.add_node("KICK", concept=kick_cpt, new=True)
        semanticWM.SemRep.add_node("MAN", concept=man_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt, new=True)
        
        semanticWM.show_state()
        
        viewer.TCG_VIEWER.display_semrep(semanticWM.SemRep)
        
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM]
        
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([cxn_retrieval._find_port('to_grammatical_WM')])
        
        def print_output(value):
            if value:
                print [v["cxn_inst"].name for v in cxn_retrieval.out_ports[0].value]
            else:
                print "NOTHING!"
        
        print_output(cxn_retrieval.out_ports[0].value)
        cxn_retrieval.out_ports[0].value = None
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)
        cxn_retrieval.out_ports[0].value = None
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)
        cxn_retrieval.out_ports[0].value = None
        semanticWM.SemRep.clear()
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)
    
    elif case == '4':
        ###########################################################################
        ### TEST STATIC SEMREP###
        my_grammar = ld.load_grammar("TCG_grammar_light.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        # Set up grammatical LTM content
        act0 = 0.6
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, 0.2), grammaticalWM.C2_params['prune_threshold']))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")
        
        entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
        
    
        # Set up Semantic WM content
        semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt, new=True)
        semanticWM.SemRep.add_node("KICK", concept=kick_cpt, new=True)
        semanticWM.SemRep.add_node("MAN", concept=man_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt, new=True)
        
        # A bit more info
        semanticWM.SemRep.add_node("BLUE", concept=blue_cpt, new=True)
        semanticWM.SemRep.add_edge("BLUE", "WOMAN", concept=modify_cpt, new=True)
        
    
        semanticWM.show_state()
                
        
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM]
        
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
    
        language_system.update()
        language_system.update()
    #        semanticWM.SemRep.clear()
        language_system.update()
        language_system.update()
        language_system.update()
        grammaticalWM.show_state()
        
        max_step = 1000
        for step in range(max_step):
            language_system.update()
            if language_system.outputs['Phonological_WM:14']:
                print language_system.outputs['Phonological_WM:14']
            
        grammaticalWM.show_dynamics()
     
    elif case == '5':
        ###########################################################################
        ### TEST STATIC SEMREP FULL GRAMMAR + TEXT2SPEECH ###
        my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        # Set up grammatical LTM content
        act0 = 0.6
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, 0.2), grammaticalWM.C2_params['prune_threshold']))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        big_cpt = cpt.CONCEPT(name="BIG", meaning="BIG")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")        
    
        # Set up Semantic WM content
        semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt, new=True)
        semanticWM.SemRep.add_node("KICK", concept=kick_cpt, new=True)
        semanticWM.SemRep.add_node("MAN", concept=man_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt, new=True)
        semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt, new=True)
        semanticWM.SemRep.add_node("BLUE", concept=blue_cpt, new=True)
        semanticWM.SemRep.add_node("BIG", concept=big_cpt, new=True) 
        semanticWM.SemRep.add_edge("BLUE", "WOMAN", concept=modify_cpt, new=True)
        semanticWM.SemRep.add_edge("BIG", "MAN", concept=modify_cpt, new=True)
            
        semanticWM.show_state()
                
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM]
        
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
    
        language_system.update()
        language_system.update()
        semanticWM.SemRep.clear()
        language_system.update()
        language_system.update()
        language_system.update()
        grammaticalWM.show_state()
        
        # Set up text2speech
        text2speech = ls.TEXT2SPEECH(rate_percent=80)
        max_step = 1000
        for step in range(max_step):
            language_system.update()
            if language_system.outputs['Phonological_WM:14']:
                output =  language_system.outputs['Phonological_WM:14']
                print output
    #                text2speech.utterance = ' '.join(output)
    #                text2speech.utter()
            
        grammaticalWM.show_dynamics()
    
    elif case == '6':
        ###############################
        ### TEST INCREMENTAL SEMREP ###
        my_grammar = ld.load_grammar("TCG_grammar_VB_light.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        
        # Parameters
        act0 = 0.1
        act_var = 0
        grammaticalWM.dyn_params['tau'] = 30
        grammaticalWM.C2_params['prune_threshold'] = 0.01
        grammaticalWM.C2_params['comp_weight'] = -1
        
        # Set up grammatical LTM content
        
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, act_var), grammaticalWM.C2_params['prune_threshold']))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        big_cpt = cpt.CONCEPT(name="BIG", meaning="BIG")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")
        entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
        
    
        # Set up Semantic WM content
        sem_info = {'woman':('node', 'WOMAN', woman_cpt), 'kick':('node', 'KICK', kick_cpt), 'man':('node', 'MAN', man_cpt), 
                    'agt':('edge', ('KICK', 'WOMAN'), agent_cpt), 'pt':('edge', ('KICK', 'MAN'), patient_cpt), 'pt2':('edge', ('KICK', 'ENTITY'), patient_cpt),
                    'blue':('node', 'BLUE', blue_cpt), 'big':('node', 'BIG', big_cpt), 
                    'mod1':('edge', ('BLUE', 'WOMAN'), modify_cpt), 'mod2':('edge', ('BIG', 'MAN'), modify_cpt),
                    'entity':('node', 'ENTITY', entity_cpt)}
        
        # Timing options
        sem_timing_1 = {100:['woman'], 200:['mod1', 'blue'], 300: ['kick'],  400:['agt', 'pt', 'man'], 500:['big', 'mod2']}
        sem_timing_2 = {100:['woman'], 200:['mod1', 'blue']}
        sem_timing_3 = {100:['woman','mod1', 'blue', 'kick', 'agt', 'pt', 'man','big', 'mod2']}
        sem_timing_4 = {100:['woman','mod1', 'blue']}
        sem_timing_5 = {100:['woman','kick', 'man', 'agt', 'pt']}
        sem_timing_6 = {100:['woman']}
        
        sem_timing = sem_timing_1
                        
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM]
        
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
    
        
        max_step = 1000
        for step in range(max_step):
            if step in sem_timing:
                for s in sem_timing[step]:
                    print "time:%i, sem:%s" %(step, s)
                    info = sem_info[s]
                    if info[0]=='node':
                        semanticWM.SemRep.add_node(info[1], concept=info[2], new=True)
                    else:
                        semanticWM.SemRep.add_edge(info[1][0], info[1][1], concept=info[2], new=True)
    #                semanticWM.show_state()
            language_system.update()
            if language_system.outputs['Phonological_WM:14']:
                print language_system.outputs['Phonological_WM:14']
            
        grammaticalWM.show_dynamics()
        
    elif case == '7':
        ###############################################
        ### TEST INCREMENTAL SEMREP with CONTROL ######
        my_grammar = ld.load_grammar("TCG_grammar_VB_light.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        
        # Parameters
        act0 = 0.1
        act_var = 0
        grammaticalWM.dyn_params['tau'] = 30
        grammaticalWM.C2_params['prune_threshold'] = 0.01
        grammaticalWM.C2_params['comp_weight'] = -1
        
        # Set up grammatical LTM content
        
        for cxn in my_grammar.constructions:
            new_cxn_schema = ls.CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, act_var), grammaticalWM.C2_params['prune_threshold']))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        big_cpt = cpt.CONCEPT(name="BIG", meaning="BIG")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")
        entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
        
    
        # Set up Semantic WM content
        sem_info = {'woman':('node', 'WOMAN', woman_cpt), 'kick':('node', 'KICK', kick_cpt), 'man':('node', 'MAN', man_cpt), 
                    'agt':('edge', ('KICK', 'WOMAN'), agent_cpt), 'pt':('edge', ('KICK', 'MAN'), patient_cpt), 'pt2':('edge', ('KICK', 'ENTITY'), patient_cpt),
                    'blue':('node', 'BLUE', blue_cpt), 'big':('node', 'BIG', big_cpt), 
                    'mod1':('edge', ('BLUE', 'WOMAN'), modify_cpt), 'mod2':('edge', ('BIG', 'MAN'), modify_cpt),
                    'entity':('node', 'ENTITY', entity_cpt)}
        
        # Timing options
        sem_timing_1 = {100:['woman'], 200:['mod1', 'blue'], 300: ['kick'],  400:['agt', 'pt', 'man'], 500:['big', 'mod2']}
        sem_timing_2 = {100:['woman'], 200:['mod1', 'blue']}
        sem_timing_3 = {100:['woman','mod1', 'blue', 'kick', 'agt', 'pt', 'man','big', 'mod2']}
        sem_timing_4 = {100:['woman','mod1', 'blue']}
        sem_timing_5 = {100:['woman','kick', 'man', 'agt', 'pt']}
        sem_timing_6 = {100:['woman']}
        
        sem_timing = sem_timing_1
                        
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM, control]

        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        language_system.add_connection(semanticWM, 'to_control', control, 'from_semantic_WM')
        language_system.add_connection(phonWM, 'to_control', control, 'from_phonological_WM')
        language_system.add_connection(control, 'to_grammatical_WM', grammaticalWM, 'from_control')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
        language_system.system2dot(image_type='png', disp=True)
    
        
        max_step = 1000
        for step in range(max_step):
            if step in sem_timing:
                for s in sem_timing[step]:
                    print "time:%i, sem:%s" %(step, s)
                    info = sem_info[s]
                    if info[0]=='node':
                        semanticWM.SemRep.add_node(info[1], concept=info[2], new=True)
                    else:
                        semanticWM.SemRep.add_edge(info[1][0], info[1][1], concept=info[2], new=True)
                semanticWM.set_output('to_control', True)
    #                semanticWM.show_state()
            language_system.update()
#            if language_system.outputs['Phonological_WM:14']:
#                print language_system.outputs['Phonological_WM:14']
            
        grammaticalWM.show_dynamics()
    
    else:
        print "ERROR"
        




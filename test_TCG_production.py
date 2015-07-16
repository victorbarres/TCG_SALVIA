# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language production schemas defined in language_schemas.py
"""
import random

import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_production_system
    
def test(seed=None):
    
    random.seed(seed)
   
    language_system_P = TCG_production_system()
    
    # Display schema system
#    language_system_P.system2dot(image_type='png', disp=True)
    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    
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

    # Parameters:
    control = language_system_P.schemas['Control']
    control.task_params['start_produce'] = 200
    sem_option = 12
    end_delay = control.task_params['start_produce']  + 200
    
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
            language_system_P.schemas['Semantic_WM'].set_output('to_control', True)
        language_system_P.update()
        output = language_system_P.get_output()
        if output:
            print "t:%i, %s" %(step, output)
    
#    language_system_P.schemas['Semantic_WM'].show_dynamics(c2_levels=False)
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(c2_levels=False)
#    language_system_P.schemas['Grammatical_WM_P'].show_state()
#    language_system_P.save_sim('./tmp/test_language_output.json')
    
    
def test2(seed=None):
    """
    Semantic input rate based (for simplicity)
    """
    
    random.seed(seed)
   
    language_system_P = TCG_production_system()
    
    # Display schema system
#    language_system_P.system2dot(image_type='png', disp=True)
    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    
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

    # Parameters:
    control = language_system_P.schemas['Control']
    
    sem_rate = 100
#    control.task_params['start_produce'] = sem_rate*2 # Start early
    control.task_params['start_produce'] = sem_rate*5 # Start late
    
    control.task_params['time_pressure'] = sem_rate*0.1 # high pressure
#    control.task_params['time_pressure'] = sem_rate*2 # low pressure
    
      
    sem_option = 4
    end_delay = control.task_params['start_produce']  + 200
    
    sem_timings = {}
    sem_timings[0] = [[woman1]]
    sem_timings[1] = [[woman1, modify1, pretty1]]
    sem_timings[2] = [[woman1, kick1, man1, agent1, patient1]]
    sem_timings[3] = [[woman1, modify1, pretty1, kick1, agent1, patient1, man1, big1, modify2]]
    sem_timings[4] = [[woman1, modify1, pretty1, man1, big1, modify2]] # SemRep contains two unconnected subgraphs.
    
    sem_timings[5] = [[woman1],[modify1, pretty1]]
    
    sem_timings[6] = [[woman1], [modify1, pretty1], [kick1], [agent1, patient1, man1], [big1, modify2]]
    sem_timings[7] = [[man1], [kick1, woman1, agent1, patient1], [modify1, pretty1], [big1, modify2]]
    sem_timings[8] = [[man1], [kick1, woman1, agent1, patient1], [big1, modify2], [modify1, pretty1]] # NOTE HOW THE FACT THAT 'big' + 'mod2' are introduced right after the TRA tends to favor man first utterances compared to the previous case.(without time pressure)
    
    sem_timings[9] = [[woman1], [modify1, pretty1], [kick1], [agent1, patient1, man1], [big1, modify2]]    
    
    sem_timings[10] = [[woman1, modify1, pretty1], [man1, big1, modify2], [kick1], [agent1, patient1]]
    
    sem_timings[11] = [[woman1, wear1, agent2, patient2, dress1, blue1, modify3, kick1, agent1, patient1, man1]] # Test IN_COLOR
    
    sem_timing = sem_timings[sem_option][:]
    sem_timing.reverse()
    
    max_time = len(sem_timing)*sem_rate
    max_time += end_delay
    for t in range(max_time):
        if (t> sem_rate -1) and (t % sem_rate) ==0 and sem_timing:
            sem_insts = sem_timing.pop()
            for inst in sem_insts:
                print "time:%i, sem:%s" %(t, inst.name)
            language_system_P.set_input(sem_insts)
            language_system_P.schemas['Semantic_WM'].set_output('to_control', True)
        language_system_P.update()
        output = language_system_P.get_output()
        if t == 250:
                language_system_P.schemas['Grammatical_WM_P'].show_state()
        if output:
            print "t:%i, %s" %(t, output)
    
#    language_system_P.schemas['Semantic_WM'].show_dynamics(c2_levels=False)
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(c2_levels=True)
    language_system_P.schemas['Grammatical_WM_P'].show_state()
#    language_system_P.save_sim('./tmp/test_language_output.json')


def test3(seed=None):
    """
    Test FOL sem inputs
    """
    
    language_system_P = TCG_production_system()
    # Display schema system
#    language_system_P.system2dot(image_type='png', disp=True)
    
    conceptLTM = language_system_P.schemas['Concept_LTM']

    sem_inputs = TCG_LOADER.load_sem_input("test.json", "./data/sem_inputs/")
    option = 0
    
    my_input = sem_inputs[option]
    sem_gen = sem_generator(my_input, conceptLTM, verbose=True)
    (sem_insts, next_time) = sem_gen.next()
    
    max_time = 2000
    # set up time:
    for t in range(10):
        language_system_P.update()
    # Start processing
    if sem_insts:
        for inst in sem_insts:
            print "time:%i, sem:%s" %(0, inst.name)
        language_system_P.set_input(sem_insts)
    language_system_P.update()
        
    for t in range(1,max_time):
        if next_time and (t> next_time):
            (sem_insts, next_time) = sem_gen.next()
            for inst in sem_insts:
                print "time:%i, sem:%s" %(t, inst.name)
            language_system_P.set_input(sem_insts)
            language_system_P.schemas['Semantic_WM'].set_output('to_control', True) #Do I need that?
        language_system_P.update()
        output = language_system_P.get_output()
        if output:
            print "t:%i, %s" %(t, output)
    
#    language_system_P.schemas['Semantic_WM'].show_dynamics(c2_levels=False)
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(c2_levels=True)
    language_system_P.schemas['Grammatical_WM_P'].show_state()
#    language_system_P.save_sim('./tmp/test_language_output.json')
    

def sem_generator(sem_input, conceptLTM, verbose=False):
    """
    Creates a generator based on a semantic_data loaded by TCG_LOADER.load_sem_input().
    Eeach time next() function is called, returns a set of concept instances as well as the next time at which the generator should be called.
    Args:
        - sem_input: a semantic input dict loaded using load_sem_input()
        - conceptLTM (CONCEPT_LTM): Contains concept schemas.
    """        
    # For reference.
#        func_pattern = r"(?P<operator>\w+)\((?P<args>.*)\)"
#        cpt_pattern = r"[A-Z0-9_]+"
#        var_pattern = r"[a-z0-9]+"
#        cpt_var_pattern = r"\?[A-Z0-9_]+"
    
    # More directly specialized pattern. Works since I limit myself to two types of expressions CONCEPT(var) or var1(var2, var3) (and ?CONCEPT(var))
    func_pattern_cpt = r"(?P<operator>[A-Z0-9_]+)\(\s*(?P<var>[a-z0-9]+)\s*\)" # Concept definition
    func_pattern_rel = r"(?P<operator>[a-z0-9]+)\(\s*(?P<var1>[a-z0-9]+)(\s*,\s*)(?P<var2>[a-z0-9]+)\s*\)"
    func_pattern_cpt_var = r"(?P<operator>?[A-Z0-9_]+)\(\s*(?P<var>[a-z0-9]+)\s*\)" # Concept variables?

    sem_rate = sem_input['sem_rate']
    propositions = sem_input['propositions']
    sequence = sem_input['sequence']
    timing = sem_input['timing']
    if sem_rate and not(timing):
        timing = [i*sem_rate for i in range(len(sequence))]
    if not(timing) and not(sem_rate):
        print "ERROR: Provide either timing or rate."
        return
        
    if verbose:
        for i in range(len(sequence)):
            print 't: %.1f, prop: %s' %(timing[i], ' & '.join(propositions[sequence[i]]))
                    
    if timing[0]>0:
        yield ([], timing[0])
        
    name_table = {}
    for idx in range(len(sequence)):          
        instances = []
        prop_name = sequence[idx]
        prop_list = propositions[prop_name]
        for prop in prop_list:
            # Case1:
            match1 = re.search(func_pattern_cpt, prop)
            match2 = re.search(func_pattern_rel, prop)
            if match1:
                dat = match1.groupdict()
                concept = dat['operator']
                var = dat['var']
                cpt_schema = conceptLTM.find_schema(name=concept)
                cpt_inst = ls.CPT_SCHEMA_INST(cpt_schema, trace={'per_inst':None, 'cpt_schema':cpt_schema, 'ref':var}) # 'ref' is used to track referent.
                name_table[var] = cpt_inst
                instances.append(cpt_inst)
            
            elif match2:
                dat = match2.groupdict()
                rel = dat['operator']
                arg1 = dat['var1']
                arg2 = dat['var2']
                if not((rel in name_table) and (arg1 in name_table) and (arg2 in name_table)):
                    print "ERROR: variable used before it is defined."
                else:
                    rel_inst = name_table[rel]
                    rel_inst.content['pFrom'] = name_table[arg1]
                    rel_inst.content['pTo'] = name_table[arg2]
            else:
                print "ERROR, unknown formula"
        
        next_idx = idx + 1       
        if next_idx<len(timing):
            next_time = timing[next_idx]
        else:
            next_time = None

        yield (instances, next_time)    

    
if __name__=='__main__':
    test3(seed=1)
        




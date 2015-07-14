# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language production schemas defined in language_schemas.py
"""
import random

import language_schemas as ls
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
    sem_option = 1
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

if __name__=='__main__':
    test(seed=1)
        




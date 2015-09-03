# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language production schemas defined in language_schemas.py
"""
import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_production_system
from viewer import TCG_VIEWER
    
def test(seed=None):
    """
    Test Incremental Semantic Formulas sem inputs
    """
    
    language_system_P = TCG_production_system()
#     Display schema system
    language_system_P.system2dot(image_type='png', disp=True)
    
    conceptLTM = language_system_P.schemas['Concept_LTM']

    sem_inputs = TCG_LOADER.load_sem_input("sem_inputs.json", "./data/sem_inputs/")    
    sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM)

    input_name = 'blue_woman_kick_man'    
    generator = sem_gen.sem_generator(input_name)
    
    (sem_insts, next_time, prop) = generator.next()
    
    set_up_time = -10 #Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 600   
    save_states = [10,20,30,60,100,400]
    
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (sem_insts, next_time, prop) = generator.next()
            print "t:%i, sem: %s (prop: %s)" %(t, ', '.join([inst.name for inst in sem_insts]), prop)
            language_system_P.set_input(sem_insts)
#            language_system_P.schemas['Semantic_WM'].show_SemRep()
        language_system_P.update()
        output = language_system_P.get_output()
        if output:
            print "t:%i, '%s'" %(t, output)
        if t - set_up_time in save_states:
            TCG_VIEWER.display_gramWM_state(language_system_P.schemas['Grammatical_WM_P'], concise=True)
            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'],language_system_P.schemas['Grammatical_WM_P'], concise=True)
            TCG_VIEWER.display_gramWM_state(language_system_P.schemas['Grammatical_WM_P'], concise=False)
            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'],language_system_P.schemas['Grammatical_WM_P'], concise=False)
    
    language_system_P.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_P.schemas['Semantic_WM'].show_SemRep()
    TCG_VIEWER.display_semWM_state(language_system_P.schemas['Semantic_WM'])
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    language_system_P.schemas['Grammatical_WM_P'].show_state()
    language_system_P.schemas['Phonological_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_P.save_sim('./tmp/test_language_output.json')


if __name__=='__main__':
    test(seed=1)
        




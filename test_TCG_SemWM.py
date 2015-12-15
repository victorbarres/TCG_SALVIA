# -*- coding: utf-8 -*-
"""
@author: Victor Barres
SemanticWM test cases.
"""

import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_SemWM
from viewer import TCG_VIEWER

language_system_sem = TCG_SemWM()

# Display system
language_system_sem.system2dot(image_type='png', disp=True)

# Setting up semantic inputs
conceptLTM = language_system_sem.schemas['Concept_LTM']
sem_inputs = TCG_LOADER.load_sem_input("sem_inputs.json", "./data/sem_inputs/")    
sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM)

input_name = 'ditransitive_give'    
generator = sem_gen.sem_generator(input_name)

(sem_insts, next_time, prop) = generator.next()

set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
max_time = 900   
save_states = [30]

for t in range(set_up_time, max_time):
    if next_time != None and t>next_time:
        (sem_insts, next_time, prop) = generator.next()
        print "t:%i, sem: %s (prop: %s)" %(t, ', '.join([inst.name for inst in sem_insts]), prop)
        language_system_sem.set_input(sem_insts)
    language_system_sem.update()
    output = language_system_sem.get_output()
    if t - set_up_time in save_states:
        language_system_sem.schemas['Semantic_WM'].show_SemRep()
        
    
language_system_sem.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
language_system_sem.schemas['Semantic_WM'].show_SemRep()

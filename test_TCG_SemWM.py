# -*- coding: utf-8 -*-
"""
@author: Victor Barres
SemanticWM test cases.
"""

import schema_theory as st
import language_schemas as ls
from loader import TCG_LOADER
from viewer import TCG_VIEWER


# Instantiating all the necessary procedural schemas
semanticWM = ls.SEMANTIC_WM()
conceptLTM = ls.CONCEPT_LTM()
control = ls.CONTROL()


language_system_sem = st.SCHEMA_SYSTEM('Semantic_WM')
language_schemas = [conceptLTM, semanticWM, control]
language_system_sem.add_schemas(language_schemas)

# Setting up schema to brain mappings
brain_mapping = st.BRAIN_MAPPING()
brain_mapping.schema_mapping = {'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus']}
language_system_sem.brain_mapping = brain_mapping

language_system_sem.add_connection(control, 'to_semantic_WM', semanticWM, 'from_control')
language_system_sem.set_input_ports([semanticWM.find_port('from_conceptualizer')])
language_system_sem.set_output_ports([semanticWM.find_port('to_cxn_retrieval_P')])

language_system_sem.system2dot(image_type='png', disp=True)

# Loading data
my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
# Initialize conceptual LTM content
conceptLTM.initialize(my_conceptual_knowledge)

# Setting up semantic inputs
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

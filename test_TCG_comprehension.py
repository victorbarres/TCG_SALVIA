# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the comprehension language schemas defined in language_schemas.py
"""
import random

import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_comprehension_system
from viewer import TCG_VIEWER
    
def test(seed=None):
    """
    Speech rate based inputs (for simplicity)
    """
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    language_system_C = TCG_comprehension_system()
    # Display schema system
    language_system_C.system2dot(image_type='png', disp=True)
    
    option = 4
    speech_rate = 100
    
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing', 'ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man']
    lang_inputs[4] = ['a', 'woman']
    
    lang_input = lang_inputs[option][:]
    lang_input.reverse()
    max_time = 2000
    
    for t in range(max_time):
        if t>speech_rate-1 and t % speech_rate == 0 and lang_input:
            word_form = lang_input.pop()
            print 't: %i, receive: %s' %(t, word_form)
            language_system_C.set_input(word_form)
        language_system_C.update()
    
    language_system_C.schemas['Phonological_WM_C'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_C.schemas['Grammatical_WM_C'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    language_system_C.schemas['Grammatical_WM_C'].show_state()

    language_system_C.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_C.schemas['Semantic_WM'].show_SemRep()
    
    
    
def test2(seed=None):
    "Uses UTTER_GEN class for inputs"
    random.seed(seed)
    language_system_C = TCG_comprehension_system()
    # Display schema system
    language_system_C.system2dot(image_type='png', disp=True)
    
    ling_inputs = TCG_LOADER.load_ling_input("ling_inputs.json", "./data/ling_inputs/")    
    utter_gen = ls.UTTER_GENERATOR(ling_inputs)

    input_name = 'test_naming'    
    
    generator = utter_gen.utter_generator(input_name)
    
    (word_form, next_time) = generator.next()
    
    set_up_time = -10 # (Threshold  = 28??)Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0. Set up time really matters! Need to analyze more cleraly why and how much time is needed.
    max_time = 300
    save_states = []
    
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (word_form, next_time) = generator.next()
            print "t:%i, receive: %s" %(t, word_form)
            language_system_C.set_input(word_form)
        language_system_C.update()
        
        if t - set_up_time in save_states:
            TCG_VIEWER.display_gramWM_state(language_system_C.schemas['Grammatical_WM_C'], concise=True)
    
    language_system_C.schemas['Phonological_WM_C'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_C.schemas['Grammatical_WM_C'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    language_system_C.schemas['Grammatical_WM_C'].show_state()
    
    language_system_C.schemas['Semantic_WM'].show_dynamics()
    language_system_C.schemas['Semantic_WM'].show_SemRep()

if __name__=='__main__':
    test2(seed=None)
        




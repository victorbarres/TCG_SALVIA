# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the comprehension language schemas defined in language_schemas.py
"""
import random

from TCG_models import TCG_comprehension_system

def test(seed=None):
    
    random.seed(seed)
    ##############################
    ### Language schema system ###
    ##############################
    language_system_C = TCG_comprehension_system()
    # Display schema system
#    language_system_C.system2dot(image_type='png', disp=True)
    
    option = 2
    
    lang_inputs = {}
    lang_inputs[1] = {1:'a', 10:'woman', 20:'kick', 30:'a', 50:'man', 60:'in', 70:'blue'}
    lang_inputs[2] = {1:'a', 10:'woman', 20:'kick', 30:'a', 50:'man', 60:'in', 65: 'a', 70:'blue', 80:'boxing ring'}
    lang_inputs[3] = {1:'a', 10:'woman', 13:'who', 14:'is', 15:'pretty', 20:'kick', 30:'a', 50:'man', 60:'in', 70:'blue'}
    lang_inputs[4] = {1:'a', 10:'woman', 20:'laugh', 60:'kick', 70:'a', 75:'man', 80:'in', 85:'blue'}
    
    lang_input = lang_inputs[option]
    max_time = 500
    for step in range(max_time):
        if step in lang_input:
            word_form = lang_input[step]
            print 't: %i, receive: %s' %(step, word_form)
            language_system_C.set_input(word_form)
        language_system_C.update()
    
    language_system_C.schemas['Phonological_WM_C'].show_dynamics()
    language_system_C.schemas['Grammatical_WM_C'].show_dynamics()
    language_system_C.schemas['Grammatical_WM_C'].show_state()
    
    language_system_C.schemas['Semantic_WM'].show_dynamics()
    language_system_C.schemas['Semantic_WM'].show_SemRep()

if __name__=='__main__':
    test(seed=None)
        




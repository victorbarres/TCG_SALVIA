# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for a system that incoporates production and comprehension
"""
import random
import numpy as np

from TCG_models import TCG_language_system
    
def test(seed=None):
    random.seed(seed)

    language_system = TCG_language_system()
    
    # Display schema system
    language_system.system2dot(image_type='png', disp=True)
    
    option = 3
    
    speech_rate = language_system.schemas['Utter'].params['speech_rate']
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    
    lang_input = lang_inputs[option]
    lang_input.reverse()
    max_time = 1000
    flag = True
    
    language_system.schemas['Control'].set_mode('listen')
    for t in range(max_time):
        if t>10 and np.mod(t, speech_rate) == 0 and lang_input: # Need some time to have the system set up before it receives the first input.
            word_form = lang_input.pop()
            print 't: %i, receive: %s' %(t, word_form)
            language_system.set_input(word_form)
        language_system.update()
        if language_system.schemas['Semantic_WM'].schema_insts and flag: #Switching from comprehension to production
            language_system.schemas['Semantic_WM'].show_SemRep()
            language_system.schemas['Control'].set_mode('produce')
            flag = False
        output = language_system.get_output()
        if output:
            print 't: %i, %s' %(t, output)  
    
    language_system.schemas['Grammatical_WM_P'].show_dynamics()
    language_system.schemas['Grammatical_WM_C'].show_dynamics()

if __name__=='__main__':
    test(seed=None)
        




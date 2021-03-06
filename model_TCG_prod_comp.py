# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for a system that incoporates production and comprehension
"""
import random

from TCG_models import TCG_language_system
    
def test(seed=None):
    random.seed(seed)

    language_system = TCG_language_system()
    
    # Display schema system
    language_system.system2dot(image_type='png', disp=True)
    
    language_system.schemas['Control'].task_params['start_produce'] = 100
    
    option = 3
    
    language_system.schemas['Utter'].params['speech_rate'] = 40
    speech_rate = language_system.schemas['Utter'].params['speech_rate']
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing', 'ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man']
    
    lang_input = lang_inputs[option]
    lang_input.reverse()
    max_time = 1000
    flag = True
    
    language_system.schemas['Control'].set_mode('listen')
    print "VB speaks. Agt1 listens"
    for t in range(max_time):
        if t>10 and (t % speech_rate) == 0 and lang_input: # Need some time to have the system set up before it receives the first input.
            word_form = lang_input.pop()
            print 't: %i, VB says: %s' %(t, word_form)
            language_system.set_input(word_form)
        if language_system.schemas['Semantic_WM'].schema_insts and flag: #Switching from comprehension to production
            language_system.schemas['Semantic_WM'].show_SemRep()
            language_system.schemas['Control'].set_mode('produce')
            flag = False
            print "Agt1 speaks."
        output = language_system.get_output()
        if output and output['Utter']:
            print 't: %i, Agt1 says: %s' %(t, output['Utter'])
        language_system.update()
    
    language_system.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    language_system.schemas['Grammatical_WM_C'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)

if __name__=='__main__':
    test(seed=None)
        




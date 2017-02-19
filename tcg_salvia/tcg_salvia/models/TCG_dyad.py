# -*- coding: utf-8 -*-
"""
@author: Victor Barres
TCG dyad model
"""
import random

from model_def import TCG_language_system
    
def test(seed=None):
    """
    """
    random.seed(seed)

    language_system_1 = TCG_language_system('Agent1')
    language_system_2 = TCG_language_system('Agent2')
    
#    language_system_1.system2dot(image_type='png', disp=True)
    
    language_system_1.schemas['Control'].set_mode('listen')
    language_system_2.schemas['Control'].set_mode(None)
    
    option = 3
    speech_rate = 100
    language_system_1.schemas['Utter'].params['speech_rate'] = speech_rate
    language_system_2.schemas['Utter'].params['speech_rate'] = speech_rate
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing', 'ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man']
    lang_inputs[4] = ['a', 'woman']
    
    lang_input = lang_inputs[option][:]
    lang_input.reverse()
    max_time = 2500
    
    flag1 = True
    flag2 = True
    print "VB speaks. Agt1 listens"
    for t in range(max_time):
        if t>10 and (t % speech_rate == 0) and lang_input: # Need some time to have the system set up before it receives the first input.
            word_form = lang_input.pop()
            print 't: %i, VB says: %s' %(t, word_form)
            language_system_1.set_input(word_form)
            
        if language_system_1.schemas['Semantic_WM'].schema_insts and flag1: #Switching from comprehension to production
            language_system_1.schemas['Semantic_WM'].show_SemRep()
            language_system_1.schemas['Control'].set_mode('produce')
            flag1 = False
            print "Agt1 speaks. Agt2 listens"
            
        output = language_system_1.get_output()
        if output and  output['Utter'] and flag2:
            language_system_2.schemas['Control'].set_mode('listen')
            language_system_2.update() # Cheat!! Need to set up the system so that it's ready to receive the utterance...
            language_system_2.update()
            print 't: %i, Agt1 says: %s' %(t,  output['Utter'])  
            language_system_2.set_input(output['Utter'])
        
        if language_system_2.schemas['Semantic_WM'].schema_insts and flag2: #Switching from comprehension to production
            language_system_2.schemas['Semantic_WM'].show_SemRep()
            language_system_2.schemas['Control'].set_mode('produce')
            language_system_1.schemas['Control'].set_mode(None)
            flag2 = False
            print "Agt2 speaks."
        
        output = language_system_2.get_output() 
        if output and output['Utter']:
            print 't: %i, Agt2 says: %s' %(t, output['Utter'])  
            
        language_system_1.update()
        language_system_2.update()
    
    language_system_1.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    language_system_2.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    
            

if __name__=='__main__':
    test(seed=None)
        




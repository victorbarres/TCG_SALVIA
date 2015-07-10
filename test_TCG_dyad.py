# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for a system that incoporates production and comprehension
"""
import random
import numpy as np

from TCG_models import TCG_language_system

    
def test(seed=None):
    """
    NOTE: The dyad cannot be run for now.
    There is an important issue to sove with respect to the handling of the conceptual knowledge. 
    When conceptual knowledge is being loaded the first time, it alters the concept class. When loaded a second time, the new conceptual knowledge
    will overide the first one in the concept class... This needs to be changed.
    """
    random.seed(seed)

    language_system_1 = TCG_language_system()
    language_system_2 = TCG_language_system()
    
    language_system_1.schemas['Control'].set_mode('listen')
    language_system_2.schemas['Control'].set_mode('listen')
    
    option = 3
    
    speech_rate = language_system_1.schemas['Utter'].params['speech_rate']
    lang_inputs = {}
    lang_inputs[0] = ['a', 'woman', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[1] = ['a', 'woman', 'kick', 'a', 'man', 'in',  'a', 'blue', 'boxing ring']
    lang_inputs[2] = ['a', 'woman', 'who', 'is', 'pretty', 'kick', 'a', 'man', 'in', 'blue']
    lang_inputs[3] = ['a', 'woman', 'kick', 'a', 'man']
    
    lang_input = lang_inputs[option]
    lang_input.reverse()
    max_time = 2000
    
    flag1 = True
    flag2 = True
    print "VB speaks. Ag1 listens"
    for t in range(max_time):
        if t>10 and np.mod(t, speech_rate) == 0 and lang_input: # Need some time to have the system set up before it receives the first input.
            word_form = lang_input.pop()
            print 't: %i, VB says: %s' %(t, word_form)
            language_system_1.set_input(word_form)
            
        if language_system_1.schemas['Semantic_WM'].schema_insts and flag1: #Switching from comprehension to production
            language_system_1.schemas['Semantic_WM'].show_SemRep()
            language_system_1.schemas['Control'].set_mode('produce')
            flag1 = False
            print "Agt1 speaks. Agt2 listens"
            
        word_form = language_system_1.get_output()
        if word_form:
            print 't: %i, Agt1 says: %s' %(t, word_form)  
            language_system_2.set_input(word_form)
        
        if language_system_2.schemas['Semantic_WM'].schema_insts and flag2: #Switching from comprehension to production
            language_system_1.schemas['Semantic_WM'].show_SemRep()
            language_system_1.schemas['Control'].set_mode('produce')
            flag2 = False
            print "Agt2 speaks."
            
        language_system_1.update()
        language_system_2.update()
            

if __name__=='__main__':
    test(seed=None)
        




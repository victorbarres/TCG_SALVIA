# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the comprehension language schemas defined in language_schemas.py
"""
from __future__ import division
import random
import time

from TCG_models import TCG_comprehension_system
import language_schemas as ls
from loader import TCG_LOADER
from viewer import TCG_VIEWER
from schema_theory import st_save

TMP_FOLDER = './tmp'

##################
#### RUNNING MODEL
def set_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', model_params = {}):
    """
    Sets up a TCG comphrehension model.
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - model_prams (DICT): Dictionary defining the model parameters (if different than default)
    
    Returns: 
        - comprehension model
    """
    
    model = TCG_comprehension_system(grammar_name=grammar_name, semantics_name=semantics_name)
    if model_params:
        model.update_params(model_params)
    
    return model
    
    
def set_inputs(model, ling_input_file='ling_inputs.json', speed_param=10):
    """
    Sets up a TCG UTTER_GENERATOR inputs generator for TCG comprehension model.
    
    Args:
        - model (): model to which the inputs will be sent
        - ling_input_file (STR): Linguistic input file name.
        - speed_param (INT): multiplier of the rate defined in the ISRF input (by default the ISFR rate is 1.)
    
    Returns:
        - input UTTER_GENERATOR object.
    """
    LING_INPUT_PATH = './data/ling_inputs/'
    ling_inputs = TCG_LOADER.load_ling_input(ling_input_file, LING_INPUT_PATH)
    
    utter_gen = ls.UTTER_GENERATOR(ling_inputs)
    
    return utter_gen
    
    
def run(model, utter_gen, input_name, sim_name='', sim_folder=TMP_FOLDER, max_time=900, seed=None, verbose=0, prob_times=[], save=False, anim=False, anim_step=10):
    """
    Run the model "model" for an utterance gerator "utter_gen" using the input "input_name"
    Verbose modes: 0,1 -> no output printed. 2 -> only semantic state printed, 3 -> input and semantic state printed as they are received and produced. >3 -> 10steps after utter_input received added to prob_times as well as 10 steps before max_time
    prob_times ([INT]): For time in list, saves a view of LinguisticWM concise in tmp folder.
    
    Returns:
        outputs (DICT): {time:model.get_output()} for all time in simulation time steps for which model's output is not empty.
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
    random.seed(seed)
    
    sim_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    
    if not(sim_name):
        sim_name = '%s_%s_(%s)' %(sim_time, input_name, str(seed))
    else:
        sim_name = '%s_%s_(%s)' %(sim_time, sim_name, str(seed))
    
    FOLDER = '%s/%s/' %(sim_folder, sim_name)
    
    if save: # Saving model and sem_gen
        st_save(model, model.name, FOLDER)
        st_save(utter_gen, 'utter_gen', FOLDER)
    
    # initializing generator for the model.
    generator = utter_gen.utter_generator(input_name, verbose = (verbose>2))
    (word_form, next_time) = generator.next()

    model.initialize_states() # initializing model
    
    if verbose>3:
        prob_times.append(max_time-10)# Will save the state 10 steps before max_time
    
    outputs = {}
    test_not_empty = lambda l: [x for x in l.values() if x!= None] != []
    
    for t in range(max_time):
        if next_time != None and t>=next_time:
            (word_form, next_time) = generator.next()
            model.set_input(word_form)
            if verbose > 3:
                prob_times.append(t + 10) #Will save the state 10 step after introduction of new inputs.
        model.update()
        # Store output
        output = model.get_output()
        if test_not_empty(output): # filter out ouputs with all valyues == None
            outputs[t] = output
        # Display methods
        if t in prob_times: # Saving figures for prob times.
            TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM'], model.schemas['Grammatical_WM_C'], concise=True, folder = FOLDER)
    
    if save:
        model.save_sim(file_path = FOLDER, file_name = 'output')
           
    # Display end states
    if verbose>2:
        model.schemas['Grammatical_WM_C'].show_dynamics(folder=FOLDER)
        model.schemas['Phonological_WM_C'].show_dynamics(folder=FOLDER)
        model.schemas['Semantic_WM'].show_dynamics(folder=FOLDER)
        
    if anim:
        if save:
            print "saving animation (might take some time!)"
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['Phonological_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
        else:
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['Phonological_WM_C'].show_dynamics_anim(step=anim_step)
              
    model.reset() # Gets model ready for next use.
    
    return outputs
    
def run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='test_naming', ling_input_file='ling_inputs.json', max_time=900, seed=None, speed_param=10, prob_times=[], verbose=0, save=True, anim=False,  anim_step=10):
    """
    Runs the model
    
    Returns
        - out (ARRAY): Array of model's outputs (single output if not macro, series of output if macro.)
    """
    model = set_model(semantics_name, grammar_name, model_params=model_params)
    utter_gen = set_inputs(model, ling_input_file, speed_param)
    
    out = {}
    out[input_name] = run(model, utter_gen, input_name, sim_name=sim_name, sim_folder=sim_folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
    return out
    
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
    run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='test_naming', ling_input_file='ling_inputs.json', max_time=900, seed=None, speed_param=100, prob_times=[], verbose=3, save=True, anim=False,  anim_step=10)
        




# -*- coding: utf-8 -*-
"""
@author: Victor Barres
TCG comprehension model
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
    
    
def set_inputs(model, ling_input_file='ling_inputs.json', speed_param=10, offset=10):
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
    
    utter_gen = ls.UTTER_GENERATOR(ling_inputs, speed_param=speed_param, offset=offset)
    
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
    generator = utter_gen.utter_generator(input_name, verbose = (verbose>0))
    (word_form, next_time) = generator.next()

    model.initialize_states() # initializing model
    
    if verbose>1:
        prob_times.append(max_time-10)# Will save the state 10 steps before max_time
    
    outputs = {}
    test_not_empty = lambda l: [x for x in l.values() if x!= None] != []
    isrf_writer = ls.ISRF_WRITER(model.schemas['Semantic_WM_C'])
    for t in range(max_time):
        if next_time != None and t>=next_time:
            (word_form, next_time) = generator.next()
            model.set_input(word_form)
            if verbose>1:
                prob_times.append(t + 10) #Will save the state 10 step after introduction of new inputs.
        model.update()
        # Store output
        output = model.get_output()
        if test_not_empty(output): # filter out ouputs with all valyues == None
            outputs[t] = output
        # Display methods
        if output['Semantic_WM_C']:
            if verbose > 2:
                state_ISRF = isrf_writer.write_ISRF()
                print "\nt:%i, Semantic state:\n%s\n" %(state_ISRF[0], state_ISRF[1])
            if verbose > 1:
                prob_times.append(t + 10) #Will save the state 10 steps after utterance
        if t in prob_times: # Saving figures for prob times.
            TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_C'], concise=True, folder = FOLDER)
            TCG_VIEWER.display_semWM_state(model.schemas['Semantic_WM_C'], folder = FOLDER)
    
    if save:
        model.save_sim(file_path = FOLDER, file_name = 'output')
           
    # Display end states
    if verbose>2:
        model.schemas['Grammatical_WM_C'].show_dynamics()
        model.schemas['Phonological_WM_C'].show_dynamics()
        model.schemas['Semantic_WM'].show_dynamics()
       
    if anim:
        if save:
            print "saving animation (might take some time!)"
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['Semantic_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['Phonological_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
        else:
            model.schemas['Phonological_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['Semantic_WM_C'].show_dynamics_anim(step=anim_step)
            
      
#    model.schemas['Semantic_WM'].show_SemRep()
    model.reset() # Gets model ready for next use.
    isrf_writer.reset()
    
    return outputs
    
def run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='test_naming', ling_input_file='ling_inputs.json', max_time=900, seed=None, speed_param=10, offset=10, prob_times=[], verbose=0, save=True, anim=False,  anim_step=10):
    """
    Runs the model
    
    Returns
        - out (ARRAY): Array of model's outputs (single output if not macro, series of output if macro.)
    """
    model = set_model(semantics_name, grammar_name, model_params=model_params)
    utter_gen = set_inputs(model, ling_input_file, speed_param, offset)
    
    out = {}
    out[input_name] = run(model, utter_gen, input_name, sim_name=sim_name, sim_folder=sim_folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
    return out
    
    
def run_diagnostic():
    """
    """
    import json
    LING_INPUT_FILE = 'ling_inputs.json'
    SEMANTICS_NAME = 'TCG_semantics_main'
    GRAMMAR_NAME = 'TCG_grammar_VB_main'
    VERBOSE = 2
    SEED = None
    ANIM = True
    MAX_TIME = 900
    SPEED_PARAM = 30
    OFFSET = 10
    with open('./data/ling_inputs/' + LING_INPUT_FILE, 'r') as f:
        json_data = json.load(f)
    input_names = json_data['inputs'].keys()
    print "\nInput list:\n %s" %'\n '.join(input_names)
    input_name = raw_input('\nEnter input name: ')
    yes_no = raw_input('\nSave? (y/n): ')
    save = yes_no == 'y'
    print "#### Processing -> %s\n" % input_name
    run_model(semantics_name=SEMANTICS_NAME, grammar_name=GRAMMAR_NAME, sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name=input_name, ling_input_file=LING_INPUT_FILE, max_time=MAX_TIME, seed=SEED, speed_param=SPEED_PARAM, offset=OFFSET, prob_times=[550], verbose=VERBOSE, save=save, anim=ANIM,  anim_step=1)
    


if __name__=='__main__':
#    input_names = [u'test_in_loc_S', u'test_SYMMETRIC_TRANS', u'test_naming', u'test_SVO', u'test_subj_rel_SVO', u'test_SV', u'test_in_blue', u'test_obj_rel_PAS_SVO', u'test_obj_rel_SVO', u'test_complex1', u'test_DOUBLE_OBJ', u'test_OBLIQUE_DATIVE', u'test_SPA', u'test_subj_rel_PAS_SVO', u'test_PAS_SVO', u'test_in_loc_N']
#    num = len(input_names)
#    for input_name in input_names:
#        print "#### Processing -> %s" % input_name
#        print "%i more to go!" % num
#        num -=1
#        run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name=input_name, ling_input_file='ling_inputs.json', max_time=900, seed=None, speed_param=10, offset=10, prob_times=[], verbose=4, save=True, anim=True,  anim_step=1)
    run_diagnostic()

#    run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='test_SVO', ling_input_file='ling_inputs.json', max_time=900, seed=None, speed_param=10, offset=10, prob_times=[], verbose=4, save=True, anim=True,  anim_step=1)





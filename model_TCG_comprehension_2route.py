# -*- coding: utf-8 -*-
"""
@author: Victor Barres
TCG WK model
"""
from __future__ import division
import random
import time
import warnings

from TCG_models import TCG_comprehension_2route_system
import language_schemas as ls
from loader import TCG_LOADER
from viewer import TCG_VIEWER
from schema_theory import st_save
from analysis_comp import analysis_gram, analysis_wk, analysis_sem

TMP_FOLDER = './tmp'

##################
#### RUNNING MODEL
def set_model(semantics_name='TCG_semantics_dev', grammar_name='TCG_grammar_VB_2route', model_params = {}):
    """
    Sets up a TCG comprehension 2route system.
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - model_prams (DICT): Dictionary defining the model parameters (if different than default)
    
    Returns: 
        - comprehension 2route model
    """
    
    model = TCG_comprehension_2route_system(grammar_name=grammar_name, semantics_name=semantics_name)
    if model_params:
        model.update_params(model_params)
    
    return model
    
    
def set_inputs(model, ling_input_file='ling_inputs_2route.json', input_name='ALL', speed_param=10, offset=10, std=0):
    """
    Sets up a TCG UTTER_GENERATOR inputs generator for TCG comprehension model.
    
    Args:
        - model (): model to which the inputs will be sent
        - ling_input_file (STR): Linguistic input file name.
        - input_name (STR): 'ALL', loads all the inputs.
        - speed_param (INT): multiplier of the rate defined in the ISRF input (by default the ISFR rate is 1.)
        - offset (FLOAT):
        - std (FLAOT)
    
    Returns:
        - input UTTER_GENERATOR object.
    """
    LING_INPUT_PATH = './data/ling_inputs/'
    ling_inputs = TCG_LOADER.load_ling_input(ling_input_file, LING_INPUT_PATH)
    ground_truths = TCG_LOADER.load_ground_truths(ling_input_file, LING_INPUT_PATH)
    if input_name != 'ALL':
        if input_name not in ling_inputs:
            error_msg = "%s input cannot be found in %s" %(input_name, ling_input_file)
            raise ValueError(error_msg)
        ling_inputs = {input_name: ling_inputs[input_name]}
        if not(ground_truths) or input_name not in ground_truths:
            warn_msg = "No ground truth for %s in %s" %(input_name, ling_input_file)
            warnings.warn(warn_msg)
        ground_truths = ground_truths.get(input_name, None)
    else:
        if not(ground_truths):
            warn_msg = "No ground truth in %s" % ling_input_file
            warnings.warn(warn_msg)
    
    utter_gen = ls.UTTER_GENERATOR(ling_inputs, speed_param=speed_param, offset=offset, std=std, ground_truths=ground_truths)
    return utter_gen
    
    
def run(model, utter_gen, input_name, sim_name='', sim_folder=TMP_FOLDER, max_time=900, seed=None, verbose=0, prob_times=[], save=False, anim=False, anim_step=1, all_imgs=True):
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
        if output['Semantic_WM_C']:
            # Convert to ISRF
            state_ISRF = isrf_writer.write_ISRF()
            outputs[t]['Semantic_WM_C'] = state_ISRF[1]
            # Display methods
            if verbose > 2:
                print "\nt:%i, Semantic state:\n%s\n" %(state_ISRF[0], state_ISRF[1])
            if verbose > 1:
                prob_times.append(t + 10) #Will save the state 10 steps after Semantic output
        if t in prob_times or all_imgs: # Saving figures for prob times (or for all time if all_imgs=True).
            TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_C'], concise=True, folder = FOLDER)
            TCG_VIEWER.display_semWM_state(model.schemas['Semantic_WM_C'], folder = FOLDER)
    
    if save:
        model.save_sim(file_path = FOLDER, file_name = 'output')
           
    # Display end states
    if verbose>2:
        model.schemas['Grammatical_WM_C'].show_dynamics(folder=FOLDER)
        model.schemas['Phonological_WM_C'].show_dynamics(folder=FOLDER)
        model.schemas['Semantic_WM_C'].show_dynamics(folder=FOLDER)
        model.schemas['WK_frame_WM'].show_dynamics(folder=FOLDER)
       
    if anim:
        if save:
            print "saving animation (might take some time!)"
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['Semantic_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['Phonological_WM_C'].show_dynamics_anim(folder=FOLDER, step=anim_step)
            model.schemas['WK_frame_WM'].show_dynamics_anim(folder=FOLDER, step=anim_step)
        else:
            model.schemas['Phonological_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['Grammatical_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['Semantic_WM_C'].show_dynamics_anim(step=anim_step)
            model.schemas['WK_frame_WM'].show_dynamics_anim(step=anim_step)
      
#    model.schemas['Semantic_WM'].show_SemRep()
    model.reset() # Gets model ready for next use.
    isrf_writer.reset()
    
    return outputs
    
def summarize_data(outputs, ground_truths=None):
    """
    Args:
        - outputs (DICT): output generate by run()
        - ground_truths (DICT): {voice, agent, patient}
    Returns:
        - summary of outputs from run()
    """
    data_to_analyze = [] # data should be ordered by time
    times = outputs.keys()
    times.sort()
    for t in times:
        data_to_analyze.append(outputs[t])
    final_output = data_to_analyze[-1] # Only looks at the last output
    print final_output
    
    # GramWM
    gram_summary = analysis_gram(final_output['Grammatical_WM_C'], ground_truths)

    # WkWM
    wk_summary=  analysis_wk(final_output['WK_frame_WM'])

    # SemWM
    sem_summary = analysis_sem(final_output['Semantic_WM_C'], ground_truths) # Should indicate whether or not proper TRA was achieved
    
    summary = {'GramWM':gram_summary, 'WkWM':wk_summary, 'SemWM':sem_summary}
    return summary
    
def run_model(semantics_name='TCG_semantics_dev', grammar_name='TCG_grammar_VB_2routes', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='woman', ling_input_file='ling_inputs_2routes.json', max_time=900, seed=None, speed_param=10, offset=10, std=0, prob_times=[], verbose=0, save=True, anim=False,  anim_step=10):
    """
    Runs the model
    
    Returns
        - out (ARRAY): Array of model's outputs (single output if not macro, series of output if macro.)
    """
    model = set_model(semantics_name, grammar_name, model_params=model_params)
    utter_gen = set_inputs(model, ling_input_file, input_name,  speed_param, offset, std)
    
    out = {}
    out[input_name] = run(model, utter_gen, input_name, sim_name=sim_name, sim_folder=sim_folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
    return out

###############
#### DIAGNOSTIC     
def run_diagnostic(verbose=3):
    """
    """
    import json
    LING_INPUT_FILE = 'ling_inputs_2route.json'
    SEMANTICS_NAME = 'TCG_semantics_dev'
    GRAMMAR_NAME = 'TCG_grammar_VB_2route'
    VERBOSE = verbose
    SEED = 1984
    ANIM = True
    MAX_TIME = 1000
    SPEED_PARAM = 100
    OFFSET = 10
    STD = 0
    PROB_TIMES = []
    with open('./data/ling_inputs/' + LING_INPUT_FILE, 'r') as f:
        json_data = json.load(f)
    input_names = json_data['inputs'].keys()
    input_names.sort()
    print "\nInput list:\n %s" %'\n '.join(input_names)
    input_name = raw_input('\nEnter input name: ')
    yes_no = raw_input('\nSave? (y/n): ')
    save = yes_no == 'y'
    print "#### Processing -> %s\n" % input_name
    res = run_model(semantics_name=SEMANTICS_NAME, grammar_name=GRAMMAR_NAME, sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name=input_name, ling_input_file=LING_INPUT_FILE, max_time=MAX_TIME, seed=SEED, speed_param=SPEED_PARAM, offset=OFFSET, std=STD, prob_times=PROB_TIMES, verbose=VERBOSE, save=save, anim=ANIM,  anim_step=1)
#    print "\nRESULTS:\n"
#    print res
############################
#### PARAMETER SPACE ANALYSIS  
def parameter_space(folder=None, input_rate=100):
    """
    Defines and returns a parameter space.
    
    Args:
        - folder (STR): Folder path. If defined, the parameter set dictionary is pickled and saved to this folder.
        - input_rate: input_rate that will be used for the SemGen object, serves as a time reference.
    
    Returns:
        - model_params_set (DICT): a parameter space dictionary.
    
    """
    import itertools
    import numpy as np
    
    # Defining fixed input rate
    INPUT_RATE = input_rate # This serves as a time reference for the range of Tau and task parameters

    # Set up the model's parameter search space.
    model_params_set = []
    
    ## Grammatical_WM_C
    # C2 parameters
    coop_weights_G =  [1.0] #np.linspace(1.0, 10.0, 2)
    coop_asymmetries_G = [1.0] #np.linspace(0.0, 1.0, 2)
    comp_weights_G = [-10.0]
    max_capacity_G = [None]
    prune_thresholds_G = [0.01] # Change prune threshold (should be done in relation to initial activation values.) 
    conf_tresholds_G = [0.3] #np.linspace(0.1, 0.9, 2) # np.linspace(0.3,0.3, 1) #0.7
    
    # Dyn parameters
    taus_G = [INPUT_RATE*10] #[INPUT_RATE/10, INPUT_RATE*10] #np.linspace(int(INPUT_RATE/10), INPUT_RATE*10, 3) # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    ks_G= [10] #np.linspace(1, 10, 2) 
    act_rests_G = [0.001] # Act rest does not take into account the noise.
    noise_stds_G = [1.0] #np.linspace(1.0, 2.0, 2) # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
    ext_weights_G = [1.0] #np.linspace(1, 10, 2)
    
    ## Semantic_WM_C
    # C2 parameters
    comp_weights_S = [-10.0]
    max_capacity_S = [None]
    prune_thresholds_S = [0.01] # Change prune threshold (should be done in relation to initial activation values.) #0.01
    conf_tresholds_S = [0.3] #np.linspace(0.1, 0.9, 2) # np.linspace(0.3,0.3, 1) #0.7

    # Dyn parameters
    taus_S = [INPUT_RATE*10] #[INPUT_RATE/10, INPUT_RATE*10] #np.linspace(int(INPUT_RATE/10), INPUT_RATE*10, 3) # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    ks_S= [10] #np.linspace(1, 10, 2)
    act_rests_S = [0.001] # Act rest does not take into account the noise.
    noise_stds_S = [1.0] #np.linspace(1.0, 2.0, 2) # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
    ext_weights_S = [1.0] #np.linspace(1, 10, 2)
    
    ## WK_WM
    # C2 parameters
    max_capacity_WK = [None]
    prune_thresholds_WK = [0.01] # Change prune threshold (should be done in relation to initial activation values.) #0.01
    conf_tresholds_WK = [0.3] #np.linspace(0.1, 0.9, 2) # np.linspace(0.3,0.3, 1) #0.7
    
    # Dyn parameters
    taus_WK = [INPUT_RATE*10] #[INPUT_RATE/10, INPUT_RATE*10] #np.linspace(int(INPUT_RATE/10), INPUT_RATE*10, 3) # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    ks_WK= [10] #np.linspace(1, 10, 2)
    act_rests_WK = [0.001] # Act rest does not take into account the noise.
    noise_stds_WK = [1.0] #np.linspace(1.0, 2.0, 2) # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
    ext_weights_WK = [1.0] #np.linspace(1, 10, 2)
    
    
    
    param_iter = itertools.product(coop_weights_G, coop_asymmetries_G, comp_weights_G, 
                                   max_capacity_G, prune_thresholds_G, conf_tresholds_G, 
                                   taus_G, ks_G, act_rests_G, noise_stds_G, ext_weights_G,
                                   comp_weights_S, max_capacity_S, prune_thresholds_S, conf_tresholds_S, 
                                   taus_S, ks_S, act_rests_S, noise_stds_S, ext_weights_S,
                                   max_capacity_WK, prune_thresholds_WK, conf_tresholds_WK, 
                                   taus_WK, ks_WK, act_rests_WK, noise_stds_WK, ext_weights_WK)
    
    for param in param_iter:
        params = {'Grammatical_WM_C.C2.coop_weight':param[0], 
                  'Grammatical_WM_C.C2.coop_asymmetry':param[1],
                  'Grammatical_WM_C.C2.comp_weight':param[2], 
                  'Grammatical_WM_C.C2.max_capacity':param[3],
                  'Grammatical_WM_C.C2.prune_threshold': param[4], 
                  'Grammatical_WM_C.C2.confidence_threshold': param[5],
                  'Grammatical_WM_C.dyn.tau':param[6], # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                  'Grammatical_WM_C.dyn.k': param[7],
                  'Grammatical_WM_C.dyn.act_rest': param[8],
                  'Grammatical_WM_C.dyn.noise_std':param[9],
                  'Grammatical_WM_C.dyn.ext_weight':param[10],
                  'Semantic_WM_C.C2.comp_weight':param[11], 
                  'Semantic_WM_C.C2.max_capacity':param[12],
                  'Semantic_WM_C.C2.prune_threshold': param[13], 
                  'Semantic_WM_C.C2.confidence_threshold': param[14],
                  'Semantic_WM_C.dyn.tau':param[15], # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                  'Semantic_WM_C.dyn.k': param[16],
                  'Semantic_WM_C.dyn.act_rest': param[17],
                  'Semantic_WM_C.dyn.noise_std':param[18],
                  'Semantic_WM_C.dyn.ext_weight':param[19],
                  'WK_frame_WM.C2.max_capacity':param[20],
                  'WK_frame_WM.C2.prune_threshold': param[21], 
                  'WK_frame_WM.C2.confidence_threshold': param[22],
                  'WK_frame_WM.dyn.tau':param[23], # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                  'WK_frame_WM.dyn.k': param[24],
                  'WK_frame_WM.dyn.act_rest': param[25],
                  'WK_frame_WM.dyn.noise_std':param[26],
                  'WK_frame_WM.dyn.ext_weight':param[27]}

        model_params_set.append(params)
    
    # Defining parameter name mapping
    param_name_mapping = {'Grammatical_WM_P.C2.coop_weight':'coop_weight_G', 
                      'Grammatical_WM_C.C2.coop_asymmetry':'coop_asymmetry_G',
                      'Grammatical_WM_C.C2.comp_weight':'comp_weight_G',
                      'Grammatical_WM_C.C2.max_capacity':'max_capacity_G',
                      'Grammatical_WM_C.C2.prune_threshold': 'prune_threshold_G', 
                      'Grammatical_WM_C.C2.confidence_threshold':'conf_threshold_G',
                      'Grammatical_WM_C.C2.sub_threshold_r':'sub_threshold_G',
                      'Grammatical_WM_C.C2.deact_weight':'deact_weight_G',
                      'Grammatical_WM_C.dyn.tau':'tau_G',
                      'Grammatical_WM_C.dyn.k':'k_G',
                      'Grammatical_WM_C.dyn.act_rest':'act_rest_G',
                      'Grammatical_WM_C.dyn.noise_std':'noise_std_G',
                      'Grammatical_WM_C.dyn.ext_weight':'ext_weight_G',
                      'Semantic_WM_C.C2.comp_weight':'coop_weight_S', 
                      'Semantic_WM_C.C2.max_capacity':'max_capacity_S',
                      'Semantic_WM_C.C2.prune_threshold': 'prune_threshold_S', 
                      'Semantic_WM_C.C2.confidence_threshold': 'conf_threshold_S',
                      'Semantic_WM_C.dyn.tau':'tau_S', # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                      'Semantic_WM_C.dyn.k': 'k_S',
                      'Semantic_WM_C.dyn.act_rest': 'act_rest_S',
                      'Semantic_WM_C.dyn.noise_std':'noise_std_S',
                      'Semantic_WM_C.dyn.ext_weight':'ext_weight_S',
                      'WK_frame_WM.C2.max_capacity':'max_capacity_WK',
                      'WK_frame_WM.C2.prune_threshold': 'prune_threshold_WK', 
                      'WK_frame_WM.C2.confidence_threshold': 'conf_threshold_WK',
                      'WK_frame_WM.dyn.tau':'tau_WK', # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                      'WK_frame_WM.dyn.k': 'k_WK',
                      'WK_frame_WM.dyn.act_rest': 'act_rest_WK',
                      'WK_frame_WM.dyn.noise_std':'noise_std_WK',
                      'WK_frame_WMC.dyn.ext_weight':'ext_weight_WK'}
                
    
    if folder:
        st_save(model_params_set, 'parameter_set', folder, 'params')
        st_save(param_name_mapping, 'param_name_mapping', folder, 'params')
    
    return (model_params_set, param_name_mapping)
    
def weight_space(folder=None):
    """
    Defines and returns a connection weights space.
    
    Args:
        - folder (STR): Folder path. If defined, the parameter set dictionary is pickled and saved to this folder.
    
    Returns:
        - model_weights_set (DICT): a weight space dictionary.
    
    """
    import itertools
    import numpy as np
    
    # Set up the model's parameter search space.
    model_weights_set = []
    
    Phon2Gram = [1.0]
    Gram2Sem = [1.0]

    Phon2WK = np.linspace(0,1,2)
    WK2Sem = np.linspace(0,1,2)
    
    
    
    weight_iter = itertools.product(Phon2Gram, Gram2Sem, Phon2WK, WK2Sem)
    
    for weight in weight_iter:
        weights = {'C9':weight[0],
                   'C11':weight[1],
                   'WK5':weight[2],
                   'WK4':weight[3]}

        model_weights_set.append(weights)
    
    # Defining parameter name mapping
    weight_name_mapping = {'C9':'Phon2Gram',
                           'C11':'Gram2Sem',
                           'WK5':'Phon2WK',
                           'WK4':'WK2Sem'}
                           
                
    
    if folder:
        st_save(model_weights_set, 'weights_set', folder, 'params')
        st_save(weight_name_mapping, 'weight_name_mapping', folder, 'params')
    
    return (model_weights_set, weight_name_mapping) 

def grid_search(model, utter_gen, input_name, max_time, folder, model_params_set=[], model_weights_set=[], num_restarts=10, seed=None, verbose=1, save_models=True):
    """
    Runs model "model" for all the inputs in "utter_gen" over the search space defined by "model_params_set" and  "model_weights_set".
    For each point of the search space, model is ran "num_restarts" times.
    
    Args:
        - model (): the model
        - utter_gen (): the lingustic input generator.
        - input_name (STR): name of the input (necessary since for now we only use macros as inputs)
        - model_params_set (ARRAY): Array of model parameters dict.
        - model_weights_set (ARRAY): Array of model weights dict
        - num_restarts (INT): Number of restarts for each model run.
        
    Returns:
        - output (ARRAY): Array of model's summarized outputs for each run in the grid search
    """
    import time
    t0 = time.time()

    grid_output = []
    count = 1
    
    num_sim = len(utter_gen.ling_inputs)*num_restarts*len(model_params_set)*len(model_weights_set)
    
    for model_params in model_params_set:
        model.update_params(model_params)
        for weight_params in model_weights_set:
            model.update_weights(weight_params)
            for name in utter_gen.ling_inputs:
                param_dict = {'input_name':input_name, 'num_restarts': num_restarts}
                param_dict.update(model_params)
                param_dict.update(weight_params)
                for i in range(num_restarts):
                    start = time.time()
                    sim_name = '%s_%s' %(input_name, name)
                    sim_output = run(model, utter_gen, name, sim_name=sim_name, sim_folder=folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=[], save=save_models, anim=False, anim_step=10)
                    # Summerize output
                    summarized_output = summarize_data(sim_output, utter_gen.ground_truths)
                    run_output = {'input_name':input_name, 'params':param_dict, 'sim_output':summarized_output}
                    grid_output.append(run_output)
                    
                    end = time.time()
                    sim_time = end - start
                    remaining_time = (num_sim - count)*sim_time
                    remaining_time = time.strftime("%H:%M:%S", time.gmtime(remaining_time))
                    if verbose>0:
                        print "RUN %i OF %i (%.2fs) (remaining %s)" %(count, num_sim, sim_time, remaining_time)
                    count +=1
    
    tf = time.time()
    tot_time = tf-t0
    grid_time = time.strftime("%H:%M:%S", time.gmtime(tot_time))
    if verbose>0:
        print "TOTAL GRID SEARCH TIME: %s" %(grid_time)
    return grid_output
    
def run_grid_search(sim_name='', sim_folder=TMP_FOLDER, seed=None, save=True, intermediate_save=True, speak=True):
    """
    Runs the production model using grid_search.
    
    Returns:
        - output ({input_name(STR):grid_search_output(ARRAY)}
    If save = True, saves results to .json file
    If intermediate_save = True: saves to json at the end of each grid_search
    """
#    import numpy as np
    
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
    random.seed(seed)
    
    sim_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    
    if not(sim_name):
        sim_name = '%s_(%s)' %(sim_time, str(seed))
    else:
        sim_name = '%s_%s_(%s)' %(sim_time, sim_name, str(seed))
    
    folder = '%s/%s/' %(sim_folder, sim_name)
    
    verbose = 1
        
    # Defining the number of restarts
    NUM_RESTARTS = 2

    # Defining fixed input rate
    INPUT_RATE = 10 # This serves as a time reference for the range of Tau and task parameters 
    INPUT_STD = 0.3
    INPUT_OFFSET = 10
    
    # Defining simulation time
    max_time = 10*INPUT_RATE
    
    
    # Saving meta parameters
    meta_params = {'seed':seed, 'num_restarts':NUM_RESTARTS, 'input_rate':INPUT_RATE, 'input_std':INPUT_STD, 'max_time':max_time}
    st_save(meta_params, 'meta_parameters', folder, 'params')
    
    # Set up and save the model's parameter search space.
    (model_params_set, param_name_mapping) = parameter_space(folder, INPUT_RATE)
    
    # Set up and save the model's connect weights search space.
    (model_weights_set, weight_name_mapping) = weight_space(folder)
    
    #Setting up and saving model
    semantics_name = 'TCG_semantics_dev'
    grammar_name = 'TCG_grammar_VB_2route'
    model  = set_model(semantics_name, grammar_name)
    st_save(model, model.name, folder)
    
    # Defining inputs.
    ling_input_file = 'ling_inputs_2route_aphasia.json'
    
    # Define the set of inputs on which the model will be run.                        
    aphasia_inputs = [u'irreversible(pas)', u'reversible_animate_pt(act)', u'reversible_animate_pt(pas)', 
                      u'irreversible(act)', u'reversible_animate(act)', u'counterfactual(pas)',
                      u'reversible_animate_agt(pas)', u'reversible_animate(pas)', u'reversible_animate_agt(act)',
                      u'counterfactual(act)']

    test_input = [u'irreversible(pas)']
                  
    inputs = test_input
    output = {}
    print "SIMULATION STARTING"
    start_time = time.time()
    # Run the grid search for inputs X parameters X weights X num_restarts
    count = 1
    for name in inputs:
        input_name = name
        print "\nProcessing input: %s (%i/%s)" %(input_name, count,len(inputs))
        #Setting up and saving input generator
        utter_gen = set_inputs(model, ling_input_file, name, speed_param=INPUT_RATE, offset=INPUT_OFFSET, std=INPUT_STD)
        st_save(utter_gen, 'utter_gen_' + input_name, folder)
        
        grid_output = grid_search(model=model, utter_gen=utter_gen, input_name=input_name, max_time=max_time, folder=folder, model_params_set=model_params_set, model_weights_set=model_weights_set, num_restarts=NUM_RESTARTS, seed=seed, verbose=verbose, save_models=False)
        
        output[name] = grid_output
        
        # if intermediate_save, saves to json each grid_search
        if intermediate_save:
            print "SAVING"
            st_save(grid_output, name, folder,'grd')
            grid_search_to_csv(grid_output, folder, input_name, meta_params, model_params_set, param_name_mapping, weight_name_mapping)
        
        # If speak, give audio feedback
        if speak:
            ls.tell_me('Grid search %i done. %i remaining.' %(count, len(inputs) - count))
        count +=1
    
    # saves full grid search
    if save:
        st_save(output, 'full_grid_search', folder, 'grd')
        if not(intermediate_save):
            print "SAVING ALL"
            for input_name, grid_output in output.iteritems():
                grid_search_to_csv(grid_output, folder, input_name, meta_params, model_params_set, param_name_mapping)
    print "\nDONE!"
    end_time = time.time()
    sim_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
    print "TOTAL SIMULATION TIME: %s" %sim_time
    
    # if speak, give audio feedback
    if speak:
        ls.tell_me('Your work is done.')
        
    return output

def grid_search_to_csv(grid_output, folder, input_name, meta_params, model_params_set, param_name_mapping, weight_name_mapping):
    """
    Only saves the statistical analysis of run outputs
    """
    pass
    import numpy as np
    param_names = meta_params.keys() + grid_output[0]['params'].keys()
    gram_output_names = grid_output[0]['sim_output']['GramWM'].keys()
    wk_output_names = grid_output[0]['sim_output']['WkWM'].keys()
    sem_output_names = grid_output[0]['sim_output']['SemWM'].keys()
    header = [param_name_mapping.get(name, name) for name in param_names] + gram_output_names + wk_output_names + sem_output_names
    line = lambda vals: ','.join([str(v) for v in vals]) + '\n'

    file_name = './%s/%s.csv' %(folder, input_name)
    with open(file_name, 'w') as f:
         header = line(header)
         f.write(header)
         for output in grid_output:
            params = output['params']
            params.update(meta_params) # adding meta parameters
            param_row = []
            for name in param_names:
                val = params[name] if params[name]!=None else np.NaN
                param_row.append(val)
            
            sim_output = output['sim_output']
            output_row = []
            # GramWM
            sim_stats = sim_output['GramWM']
            for name in gram_output_names:
                val = sim_stats[name]
                output_row.append(val)
                
            # WkWM
            sim_stats = sim_output['WkWM']
            for name in wk_output_names:
                val = sim_stats[name] if sim_stats[name] else np.NaN
                output_row.append(val)

            # SemWM
            sim_stats = sim_output['SemWM']
            for name in sem_output_names:
                val = sim_stats[name] if sim_stats[name] else np.NaN
                output_row.append(val)
            
            # write to csv
            new_line = line(param_row + output_row)
            f.write(new_line)

if __name__=='__main__':
    model = set_model()
#    model.system2dot(image_type='png', disp=True)
    out = run_diagnostic()
#    print out
#    run_grid_search(sim_name='test')





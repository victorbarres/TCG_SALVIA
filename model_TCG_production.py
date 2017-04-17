# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Functions required to run the TCG production system defined in TCG_model as "TCG_production_system".
 - Set the model and the input generator using set_model() and set_input()
 - If the model is to be run only on one input and one set of parameter use run()
 - Run directly a model using run_model()
 - If the model is to be run as part of grid search over a parameter space use "run_grid_search"
"""
from __future__ import division
import random
import time
import json

from TCG_models import TCG_production_system
from viewer import TCG_VIEWER
from loader import TCG_LOADER
from schema_theory import st_save
from analysis_prod import prod_summary, BLEU
import language_schemas as ls

TMP_FOLDER = './tmp'

##################
#### RUNNING MODEL
def set_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', model_params = {}):
    """
    Sets up a TCG production model.
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - model_prams (DICT): Dictionary defining the model parameters (if different than default)
    
    Returns: 
        - production model
    """
    
    model = TCG_production_system(grammar_name=grammar_name, semantics_name=semantics_name)
    if model_params:
        model.update_params(model_params)
    
    return model
    
def set_inputs(model, input_name, sem_input_file='diagnostic.json', sem_input_macro=False, speed_param=10, offset=0, std=0):
    """
    Sets up a TCG ISRF inputs generator for TCG production model.
    
    Args:
        - model (): model to which the inputs will be sent
        - input_name (STR): name of the input to be used.
        - sem_input_file (STR): Semantic input file name. For non-macro input, set to 'ALL' to load all inputs from file.
        - sem_input_macro (BOOL): True is the input is an ISRF macro.
        - speed_param (FLOAT): multiplier of the rate defined in the ISRF input (by default the ISFR rate is 1.)
        - offset (FLOAT):
        - std (FLOAT): standard deviation of the uniform distribution used around a mean utter time to determine the actual utter time.
    
    Returns:
        - input SEM_GENERATOR object.
    """
    SEM_INPUT_PATH = './data/sem_inputs/'
    
    
    conceptLTM = model.schemas['Concept_LTM']
    if not(sem_input_macro):
        sem_inputs = TCG_LOADER.load_sem_input(sem_input_file, SEM_INPUT_PATH)
        if input_name == 'ALL':
            sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param=speed_param, offset=offset, std=std, is_macro=sem_input_macro)
            sem_gen.ground_truths = TCG_LOADER.load_ground_truths(sem_input_file, SEM_INPUT_PATH)
        else:
            sem_input = {input_name:sem_inputs[input_name]}
            sem_gen = ls.SEM_GENERATOR(sem_input, conceptLTM, speed_param=speed_param, offset=offset, std=std, is_macro=sem_input_macro)
            ground_truths = TCG_LOADER.load_ground_truths(sem_input_file, SEM_INPUT_PATH)
            sem_gen.ground_truths = ground_truths.get(input_name, None)
    if sem_input_macro:
        sem_inputs = TCG_LOADER.load_sem_macro(input_name, sem_input_file, SEM_INPUT_PATH)
        sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param=speed_param, offset=offset, std=std, is_macro=sem_input_macro)
        ground_truths = TCG_LOADER.load_ground_truths(sem_input_file, SEM_INPUT_PATH)
        sem_gen.ground_truths = ground_truths.get(input_name, None)
    
    return sem_gen
    
def run(model, sem_gen, input_name, sim_name='', sim_folder=TMP_FOLDER, max_time=900, seed=None, verbose=0, prob_times=[], save=False, anim=False, anim_step=10):
    """
    Run the model "model" for an semantic generator "sem_gen" using the input "input_name"
    Verbose modes: 0,1 -> no output printed. 2 -> only final utterance printed, 3 -> input and utterances printed as they are received and produced. >3 -> 10steps after sem_input received added to prob_times as well as 10 steps before max_time
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
        st_save(sem_gen, 'sem_gen', FOLDER)
    
    # initializing generator for the model.
    generator = sem_gen.sem_generator(input_name, verbose = (verbose>0))
    (sem_insts, next_time, prop) = generator.next()
    model.initialize_states() # initializing model
    
    if verbose > 1:
        prob_times.append(max_time-10)# Will save the state 10 steps before max_time
    
    outputs = {}
    test_not_empty = lambda l: [x for x in l.values() if x!= None] != []
    
    for t in range(max_time):
        if  next_time != None and t>=next_time:
            (sem_insts, next_time, prop) = generator.next()
            model.set_input(sem_insts)
            if verbose > 1:
                prob_times.append(t + 10) #Will save the state 10 step after introduction of new inputs.
        model.update()
        # Store output
        output = model.get_output()
        if test_not_empty(output): # filter out outputs with all values == None
            outputs[t] = output
        # Display methods
        if output['Grammatical_WM_P'] and output['Grammatical_WM_P'][0]['phon_form']:
            if verbose > 1:
                print "t:%i, '%s'" %(t, ' '.join(output['Grammatical_WM_P'][0]['phon_form']))
            if verbose > 1:
                prob_times.append(t + 10) #Will save the state 10 steps after utterance
        if t in prob_times: # Saving figures for prob times.
            TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM_P'], model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER, file_type='png', show=False)
            TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER, file_type='png', show=False)
            TCG_VIEWER.display_semWM_state(model.schemas['Semantic_WM_P'], folder = FOLDER, file_type='png', show=False)
#        if t>=2000: # Saving all_figures
##            TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM_P'], model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER, file_type='png', show=False)
#            TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER, file_type='png', show=False)
##            TCG_VIEWER.display_semWM_state(model.schemas['Semantic_WM_P'], folder = FOLDER, file_type='png', show=False)
    if save:
        model.save_sim(file_path = FOLDER, file_name = 'output')
        
    # Prints utterance in verbose mode.
    if verbose>1:                
        print get_produced_utterances(outputs)
           
    # Display end states
    if verbose>2:
        model.schemas['Grammatical_WM_P'].show_dynamics()
        
    if anim:
        if save:
            print "saving animation (might take some time!)"
            model.schemas['Grammatical_WM_P'].show_dynamics_anim(folder=FOLDER, step=anim_step)
        else:
            model.schemas['Grammatical_WM_P'].show_dynamics_anim(step=anim_step)
        
         
    model.reset() # Gets model ready for next use.
    
    return outputs   

def get_produced_utterances(outputs):
    """
    Args:
        - outputs (DICT): output generate by run()
    Returns:
        - produced utterances from run outputs
    """
    utterance_list = []
    start= '<START>'
    end ='<END>'
    produced_utterance = ''
    for t in sorted(outputs):
        w = outputs[t]['Phonological_WM_P']
        if w:
            utterance = '<%i>%s' %(t, ' '.join(w))
            produced_utterance += utterance
            utterance_list.append(' '.join(w))
            
    utterance_output = start + produced_utterance + end if produced_utterance else None
        
    return utterance_output, utterance_list

def get_requested_info(outputs):
    """
    Args:
        - outputs (DICT): output generate by run()
    Returns:
        - TD requested info
    """
    request_list = []
    start= '<START>'
    end = '<END>'
    requested_info = ''
    for t in sorted(outputs):
        r = outputs[t]['Semantic_WM']
        if r:
            request = '<%i>%s(%s)' %(t, r['missing_info'], r['var_name'])
            requested_info += request
            request_list.append(r)
    request_output = start + requested_info + end if requested_info else None
    return request_output, request_list

def bleu_scores(utter_list, ground_truth, n_gram=1):
    """
    Returns the listof BLEU scores for each utterance that composes prod_utterance defined as the output of get_produced_utterances()
    """
    scores = []
    for utterance in utter_list:
        score = BLEU(utterance, ground_truth, n_gram)
        scores.append(score)
    return scores
    
def summarize_data(outputs, ground_truths=None):
    """
    Args:
        - outputs (DICT): output generate by run()
        - ground_truths (ARRAY): Array of ground truth utterances
    Returns:
        - summary of outputs from run()
    
    Notes:
        - should take a function from the analyses modules as argument.
    """
    # GramWM
    data_to_analyze = [] # data should be ordered by time
    times = outputs.keys()
    times.sort()
    for t in times:
        v = outputs[t]['Grammatical_WM_P']
        if v:
            data_to_analyze.extend(v)
    gram_analysis = prod_summary(data_to_analyze)
    
    # PhonWM
    phon_analysis = {}
    utter, utter_list = get_produced_utterances(outputs)
    phon_analysis['utterance'] = utter
    max_BLEU_score = None
    if ground_truths and utter_list:
        BLEU_scores = bleu_scores(utter_list, ground_truths)
        max_BLEU_score = max(BLEU_scores)
    phon_analysis['max_BLEU_score'] = max_BLEU_score
        
    # SemWM
    sem_analysis = {}
    request, request_list = get_requested_info(outputs)
    sem_analysis['requested_info'] = request
    sem_analysis['num_requests'] = len(request_list)
    sem_analysis['first_request']= request_list[0]['var_name'] if len(request_list)>0 else None
    
    summary = {'GramWM':gram_analysis, 'PhonWM':phon_analysis, 'SemWM':sem_analysis}
    return summary
                       
def run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', sim_name='', sim_folder=TMP_FOLDER, model_params = {}, input_name='woman_kick_man_static', sem_input_file='diagnostic.json', sem_input_macro=False, max_time=900, seed=None, speed_param=10, offset=0, std=0, prob_times=[], verbose=0, save=True, anim=False,  anim_step=10):
    """
    Runs the model
    
    Returns
        - out (ARRAY): Array of model's outputs (single output if not macro, series of output if macro.)
    """
    model = set_model(semantics_name, grammar_name, model_params=model_params)
    sem_gen = set_inputs(model, input_name, sem_input_file, sem_input_macro, speed_param, offset=offset, std=std)
        
    ground_truth = sem_gen.ground_truths
    
    out = {}
    if sem_gen.is_macro:
        for name in sem_gen.sem_inputs:
            out[name] = run(model, sem_gen, name, sim_name=sim_name, sim_folder=sim_folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
    else:
        out[input_name] = run(model, sem_gen, input_name, sim_name=sim_name, sim_folder=sim_folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
    
    if verbose > 0:
        out2str = ''
        for k,v in out.iteritems():
            (utter, utter_list) = get_produced_utterances(v)
            (info, info_list) = get_requested_info(v)
            out2str += '\n\n#############\n'
            out2str += 'macro: %s\n' %sem_gen.is_macro
            if sem_gen.is_macro:
                out2str += 'macro_name: %s \n' % input_name 
            out2str += 'input_name: %s\n' %k
            out2str += 'utterances:\n'
            out2str += '%s\n' % utter
            out2str += 'requested info:\n'
            out2str += '%s\n' % info
            out2str += 'analysis:\n'
            out2str += '%s\n\n' %json.dumps(summarize_data(v, ground_truth), sort_keys=True, indent=4)
            out2str += '#############'
        print out2str
    return out, out2str
    
###############
#### DIAGNOSTIC 
def run_diagnostics(verbose=2, prob_times=[]):
    """
    Allows to run a set of diagnostics.
    """
    DIAGNOSTIC_FILE = 'diagnostic.json'
    SEM_MACRO = False
    SPEED_PARAM = 100
    OFFSET = 100
    STD = .3
    MODEL_PARAMS = {'Control.task.start_produce':500, 
                    'Control.task.time_pressure':100, 
                    'Grammatical_WM_P.dyn.ext_weight':1.0, 
                    'Grammatical_WM_P.C2.prune_threshold': 0.01, 
                    'Grammatical_WM_P.C2.coop_weight':1.0, 
                    'Grammatical_WM_P.C2.comp_weight':-10.0, 
                    'Grammatical_WM_P.C2.coop_asymmetry':1.0}
    
    # Attempts to model lesion
#    MODEL_PARAMS['Grammatical_WM_P.C2.coop_weight']=0.1 # Reduce cooperation weights
#    MODEL_PARAMS['Grammatical_WM_P.dyn.noise_std']=2.0 # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
#    MODEL_PARAMS['Grammatical_WM_P.C2.prune_threshold']=0.2 # Change prune threshold (shoudl be done in relation to initial activation values.)
#    MODEL_PARAMS['Grammatical_WM_P.dyn.k'] = 3.4 # Interesting effects, bifurcation at a given value.
#    MODEL_PARAMS['Grammatical_WM_P.dyn.act_rest'] = 0.001 # Act rest does not take into account the noise.

    ### GENERAL PARAMETERS
    semantics_name = 'TCG_semantics_main'
    grammar_name='TCG_grammar_VB_main'  
    max_time = 1500
    seed = None
    save = True
    anim = False
    anim_step = 1
    ###    
    
    model = set_model(semantics_name, grammar_name, model_params = MODEL_PARAMS)
    my_inputs = set_inputs(model, 'ALL', sem_input_file=DIAGNOSTIC_FILE, sem_input_macro=SEM_MACRO, speed_param=SPEED_PARAM, offset=OFFSET, std=STD)
    
    input_names = my_inputs.sem_inputs.keys()
    diagnostic_list = dict(zip(range(len(input_names)), input_names))
    
    print "\n\nDiagnostic cases\n\n"
    for num, name in diagnostic_list.iteritems():
       print "%i -> %s" %(num, name)
     
    input_vals = raw_input("\nInput case numbers as (e.g 1, 2, 6, 7). For all input use ALL:\n->")   
    if input_vals == 'ALL':
        input_vals = diagnostic_list.keys()
        input_vals.sort()
    else:
        input_vals = [int(s.strip()) for s in input_vals.split(',')]
    
    diagnostic_cases = [diagnostic_list[value] for value in input_vals]
    
    for input_name in diagnostic_cases:
        print "\nINPUT NAME: %s\n" %input_name
        print "\nSIMULATION RUN:\n"
        res = run(model, my_inputs, input_name, sim_name='', sim_folder=TMP_FOLDER, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, save=save, anim=anim, anim_step=anim_step)
#        print "\nRESULTS:\n"
#        print res

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
    
    Notes:
    - Should I allow this to be passed to a model?
    - For many of those things I should allow those to be saved and then reloaded.
    - I NEED TO INCLUDE THE USE OF GROUPS LEXICAL VS NON-LEXICAL CXN PARAMETERS!!!
    - I NEED TO INCLUDE THE STYLE PARAMETERS
    
    """
    import itertools
    import numpy as np
    
    # Defining fixed input rate
    INPUT_RATE = input_rate # This serves as a time reference for the range of Tau and task parameters

    # Set up the model's parameter search space.
    model_params_set = []
    
    # Task parameters
    start_produces = [10] #np.linspace(1, INPUT_RATE*10, 2)
    time_pressures = [INPUT_RATE/2, INPUT_RATE*5] #np.linspace(INPUT_RATE/2, INPUT_RATE*10, 10)
    
    # C2 parameters
    coop_weights =  [1.0] #np.linspace(1.0, 10.0, 2)
    coop_asymmetries = [1.0] #np.linspace(0.0, 1.0, 2)
    comp_weights = [-10.0]
    max_capacity = [None]
    prune_thresholds = [0.01] # Change prune threshold (should be done in relation to initial activation values.) #0.01 # Manipulations can yield "broca's aphasia" (0.3)
    conf_tresholds = [0.3] #np.linspace(0.1, 0.9, 2) # np.linspace(0.3,0.3, 1) #0.7
    sub_threholds = [0.8]
    deact_weights = [0.0] #np.linspace(0.0, 0.9, 2)
    
    # Dyn parameters
    taus = [INPUT_RATE*10] #[INPUT_RATE/10, INPUT_RATE*10] #np.linspace(int(INPUT_RATE/10), INPUT_RATE*10, 3) # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
    ks= [10] #np.linspace(1, 10, 2) # Interesting effects, bifurcation at a given value.
    act_rests = [0.001] # Act rest does not take into account the noise.
    noise_stds = [1.0] #np.linspace(1.0, 2.0, 2) # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
    ext_weights = [1.0] #np.linspace(1, 10, 2)
    
    param_iter = itertools.product(start_produces, time_pressures, coop_weights, coop_asymmetries, comp_weights, max_capacity, prune_thresholds, conf_tresholds, sub_threholds, deact_weights, taus, ks, act_rests, noise_stds, ext_weights)
    for start_produce, time_pressure, coop_weight, coop_asymmetry, comp_weight, max_capacity, prune_threshold, conf_threshold, sub_threshold, deact_weight, tau, k, act_rest, noise_std, ext_weight in param_iter:
                params = {'Control.task.start_produce':start_produce,  
                          'Control.task.time_pressure':time_pressure,
                          'Grammatical_WM_P.C2.coop_weight':coop_weight, 
                          'Grammatical_WM_P.C2.coop_asymmetry':coop_asymmetry,
                          'Grammatical_WM_P.C2.comp_weight':comp_weight, 
                          'Grammatical_WM_P.C2.max_capacity':max_capacity,
                          'Grammatical_WM_P.C2.prune_threshold': prune_threshold, 
                          'Grammatical_WM_P.C2.confidence_threshold':conf_threshold,
                          'Grammatical_WM_P.C2.sub_threshold_r':sub_threshold,
                          'Grammatical_WM_P.C2.deact_weight':deact_weight,
                          'Grammatical_WM_P.dyn.tau':tau, # Need to analyze the impact of that factor with respect to the rates of input to other WM and their own tau.
                          'Grammatical_WM_P.dyn.k': k,
                          'Grammatical_WM_P.dyn.act_rest': act_rest,
                          'Grammatical_WM_P.dyn.noise_std':noise_std,
                          'Grammatical_WM_P.dyn.ext_weight':ext_weight}

                model_params_set.append(params)
    
    # Defining parameter name mapping
    param_name_mapping = {'Control.task.start_produce':'start_produce',  
                      'Control.task.time_pressure':'time_pressure',
                      'Grammatical_WM_P.C2.coop_weight':'coop_weight', 
                      'Grammatical_WM_P.C2.coop_asymmetry':'coop_asymmetry',
                      'Grammatical_WM_P.C2.comp_weight':'comp_weight',
                      'Grammatical_WM_P.C2.max_capacity':'max_capacity',
                      'Grammatical_WM_P.C2.prune_threshold': 'prune_threshold', 
                      'Grammatical_WM_P.C2.confidence_threshold':'conf_threshold',
                      'Grammatical_WM_P.C2.sub_threshold_r':'sub_threshold',
                      'Grammatical_WM_P.C2.deact_weight':'deact_weight',
                      'Grammatical_WM_P.dyn.tau':'tau',
                      'Grammatical_WM_P.dyn.k':'k',
                      'Grammatical_WM_P.dyn.act_rest':'act_rest',
                      'Grammatical_WM_P.dyn.noise_std':'noise_std',
                      'Grammatical_WM_P.dyn.ext_weight':'ext_weight'}
                
    
    if folder:
        st_save(model_params_set, 'parameter_set', folder, 'params')
        st_save(param_name_mapping, 'param_name_mapping', folder, 'params')
    
    return (model_params_set, param_name_mapping) 
        
        
def grid_search(model, sem_gen, input_name, max_time, folder, model_params_set=[], num_restarts=10, seed=None, verbose=1, save_models=True):
    """
    Runs model "model" for all the inputs in "sem_gen" over the search space defined by "model_params_set".
    For each point of the search space, model is ran "num_restarts" times.
    
    Args:
        - model (): the model
        - sem_gen (): the semantic input generator. Needs to be generated by macros
        - input_name (STR): name of the input (necessary since for now we only use macros as inputs)
        - model_params_set (ARRAY): Array of model parameters dict.
        - num_restarts (INT): Number of restarts for each model run.
        
    Returns:
        - output (ARRAY): Array of model's summarized outputs for each run in the grid search
    """
    import time
    t0 = time.time()

    grid_output = []
    count = 1
    
    num_sim = len(sem_gen.sem_inputs)*num_restarts*len(model_params_set)
    
    for model_params in model_params_set:
        model.update_params(model_params)
        for name in sem_gen.sem_inputs:
            param_dict = {'input_name':input_name, 'num_restarts': num_restarts}
            param_dict.update(model_params)
            # Storing the parameters defined by the input names of a macro input.
            param_vals = eval(name)
            param_dict.update(param_vals)
            for i in range(num_restarts):
                start = time.time()
                sim_name = '%s_%s' %(input_name, name)
                sim_output = run(model, sem_gen, name, sim_name=sim_name, sim_folder=folder, max_time=max_time, seed=seed, verbose=verbose, prob_times=[], save=save_models)
                # Summerize output
                summarized_output = summarize_data(sim_output, sem_gen.ground_truths)
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
    NUM_RESTARTS = 10

    # Defining fixed input rate
    INPUT_RATE = 100 # This serves as a time reference for the range of Tau and task parameters 
    INPUT_OFFSET = 0
    INPUT_STD = 0
    
    # Defining simulation time
    max_time = 10*INPUT_RATE
    
    
    # Saving meta parameters
    meta_params = {'seed':seed, 'num_restarts':NUM_RESTARTS, 'input_rate':INPUT_RATE, 'input_offset':INPUT_OFFSET, 'input_std':INPUT_STD, 'max_time':max_time}
    st_save(meta_params, 'meta_parameters', folder, 'params')
    
    # Set up and save the model's parameter search space.
    (model_params_set, param_name_mapping) = parameter_space(folder, INPUT_RATE)
    
    #Setting up and saving model
    semantics_name = 'TCG_semantics_main'
    grammar_name = 'TCG_grammar_VB_SVO_only'
    model  = set_model(semantics_name, grammar_name)
    st_save(model, model.name, folder)
    
    # Defining inputs.
    sem_input_file = 'kuchinsky_simple.json'
    sem_input_macro = True # For now it only uses macros
    
    # Define the set of inputs on which the model will be run.
    #    inputs = ["scene_girlkickboy"]
    #    inputs = ["woman_kick_man_static", "young_woman_punch_man_static", "woman_punch_man_kick_can_static"]
    #    inputs = ["woman_kick_man_static"]
    
    benchmark_inputs = ["test_naming", "test_naming_ambiguous", "test_naming_2", "young_woman_static","young_woman_dyn","woman_kick_man_static", "woman_kick_man_dyn", "young_woman_punch_man_static", "young_woman_punch_man_dyn", "woman_punch_man_kick_can_static", "woman_punch_man_kick_can_dyn", "woman_in_blue_static"] 

    kuchinksy_inputs = [u'event_agent_patient_action', u'patient_event_agent_action', u'action_event_agent_patient', 
                         u'event_agent_action_patient', u'event_patient_agent_action', u'action_patient_agent_event', 
                         u'action_patient_event_agent', u'patient_agent_action_event', u'patient_agent_event_action', 
                         u'agent_action_event_patient', u'action_agent_event_patient', u'patient_action_event_agent', 
                         u'event_action_agent_patient', u'event_patient_action_agent', u'agent_event_patient_action', 
                         u'agent_patient_action_event', u'patient_event_action_agent', u'action_agent_patient_event', 
                         u'agent_action_patient_event', u'agent_patient_event_action', u'event_action_patient_agent', 
                         u'patient_action_agent_event', u'agent_event_action_patient', u'action_event_patient_agent'
                        ] # 24 inputs (all the permutations)
                        
    kuchinsky_simple = ["agent_patient_action", "patient_agent_action",
                        "action_agent_patient", "action_patient_agent",
                        "agent_action_patient", "patient_action_agent"
                        ] # 6 inputs (all the permutations)
                        
    kuchinsky_jin = ["scene_incremental", "scene_structural"]
                        
    threshold_inputs = ["girl_man_kick_act_agent_cued", "man_girl_kick_act_patient_cued", "act_kick_girl_man", "act_kick_girl_man_agent_cued","act_kick_man_girl", "act_kick_man_girl_patient_cued",
                        "woman_man_kick_act_agent_cued", "man_woman_kick_act_patient_cued", "act_kick_woman_man", "act_kick_woman_man_agent_cued","act_kick_man_woman", "act_kick_man_woman_patient_cued",
                        "girl_woman_kick_act_agent_cued", "woman_girl_kick_act_patient_cued", "act_kick_girl_woman", "act_kick_girl_woman_agent_cued","act_kick_woman_girl", "act_kick_woman_girl_patient_cued",
                        "young_woman_punch_man_dyn", "young_woman_punch_man_dyn_agent_cued", "young_woman_punch_man_dyn_patient_cued", 
                        "complex1_dyn", "complex2_dyn", "complex3_dyn", "complex4_dyn", "complex5_dyn"
                        ]
                        
    test_inputs = [u'event_action_patient_agent', u'patient_action_agent_event', u'agent_event_action_patient', u'action_event_patient_agent']
                        
    inputs = kuchinsky_jin
    output = {}
    print "SIMULATION STARTING"
    start_time = time.time()
    # Run the grid search for inputs X parameters X num_restarts
    count = 1
    for name in inputs:
        input_name = name
        print "\nProcessing input: %s (%i/%s)" %(input_name, count,len(inputs))
        #Setting up and saving input generator
        sem_gen = set_inputs(model, input_name, sem_input_file, sem_input_macro, speed_param=INPUT_RATE, offset = INPUT_OFFSET, std=INPUT_STD)
        st_save(sem_gen, 'sem_gen_' + input_name, folder)
        
        grid_output = grid_search(model=model, sem_gen=sem_gen, input_name=input_name, max_time=max_time, folder=folder, model_params_set=model_params_set, num_restarts=NUM_RESTARTS, seed=seed, verbose=verbose, save_models=False)
        
        output[name] = grid_output
        
        # if intermediate_save, saves to json each grid_search
        if intermediate_save:
            print "SAVING"
            st_save(grid_output, name, folder,'grd')
            grid_search_to_csv(grid_output, folder, input_name, meta_params, model_params_set, param_name_mapping)
        
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
    
def grid_search_to_csv(grid_output, folder, input_name, meta_params, model_params_set, param_name_mapping):
    """
    Only saves the statistical analysis of run outputs
    """
    import numpy as np
    param_names = meta_params.keys() + grid_output[0]['params'].keys()
    gram_output_names = grid_output[0]['sim_output']['GramWM'].keys()
    sem_output_names = grid_output[0]['sim_output']['SemWM'].keys()
    phon_output_names = grid_output[0]['sim_output']['PhonWM'].keys()
    header = [param_name_mapping.get(name, name) for name in param_names] + gram_output_names + sem_output_names + phon_output_names
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
                val = sim_stats[name]['mean']
                output_row.append(val)
                
            # SemWM
            sim_stats = sim_output['SemWM']
            for name in sem_output_names:
                val = sim_stats[name] if sim_stats[name] else np.NaN
                output_row.append(val)
            
            # PhonWM
            sim_stats = sim_output['PhonWM']
            for name in phon_output_names:
                val = sim_stats[name] if sim_stats[name] else np.NaN
                output_row.append(val)
            
            # write to csv
            new_line = line(param_row + output_row)
            f.write(new_line)
    
if __name__=='__main__':
    run_diagnostics(verbose=0, prob_times=[])
#    run_grid_search()
#    output  = run_grid_search(sim_name='kuchinksy_Jin_SVO_only', sim_folder=TMP_FOLDER, seed=None, save=True, intermediate_save=True, speak=False)
#    run_model()
#    out, out2str = run_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', model_params = {}, input_name="woman_punch_man_dyn", sem_input_file='TCG_AAAI_input.json', sem_input_macro=False, max_time=1000, seed=None, speed_param=100, prob_times=[], verbose=4, save=True, anim=False, anim_step=1)
#    file_name = './%s/output.txt' %TMP_FOLDER
#    with open(file_name, 'w') as f:
#        f.write(out2str)
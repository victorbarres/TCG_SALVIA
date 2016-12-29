# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Functions required to run the TCG production system defined in TCG_model as "TCG_production_system".
 - Set the model and the input generator using set_model() and set_input()
 - If the model is to be run only on one input and one set of parameter use run_model()
 - If the model is to be run as part of grid search over a parameter space use "grid_search"
 - Use main() to run grid_search + run on multiple inputs.
"""
import random

import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_production_system
from viewer import TCG_VIEWER
from prod_analysis import prod_analyses, prod_statistics

TMP_FOLDER = './tmp'
    
def test_run(seed=None):
    """
    Test run function for the production model.
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
        print "seed = %i" %seed
        
    random.seed(seed)
    SEM_INPUT = 'sem_inputs.json' # semantic input files (no macros)
    INPUT_NAME = 'blue_woman_kick_man' # Name of the input to use.
    
    FOLDER = './tmp/TEST_%s_%s/' %(INPUT_NAME, str(seed)) # Folder where the simulation results will be saved.
    
    language_system_P = TCG_production_system(grammar_name='TCG_grammar_VB_main', semantics_name='TCG_semantics_main') # Create model
    
    # Set up semantic input generator    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    sem_inputs = TCG_LOADER.load_sem_input(SEM_INPUT, "./data/sem_inputs/")   
    speed_param = 1
    sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param)
 
    generator = sem_gen.sem_generator(INPUT_NAME)
    
    (sem_insts, next_time, prop) = generator.next() #Getting the initial input.
    
    # Test paramters
    language_system_P.params['Control']['task']['start_produce'] = 3100
    language_system_P.params['Control']['task']['time_pressure'] = 200
    language_system_P.params['Grammatical_WM_P']['C2']['confidence_threshold'] = 0.3
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 3000
    save_states = [30, 700, 2000]
    
    flag = False
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (sem_insts, next_time, prop) = generator.next()
            print "t:%i, sem: %s (prop: %s)" %(t, ', '.join([inst.name for inst in sem_insts]), prop)
            language_system_P.set_input(sem_insts)
        language_system_P.update()
        output = language_system_P.get_output()
        if not(language_system_P.schemas['Grammatical_WM_P'].comp_links) and t>10 and not(flag):
            print "t:%i, Competition done" % t
            flag = True
            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'], language_system_P.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
            language_system_P.params['Control']['task']['start_produce'] = t + 10
        if output['Utter']:
            print "t:%i, '%s'" %(t, output['Utter'])
        if t - set_up_time in save_states:
            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'], language_system_P.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
    
    language_system_P.schemas['Semantic_WM'].show_SemRep()
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=True,  c2_network=False)
    language_system_P.save_sim(FOLDER, 'test_language_output.json')
    
    return language_system_P

def set_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', model_params = {}):
    """
    Sets up a TCG production model.
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - model_prams (dict): Dictionary defining the model parameters (if different than default)
    
    Returns: production model
    """
    
    model = TCG_production_system(grammar_name=grammar_name, semantics_name=semantics_name)
    if model_params:
        model.update_params(model_params)
    
    return model
    
def set_inputs(model, input_name, sem_input_file='diagnostic.json', sem_input_macro=False, speed_param=10):
    """
    Sets up a TCG ISRF inputs generator for TCG production model.
    
    Args:
        - sem_name (STR): Semantic input name.
        - sem_input_file (STR): Semantic input file name. For non-macro input, set to 'ALL' to load all inputs from file.
        - sem_input_macro (BOOL): True is the input is an ISRF macro.
        - speed_param (INT): multiplier of the rate defined in the ISRF input (by default the ISFR rate is 1.)
    
    Returns input SEM_GENERATOR object.
    """
    SEM_INPUT_PATH = './data/sem_inputs/'
    
    conceptLTM = model.schemas['Concept_LTM']
    if not(sem_input_macro):
        sem_inputs = TCG_LOADER.load_sem_input(sem_input_file, SEM_INPUT_PATH)
        if input_name == 'ALL':
            sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param=speed_param)
        else:
            sem_input = {input_name:sem_inputs[input_name]}
            sem_gen = ls.SEM_GENERATOR(sem_input, conceptLTM, speed_param=speed_param)
    if sem_input_macro:
        sem_inputs = TCG_LOADER.load_sem_macro(input_name, sem_input_file, SEM_INPUT_PATH)
        sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param=speed_param)
    
    return sem_gen    
    

def run_model(model, sem_gen, input_name, max_time=900, seed=None, verbose=0, prob_times=[]):
    """
    Run the model "model" for an semantic gerator "sem_gent" using the input "input_name"
    Verbose modes: 0 -> no output printed. 1 -> only final utterance printed, 2 -> input and utterances printed as they are received and produced.
    prob_times ([INT]): For time in list, saves a view of LinguisticWM concise in tmp folder.
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
    random.seed(seed)
    
    FOLDER = '%s/TEST_%s_%s/' %(TMP_FOLDER, input_name, str(seed))
    
    generator = sem_gen.sem_generator(input_name, verbose = (verbose>1))
    (sem_insts, next_time, prop) = generator.next()
    model.initialize_states()
    
    if verbose>2:
        prob_times.append(max_time-10)# Will save the state 10 steps before max_time
    
    out_data = []
    out_utterance = []
    for t in range(max_time):
        if  next_time != None and t>=next_time:
            (sem_insts, next_time, prop) = generator.next()
            model.set_input(sem_insts)
            if verbose>2:
                prob_times.append(t + 10) #Will save the state 10 step after introduction of new inputs.
        model.update()
        # Store output
        output = model.get_output()
        if output['Grammatical_WM_P']:
            out_data.extend(output['Grammatical_WM_P'])
        if output['Utter']:
            if verbose > 1:
                 print "t:%i, '%s'" %(t, output['Utter'])
            out_utterance.append(output['Utter'])
        if t in prob_times:
            TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM'], model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
            
    
    if verbose>2:
        model.schemas['Semantic_WM'].show_SemRep()
        model.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=True,  c2_network=False)
            
    # Output analysis
    res = prod_analyses(out_data)
    model.save_sim(file_path = FOLDER, file_name = 'output.json')
    model.reset()
    
    # Prints utterance in verbose mode.
    if verbose == 1:
        print ' '.join(out_utterance)
    return (res, ' '.join(out_utterance))
    
    
def run_prod_diagnostics(verbose=2, prob_times=[]):
    """
    Allows to run a set of production diagnostics.
    """
    DIAGNOSTIC_FILE = 'diagnostic.json'
    SPEED_PARAM = 20
    MODEL_PARAMS = {'Control.task.start_produce':200, 'Control.task.time_pressure':200, 'Grammatical_WM_P.dyn.ext_weight':1.0, 'Grammatical_WM_P.C2.prune_threshold': 0.1, 'Grammatical_WM_P.C2.coop_weight':1.0, 'Grammatical_WM_P.C2.comp_weight':-10.0, 'Grammatical_WM_P.C2.coop_asymmetry':1.0}
    
    # Attempts to model lesion
#    MODEL_PARAMS['Grammatical_WM_P.C2.coop_weight']=0.1 # Reduce cooperation weights
#    MODEL_PARAMS['Grammatical_WM_P.dyn.noise_std']=10.0 # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
#    MODEL_PARAMS['Grammatical_WM_P.C2.prune_threshold']=0.2 # Change prune threshold (shoudl be done in relation to initial activation values.)
#    MODEL_PARAMS['Grammatical_WM_P.dyn.k'] = 3.4 # Interesting effects, bifurcation at a given value.
#    MODEL_PARAMS['Grammatical_WM_P.dyn.act_rest'] = 0.001 # Act rest does not take into account the noise.

    ### GENERAL PARAMETERS
    semantics_name = 'TCG_semantics_main'
    grammar_name='TCG_grammar_VB_main'  
    max_time =1000
    seed=None
    ###    
    
    model = set_model(semantics_name, grammar_name, model_params=MODEL_PARAMS)
    my_inputs = set_inputs(model, 'ALL', sem_input_file=DIAGNOSTIC_FILE, sem_input_macro = False, speed_param=SPEED_PARAM)
    
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
        res = run_model(model, my_inputs, input_name, max_time, seed, verbose=verbose, prob_times=prob_times)
        print "\nRESULTS:\n"
        print res

def grid_search(input_name, model_params_set=[], num_restarts=10, seed=None):
    """
    Runs model for input "input_name" over the search space defined by "model_params_set".
    For each point of the search space, model is ran "num_restarts" times.
    
    Args:
        - input_name (STR): Name of the semantic input (needs to be in sem_macros.json)
        - model_params_set (ARRAY): Array of model paramters dict.
        - num_restarts (INT): Number of restarts for each model run.
        
    Note: If a macro is used as input, the number of inputs generated by the macro multiplies the parameter space.
        
    To do: I should have grid search take a model and SemGen as input.
    """
    import time
    t0 = time.time()
    
    # Defining inputs.
    sem_input_file = 'sem_macros.json'
    sem_input_macro = True # For now it only uses macros
    
    
    semantics_name = 'TCG_semantics_main'
    grammar_name = 'TCG_grammar_VB_main'
    
    
    #Setting up model
    model  = set_model(semantics_name, grammar_name)
    
    #Setting up input
    sem_gen = set_inputs(model, sem_input_file, input_name, sem_input_macro)
    
    output = []
    count = 1
    
    num_sim = len(sem_gen.sem_inputs)*num_restarts*len(model_params_set)
    
    for model_params in model_params_set:
        model.update_params(model_params)
        for name in sem_gen.sem_inputs:
            param_dict = {'input_name':input_name, 'num_restarts': num_restarts}
            param_dict.update(model_params)
            if sem_input_macro:
                param_vals = eval(name)
                param_dict.update(param_vals)
            for i in range(num_restarts):
                run_output = []
                start = time.time()
                (sim_output, utterance) = run_model(model, sem_gen, name, seed=seed, verbose=0)
                run_output.append(sim_output)
                end = time.time()
                print "SIMULATION %i OF %i (%.2fs)" %(count, num_sim, end - start)
                sim_stats = prod_statistics(run_output)
                run_outputs = { 'params': param_dict, 'sim_stats':sim_stats, 'utterance':utterance}
                output.append(run_outputs)
                count +=1
    
    tf = time.time()
    print "TOTAL SIMULATION TIME: %.2f" %(tf-t0)
    return output
    
    
def run_grid_search():
    """
    Runs the production model using grid_search.
    """
    import numpy as np
    
    # Set up the model's parameter search space.
    model_params_set = []
    start_produce_samples = [800] #np.linspace(1,500,10)
    conf_samples = np.linspace(0.3,0.3, 1)
    for start_param in start_produce_samples:
        for conf_param in conf_samples:
            params = {'Control.task.start_produce':start_param, 
                      'Grammatical_WM_P.C2.confidence_threshold':conf_param}
            model_params_set.append(params)
    
    # Define the set of inputs on which the model will be run.
    inputs = ["test_naming"]
    
    # If seed != None, then all the restart will yield the same results.
    seed=None    
    
    # Define the number of restarts
    num_restarts = 10
    
    # Run the grid search for inputs X parameters X num_restarts
    for name in inputs:
        input_name = name
        output = grid_search(input_name=input_name, model_params_set=model_params_set, num_restarts=num_restarts, seed=seed)
        if output:
            header = {'params':[], 'outputs':['syntactic_complexity_mean', 'syntactic_complexity_std', 'utterance_length_mean', 'utterance_length_std', 'active', 'passive', 'total_constructions', 'produced', 'utterance']}
            dat = []
            for run_dat in output:
                if not header['params']:
                    header['params'] += run_dat ['params'].keys()
                new_row = []
                params_vals = [run_dat['params'][param] for param in header['params']]
                output_stats = run_dat['sim_stats']
                if not output_stats['utterance_lengths']:
                    produced = False
                    syntactic_complexity_mean = np.NaN
                    syntactic_complexity_std = np.NaN
                    utterance_length_mean = np.NaN
                    utterance_length_std = np.NaN
                    active = np.NaN
                    passive = np.NaN
                    total_constructions = np.NaN
                    utterance = ''
                else:
                    produced = True
                    syntactic_complexity_mean = output_stats['syntactic_complexity']['mean']
                    syntactic_complexity_std = output_stats['syntactic_complexity']['std']
                    utterance_length_mean = output_stats['utterance_lengths']['mean']
                    utterance_length_std = output_stats['utterance_lengths']['std']
                    active = output_stats['cxn_usage_count'].get('SVO', 0)
                    passive = output_stats['cxn_usage_count'].get('PAS_SVO', 0)
                    total_constructions = output_stats['cxn_usage_count']['total_count']
                    utterance = run_dat['utterance']
                output_vals = [syntactic_complexity_mean, syntactic_complexity_std, utterance_length_mean, utterance_length_std, active, passive, total_constructions, produced, utterance]
                new_row += params_vals + output_vals
                dat.append(new_row)
        
        # Write results to file
        line = lambda vals: ','.join([str(v) for v in vals]) + '\n'
        file_name = './simulation_analyses/%s.csv' % input_name
        with open(file_name, 'w') as f:
            header = line(header['params'] + header['outputs'])
            f.write(header)
            for d in dat:
                new_line = line(d)
                f.write(new_line)
    
if __name__=='__main__':
    run_prod_diagnostics(verbose=3, prob_times=[])
    
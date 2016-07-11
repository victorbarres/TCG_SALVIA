# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Test cases for the language production schemas defined in language_schemas.py
"""
import random

import language_schemas as ls
from loader import TCG_LOADER
from TCG_models import TCG_production_system
from viewer import TCG_VIEWER
from test_prod_analysis import prod_analyses, prod_statistics
    
def test(seed=None):
    """
    Test Incremental Semantic Representation Format (ISRF) sem inputs
    """
    
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
        print "seed = %i" %seed
    random.seed(seed)
    SEM_INPUT = 'sem_inputs.json'
    INPUT_NAME = 'kick_static'
    FOLDER = './tmp/TEST_%s_%s/' %(INPUT_NAME, str(seed))
    
    language_system_P = TCG_production_system(grammar_name='TCG_grammar_VB_main_pref1', semantics_name='TCG_semantics_main')
    
    # Set up semantic input generator    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    sem_inputs = TCG_LOADER.load_sem_input(SEM_INPUT, "./data/sem_inputs/")   
    speed_param = 1
    sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param)
 
    generator = sem_gen.sem_generator(INPUT_NAME)
    
    (sem_insts, next_time, prop) = generator.next()
    
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

def test_params_dyn(seed=None):
    """
    Grid search algorithm.
    First quick function to test the impact of params on outputs.
    """
    from sys import stdout
    import numpy as np
    
    random.seed(seed)
    # Choose input name
    input_name = 'ditransitive_give'    
    
    # Set up parameter space
    sample_rate = 40
    tau_samples = np.linspace(30,30, 1)
    noise_samples = np.linspace(0.2,0.2, 1)
    k_samples = np.linspace(10.0, 10.0,  1)
    conf_samples = np.linspace(0.4,0.4, 1)
    prune_samples = np.linspace(0.3,0.3,1)
    coop_samples = np.linspace(0.0,2.0, sample_rate)
    comp_samples = np.linspace(-1.0,-1.0,1)
    
    params_samples = []
    for tau_param in tau_samples:
        for k_param in k_samples:
            for noise_param in noise_samples:
                for conf_param in conf_samples:
                    for prune_param in prune_samples:
                        for coop_param in coop_samples:
                            for comp_param in comp_samples:
                                param_set = {'tau':float(tau_param), 
                                             'k':float(k_param), 
                                             'noise_std':float(noise_param), 
                                             'conf_thresh':float(conf_param), 
                                             'prune_thresh':float(prune_param), 
                                             'coop_weight':float(coop_param), 
                                             'comp_weight':float(comp_param)}
                                params_samples.append(param_set)
                                
    num_sims = len(params_samples)
                                
    
    # Running simulations
    num  = 1
    for params in params_samples:
        # Set up model
        language_system_P = TCG_production_system() # Better if I could just reset the model...
        conceptLTM = language_system_P.schemas['Concept_LTM']
      
        grammaticalWM_P = language_system_P.schemas['Grammatical_WM_P']
        
        grammaticalWM_P.params['dyn']['tau'] = params['tau']
        grammaticalWM_P.params['dyn']['act_inf'] = 0.0
        grammaticalWM_P.params['dyn']['L'] = 1.0
        grammaticalWM_P.params['dyn']['k'] = params['k']
        grammaticalWM_P.params['dyn']['x0'] = 0.5
        grammaticalWM_P.params['dyn']['noise_mean'] = 0.0
        grammaticalWM_P.params['dyn']['noise_std'] = params['noise_std']
        grammaticalWM_P.params['C2']['confidence_threshold'] = params['conf_thresh']
        grammaticalWM_P.params['C2']['prune_threshold'] = params['prune_thresh']
        grammaticalWM_P.params['C2']['coop_weight'] = params['coop_weight']
        grammaticalWM_P.params['C2']['comp_weight'] = params['comp_weight']
        grammaticalWM_P.params['C2']['sub_threshold_r'] = 0.8
        grammaticalWM_P.params['C2']['deact_weight'] = 0.0 # When set at 1, the output act as if the start_produce always occured right after new sem elements are introduced.
        grammaticalWM_P.params['style']['activation'] = 0.7
        grammaticalWM_P.params['style']['sem_length'] = 0.3
        
        # Set up input
        sem_inputs = TCG_LOADER.load_sem_input("sem_inputs.json", "./data/sem_inputs/")    
        sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM)
        generator = sem_gen.sem_generator(input_name)
        (sem_insts, next_time, prop) = generator.next()
        stdout.flush();
        stdout.write(" Sim number: %i (%.2f%%)      %s" %(num,num/float(num_sims)*100,"\r"))

        num += 1
        utter = []
        
        set_up_time = -10 #Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
        max_time = 900
        
        # Run production simulation
        for t in range(set_up_time, max_time):
            if next_time != None and t>next_time:
                (sem_insts, next_time, prop) = generator.next()
                language_system_P.set_input(sem_insts)
            language_system_P.update()
            output = language_system_P.get_output()
            if output['Utter']:
               utter.append(output['Utter'])
        
        params['utter'] = ' '.join(utter)
        
    
    file_name = 'test.csv'
    params_name = ['tau', 'k', 'noise_std', 'conf_thresh', 'prune_thresh', 'coop_weight', 'comp_weight', 'utter']
    
    line = lambda vals: ','.join([str(v) for v in vals]) + '\n'
    with open(file_name, 'w') as f:
        header = line(params_name)
        f.write(header)
        for params in params_samples:
            vals = [params[name] for name in params_name]
            new_line = line(vals)
            f.write(new_line)

def test_time_pressure(seed=None):
    
    """
    Grid search algorithm.
    Impact of time pressure
    """
    from sys import stdout
    import numpy as np
    
    random.seed(seed)
    
    # Input name
    input_file = 'sem_inputs.json'
    input_name = 'blue_woman_kick_man'
    
    # Set up parameter space
    start_produce_samples = np.linspace(1,500,20)
    
    params_samples = []
    for start_produce in start_produce_samples:
        param_set = {'start_produce':start_produce}
        params_samples.append(param_set)
        
    num_sims = len(params_samples)
                                
    
    # Running simulations
    num  = 1
    for params in params_samples:
        # Set up model
        language_system_P = TCG_production_system() # Better if I could just reset the model...
        conceptLTM = language_system_P.schemas['Concept_LTM']
        
        control = language_system_P.schemas['Control']
        control.params['task']['start_produce'] = params['start_produce']
        
        # Set up input
        sem_inputs = TCG_LOADER.load_sem_input(input_file, "./data/sem_inputs/")    
        sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM)
        generator = sem_gen.sem_generator(input_name)
        (sem_insts, next_time, prop) = generator.next()
        stdout.flush();
        stdout.write(" Sim number: %i (%.2f%%)      %s" %(num,num/float(num_sims)*100,"\r"))
        
        num += 1
        utter = []
        
        set_up_time = -10 #Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
        max_time = 900
        
        # Run production simulation
        for t in range(set_up_time, max_time):
            if next_time != None and t>next_time:
                (sem_insts, next_time, prop) = generator.next()
                language_system_P.set_input(sem_insts)
            language_system_P.update()
            output = language_system_P.get_output()
            if output['Utter']:
                prod = "[%i, %s]" %(t, output['Utter'])
                utter.append(prod)
        
        params['utter'] = ' '.join(utter)
        
    
    file_name = 'test.csv'
    params_name = ['start_produce', 'utter']
    
    line = lambda vals: ', '.join([str(v) for v in vals]) + '\n'
    with open(file_name, 'w') as f:
        header = line(params_name)
        f.write(header)
        for params in params_samples:
            vals = [params[name] for name in params_name]
            new_line = line(vals)
            f.write(new_line)

def run_model(seed=None):
    """
    """
    SEM_INPUT = 'sem_inputs.json'
    INPUT_NAME = 'kick_static_focus_agent'
    
    language_system_P = TCG_production_system(grammar_name='TCG_grammar_VB_main', semantics_name='TCG_semantics_main')
    
    # Set up semantic input generator    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    sem_inputs = TCG_LOADER.load_sem_input(SEM_INPUT, "./data/sem_inputs/")   
    speed_param = 1
    sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param)
 
    generator = sem_gen.sem_generator(INPUT_NAME)
    
    (sem_insts, next_time, prop) = generator.next()
    
    # Test paramters
    language_system_P.params['Control']['task']['start_produce'] = 400
    language_system_P.params['Control']['task']['time_pressure'] = 200
    language_system_P.params['Grammatical_WM_P']['C2']['confidence_threshold'] = 0.3
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 900
    out_data = []
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (sem_insts, next_time, prop) = generator.next()
            language_system_P.set_input(sem_insts)
        language_system_P.update()
        # Store output
        output = language_system_P.get_output()
        if output['Grammatical_WM_P']:
            out_data.append(output['Grammatical_WM_P'])
        if output['Utter']:
            print "t:%i, '%s'" %(t, output['Utter'])
    
    # Output analysis
    res = prod_analyses(out_data)
    return res

def set_model(sem_input_file, sem_name, sem_input_macro = True, semantics_name='TCG_semantics_main', 
              grammar_name='TCG_grammar_VB_main', params = {}):
    """
    """
    SEM_INPUT_PATH = './data/sem_inputs/'
    
    language_system_P = TCG_production_system(grammar_name=grammar_name, semantics_name=semantics_name)
    
    # Set up semantic input generator    
    conceptLTM = language_system_P.schemas['Concept_LTM']
    if not(sem_input_macro):
        sem_inputs = TCG_LOADER.load_sem_input(sem_input_file, SEM_INPUT_PATH)
        sem_input = {sem_name:sem_inputs[sem_name]}
        sem_gen = ls.SEM_GENERATOR(sem_input, conceptLTM, speed_param=1)
    if sem_input_macro:
        sem_inputs = TCG_LOADER.load_sem_macro(sem_name, sem_input_file, SEM_INPUT_PATH)
        sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM, speed_param=1)
    
    return (language_system_P, sem_gen)

def run_model2(model, generator, seed=None):
    """
    Temporary new version of run_model. 
    """
    (sem_insts, next_time, prop) = generator.next()
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 900
    
    out_data = []
    out_utterance = []
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (sem_insts, next_time, prop) = generator.next()
            model.set_input(sem_insts)
        model.update()
        # Store output
        output = model.get_output()
        if output['Grammatical_WM_P']:
            out_data.append(output['Grammatical_WM_P'])
        if output['Utter']:
            out_utterance.append(output['Utter'])
            
    # Output analysis
    res = prod_analyses(out_data)
    model.reset()
    return (res, ' '.join(out_utterance))

def test_sem_frame(seed=None, input_name=''):
    """
    """
    import time
    t0 = time.time()
    sem_input_macro = True
    
    (model, sem_gen) = set_model('sem_macros.json', input_name, sem_input_macro, semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', params = {})
    
    output = []
    count = 1
    num_restarts = 10
    
    num_sim = len(sem_gen.sem_inputs)*num_restarts
    
    for name in sem_gen.sem_inputs:
        param_dict = {'input_name':input_name, 'num_restarts': num_restarts}
        if sem_input_macro:
            param_vals = eval(name)
            param_dict.update(param_vals)
        for i in range(num_restarts):
            run_output = []
            start = time.time()
            generator = sem_gen.sem_generator(name, verbose=False)
            (sim_output, utterance) = run_model2(model, generator)
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

def grid_search(input_name, model_params_set=[],seed=None):
    """
    """
    import time
    t0 = time.time()
    sem_input_macro = True
    
    (model, sem_gen) = set_model('sem_macros.json', input_name, sem_input_macro, semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', params = {})
    
    output = []
    count = 1
    num_restarts = 30
    
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
                generator = sem_gen.sem_generator(name, verbose=False)
                (sim_output, utterance) = run_model2(model, generator)
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
    
    
def main():
    import numpy as np
    
    model_params_set = []
    start_produce_samples = [800] #np.linspace(1,500,10)
    conf_samples = np.linspace(0.3,0.3, 1)
    for start_param in start_produce_samples:
        for conf_param in conf_samples:
            params = {'Control.task.start_produce':start_param, 
                      'Grammatical_WM_P.C2.confidence_threshold':conf_param}
            model_params_set.append(params)

    for name in ["blue_woman_kick_man_static"]:
        input_name = name
        output = grid_search(input_name=input_name, model_params_set=model_params_set)
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
        
        line = lambda vals: ','.join([str(v) for v in vals]) + '\n'
        file_name = './simulation_analyses/%s.csv' % input_name
        with open(file_name, 'w') as f:
            header = line(header['params'] + header['outputs'])
            f.write(header)
            for d in dat:
                new_line = line(d)
                f.write(new_line)
    
    
if __name__=='__main__':
    test()
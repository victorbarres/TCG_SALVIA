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
    
def test(seed=None):
    """
    Test Incremental Semantic Formulas sem inputs
    """
    
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
        print "seed = %i" %seed
    random.seed(seed)
    SEM_INPUT = 'sem_inputs_debug.json'
    INPUT_NAME = 'test_spec_cxn_incremental'
    FOLDER = './tmp/TEST_%s_%s/' %(INPUT_NAME, str(seed))
    
    language_system_P = TCG_production_system()
#     Display schema system
    language_system_P.system2dot(image_type='png', disp=False, folder = FOLDER)
    
    conceptLTM = language_system_P.schemas['Concept_LTM']

    sem_inputs = TCG_LOADER.load_sem_input(SEM_INPUT, "./data/sem_inputs/")    
    sem_gen = ls.SEM_GENERATOR(sem_inputs, conceptLTM)
 
    generator = sem_gen.sem_generator(INPUT_NAME)
    
    language_system_P.schemas['Grammatical_WM_P'].params['C2']['prune_threshold'] = 0.1
    
    (sem_insts, next_time, prop) = generator.next()
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 900   
    save_states = [50, 100, 450, 550, 650]
    
    for t in range(set_up_time, max_time):
        if next_time != None and t>next_time:
            (sem_insts, next_time, prop) = generator.next()
            print "t:%i, sem: %s (prop: %s)" %(t, ', '.join([inst.name for inst in sem_insts]), prop)
            language_system_P.set_input(sem_insts)
#            language_system_P.schemas['Semantic_WM'].show_SemRep()
        language_system_P.update()
        output = language_system_P.get_output()
        if output['Utter']:
            print "t:%i, '%s'" %(t, output['Utter'])
        if t - set_up_time in save_states:
#            TCG_VIEWER.display_gramWM_state(language_system_P.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'], language_system_P.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
#            TCG_VIEWER.display_gramWM_state(language_system_P.schemas['Grammatical_WM_P'], concise=False, folder = FOLDER)
#            TCG_VIEWER.display_lingWM_state(language_system_P.schemas['Semantic_WM'], language_system_P.schemas['Grammatical_WM_P'], concise=False, folder = FOLDER)
    
#    language_system_P.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_P.schemas['Semantic_WM'].show_SemRep()
#    TCG_VIEWER.display_semWM_state(language_system_P.schemas['Semantic_WM'], folder = FOLDER)
    language_system_P.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
#    language_system_P.schemas['Grammatical_WM_P'].show_state()
#    language_system_P.schemas['Phonological_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    language_system_P.save_sim(FOLDER + 'test_language_output.json')
#    language_system_P.show_params()

def test_params(seed=None):
    """
    First quick function to test the impact of param on outputs
    """
    from sys import stdout
    import numpy as np
    
    random.seed(seed)
    # Chose input name
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
        
    
    file_name = 'test11.csv'
    params_name = ['tau', 'k', 'noise_std', 'conf_thresh', 'prune_thresh', 'coop_weight', 'comp_weight', 'utter']
    
    line = lambda vals: ','.join([str(v) for v in vals]) + '\n'
    with open(file_name, 'w') as f:
        header = line(params_name)
        f.write(header)
        for params in params_samples:
            vals = [params[name] for name in params_name]
            new_line = line(vals)
            f.write(new_line)


if __name__=='__main__':
    test(seed=None)
#    test_params(seed=1)
        




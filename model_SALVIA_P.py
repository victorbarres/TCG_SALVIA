# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG description
"""
import random

from TCG_models import SALVIA_P, SALVIA_P_verbal_guidance
from viewer import TCG_VIEWER
from loader import TCG_LOADER

TMP_FOLDER = './tmp'

def test(seed=None):
    """
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
        print "seed = %i" %seed
    random.seed(seed)
    
    description_system = SALVIA_P_verbal_guidance()

    # Generating schema system graph visualization
#    description_system.system2dot(image_type='png', disp=True)

    # Defining scene input
    FOLDER  = "./data/scenes/"
    SCENE_FILE = "TCG_scene.json"
    SCENE_NAME = 'test'
    SCENE_FOLDER = "%s%s/" %(FOLDER, SCENE_NAME)
    IMG_FILE = SCENE_FOLDER + 'scene.png'
    
    my_scene = TCG_LOADER.load_scene(SCENE_FILE, SCENE_FOLDER)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    description_system.schemas['Control'].params['task']['start_produce'] = 0
    description_system.schemas['Control'].params['task']['time_pressure'] = 300
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 1000
    save_states = [130]
    
    fixations = []
    # Running the schema system
    for t in range(max_time):
        if t== -1*set_up_time:
            
            description_system.schemas['Subscene_recognition'].show_scene(IMG_FILE)
            
        description_system.update()
        output = description_system.get_output()
        if output:
            if output['Utter']:
             print "t:%i, '%s'" %(t, output['Utter'])
            if output['Subscene_recognition']:
                eye_pos = output['Subscene_recognition']['eye_pos']
                subscene = output['Subscene_recognition']['subscene']
                if eye_pos:
                    fixations.append({'time':t, 'pos':eye_pos, 'subscene':subscene})
                vals = [(u,v) for u,v in output['Subscene_recognition'].iteritems() if v]
                if vals:
                    print "t:%i, '%s'" %(t, vals)
#        if t - set_up_time in save_states:
#                TCG_VIEWER.display_WMs_state(description_system.schemas['Visual_WM'], description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
#                TCG_VIEWER.display_gramWM_state(description_system.schemas['Grammatical_WM_P'], concise=True)
#                TCG_VIEWER.display_lingWM_state(description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
    
    description_system.schemas['Visual_WM'].show_SceneRep()
    description_system.schemas['Visual_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Semantic_WM'].show_SemRep()
    description_system.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Grammatical_WM_P'].show_state()
    
    TCG_VIEWER.display_saccades(fixations, IMG_FILE, ss_radius=True)
    
#    description_system.save_sim('./tmp/test_description_output.json')
    
    
def set_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', verbal_guidance=False, model_params = {}):
    """
    Sets up a SALVIA_P.
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - verbal_guidance (BOOL): If true returns SAVLIA_P_verbal_guidance.
        - model_prams (dict): Dictionary defining the model parameters (if different than default)
    
    Returns: SALVIA_P model
    """
    
    if verbal_guidance:
        model = SALVIA_P_verbal_guidance(grammar_name=grammar_name, semantics_name=semantics_name)
    else:
        model = SALVIA_P(grammar_name=grammar_name, semantics_name=semantics_name)
        
    if model_params:
        model.update_params(model_params)
    
    return model
    

def set_inputs(model, input_name, input_file='TCG_scene.json', show_scene=True):
    """
    Sets up a SCENE input for SALVIA_P model
    
    Args:
        - sem_name (STR): Semantic input name.
        - sem_input_file (STR): Semantic input file name. For non-macro input, set to 'ALL' to load all inputs from file.
        - sem_input_macro (BOOL): True is the input is an ISRF macro.
        - speed_param (INT): multiplier of the rate defined in the ISRF input (by default the ISFR rate is 1.)
    
    Returns input SEM_GENERATOR object.
    """
    
    # Defining scene input
    SCENE_INPUT_PATH  = "./data/scenes/"
    SCENE_FOLDER = "%s%s/" %(SCENE_INPUT_PATH, input_name)
    IMG_FILE = SCENE_FOLDER + 'scene.png'
    
    my_scene = TCG_LOADER.load_scene(input_file, SCENE_FOLDER)
    model.set_input(my_scene)
    
    if show_scene:
        model.schemas['Subscene_recognition'].show_scene(IMG_FILE)
    
    return (input_name, IMG_FILE)

def run_model(model, sim_name, max_time=900, seed=None, verbose=0, prob_times=[], IMG_FILE =''):
    """
    Run the model "model".
    
    input_name(STR): input name
    Verbose modes: 0 -> no output printed.
    prob_times ([INT]): 
    IMG_FILE (STR): path to the image file (to display saccades.)
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
    random.seed(seed)
    
    FOLDER = '%s/TEST_%s_%s/' %(TMP_FOLDER, sim_name, str(seed))

    model.verbose = False
    
    model.initialize_states()
    
    out_data = []
    out_fixation = []
    out_utterance = []
     
    if verbose>1:
        prob_times.append(max_time-10)# Will save the state 10 steps before max_time

    
    # Running the schema system
    for t in range(max_time):
        model.update()
        # Store output
        output = model.get_output()
        out_data.append(output)
        if output:
            if output['Utter']:
                if verbose > 1:
                    print "t:%i, '%s'" %(t, output['Utter'])
                out_utterance.append(output['Utter'])
            if output['Subscene_recognition']:
                eye_pos = output['Subscene_recognition']['eye_pos']
                subscene = output['Subscene_recognition']['subscene']
                if eye_pos:
                    out_fixation.append({'time':t, 'pos':eye_pos, 'subscene':subscene})
                    if verbose>1:
                        vals = [(u,v) for u,v in output['Subscene_recognition'].iteritems() if v]
                        print "t:%i, '%s'" %(t, vals)
        if t in prob_times:
                TCG_VIEWER.display_WMs_state(model.schemas['Visual_WM'], model.schemas['Semantic_WM'], model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
                TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM'], model.schemas['Grammatical_WM_P'], concise=True)
    
    if verbose >2:
        model.schemas['Visual_WM'].show_SceneRep()
        model.schemas['Visual_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
        model.schemas['Semantic_WM'].show_SemRep()
        model.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
        model.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=True, c2_network=False)
        model.schemas['Grammatical_WM_P'].show_state()
        if IMG_FILE:
            TCG_VIEWER.display_saccades(out_fixation, IMG_FILE, ss_radius=True)
    
    model.save_sim(file_path = FOLDER, file_name = 'output.json')
    model.reset()
    
    # Prints utterance and fixation sequence in verbose mode.
    if verbose > 0:
        print ## FIXATIONS ##
        print out_fixation
        print ## UTTERANCES ##
        print ' '.join(out_utterance)

    ## NO DATA ANALYSIS HERE

def run_diagnostics(verbose=2, prob_times=[]):
    """
    Allows to run a set of diagnostics.
    """
    DIAGNOSTIC_NAME = 'test'
    SPEED_PARAM = 10
    MODEL_PARAMS = {'Subscene_recognition.recognition_time':SPEED_PARAM, 'Control.task.start_produce':0.0, 'Control.task.time_pressure':200, 'Grammatical_WM_P.dyn.ext_weight':1.0, 'Grammatical_WM_P.C2.prune_threshold': 0.01, 'Grammatical_WM_P.C2.coop_weight':1.0, 'Grammatical_WM_P.C2.comp_weight':-10.0, 'Grammatical_WM_P.C2.coop_asymmetry':1.0}
    
    # Attempts to model lesion
#    MODEL_PARAMS['Grammatical_WM_P.C2.coop_weight']=0.1 # Reduce cooperation weights
#    MODEL_PARAMS['Grammatical_WM_P.dyn.noise_std']=2.0 # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
#    MODEL_PARAMS['Grammatical_WM_P.C2.prune_threshold']=0.2 # Change prune threshold (shoudl be done in relation to initial activation values.)
#    MODEL_PARAMS['Grammatical_WM_P.dyn.k'] = 3.4 # Interesting effects, bifurcation at a given value.
#    MODEL_PARAMS['Grammatical_WM_P.dyn.act_rest'] = 0.001 # Act rest does not take into account the noise.

    ### GENERAL PARAMETERS
    semantics_name = 'TCG_semantics_main'
    grammar_name='TCG_grammar_VB_main'  
    max_time =3000
    seed=None
    ###    
    
    model = set_model(semantics_name, grammar_name, model_params=MODEL_PARAMS)
    (input_name, IMG_FILE) = set_inputs(model, input_name=DIAGNOSTIC_NAME, show_scene=True)
    
    run_model(model, sim_name=input_name, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, IMG_FILE=IMG_FILE)

if __name__ == '__main__':
   run_diagnostics(verbose=3, prob_times=[])
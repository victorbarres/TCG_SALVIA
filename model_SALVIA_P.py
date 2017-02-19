# -*- coding: utf-8 -*-
"""
@author: Victor Barres

SALVIA production model
"""
import random

from TCG_models import SALVIA_P, SALVIA_P_verbal_guidance
from viewer import TCG_VIEWER
from loader import TCG_LOADER

TMP_FOLDER = './tmp'
    
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
    
    perceptLTM = model.schemas['Percept_LTM']
    my_scene = TCG_LOADER.load_scene(input_file, SCENE_FOLDER, perceptLTM)
    model.set_input(my_scene)
    
    return (input_name, IMG_FILE)

def run(model, sim_name, max_time=900, seed=None, verbose=0, prob_times=[], IMG_FILE =''):
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
                TCG_VIEWER.display_WMs_state(model.schemas['Visual_WM'], model.schemas['Semantic_WM_P'], model.schemas['Grammatical_WM_P'], concise=True, folder = FOLDER)
                TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM_P'], model.schemas['Grammatical_WM_P'], concise=True)
    
    if verbose >2:
        model.schemas['Subscene_recognition'].show_scene(IMG_FILE)
        model.schemas['Visual_WM'].show_SceneRep()
#        model.schemas['Visual_WM'].show_dynamics()
        model.schemas['Semantic_WM_P'].show_SemRep()
#        model.schemas['Semantic_WM_P'].show_dynamics()
        model.schemas['Grammatical_WM_P'].show_dynamics()
#        model.schemas['Grammatical_WM_P'].show_state()
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

def run_diagnostics(verbal_guidance=False, verbose=2, prob_times=[]):
    """
    Allows to run a set of diagnostics.
    """
    DIAGNOSTIC_NAME = 'test'
    SPEED_PARAM = 50
    MODEL_PARAMS = {'Subscene_recognition.recognition_time':SPEED_PARAM, 
                    'Control.task.start_produce':0.0, 
                    'Control.task.time_pressure':200, 
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
    max_time =3000
    seed=None
    ###    
    
    model = set_model(semantics_name, grammar_name,verbal_guidance=verbal_guidance, model_params=MODEL_PARAMS)
    (input_name, IMG_FILE) = set_inputs(model, input_name=DIAGNOSTIC_NAME, show_scene=True)
    
    run(model, sim_name=input_name, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times, IMG_FILE=IMG_FILE)

if __name__ == '__main__':
   run_diagnostics(verbal_guidance=True, verbose=3, prob_times=[])
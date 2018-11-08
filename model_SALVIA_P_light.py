# -*- coding: utf-8 -*-
"""
@author: Victor Barres

SALVIA_P model light version (No VisualWM and Conceptualization)
"""
import random

from TCG_models import SALVIA_P_light
from viewer import TCG_VIEWER
from loader import TCG_LOADER

TMP_FOLDER = './tmp'


def set_model(semantics_name='TCG_semantics_main', grammar_name='TCG_grammar_VB_main', model_params={}):
    """
    Sets up a SALVIA_P_light
    
    Args:
        - semantics_name (STR): Name of the semantic file containing the perceptual, world, and conceptualization knowledge.
        - grammar_name (STR): Name of the grammar file to use.
        - model_prams (dict): Dictionary defining the model parameters (if different than default)
    
    Returns: SALVIA_P_light model
    """

    model = SALVIA_P_light(grammar_name=grammar_name, semantics_name=semantics_name)

    if model_params:
        model.update_params(model_params)

    return model


def set_inputs(model, input_name, input_file='kuchinsky.json'):
    """
    Sets up a SCENE_LIGHT input for SALVIA_P_light model
    
    Args:
        - input_name (STR): scene input name.
        - input_input_file (STR): scene_input file name.
    
    Sets up the SCENE_LIGHT input for the model.
    """

    # Defining scene input
    SCENE_INPUT_PATH = "./data/scene_inputs/"

    conceptLTM = model.schemas['Concept_LTM']
    my_scene = TCG_LOADER.load_scene_light(input_file, SCENE_INPUT_PATH, input_name, conceptLTM)

    model.set_input(my_scene)

    return input_name


def run(model, sim_name, max_time=900, seed=None, verbose=0, prob_times=[]):
    """
    Run the model "model".
    
    Args:
        - input_name(STR): input name
        - Verbose modes: 0 -> no output printed.
        - prob_times ([INT]):
    """
    if not (seed):  # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0, 10 ** 9)
    random.seed(seed)

    FOLDER = '{}/TEST_{}_{}/'.format(TMP_FOLDER, sim_name, str(seed))

    model.verbose = False

    model.initialize_states()

    out_data = []
    out_utterance = []

    if verbose > 1:
        prob_times.append(max_time - 10)  # Will save the state 10 steps before max_time

    # Running the schema system
    for t in range(max_time):
        model.update()
        # Store output
        output = model.get_output()
        out_data.append(output)
        if output:
            if output['Utter']:
                if verbose > 1:
                    print("t:{}, '{}'".format(t, output['Utter']))
                out_utterance.append(output['Utter'])
            if output['Scene_perception'] and verbose > 1:
                vals = [(u, v) for u, v in output['Scene_perception'].iteritems() if v]
                if vals:
                    print("t:{}, '{}'".format(t, vals))
        if t in prob_times:
            TCG_VIEWER.display_gramWM_state(model.schemas['Grammatical_WM_P'], concise=True)
            TCG_VIEWER.display_lingWM_state(model.schemas['Semantic_WM_P'], model.schemas['Grammatical_WM_P'],
                                            concise=True)

    if verbose > 2:
        #        model.schemas['Visual_WM'].show_dynamics()
        model.schemas['Semantic_WM_P'].show_SemRep()
        #        model.schemas['Semantic_WM_P'].show_dynamics()
        model.schemas['Grammatical_WM_P'].show_dynamics()
    #        model.schemas['Grammatical_WM_P'].show_state()

    model.save_sim(file_path=FOLDER, file_name='output.json')
    model.reset()

    # Prints utterance and fixation sequence in verbose mode.
    if verbose > 0:
        print("## UTTERANCES ##")
        print(' '.join(out_utterance))

    ## NO DATA ANALYSIS HERE


def run_diagnostics(verbose=2, prob_times=[]):
    """
    Allows to run a set of diagnostics.
    """
    DIAGNOSTIC_NAME = "act_kick_woman_man"
    SPEED_PARAM = 70
    ANIM = True
    MODEL_PARAMS = {'Scene_perception.recognition_time': SPEED_PARAM,
                    'Control.task.start_produce': 0.0,
                    'Control.task.time_pressure': 10,
                    'Grammatical_WM_P.dyn.ext_weight': 1.0,
                    'Grammatical_WM_P.C2.prune_threshold': 0.01,
                    'Grammatical_WM_P.C2.coop_weight': 1.0,
                    'Grammatical_WM_P.C2.comp_weight': -10.0,
                    'Grammatical_WM_P.C2.coop_asymmetry': 1.0,
                    'Grammatical_WM_P.C2.confidence_threshold': 0.3}

    # Attempts to model lesion
    #    MODEL_PARAMS['Grammatical_WM_P.C2.coop_weight']=0.1 # Reduce cooperation weights
    #    MODEL_PARAMS['Grammatical_WM_P.dyn.noise_std']=2.0 # Impact of dynamic noise -> Not useful. But might have impact in early symmetry breaking.
    #    MODEL_PARAMS['Grammatical_WM_P.C2.prune_threshold']=0.2 # Change prune threshold (shoudl be done in relation to initial activation values.)
    #    MODEL_PARAMS['Grammatical_WM_P.dyn.k'] = 3.4 # Interesting effects, bifurcation at a given value.
    #    MODEL_PARAMS['Grammatical_WM_P.dyn.act_rest'] = 0.001 # Act rest does not take into account the noise.

    ### GENERAL PARAMETERS
    semantics_name = 'TCG_semantics_main'
    grammar_name = 'TCG_grammar_VB_main'
    max_time = 1000
    seed = None
    ###    

    model = set_model(semantics_name, grammar_name, model_params=MODEL_PARAMS)
    input_name = set_inputs(model, input_name=DIAGNOSTIC_NAME)

    run(model, sim_name=input_name, max_time=max_time, seed=seed, verbose=verbose, prob_times=prob_times)


if __name__ == '__main__':
    run_diagnostics(verbose=2, prob_times=[])

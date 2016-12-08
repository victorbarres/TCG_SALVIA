# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG description
"""
import random

from TCG_models import TCG_description_system, TCG_description_system_verbal_guidance
from viewer import TCG_VIEWER
from loader import TCG_LOADER

def test(seed=None):
    """
    """
    if not(seed): # Quick trick so that I can have access to the seed used to run the simulation.
        random.seed(seed)
        seed = random.randint(0,10**9)
        print "seed = %i" %seed
    random.seed(seed)
    
    description_system = TCG_description_system_verbal_guidance()

    # Generating schema system graph visualization
    description_system.system2dot(image_type='png', disp=True)

    # Defining scene input
    FOLDER  = "./data/scenes/"
    SCENE_FILE = "TCG_scene.json"
    SCENE_NAME = 'KC06_1_1_ActPt'
    SCENE_FOLDER = "%s%s/" %(FOLDER, SCENE_NAME)
    IMG_FILE = SCENE_FOLDER + 'scene.png'
    
    my_scene = TCG_LOADER.load_scene(SCENE_FILE, SCENE_FOLDER)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    description_system.schemas['Control'].params['task']['start_produce'] = 20
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 300
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
        if t - set_up_time in save_states:
                TCG_VIEWER.display_WMs_state(description_system.schemas['Visual_WM'], description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_gramWM_state(description_system.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_lingWM_state(description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
    
    description_system.schemas['Visual_WM'].show_SceneRep()
#    description_system.schemas['Visual_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Semantic_WM'].show_SemRep()
#    description_system.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Grammatical_WM_P'].show_state()
    
    TCG_VIEWER.display_saccades(fixations, IMG_FILE, ss_radius=True)
    
#    description_system.save_sim('./tmp/test_description_output.json')

if __name__ == '__main__':
    test(seed=None)
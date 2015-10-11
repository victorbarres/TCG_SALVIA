# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG description
"""
import random

from TCG_models import TCG_description_system
from viewer import TCG_VIEWER
from loader import TCG_LOADER

def test(seed=None):
    """
    """
    random.seed(seed)
    
    description_system = TCG_description_system()

    # Generating schema system graph visualization
    description_system.system2dot(image_type='png', disp=True)

    # Defining scene input
    scene_name = 'KC06_1_1'
    scene_folder = "./data/scenes/%s/" %scene_name
    img_file = scene_folder + 'scene.png'
    
    my_scene = TCG_LOADER.load_scene("TCG_scene.json", scene_folder)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    description_system.schemas['Control'].task_params['start_produce'] = 300
    
    set_up_time = -10 # Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 500
    save_states = [130]
    
    fixations = []
    # Running the schema system
    for t in range(max_time):
        if t== -1*set_up_time:
            
            description_system.schemas['Subscene_recognition'].show_scene(img_file)
            
        description_system.update()
        output = description_system.get_output()
        if output:
            if output['Utter']:
             print "t:%i, '%s'" %(t, output['Utter'])
            if output['Subscene_recognition']:
                eye_pos = output['Subscene_recognition']['eye_pos']
                if eye_pos:
                    fixations.append({'time':t, 'pos':eye_pos})
                vals = [(u,v) for u,v in output['Subscene_recognition'].iteritems() if v]
                if vals:
                    print "t:%i, '%s'" %(t, vals)
        if t - set_up_time in save_states:
                TCG_VIEWER.display_WMs_state(description_system.schemas['Visual_WM'], description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_gramWM_state(description_system.schemas['Grammatical_WM_P'], concise=True)
                TCG_VIEWER.display_lingWM_state(description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
    
    description_system.schemas['Visual_WM'].show_SceneRep()
    description_system.schemas['Visual_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Semantic_WM'].show_SemRep()
    description_system.schemas['Semantic_WM'].show_dynamics(inst_act=True, WM_act=False, c2_levels=False, c2_network=False)
    description_system.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
    description_system.schemas['Grammatical_WM_P'].show_state()
    
    TCG_VIEWER.display_saccades(fixations, img_file)
    
#    description_system.save_sim('./tmp/test_description_output.json')

if __name__ == '__main__':
    test(seed=0)
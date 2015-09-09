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
    description_system.system2dot(image_type='svg', disp=False)

    # Defining scene input
    scene_name = 'KC06_1_1'
    scene_folder = "./data/scenes/%s/" %scene_name
    
    my_scene = TCG_LOADER.load_scene("TCG_scene.json", scene_folder)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    description_system.schemas['Control'].task_params['start_produce'] = 300
    
    set_up_time = -10 #Starts negative to let the system settle before it receives its first input. Also, easier to handle input arriving at t=0.
    max_time = 900
    save_states = [10,20,30,60,100,400]
    
    # Running the schema system
    for t in range(max_time):
        description_system.update()
        output = description_system.get_output()
        if output:
            print output
        if t - set_up_time in save_states:
                TCG_VIEWER.display_visWM_state(description_system.schemas['Visual_WM'])
#                TCG_VIEWER.display_gramWM_state(description_system.schemas['Grammatical_WM_P'], concise=True)
#                TCG_VIEWER.display_lingWM_state(description_system.schemas['Semantic_WM'], description_system.schemas['Grammatical_WM_P'], concise=True)
    
#    description_system.schemas['Visual_WM'].show_SceneRep()
#    description_system.schemas['Visual_WM'].show_dynamics()
#    description_system.schemas['Semantic_WM'].show_SemRep()
#    description_system.schemas['Grammatical_WM_P'].show_dynamics(inst_act=True, WM_act=True, c2_levels=True, c2_network=True)
#    description_system.schemas['Grammatical_WM_P'].show_state()
#    
    #description_system.save_sim('./tmp/test_description_output.json')

if __name__ == '__main__':
    test(seed=0)
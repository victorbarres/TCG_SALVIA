# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Test TCG description
"""
import random

from loader import TCG_LOADER
from TCG_models import TCG_description_system

def test(seed=None):
    """
    """
    random.seed(seed)
    
    description_system = TCG_description_system()

    # Generating schema system graph visualization
    description_system.system2dot(image_type='svg', disp=False)

    # Setting up BU saliency data
    scene_name = 'KC06_1_1'
    scene_folder = "./data/scenes/%s/" %scene_name
    
    my_scene = TCG_LOADER.load_scene("TCG_scene.json", scene_folder)
    
    # Schema rec intialization
    description_system.set_input(my_scene)
    description_system.verbose = False
    
    description_system.schemas['Control'].task_params['start_produce'] = 300
    
    # Running the schema system
    time = 900
    for t in range(time):
        description_system.update()
        output = description_system.get_output()
        if output:
            print output
    
#    description_system.schemas['Visual_WM'].show_SceneRep()
#    description_system.schemas['Semantic_WM'].show_SemRep()
    description_system.schemas['Grammatical_WM_P'].show_dynamics()
#    description_system.schemas['Grammatical_WM_P'].show_state()
    
    #description_system.save_sim('./tmp/test_description_output.json')

if __name__ == '__main__':
    test(seed=0)
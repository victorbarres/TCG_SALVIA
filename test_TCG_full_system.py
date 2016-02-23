# -*- coding: utf-8 -*-
"""
@author: Victor Barres
"""
import random
from TCG_models import TCG_full_system

def test(seed=None):
    """
    """
    random.seed(seed)
    
    full_system = TCG_full_system()

    # Generating schema system graph visualization
    full_system.system2dot(image_type='svg', disp=False)

if __name__=='__main__':
    test(seed=None)
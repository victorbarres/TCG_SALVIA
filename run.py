# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:42:04 2017

@author: victor barres
Run models
"""
import sys

import model_TCG_production as TCG_prod
import model_TCG_comprehension as TCG_comp
import model_TCG_comprehension_2route as TCG_C2
def run_model():
    """
    """
    model_types = ['TCG_c', 'TCG_p', 'TCG_c_C2']
    help_message = "Usage: python run.py model_type\nmodel_types: %s\n" %", ".join(model_types)
    if len(sys.argv) <2 or sys.argv[1] not in model_types:
        print help_message
        return
    model_type = sys.argv[1]
    if model_type == model_types[0]:
        TCG_comp.run_diagnostic()
    elif model_type == model_types[1]:
        TCG_prod.run_diagnostics(verbose=2, prob_times=[])
    elif model_type == model_types[2]:
        TCG_C2.run_diagnostic()
    else:
        print help_message
        
        
    

if __name__ =='__main__':
    run_model()



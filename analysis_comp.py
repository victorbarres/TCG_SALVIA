# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:26 2016

@author: victor
"""
from __future__ import division
import numpy as np

from language_schemas import ISRF_INTERPRETER



def get_TRA(isrf_sem_state):
    """
    Returns info about agent and patient given an isrf_sem_state that contains only one action event.
    """
    res = {'agent':None, 'patient':None}
    graph = ISRF_INTERPRETER.prop_grapher(isrf_sem_state)
    
    # Find action node
    act_name = None
    for name, data in graph.nodes(data=True):
        if data['concept'] == 'TRANS_ACT':
            act_name = name
            break
    if not act_name:
        return res
    
    agt_ent_name = None
    pt_ent_name = None
    # Find agent and patient entity if they exist (if ambiguous picks the most active edge)
    for ent_name in graph.successors_iter(act_name):
        act = 0
        key = None
        edge_data = graph.get_edge_data(act_name, ent_name)
        for k, dat in edge_data:
            if float(dat['act']) > act:
                key = k
                act = float(dat['act'])
        win_dat = edge_data(act_name, ent_name, key)
        if win_dat['concept'] == 'AGENT':
            if agt_ent_name:
                error_msg = "Multiple agent winner found"
                raise ValueError(error_msg)  
            agt_ent_name = ent_name
        elif win_dat['concept'] == 'PATIENT':
            if pt_ent_name:
                error_msg = "Multiple patient winner found"
                raise ValueError(error_msg)  
            pt_ent_name = ent_name
        else:
            error_msg = "Unexpected TRA relation %s" %win_dat['concept']
            raise ValueError(error_msg)
    
    # Find agent concept
    if agt_ent_name:
        successors = graph.successors(agt_ent_name)
        if len(successors) > 1:
            error_msg = "Multiple agent concept"
            raise ValueError(error_msg)
        if len(successors) == 1:
            data = graph.get_edge_data(agt_ent_name, successors[0])
            edge_data = data.keys()
            if len(edge_data) > 1:
                error_msg = "Unexpected multiple relation (only IS expected)"
                raise ValueError(error_msg)
            edge_data = edge_data[0]
            if edge_data['concept'] != 'IS':
                error_msg = "Unexpected relation %s (IS expected)" %edge_data['concept']
                raise ValueError(error_msg)
            res['agent'] = graph[successors[0]]['concept']
    
    # Find patient concept
    if pt_ent_name:
        successors = graph.successors(pt_ent_name)
        if len(successors) > 1:
            error_msg = "Multiple patient concept"
            raise ValueError(error_msg)
        if len(successors) == 1:
            data = graph.get_edge_data(pt_ent_name, successors[0])
            edge_data = data.keys()
            if len(edge_data) > 1:
                error_msg = "Unexpected multiple relation (only IS expected)"
                raise ValueError(error_msg)
            edge_data = edge_data[0]
            if edge_data['concept'] != 'IS':
                error_msg = "Unexpected relation %s (IS expected)" %edge_data['concept']
                raise ValueError(error_msg)
            res['patient'] = graph[successors[0]]['concept']

    return res    
    
def analysis_gram(data):
    """
    Looks at the final usage of passive and active construciton
    """
    res = {}
    res['active'] = data.get('SVO', np.NaN)
    res['passive'] = data.get('PAS_SVO', np.NaN)  
    return res

def analysis_wk(data):
    """
    """
    return data
    
def analysis_sem(data, ground_truths):
    """
    """
    pass
    
##########################
### WkWM ANALYSES ###
    
    
###############################################################################
if __name__ == '__main__':
    print "No test case implemented"
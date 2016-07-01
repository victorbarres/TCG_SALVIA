# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:26 2016

@author: victor
"""

def tree_data(assemblage):
    """
    Given an cxn_assemblage(Tree), returns the number of inner_nodes and outter_nodes (leaves)
    
    Args:
        assemblage (ASSEMBLAGE): A CXN assemblage.
    """
    nodes = assemblage.schema_insts[:]
    edges = assemblage.coop_links[:]
    
    # compute outter nodes and inner node set
    outter_nodes = []
    inner_nodes = []
    
    while nodes:
        n = nodes.pop()
        inner = False
        for e in edges:
            if e.inst_to == n:
                inner = True
                break
        if inner:
            inner_nodes.append(n)
        else:
            outter_nodes.append(n)
        
    return (outter_nodes, inner_nodes)
    

def syntactic_complexity(data):
    """
    Given an the assemblage_out data state of a GRAMMATICAL_WM_P schema,
    Returns the list of tree_data() applied to each output cxn_assemblage.
    """
    syn_complexity = {'nodes':[], 'inner_nodes':[]}
    for dat in data:
        (outter_nodes, inner_nodes) = tree_data(dat['assemblage'])
        syn_complexity['nodes'].append(len(outter_nodes) + len(inner_nodes))
        syn_complexity['inner_nodes'].append(len(inner_nodes))
    return syn_complexity

            
def cxn_usage_count(data):
    """
    Given an the assemblage_out data state of a GRAMMATICAL_WM_P schema,
    Returns
        - a count of how many time each cxn type has been used.
    """
    cxn_usage = {}
    for d in data:
        cxn_insts = d['assemblage'].schema_insts
        for inst in cxn_insts:
            cxn_name = inst.content.name
            if cxn_usage.has_key(cxn_name):
                cxn_usage[cxn_name] += 1
            else:
                cxn_usage[cxn_name] = 1
                
    return cxn_usage
    

def utterance_intervals(data):
    """
    Given an the assemblage_out data state of a GRAMMATICAL_WM_P schema,
    Returns
        - a list of the time intervals between each utterance produced.
    """
    utter_intervals= []
    if not data:
        return utter_intervals
    t = data[0]['t']
    for dat in data[1:]:
        next_t = dat['t']
        interval = (next_t - t)
        utter_intervals.append(interval)
        t = next_t
        
    return utter_intervals

def utterance_lengths(data):
    """
    Given an the assemblage_out data state of a GRAMMATICAL_WM_P schema,
    Returns
        - a list of the utternances lengths.
    """
    utter_length = [len(dat['phon_form']) for dat in data]
    
    return utter_length
    
    
def prod_analyses(data):
    """
    Carries out all the analyses and returns a single output
    """
    res = {}
    res['syntactic_complexity'] = syntactic_complexity(data)
    res['cxn_usage_count'] = cxn_usage_count(data)
    res['utterance_intervals'] = utterance_intervals(data)
    res['utterance_lengths'] = utterance_lengths(data)
    
    return res

def prod_statistics(res_list):
    """
    Carries basic statistical analyses on a set of prod_analyses.
    
    Args:
        -res_list (ARRAY): Array of objects returned by prod_analyses
    
    Notes:
        - syntactic complexity only keeps inner_nodes proportion.
    """
    import numpy as np
    import pandas as pd
    
    total_res = {'syntactic_complexity':[], 'cxn_usage_count':{}, 'utterance_intervals':[], 'utterance_lengths':[]}
    
    for res in res_list:
        field_name = 'syntactic_complexity'
        for i in range(len(res[field_name]['inner_nodes'])):
            total_res[field_name].append(float(res[field_name]['inner_nodes'][i])/float(res[field_name]['nodes'][i]))
        
        field_name = 'cxn_usage_count'
        for k,v in res[field_name].iteritems():
            if total_res[field_name].has_key(k):
                total_res[field_name][k] += v
            else:
                total_res[field_name][k] = v
        
        field_name = 'utterance_intervals'
        for val in res[field_name]:
            total_res[field_name].append(res[val])
        
        field_name = 'utterance_lengths'
        for val in res[field_name]:
            total_res[field_name].append(val)
        
                
    res_stats = {}
    my_stats = lambda vals:{"mean":np.mean(vals), "std":np.std(vals), "median":np.median(vals), "max":np.max(vals), "min":np.min(vals)}  
    
    for field_name in ['syntactic_complexity', 'utterance_intervals', 'utterance_lengths']:  
        if total_res[field_name]:
            res_stats[field_name] = my_stats(total_res[field_name])
        else: res_stats[field_name] = None
    
    res_stats['cxn_usage_count'] = {}
    total_count = 0
    for k,v in total_res['cxn_usage_count'].iteritems():
        s = np.sum(v)
        res_stats['cxn_usage_count'][k] = np.sum(v)
        total_count += s
    
    res_stats['cxn_usage_count']['total_count'] = total_count
    
    return res_stats
    
    
###############################################################################
if __name__ == '__main__':
    
    from test_TCG_production import test
    
    model = test()

    gram_WM = model.schemas['Grammatical_WM_P']

    data = gram_WM.save_state['assemblage_out'] 
    
    ###############
    # ANALYSIS
    import pprint as pp
    
    
    section_title = lambda x: "\n###### %s ######\n" %(str(x))
    
    print section_title('CXN USAGE')
        
    cxn_usage = cxn_usage_count(data)
    pp.pprint(cxn_usage) 
    
    num_types = len(cxn_usage.keys())
    num_tokens = sum([cxn_usage.values()])
    print '\nnum_types = %i\n' %num_types
    print 'num_tokens = %i\n' %num_tokens
    
    print section_title('SYNTACTIC COMPLEXITY')
    
    syn_complexity = syntactic_complexity(data)
    pp.pprint(syn_complexity)
    
    print section_title('UTTERANCE INTERVALS')
    
    utter_intervals = utterance_intervals(data)
    pp.pprint(utter_intervals)
    
    print section_title('UTTERANCE LENGTHS')
    
    utter_lengths = utterance_lengths(data)
    pp.pprint(utter_lengths)
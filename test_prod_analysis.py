# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:26 2016

@author: victor
"""

from test_TCG_production import test

model = test()

gram_WM = model.schemas['Grammatical_WM_P']

data = gram_WM.save_state['assemblage_out']


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

            
def cxn_usage_frequency(data):
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
    t = data[0]['t']
    for dat in data[1:]:
        next_t = dat['t']
        interval = (next_t - t)
        utter_intervals.append(interval)
        t = next_t
        
    return utter_intervals

def utterance_length(data):
    """
    Given an the assemblage_out data state of a GRAMMATICAL_WM_P schema,
    Returns
        - a list of the utternances lengths.
    """
    utter_length = [len(dat['phon_form']) for dat in data]
    
    return utter_length

###############
# ANALYSIS
import pprint as pp


section_title = lambda x: "\n###### %s ######\n" %(str(x))

print section_title('CXN USAGE')
    
cxn_usage = cxn_usage_frequency(data)
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

utter_length = utterance_length(data)
pp.pprint(utter_length)
    
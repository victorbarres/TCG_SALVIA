# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:26 2016

@author: victor
"""

from test_TCG_production import test

model = test()

gram_WM = model.schemas['Grammatical_WM_P']

data = gram_WM.save_state['assemblage_out']


def tree_complexity(assemblage):
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
    syn_complexity = {'nodes':[], 'inner_nodes':[]}
    for dat in data:
        (outter_nodes, inner_nodes) = tree_complexity(dat['assemblage'])
        syn_complexity['nodes'].append(len(outter_nodes) + len(inner_nodes))
        syn_complexity['inner_nodes'].append(len(inner_nodes))
    return syn_complexity

            
def cxn_usage_frequency(data):
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
    

def utterance_time_delays(data):
    utter_delays = []
    t = data[0]['t']
    for dat in data[1:]:
        next_t = dat['t']
        delay = (next_t - t)
        utter_delays.append(delay)
        t = next_t
        
    return utter_delays

for dat in data:
    print "t: %i" %dat['t']
    print "form_output: %s" %' '.join(dat['phon_form'])
    print "num_cxn_insts: %i" %len(dat['assemblage'].schema_insts)
    print "num_coop_links %i" %len(dat['assemblage'].coop_links)
    
    (outter_nodes, inner_nodes) = tree_complexity(dat['assemblage'])
    
    print [n.name for n in outter_nodes]
    print [n.name for n in inner_nodes]
    
cxn_usage = cxn_usage_frequency(data)
print cxn_usage

syn_complexity = syntactic_complexity(data)
print syn_complexity

utter_delays = utterance_time_delays(data)
print utter_delays
    
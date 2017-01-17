# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 15:33:26 2016

@author: victor
"""
from __future__ import division
import numpy as np

#########################################
### GRAMMATICAL WM OUTPUTS PROCESSING ###
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

    cxn_usage['total_count'] = sum([n for n in cxn_usage.values()])
        
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
    
    return [res]

def prod_statistics(res_list):
    """
    Carries basic statistical analyses on a set of prod_analyses.
    
    Args:
        -res_list (ARRAY): Array of objects returned by prod_analyses
    
    Notes:
        - syntactic complexity only keeps inner_nodes proportion.
    """
    import numpy as np
    
    total_res = {'syntactic_complexity':[], 'cxn_usage_count':{}, 'utterance_intervals':[], 'utterance_lengths':[]}
    
    for res in res_list:
        field_name = 'syntactic_complexity'
        for i in range(len(res[field_name]['inner_nodes'])):
            total_res[field_name].append(float(res[field_name]['inner_nodes'][i])/float(res[field_name]['nodes'][i]))
        
        field_name = 'cxn_usage_count'
        for k,v in res[field_name].iteritems():
            if total_res[field_name].has_key(k):
                total_res[field_name][k].append(v)
            else:
                total_res[field_name][k] = [v]
        
        field_name = 'utterance_intervals'
        for val in res[field_name]:
            total_res[field_name].append(val)
        
        field_name = 'utterance_lengths'
        for val in res[field_name]:
            total_res[field_name].append(val)
        
                
    res_stats = {}
    my_stats = lambda vals:{"num":len(vals), "sum":np.sum(vals), "mean":np.mean(vals), "std":np.std(vals), "max":np.max(vals), "min":np.min(vals)}  
    
    for field_name in ['syntactic_complexity', 'utterance_intervals', 'utterance_lengths']:  
        if total_res[field_name]:
            res_stats[field_name] = my_stats(total_res[field_name])
        else:
            res_stats[field_name] = my_stats([np.nan])
    
    res_stats['cxn_usage_count'] = {}
    for k,v in total_res['cxn_usage_count'].iteritems():
        res_stats['cxn_usage_count'][k] = my_stats(v)

    res_stats['cxn_usage_count']['mean'] = res_stats['cxn_usage_count']['total_count']['mean']
    
    return res_stats

def prod_summary(data):
    """
    """
    res = prod_analyses(data)
    res_stats = prod_statistics(res)
    return res_stats
    
##########################
### UTTERANCE ANALYSES ###

def n_grams(sentence, n):
    """
    Returns the sentence as a list of n-grams.
    """
    sentence = sentence.split()
    sentence_n_gram = []
    if n > len(sentence):
        print "error: n too large"
        return None
    
    for i in range(len(sentence)-n+1):
        sentence_n_gram.append(tuple(sentence[i:i+n]))
    
    return sentence_n_gram
    

def BLEU(candidate, ground_truths, n_gram):
    """
    Returns the BLEU score for a given candidate given a set of ground truths.
    Args:
        - candidate (STR): utterance candidate.
        - ground_truths (STR): List of strings, utterance ground truth
        - n_gram (INT): the n_gram value to use for BLEU calculation.
      
   
    Returns:
       - n_gram BLEU score for the candidate.
    """
    candidate = n_grams(candidate, n_gram)
    
    candidate_dict = dict((word,[0, candidate.count(word)]) for word in candidate)

    ground_truths = [n_grams(gt, n_gram) for gt in ground_truths]
   
    for word, counts in candidate_dict.iteritems():
        for gt in ground_truths:
            word_count = gt.count(word)
            if word_count > counts[0]:
                counts[0] = word_count
   
    bleu_counts = [min(counts) for counts in candidate_dict.values()]
    
    BLEU_SCORE = np.sum(bleu_counts)/float(len(candidate))

    return BLEU_SCORE
    
    
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
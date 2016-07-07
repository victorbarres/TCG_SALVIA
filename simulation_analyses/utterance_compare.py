# -*- coding: utf-8 -*-
"""
@author: victor barres

utterance comparison tools.
"""
import numpy as np


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
if __name__=="__main__":
    
    candidate = "the brown fox jumps over the lazy dog"
    
    ground_truths = ["it is the brown fox that jumps over the lazy dogs", "the brown fox has jumped over the lazy dog"]
    
    bleu_score = BLEU(candidate, ground_truths, 3)
    print bleu_score

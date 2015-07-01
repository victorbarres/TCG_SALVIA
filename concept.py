# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define semantic network related classes for TCG.
"""
from knowledge_rep import K_ENT, K_REL, K_NET

class CONCEPT(K_ENT):
    """
    Conceptual knowledge entity
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (STR): Meaning associated with the semantic entity. A string for now.

    """
    CONCEPTUAL_KNOWLEDGE= None  
    def __init__(self, name='',  meaning=''):
        K_ENT.__init__(self, name=name, meaning=meaning)
    
    def match(self, cpt, match_type = "is_a"):
        """
        Check if it matches cpt. 
        Uses CONCEPTUAL_KNOWLEDGE.match() method.
            Type = "is_a":  concept1 matches concept2 if concept1 is a hyponym of concept2 (or equal to concept2)
            Type = "equal": concept1 matches concept2 if concept1 is equal to concept2.
        """
        return CONCEPT.CONCEPTUAL_KNOWLEDGE.match(self, cpt, match_type)
    
    def similarity(self, cpt):
        """
        Returns a similarity score with cpt.
        Uses CONCEPTUAL_KNOWLEDGE.similarity() method.
        """
        return CONCEPT.CONCEPTUAL_KNOWLEDGE.similarity(self ,cpt)
    
class SEM_REL(K_REL):
    """
    Semantic relation between concept
    
    Data:
        - type (STR): Type of relation.
        - pFrom (CONCEPT):  Source concept.
        - pTo (CONCEPT): Target concept.
    
    Note: ONLY is_a IMPLEMENTED FOR NOW.
    """    
    def __init__(self, aType = 'UNDEFINED', from_cpt = None, to_cpt = None):
        K_REL.__init__(self,aType = aType, from_ent=from_cpt, to_ent = to_cpt)

class CONCEPTUAL_KNOWLEDGE(K_NET):
    """
    Conceptual knowledge. Implemented as a semantic network.
    
    Data(inherited):
        - nodes ([CONCEPT]): List of concepts.
        - edges ([SEM_REL]): List of semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attributes meaning = concept.meaning
            Each edge has an additional attribute type = sem_rel.type
    
    """
    def __init__(self, nodes=[], edges=[]):
        K_NET.__init__(self, nodes=nodes, edges=edges)
       
    def concepts(self):
        """
        Returns all the concepts
        """
        return self.nodes
    
    def has_concept(self, concept_name):
        """
        Returns concept iff there is a concept with name "name".
        
        Args:
            - concept_name (STR):
        """
        return self._has_entity(concept_name)
        
    def find_meaning(self, meaning):
        """
        Find concept with meaning "meaning". Returns the concept if found, else returns None.
        
        Args:
            - meaning (): Meaning of a concept
        """
        return super(CONCEPTUAL_KNOWLEDGE, self).find_meaning(meaning)
#        return self._find_meaning(meaning)
                     
    def similarity(self, cpt1, cpt2):
        """
        Returns a similarity score between cpt1 and cpt2.
        Uses path similarity.
        Args:
            - cpt1 (CONCEPT):
            - cpt2 (CONCEPT):
        
        Examples for is-a taxonomy (e.g. Wordnet):
            Path similarity: 1/(L+1), L=shortest path distance
            Leackock-Chodrow Similarity: -log(L/2*D) where L=shortest path length, D=taxonomy depth
            Wu-Palmer Similarlity: 2*depth(lcs)/(depth(s1) + depth(s2)), lcs = Least Common Subsumer.
            Resnik Similarity (Corpus dependent): IC(lcs)
            Lin Similarity (Corpus dependent): 2*IC(lcs)/(IC(s1) + IC(s2))
            Jiang & Conrath Similarity:  1/jcn_distance, jcn_distance =  IC(concept1) + IC(concept2) - 2 * IC(lcs). 
            See: http://maraca.d.umn.edu/umls_similarity/similarity_measures.html
        Note:
            - ONLY PATH SIMILARITY IMPLEMENTED
            - Question: What does it mean how similar is DOG to ANIMAL? Using path lengths, DALMATIAN being an hyponym of DOG, is necessarily less similar to ANIMAL than DOG...
        """
        return super(CONCEPTUAL_KNOWLEDGE, self).similarity(cpt1, cpt2)        
#        return self._similarity(cpt1, cpt2)`
    
    def match(self, cpt1, cpt2, match_type = "is_a"):
        """        
        Check if cpt1 matches cpt2. 
        Type = "is_a":  cpt1 matches cpt2 if cpt2 is a hyponym of cpt2 (or equal to cpt2)
        Type = "equal": cpt1 matches cpt2 iff cpt1 is equal to cpt2.
        
        Args:
            - cpt1 (CONCEPT)
            - cpt2 (CONCEPT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
            See similarity()
        
        """
        return super(CONCEPTUAL_KNOWLEDGE, self).match(cpt1, cpt2, match_type = match_type)   
#        return self._match(cpt1, cpt2, match_type=match_type)

###############################################################################
if __name__=='__main__':
    print "NOTHING IMPLEMENTED"

    
    
    
    
    
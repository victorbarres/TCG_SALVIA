# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define perceptual knowledge related classes for TCG.

Uses NetworkX module to represent the semantic net.
"""
from knowledge_rep import K_ENT, K_REL, K_NET

class PERCEPT(K_ENT):
    """
    Perceptual knowledge entity
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (): Meaning associated with the percept

    """
    SEMANTIC_NETWORK = None  
    def __init__(self, name='',  meaning=''):
        K_ENT.__init__(self, name=name, meaning=meaning)
    
class SEM_REL(K_REL):
    """
    Semantic Relation
    Type implemented:
        - 'is_a'
        - 'has_token'
    
    Data:
        - type (STR): Type of relation.
        - pFrom (PERCEPT):  Source percept.
        - pTo (PERCEPT): Target precept.
    """    
    def __init__(self, aType = 'UNDEFINED', from_sem = None, to_sem = None):
        K_REL.__init__(self,aType = aType, from_ent=from_sem, to_ent = to_sem)

class PERCEPTUAL_KNOWLEDGE(K_NET):
    """
    Semantic network.
    
    Data:
        - nodes ([CONCEPT]): List of concepts.
        - edges ([SEM_REL]): List of semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attributes meaning = concept.meaning
            Each edge has an additional attribute type = sem_rel.type
    """
    def __init__(self, nodes=[], edges=[]):
        K_NET.__init__(self, nodes=nodes, edges=edges)
    
    def clear(self):
        """
        Clear all.
        """
        self.nodes = []
        self.edges = []
        self._create_NX_graph()
    
    def add_concept(self, concept):
        """
        Add a concept to the semantic network
        
        Args:
            concept (CONCEPT): A semantic entity
        """
        self.add_ent(concept)    
                
    def shortest_path(self, from_cpt, to_cpt):
        """
        Returns the length of the shortest path, if it exists, between from_cpt and to_cpt in the SemNet graph.
        If no path exists, returns -1
        
        Args:
            - from_cpt (CONCEPT): Origin
            - to_cpt (CONCEPT): Target
        """
        path_len = -1
        try:
            path_len = nx.shortest_path_length(self.graph, source=from_cpt.id, target=to_cpt.id, weight=None)
        except nx.NetworkXNoPath:
            return path_len
            
        return path_len
     
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
        L = self.shortest_path(cpt1, cpt2)
        if L == -1: # Case no path found
            sim = 0
        else:
            sim = 1.0/(1.0 + L)
        return sim
    
    def match(self, cpt1, cpt2, match_type = "is_a"):
        """        
        Check if cpt1 matches cpt2. 
        Type = "is_a":  cpt1 matches ent2 if cpt2 is a hyponym of cpt2 (or equal to cpt2)
        Type = "equal": cpt1 matches cpt2 iff ent1 is equal to cpt2.
        
        Args:
            - cpt1 (CONCEPT)
            - cpt2 (CONCEPT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
            See similarity()
        
        """
        dist = self.shortest_path(cpt1, cpt2)
        if (match_type == "is_a" and dist >= 0):
            return True
        elif (match_type == "equal" and dist == 0):
            return True
        return False

###############################################################################
if __name__=='__main__':
    print "NOTHING IMPLEMENTED"

    
    
    
    
    
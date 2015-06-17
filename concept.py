# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define semantic network related classes for TCG1.1

Uses NetworkX module to represent the semantic net.
"""
import networkx as nx

class CONCEPT:
    """
    Semantic entity
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (STR): Meaning associated with the semantic entity. A string for now.
    
    Note:
        - '==' has to be defined for meaning.
    """
    SEMANTIC_NETWORK = None
    ID_NEXT = 1 # Global concept counter    
    def __init__(self, name='',  meaning=''):
        self.id = CONCEPT.ID_NEXT
        CONCEPT.ID_NEXT += 1
        self.name = name
        self.meaning = meaning # Concept meaning
    
    def match(self, cpt, match_type = "is_a"):
        """
        Check if it matches cpt. 
        Uses SEM_NET.match() method.
            Type = "is_a":  concept1 matches concept2 if concept1 is a hyponym of concept2 (or equal to concept2)
            Type = "equal": concept1 matches concept2 if concept1 is equal to concept2.
        """
        return CONCEPT.SEMANTIC_NETWORK.match(self, cpt, match_type)
    
    def similarity(self, cpt):
        """
        Returns a similarity score with cpt.
        Uses SEM_NET.similarity() method.
        """
        return CONCEPT.SEMANTIC_NETWORK.similarity(self ,cpt)
    
    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.id == other.id) and
            (self.meaning == other.meaning))
        return is_equal
    
class SEM_REL:
    """
    Semantic Relation
    
    Data:
        - type (STR): Type of relation.
        - pFrom (CONCEPT):  Source concept.
        - pTo (CONCEPT): Target concept.
    
    Note: ONLY IS-A IMPLEMENTED FOR NOW.
    """    
    def __init__(self, aType = 'UNDEFINED', from_sem = None, to_sem = None):
        self.type = aType
        self.pFrom = from_sem 
        self.pTo= to_sem
        
    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.type == other.type) and
            (self.pFrom == other.pFrom) and 
            (self.pTo == other.pTo))
        return is_equal
    
    def __str__(self):
        p = "%s %s %s" % (self.pFrom.meaning, self.type, self.pTo.meaning)
        return p

class SEM_NET:
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
        self.nodes = nodes
        self.edges = edges
        self.graph = None
    
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
        # Check validity        
        if(not(isinstance(concept, CONCEPT)) or not(concept.meaning)):
            return False
        
        # Check duplication
        if self.find_meaning(concept.meaning):
            return False
        
        # Add new semantic entity
        self.nodes.append(concept)
        self._create_NX_graph()
        return True
        
    def add_relation(self, sem_rel):
        """
        Add a relation to the semantic network
        
        Args:
            sem_rel (SEM_REL): A semantic relation
        """        
        # Check validity
        if (not(isinstance(sem_rel, SEM_REL)) or 
            (sem_rel.type == 'UNDEFINED') or 
            not(sem_rel.pFrom) or 
            not(sem_rel.pTo)):
            return False
        
        # Check duplication
        for r in self.edges:
            if r == sem_rel:
                return False
        
        # Check that source and target of relation are defined.
        if not(self.find_meaning(sem_rel.pFrom.meaning)) or not(self.find_meaning(sem_rel.pTo.meaning)):
            return False
        
        # Add new relation
        self.edges.append(sem_rel)
        self._create_NX_graph()
        return True
        
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.id, meaning=node.meaning)
        for edge in self.edges:
            graph.add_edge(edge.pFrom.id, edge.pTo.id, type= edge.type)
        
        self.graph = graph
    
    def find_meaning(self, meaning):
        """
        Find concept with meaning "meaning". Returns the concept if found, else returns None.
        
        Args:
            - meaning (): Meaning of a concept.
        """
        for n in self.nodes:
            if n.meaning == meaning:
                return n
        
        return None
    
                
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

    
    
    
    
    
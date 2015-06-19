# -*- coding: utf-8 -*-
"""
@author: Victor Barres
!!DEPREACTED!!

Define semantic network related classes for TCG1.1

Uses NetworkX module to represent the semantic net.
"""
import networkx as nx

class SEM_ENT:
    """
    Semantic entity
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (STR): Meaning associated with the semantic entity. A string for now.
    
    Note:
        - '==' has to be defined for meaning.
    """
    ID_NEXT = 1 # Global entity counter    
    def __init__(self, meaning=''):
        self.id = SEM_ENT.ID_NEXT
        SEM_ENT.ID_NEXT += 1
        self.meaning = meaning # Concept meaning
    
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
        - pFrom (SemEnt): Name of the source semantic entity.
        - pTo (SemEnt): Name of the target semantic entity.
    
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
        - nodes ([SEM_ENT]): List of semantic entities.
        - edges ([SEM_REL]): List of semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attributes meaning = sem_ent.meaning
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
    
    def add_entity(self, sem):
        """
        Add a semantic entity to the semantic network
        
        Args:
            sem (SEM_ENT): A semantic entity
        """
        # Check validity        
        if(not(isinstance(sem, SEM_ENT)) or not(sem.meaning)):
            return False
        
        # Check duplication
        if self.find_meaning(sem.meaning):
            return False
        
        # Add new semantic entity
        self.nodes.append(sem)
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
        Find entity with meaning "meaning". Returns the entity if found, else returns None.
        
        Args:
            - meaning (): Meaning of a semantic entity.
        """
        for n in self.nodes:
            if n.meaning == meaning:
                return n
        
        return None
    
                
    def shortest_path(self, from_ent, to_ent):
        """
        Returns the length of the shortest path, if it exists, between from_ent and to_ent in the SemNet graph.
        If no path exists, returns -1
        
        Args:
            - from_ent (SEM_ENT): Origin
            - to_ent (SEM_ENT): Target
        """
        path_len = -1
        try:
            path_len = nx.shortest_path_length(self.graph, source=from_ent.id, target=to_ent.id, weight=None)
        except nx.NetworkXNoPath:
            return path_len
            
        return path_len
     
    def similarity(self, ent1, ent2):
        """
        Returns a similarity score between ent1 and ent2.
        Uses path similarity.
        
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
        L = self.shortest_path(ent1, ent2)
        if L == -1: # Case no path found
            sim = 0
        else:
            sim = 1.0/(1.0 + L)
        return sim
    
    def match(self, ent1, ent2, match_type = "is_a"):
        """        
        Check if ent1 matches ent2. 
        Type = "is_a":  ent1 matches ent2 if ent1 is a hyponym of ent2 (or equal to ent2)
        Type = "equal": ent1 matches en2 iff ent1 is equal to ent2.
        
        Args:
            - ent1 (SEM_ENT)
            - ent2 (SEM_ENT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
            See similarity()
        
        """
        dist = self.shortest_path(ent1, ent2)
        if (match_type == "is_a" and dist >= 0):
            return True
        elif (match_type == "equal" and dist == 0):
            return True
        return False
            
###############################################################################    
class CONCEPT:
    """
    Concept (semantico-syntactic knowledge)
    
    Data:
        - name (STR): Name of the concept.
        - meaning (STR) : Meaning it carries.
    """
    SEMANTIC_NETWORK = None # A constant SEM_NET
    
    def __init__(self, name='', meaning=''):
        self.name = name # Concept name
        self.meaning = meaning # Concept meaning
        
    # Create concept (temporary)
    def create(self, meaning='', concept=None):
        """
        Creates a concept from a meaning string or another concept.
        (TEMPORARY)
        """
        # set field (temporary)
        if meaning:
            self.name = meaning
            self.meaning = meaning
            return True
        
        # set field (temporary)
        if concept:
            self.name = concept.name
            self.meaning = concept.meaning
            return True
        
        return False
        
    @staticmethod   
    def match(concept1, concept2, match_type = "is_a"):
        """        
        Check if concept1 matches concept2. 
        Type = "is_a":  concept1 matches concept2 if concept1 is a hyponym of concept2 (or equal to concept2)
        Type = "equal": concept1 matches concept2 if concept1 is equal to concept2.
        
        Args:
            - concept1 (CONCEPT)
            - concept2 (CONCEPT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
        
        """
        if not(CONCEPT.SEMANTIC_NETWORK):
            return False
        
        # Forward direction
        sem_ent1 = CONCEPT.SEMANTIC_NETWORK.find_meaning(concept1.meaning)
        sem_ent2 = CONCEPT.SEMANTIC_NETWORK.find_meaning(concept2.meaning)
        dist = CONCEPT.SEMANTIC_NETWORK.shortest_path(sem_ent1, sem_ent2)
        if (match_type == "is_a" and dist >= 0):
            return True
        elif (match_type == "equal" and dist == 0):
            return True

        return False

###############################################################################
if __name__=='__main__':
    s1 = SEM_REL(SEM_REL.IS_A, 'cat', 'animal')
    s2 = SEM_REL(SEM_REL.IS_A, 'dog', 'animal')
    s3 = SEM_REL(SEM_REL.IS_A, 'animal', 'being')
    
    print s1
    print s2
    print s3
    
    semantic_network = SEM_NET(relations = [s1, s2])

    semantic_network.add_relation(s3)
    
    print semantic_network
    
    concept1 = 'being'
    concept2 = 'cat'
    dist = semantic_network.distance(concept1, concept2, heuristic = False)
    print "Distance between %s and %s = %i" %(concept1, concept2, dist)  

    CONCEPT.SEMANTIC_NETWORK = semantic_network
    
    c1 = CONCEPT('c1', 'dog')
    c2 = CONCEPT('c2', 'animal+')
    
    print CONCEPT.match(c1, c1)

    
    
    
    
    
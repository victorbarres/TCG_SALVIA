# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 13:21:41 2014

@author: Victor Barres

Define semantic network related classes for TCG1.1

Uses NetworkX module to represent the semantic net.
"""
import networkx as nx

class SEM_ENT:
    """
    Semantic entity
    
    Data:
        - name (STR): Unique identifier of the entity.
        - meaning (): Meaning associated with the semantic entity.
    """    
    def __init__(self, name='', meaning=''):
        self.name = name # Concept name
        self.meaning = meaning # Concept meaning
    
    def set_name(self, name=''):
        """
        Set semantic entity name.
        """
        self.name = name
    
    def set_meaning(self, meaning=''):
        """
        Set semantic entity meaning
        """
        self.meaning = meaning
    
    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.nametype == other.name) and
            (self.meaning == other.meaning))
        return is_equal
    
class SEM_REL:
    """
    Semantic Relation
    
    Data:
        - type (STR): Type of relation.
        - pFrom (STR): Name of the source semantic entity.
        - pTo (STR): Name of the target semantic entity.
    """    
    def __init__(self, aType = 'UNDEFINED', from_sem = '', to_sem = ''):
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
        p = "%s %s %s" % (self.pFrom, self.type, self.pTo)
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
        if(not(isinstance(sem, SEM_ENT)) or sem.name==''):
            return False
        
        # Check duplication
        if self.find_node(sem.name):
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
        if not(self.find_node(sem_rel.pFrom)) or not(self.find_node(sem_rel.pTo)):
            return False
        
        # Add new relation
        self.edges.append(sem_rel)
        self._create_NX_graph()
        return True
        
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.name, meaning = node.meaning)
        for edge in self.edges:
            graph.add_edge(edge.pFrom, edge.pTo, type= edge.type)
        
        self.graph = graph
    
    def find_node(self, name):
        """
        Find node with name 'name' (STR). Returns the node if found, else returns None.
        
        Args:
            - name (STR): Name of a semantic entity.
        """
        for n in self.nodes:
            if n.name == name:
                return n
        
        return None
    
    ######
    # TO REWRITE
    ######
#    def distance(self, supMean, subMean, relType = SEM_REL.IS_A, heuristic = False):
#        """
#        Return the distance in the semantic network between a concept (subMean) and an hypernym (supMean).
#        Return -1 if supMean is not a hypernym of subMean.
#        If heuristic = True: -> does not guarantee to find the shortest distance.
#        
#        Args:
#         - supMean (str)
#         - subMean (str)
#         - relType (int)
#         - heuristic (bool)
#        """
#        visited = [] # Explored elements of the semantic network
#        dist = 0
#        
#        return self._travel(supMean, subMean, relType, dist, heuristic, visited)
#    
#    def _travel(self, supMean, subMean, relType, dist, heuristic, visited):
#        
#        if supMean == subMean: # Match found
#            return dist
#        
#        minDist = -1
#        
#        for r in self.relations:
#            if r in visited:
#                continue
#            if (r.type != relType) or (r.subMeaning != subMean):
#                continue
#            
#            # Visit the current relation
#            visited.append(r)
#            
#            # Recursively travel
#            nextDist = self._travel(supMean, r.supMeaning, relType, dist+1, heuristic, visited)
#            
#            # Un-visit
#            if not(heuristic): # if heuristic: path does not have to be the shortest
#                visited.pop()
#                     
#            if nextDist >= 0:
#                if (minDist < 0) or (minDist > nextDist):
#                    minDist = nextDist
#                if minDist <= dist + 1: 
#                    break # assumed to be the possible minimum distance
#                
#                if heuristic:
#                    break # if heuristicL just find one possible path
#            
#        return minDist
#    
#    def __str__(self):
#        p = ''
#        p += '### SEMANTIC NETWORK ###\n\n'
#        for r in self.relations:
#            p += str(r) + '\n'
#        return p      
            
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
        
    def match(concept1, concept2, inclusive = True):
        """        
        Check if two concept match. Case inclusive = False: concepts match only if they carry the same meaning.
        Case inclusive = True: If a concept is tagged with + (e.g. ANIMAL+) it will match with any of its hyponyms.
        Otherwise, concepts match if they carry the same meaning.
        
        Args:
            - concept1 (CONCEPT)
            - concept2 (CONCEPT)
            - inclusive (BOOL)
        
        Notes:
            - In the c++ version matching is boolean. No impact of distance on similarity.
        
        """
        if not(CONCEPT.SEMANTIC_NETWORK):
            return False
        
        mean1 = concept1.meaning
        incl1 = mean1[-1] == '+'
        if incl1:
            mean1 = mean1[:-1]
            
        mean2 = concept2.meaning
        incl2 = mean2[-1] == '+'
        if incl2:
            mean2 = mean2[:-1]
        
        # Forward direction
        dist1 = CONCEPT.SEMANTIC_NETWORK.distance(mean1, mean2, heuristic = True)
        if (inclusive and dist1>=0 and incl1):
            dist1 = 0 # Inclusive
        
        # Backward direction
        dist2 = CONCEPT.SEMANTIC_NETWORK.distance(mean2, mean1, heuristic = True)
        if (inclusive and dist2>=0 and incl2):
            dist2 = 0 # Inclusive
        
        if (dist1!=0) and (dist2!=0):
         return False # Only meaning with distance 0 are accepted as matched
        
        #
        # Check other fields too
        2
        return True

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

    
    
    
    
    
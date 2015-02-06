# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 13:21:41 2014

@author: Victor Barres

Define semantic knowledge related classes for TCG1.0
"""
###############################################################################
class SEM_REL:
    """
    Semantic Relation
    
    Data:
        - type (INT): UNDEFINED=0, IS_A =1
        - supMeaning (STR): Hypernym of subMeaning
        - subMeaning (STR): Hyponym of supMeaning
        
    Note:
        - Only IS_A hyponymic relation is defined in c++ code.
    """
    # Relation types
    UNDEFINED = 0
    IS_A = 1 # C++ code for TCG1.0 only handles hyponymy
    
    def __init__(self, aType = UNDEFINED, subMeaning = '', supMeaning = ''):
        self.type = aType # Relation type
        self.supMeaning = supMeaning # Superordinate meaning
        self.subMeaning= subMeaning # Subordinate meaning
    
    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.type == other.type) and
            (self.supMeaning == other.supMeaning) and 
            (self.subMeaning == other.subMeaning))
        return is_equal
    
    def __str__(self):
        if self.type == SEM_REL.IS_A:
            p = "%s IS_A %s" % (self.subMeaning, self.supMeaning)
        else:
            p = "type: %i, subMeaning: %s, supMeaning: %s" % (self.type, self.subMeaning, self.supMeaning)
        return p
    
###############################################################################
class SEM_NET:
    """
    Semantic network (acting as world knowledge)
    
    Data:
        - relation ([SEM_REL]): List of semantic relations
    
    Notes: 
        - The network is simply defined as a list of semantic relations.
    """
    def __init__(self, relations = []):
        self.relations = relations
    
    def clear(self):
        """
        Clear all relations
        """
        self.relations = []
    
    def add_relation(self, sem_rel):
        """
        Add a relation to the semantic network
        
        Args:
            sem_rel = SEM_REL
        """        
        # Check validity
        if ((sem_rel.type == SEM_REL.UNDEFINED) or 
            (sem_rel.supMeaning == '') or 
            (sem_rel.subMeaning == '')):
            return False
        
        # Check duplication
        for r in self.relations:
            if r == sem_rel:
                return False
        
        # Add new relation
        self.relations.append(sem_rel)
        return True
    
    def root(self, concept, relType):
        """
        Get the farthest semantic root of a given concept (concept) for a given relation type (relType)
        
        Args:
            - concept (str)
            - relType (int)
        
        Notes: 
            - Does not seem to be used anywhere in c++ code
        """
        return None
    
    def distance(self, supMean, subMean, relType = SEM_REL.IS_A, heuristic = False):
        """
        Return the distance in the semantic network between a concept (subMean) and an hypernym (supMean).
        Return -1 if supMean is not a hypernym of subMean.
        If heuristic = True: -> does not guarantee to find the shortest distance.
        
        Args:
         - supMean (str)
         - subMean (str)
         - relType (int)
         - heuristic (bool)
        """
        visited = [] # Explored elements of the semantic network
        dist = 0
        
        return self._travel(supMean, subMean, relType, dist, heuristic, visited)
    
    def _travel(self, supMean, subMean, relType, dist, heuristic, visited):
        
        if supMean == subMean: # Match found
            return dist
        
        minDist = -1
        
        for r in self.relations:
            if r in visited:
                continue
            if (r.type != relType) or (r.subMeaning != subMean):
                continue
            
            # Visit the current relation
            visited.append(r)
            
            # Recursively travel
            nextDist = self._travel(supMean, r.supMeaning, relType, dist+1, heuristic, visited)
            
            # Un-visit
            if not(heuristic): # if heuristic: path does not have to be the shortest
                visited.pop()
                     
            if nextDist >= 0:
                if (minDist < 0) or (minDist > nextDist):
                    minDist = nextDist
                if minDist <= dist + 1: 
                    break # assumed to be the possible minimum distance
                
                if heuristic:
                    break # if heuristicL just find one possible path
            
        return minDist
    
    def __str__(self):
        p = ''
        p += '### SEMANTIC NETWORK ###\n\n'
        for r in self.relations:
            p += str(r) + '\n'
        return p
            
            
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

    
    
    
    
    
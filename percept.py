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
        - perceptual_knowledge (PERCEPTUAL_KNOWLEDGE): The perceptual knowledge instance the precept is part of.

    """
    def __init__(self, name='',  meaning='', perceptual_knowledge=None):
        K_ENT.__init__(self, name=name, meaning=meaning)
        self.perceptual_knowledge = perceptual_knowledge
        
class PERCEPT_CAT(PERCEPT):
    """
    Perceptual knowledge category
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (): Meaning associated with the category

    """
    SEMANTIC_NETWORK = None  
    def __init__(self, name='',  meaning=''):
        PERCEPT.__init__(self, name=name, meaning=meaning)

class PERCEPT_TOKEN(PERCEPT):
    """
    Perceptual knowledge TOKEN PERCEPT
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (): Meaning associated with the category

    """
    SEMANTIC_NETWORK = None  
    def __init__(self, name='',  meaning=''):
        PERCEPT.__init__(self, name=name, meaning=meaning)
    
    def category(self):
        """
        Returns the perceptual cateory of the token
        """
        
        
class SEM_REL(K_REL):
    """
    Semantic relation between pecepts.
    Type implemented:
        - 'is_a'
        - 'is_token'
    
    Data:
        - type (STR): Type of relation.
        - pFrom (PERCEPT):  Source percept.
        - pTo (PERCEPT): Target precept.
    """    
    def __init__(self, aType = 'UNDEFINED', from_per = None, to_per = None):
        K_REL.__init__(self,aType = aType, from_ent=from_per, to_ent = to_per)

class PERCEPTUAL_KNOWLEDGE(K_NET):
    """
    Semantic network.
    
    Data:
        - nodes ([PERCEPT]): List of percepts.
        - edges ([SEM_REL]): List of semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attributes meaning = percept.meaning
            Each edge has an additional attribute type = sem_rel.type
    """
    def __init__(self, nodes=[], edges=[]):
        K_NET.__init__(self, nodes=nodes[:], edges=edges[:])
    
    def add_ent(self, percept):
        """
        Adds a percept to the the perceptual knowlege while also linking the perceptual knowledge back to the perceptt.
        """
        flag  = super(PERCEPTUAL_KNOWLEDGE, self).add_ent(percept)
        if flag:
            percept.conceptual_knowledge = self
        return flag
    
    def percepts(self, type='ALL'):
        """
        Returns a list of all percepts (type='ALL'), of all perceptual_category (type='CAT'), of all tokens ('type'='TOKEN')
        """
        if type=='ALL':
            return self.nodes
        elif type=='CAT':
            return [per for per in self.nodes if isinstance(per, PERCEPT_CAT)]
        elif type=='TOKEN':
            return [per for per in self.nodes if isinstance(per, PERCEPT_TOKEN)]
        else:
            print 'invalid type'
            return None
    
    def has_percept(self, percept_name):
        """
        Returns true iff there is a percept with name "name".
        
        Args:
            - percept_name (STR):
        """
        return self._has_entity(percept_name)
    
    def find_meaning(self, meaning):
        """
        Find percept with meaning "meaning". Returns the percept if found, else returns None.
        
        Args:
            - meaning (): Meaning of a percept
        """
        return super(PERCEPTUAL_KNOWLEDGE, self).find_meaning(meaning)
#        return self._find_meaning(meaning)
    
    def match(self, per1, per2, match_type = "is_a"):
        """        
        Check if per1 matches per2. 
        Type = "is_a":  per1 matches per2 if cpt2 is a hyponym of per2 (or equal to per2)
        Type = "equal": per1 matches per2 iff per1 is equal to per2.
        
        Args:
            - per1 (PERCEPT)
            - per2 (PERCEPT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
            See similarity()
        
        """
        return super(PERCEPTUAL_KNOWLEDGE, self).match(per1, per2, match_type = match_type) 
#        return self._match(per1, per2, match_type=match_type)`

class CONCEPTUALIZATION(object):
    """
    Knowledge of conceptualization relations mapping percepts onto concepts.
    
    Data:
        - per2cpt (DICT): Mapping from percept to concept.
    
    Note:
        - For now a percept is only associated with a single conept.

    """
    def __init__(self):
        self.per2cpt = {}
    
    def add_mapping(self, per, cpt):
        """
        Add a mapping from per (STR) name of a percept (PERCEPT) to cpt (str) name of concept (CONCEPT)
        """
        if not(per in self.per2cpt):
            self.per2cpt[per] = cpt
        else:
            err_message = "Percept %s already associated with concept %s" %(per, self.per2cpt[per])
            raise ValueError(err_message)
        
    
    def conceptualize(self, per):
        """
        For now simply returns the concept associated with per.
        """
        return self.per2cpt[per]
    
###############################################################################
if __name__=='__main__':
    print "NOTHING IMPLEMENTED"

    
    
    
    
    
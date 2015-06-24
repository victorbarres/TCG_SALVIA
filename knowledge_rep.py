# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Define knowledge representations for TCG.
For now only implements semantic net.

Uses NetworkX module to represent the semantic net.
"""
import networkx as nx

####################
### SEMANTIC NET ###
####################
class K_ENT:
    """
    Knowledge entity
    Data:
        - id (INT): Unique identifier of the knowlege entity.
        - meaning: meaning associated with the knowledge entity.
    
    Note:
        - '==' has to be defined for meaning.
    """
    ID_NEXT = 1 # Global knowledge entity counter    
    def __init__(self, name='',  meaning=''):
        self.id = K_ENT.ID_NEXT
        K_ENT.ID_NEXT += 1
        self.name = name
        self.meaning = meaning

    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.id == other.id) and
            (self.meaning == other.meaning))
        return is_equal
    
class K_REL:
    """
    Knowledge relation. Only 2 place relations are allowed. Relations are defined as directed.
    
    Data:
        - type (STR): Type of relation.
        - pFrom (K_ENT):  Source knowledge entity.
        - pTo (K_ENT): Target knowledge entity.
    """
    
    def __init__(self, aType = 'undefined', from_ent = None, to_ent = None):
        self.type = aType
        self.pFrom = from_ent
        self.pTo= to_ent
        
    def __eq__(self, other):
        is_equal = (isinstance(other, self.__class__) and 
            (self.type == other.type) and
            (self.pFrom == other.pFrom) and 
            (self.pTo == other.pTo))
        return is_equal
    
    def __str__(self):
        p = "%s %s %s" % (self.pFrom.name, self.type, self.pTo.name)
        return p

class K_NET:
    """
    Semantic network.
    
    Data:
        - nodes ([K_ENT]): List of knowledge entity.
        - edges ([K_REL]): List of knowledge relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attribute meaning = k_ent.meaning
            Each edge has an additional attribute type = k_rel.type
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
        self.create_NX_graph()
    
    def add_ent(self, k_ent):
        """
        Add a knowledge entity to the semantic network
        
        Args:
            k_ent (K_ENT): A knowlege entity
        """
        # Check validity        
        if(not(isinstance(k_ent, K_ENT)) or not(k_ent.meaning)):
            return False
        
        # Check duplication
        if self.find_meaning(k_ent.meaning):
            return False
        
        # Add new semantic entity
        self.nodes.append(k_ent)
        self.create_NX_graph()
        return True
        
    def add_relation(self, k_rel):
        """
        Add a relation to the semantic network
        
        Args:
            k_rel (K_REL): A knowledge relation
        """        
        # Check validity
        if (not(isinstance(k_rel, K_REL)) or 
            (k_rel.type == 'undefined') or 
            not(k_rel.pFrom) or 
            not(k_rel.pTo)):
            return False
        
        # Check duplication
        for r in self.edges:
            if r == k_rel:
                return False
        
        # Check that source and target of relation are defined.
        if not(self.find_meaning(k_rel.pFrom.meaning)) or not(self.find_meaning(k_rel.pTo.meaning)):
            return False
        
        # Add new relation
        self.edges.append(k_rel)
        self.create_NX_graph()
        return True
        
    def create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.id, meaning=node.meaning)
        for edge in self.edges:
            graph.add_edge(edge.pFrom.id, edge.pTo.id, type= edge.type)
        
        self.graph = graph
    
    def find_meaning(self, meaning):
        """
        Find k_ent with meaning "meaning". Returns the entity if found, else returns None.
        
        Args:
            - meaning (): Meaning of a knowledge entity.
        """
        for n in self.nodes:
            if n.meaning == meaning:
                return n
        
        return None
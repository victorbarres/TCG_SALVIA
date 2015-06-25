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
        self._create_NX_graph()
    
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
        if self._find_meaning(k_ent.meaning):
            return False
        
        # Add new semantic entity
        self.nodes.append(k_ent)
        self._create_NX_graph()
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
        if not(self._find_meaning(k_rel.pFrom.meaning)) or not(self._find_meaning(k_rel.pTo.meaning)):
            return False
        
        # Add new relation
        self.edges.append(k_rel)
        self._create_NX_graph()
        return True
    
    def shortest_path(self, from_ent, to_ent, rel_types=['is_a']):
        """
        Returns the length of the shortest path, if it exists, between from_cpt and to_cpt in the k_net graph.
        Only considers the edges of type belonging to rel_types.
        
        If no path exists, returns -1
        
        Relies on NetworkX implementation of path length
        
        Args:
            - from_ent (K_ENT): Origin
            - to_cpt (K_ENT): Target
        """
        path_len = -1
        graph = self.graph.copy() # Not efficient...
        
        #Only keep the relevant edges
        to_remove =[]
        for u,v,d in graph.edges_iter(data=True):
            if not(d['type'] in rel_types):
                to_remove.append((u,v))
        graph.remove_edges_from(to_remove)
        
        try:
            path_len = nx.shortest_path_length(graph, source=from_ent.id, target=to_ent.id, weight=None)
        except nx.NetworkXNoPath:
            return path_len
            
        return path_len
    
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.id, meaning=node.meaning)
        for edge in self.edges:
            graph.add_edge(edge.pFrom.id, edge.pTo.id, type= edge.type)
        
        self.graph = graph
    
    def _find_meaning(self, meaning):
        """
        Find k_ent with meaning "meaning". Returns the entity if found, else returns None.
        
        Args:
            - meaning (): Meaning of a knowledge entity.
        """
        for n in self.nodes:
            if n.meaning == meaning:
                return n
        
        return None
    
    def satisfy_rel(self, ent1, rel_type, ent2):
        """
        """
        if ent1 and ent2:
            if not(self.graph.has_edge(ent1.id, ent2.id)):
                return False
            else:
                edge_data = self.graph.get_edge_data(ent1.id, ent2.id)
                if not(rel_type):
                    return [(ent1, edge_data['type'], ent2)]
                elif edge_data['type'] == rel_type:
                    return [(ent1, rel_type, ent2)]
                else:
                    return []     
        elif ent1 and not(ent2):
            successors = self.graph.successors(ent1.id)
            res = []
            for s in successors:
                res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
        elif not(ent1) and ent2:
            predecessors = self.graph.predecessors(ent2.id)
            res = []
            for p in predecessors:
                res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
        else:
            res = []
            for ent1 in self.nodes:
                for ent2 in self.nodes:
                    res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
    
    def _similarity(self, ent1, ent2):
        """
        Returns a similarity score between ent1 and ent2.
        Uses path similarity.
        Args:
            - ent1 (K_ENT):
            - ent2 (K_ENT):
        
        Examples for is-a taxonomy (e.g. Wordnet):
            Path similarity: 1/(L+1), L=shortest path distance
            Leackock-Chodrow Similarity: -log(L/2*D) where L=shortest path length, D=taxonomy depth
            Wu-Palmer Similarlity: 2*depth(lcs)/(depth(s1) + depth(s2)), lcs = Least Common Subsumer.
            Resnik Similarity (Corpus dependent): IC(lcs)
            Lin Similarity (Corpus dependent): 2*IC(lcs)/(IC(s1) + IC(s2))
            Jiang & Conrath Similarity:  1/jcn_distance, jcn_distance =  IC(s1) + IC(s2) - 2 * IC(lcs). 
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
    
    def _match(self, ent1, ent2, match_type = "is_a"):
        """        
        Check if ent1 matches ent2. 
        Type = "is_a":  ent1 matches ent2 if ent2 is a hyponym of ent2 (or equal to ent2)
        Type = "equal": ent1 matches ent2 iff ent1 is equal to ent2.
        
        Args:
            - ent1 (K_ENT)
            - ent2 (K_ENT)
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
        
# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Define knowledge representations for TCG.
For now only implements: semantic net and simple knowledge frames.

Uses NetworkX module to represent the semantic net and the frames' content.
"""
from __future__ import division
import matplotlib.pyplot as plt
import networkx as nx

####################
### SEMANTIC NET ###
####################
class K_ENT(object):
    """
    Knowledge entity
    Data:
        - id (INT): Unique identifier of the knowlege entity.
        - meaning: meaning associated with the knowledge entity.
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
    
class K_REL(object):
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

class K_NET(object):
    """
    Semantic network.
    
    Data:
        - nodes ([K_ENT]): List of knowledge entity.
        - edges ([K_REL]): List of knowledge relations.
        - graph (networkx.DiGraph): A NetworkX graph implementation of the semantic net.
            Each node has an additional attribute meaning = k_ent.meaning
            Each edge has an additional attribute type = k_rel.type
    """
    def __init__(self, nodes=[], edges=[]):
        self.nodes = nodes[:]
        self.edges = edges[:]
        self.graph = None
    
    def clear(self):
        """
        Clear all.
        """
        self.nodes = []
        self.edges = []
        self._create_graph()
    
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
        self._create_graph()
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
        self._create_graph()
        return True
    
    def shortest_path(self, from_ent, to_ent, rel_types=['is_a']):
        """
        Returns the length of the shortest path, if it exists, between from_cpt and to_cpt in the k_net graph.
        Only considers the edges of type belonging to rel_types.
        
        If no path exists, returns -1
        
        Relies on NetworkX implementation of path length
        
        Args:
            - from_ent (K_ENT): Origin
            - to_ent (K_ENT): Target
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
    
    def satisfy_rel(self, ent1, rel_type, ent2):
        """
        """
        if ent1 and ent2:
            if not(self.graph.has_edge(ent1.id, ent2.id)):
                return []
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
                node_data = self.graph.node[s]
                ent2 = self.find_meaning(node_data['meaning'])
                res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
        elif not(ent1) and ent2:
            predecessors = self.graph.predecessors(ent2.id)
            res = []
            for p in predecessors:
                node_data = self.graph.node[p]
                ent1 = self.find_meaning(node_data['meaning'])
                res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
        else:
            res = []
            for ent1 in self.nodes:
                for ent2 in self.nodes:
                    res.extend(self.satisfy_rel(ent1, rel_type, ent2))
            return res
    
    def similarity(self, ent1, ent2):
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
    
    def match(self, ent1, ent2, match_type = "is_a"):
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
    
    def show(self):
        """
        """
        plt.figure()
        node_labels = dict((n, d) for n,d in self.graph.nodes(data=True))
        pos = nx.spring_layout(self.graph)        
        nx.draw_networkx(self.graph, pos=pos, with_labels= False, node_color='g')
        nx.draw_networkx_labels(self.graph, pos=pos, labels= node_labels)


    def _create_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.id, meaning=node.meaning)
        for edge in self.edges:
            graph.add_edge(edge.pFrom.id, edge.pTo.id, type= edge.type)
        
        self.graph = graph
        
    
    def _has_entity(self, ent_name):
        """
        Returns entity iff there is a entity with name "name".
        
        Args:
            - entt_name (STR):
        """
        for n in self.nodes:
            if n.name == ent_name:
                return n
        return None

################
### FRAME ###
################
class FRAME_ELEM:
    """
    Frame element (base class).
    """
    
    ID_NEXT = 1 # GLOBAL FRAME_ELEM ID COUNTER
    
    def __init__(self):
        self.id = FRAME_ELEM.ID_NEXT
        FRAME_ELEM.ID_NEXT += 1
        self.name = ''
        self.concept = None # Representing concept
        
class FRAME_NODE(FRAME_ELEM):
    """
    Frame node.
    
    Data(inherited):
    """
    def __init__(self):
        FRAME_ELEM.__init__(self)
    
    def copy(self):
        new_node = FRAME_NODE()
        new_node.name = '%s_%i' %(self.name, new_node.id)
        name_corr = (self.name, new_node.name)
        new_node.concept = self.concept
        return (new_node, name_corr)

class FRAME_REL(FRAME_ELEM):
    """
    Frame relation.
    
    Data(inherited):
    Data:
        - pFrom (TP_NODE): 
        - pTo (TP_NODE):
    """
    def __init__(self):
        FRAME_ELEM.__init__(self)
        self.pFrom = None
        self.pTo = None
    
    def copy(self):
        new_rel = FRAME_REL()
        new_rel.name = '%s_%i' %(self.name, new_rel.id)
        name_corr = (self.name, new_rel.name)
        new_rel.concept = self.concept
        new_rel.pfrom = self.pFrom
        new_rel.pTo = self.pTo
        return (new_rel, name_corr)

class FRAME(object):
    """
    Knowledge Frame

    Data:
        - name (STR): rame name
        - nodes ([FRAME_NODES]): Set of FRAME nodes.
        - edges ([FRAME_REL]): Set of FRAME relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
    
    The use of NetworkX graph allows the system to rely on NetworkX efficient python implementation of graph algorithms (in particular
    subgraph isomorphisms search).
    """
    def __init__(self, name=''):
        self.name =  name
        self.nodes = []
        self.edges = []
        self.graph = None
    
    def find_elem(self, name):
        """
        Returns the element with name "name". Returns None if name is not found.
        """
        for elem in self.nodes + self.edges:
            if elem.name == name:
                return elem
        return None
    
    def add_frame_elem(self, frame_elem):
        """
        Add frame_elem (FRAME_ELEM) to the Frame.
        If frame_elem is a NODE, it is added to nodes.
        If frame_elem is a RELATION, it is added to edges.
        
        OPTION: MAKE SURE THAT THE CONCEPTS DO BELONG TO THE CONCEPTUAL KNOWLEDGE, ELSE RETURN AN ERROR.
        """
        # Check for duplicate
        if self.find_elem(frame_elem.name):
            return False
        
        # Add a new frame_elem to either node or edge list.
        if isinstance(frame_elem, FRAME_NODE):
            self.nodes.append(frame_elem)
        elif isinstance(frame_elem, FRAME_REL):
            self.edges.append(frame_elem)
        else:
            return False
        
        # Update NetworkX graph
        self._create_NX_graph()
    
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.name, concept=node.concept)
        for edge in self.edges:
            pFrom = edge.pFrom.name if edge.pFrom else None
            pTo =  edge.pTo.name if edge.pTo else None
            graph.add_edge(pFrom, pTo, name=edge.name, concept=edge.concept)
        
        self.graph = graph
    
    def copy(self):
        """
        """
        new_frame = FRAME()
        new_frame.name = self.name
        node_corr = {}
        name_corr = {}
        for node in self.nodes:
            (new_node, c) = node.copy()
            node_corr[node] = new_node
            name_corr[c[0]] = c[1]
            new_frame.nodes.append(new_node)
        for edge in self.edges:
            (new_edge, c) = edge.copy()
            name_corr[c[0]] = c[1]
            new_edge.pFrom = node_corr[edge.pFrom]
            new_edge.pTo = node_corr[edge.pTo]
            new_frame.edges.append(new_edge)
        new_frame._create_NX_graph()
        
        return (new_frame, name_corr)
    
    def show(self):
        """
        """
        self._create_NX_graph()
        plt.figure(facecolor='white')
        plt.axis('off')
        title = 'Frame'
        plt.title(title)
        node_labels = dict((n, d['concept'].meaning) for n,d in self.graph.nodes(data=True))
        edge_labels = dict(((u,v), d['concept'].meaning) for u,v,d in self.graph.edges(data=True))
        pos = nx.spring_layout(self.graph)        
        nx.draw_networkx(self.graph, pos=pos, with_labels= False, node_color='g')
        nx.draw_networkx_labels(self.graph, pos=pos, labels= node_labels)
        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)

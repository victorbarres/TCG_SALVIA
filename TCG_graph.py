# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 10:53:22 2015

@author: Victor Barres

TCG graph operations

Uses networkx
"""
from networkx.algorithms import isomorphism

## Find subgraph isomorphisms ###
def find_sub_iso(G, G_pat, node_match=None, edge_match=None): ### NEEDS TO RETURN ISOS THAT INCLUDE THE EDGE MAPPINGS!
    """
    Returns the list of all the graph isomorphisms between a subgraph of G and the graph pattern G_pat.
    G and G_pat should be NetworkX Digraphs.
    node_match and edge_match should be either "None" are networkx isomorphisms matching functions (categorical, numerical, or generic)
    Each isomorphim is defined as a dictionary with keys "nodes" itself a dictionary mapping G_pat nodes to G nodes, and "edges" a dictionary mappign G_pat edges to 
    G edges.
    """
    DiGM = isomorphism.DiGraphMatcher(G, G_pat, node_match=node_match, edge_match=edge_match)

    sub_iso = []

    my_iter  = DiGM.subgraph_isomorphisms_iter()
    for mapping in my_iter:
        iso = {"nodes":{}, "edges":{}}
        for key in mapping:
            iso["nodes"][mapping[key]] = key # reverse mapping for convenience (SemFrame -> SemRep)
        
        for edge in G_pat.edges(): # Add mapping between edges
            iso["edges"][edge] = (iso["nodes"][edge[0]], iso["nodes"][edge[1]])
        sub_iso.append(iso)
    
    return sub_iso

###############################################################################
if __name__=="__main__":
    import networkx as nx    
    # Main graph
    G = nx.DiGraph()
    
    G.add_node(0, attr=0)
    G.add_node(1, attr=0)
    G.add_node(2, attr=0)
    G.add_node(3, attr=0)
    
    G.add_edge(0,1, attr=-1)
    G.add_edge(1,2, attr=-1)
    G.add_edge(2,3, attr=-1)
    G.add_edge(3,0, attr=-1)
    
    nx.draw(G)
    
    # Graph pattern
    G_pat= nx.DiGraph()
    
    G_pat.add_node("a", attr=0)
    G_pat.add_node("b", attr=0)
    G_pat.add_node("c", attr=0)
    
    G_pat.add_edge("a","b", attr=-1)
    G_pat.add_edge("b","c", attr=-1)
    
    nx.draw(G_pat)
    
    # Categorical match functions
    nm_cat = isomorphism.categorical_node_match("attr", 1)
    em_cat = isomorphism.categorical_edge_match("attr", 1)
    
    print find_sub_iso(G, G_pat, node_match = nm_cat, edge_match=em_cat)
    
    # Numerical match functions
    nm_num = isomorphism.numerical_node_match("attr", 0, atol=0.5, rtol=1e-05) # Matches if |x-y|<= atol + abs(y)*rtol
    print find_sub_iso(G, G_pat, node_match = nm_num, edge_match=None)
    
    # Generic match functions
    op = lambda x,y: x >= y
    nm_gen = isomorphism.generic_node_match("attr", 0, op)
    sub_iso = find_sub_iso(G, G_pat, node_match = nm_gen, edge_match=None)
    
    print sub_iso[0]["nodes"].values()
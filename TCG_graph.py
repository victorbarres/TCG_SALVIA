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
    """
    DiGM = isomorphism.DiGraphMatcher(G, G_pat, node_match=node_match, edge_match=edge_match)

    sub_iso = []

    my_iter  = DiGM.subgraph_isomorphisms_iter()
    for iso in my_iter:
        print iso
        sub_iso.append(iso)
    
    return sub_iso


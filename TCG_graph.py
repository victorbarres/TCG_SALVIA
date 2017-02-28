# -*- coding: utf-8 -*-
"""
@author: Victor Barres

TCG graph operations

Uses networkx
"""
from __future__ import division
from networkx import DiGraph, MultiDiGraph
from networkx.algorithms import isomorphism

## Find subgraph isomorphisms ###
def find_sub_iso(G_subgraphs, G_pat, node_match=None, edge_match=None, iso_filter=lambda x:True):
    """
    Returns the list of all the graph isomorphisms between one of the subgraphs of G in G_subgraphs and the graph pattern G_pat. 
    Each isomorphim is defined as a dictionary with keys "nodes" itself a dictionary mapping G_pat nodes to G nodes, and "edges" a dictionary mapping G_pat edges to G edges.
    
    Args:
        - G_subgraphs([NetworkX.DiGraph]): List of subgraphs
        - G_pat(NetworkX.DiGraph)
        - node_match (callable): node_match should be either "None" or networkx isomorphisms matching functions generated by node_iso_match().
        - edge_match (callable): edge_match should be either "None" or networkx isomorphisms matching functions generated by edge_iso_match().
        - iso_filter (callable): a filter imposed on the isomorphisms that will be returned. Should go from sub_iso to BOOL
    """
    sub_iso = []
    mappings = []
    
    for subgraph in G_subgraphs:
            DiGM = isomorphism.DiGraphMatcher(subgraph, G_pat, node_match=node_match, edge_match=edge_match)
            if DiGM.is_isomorphic():
                mappings.append(DiGM.mapping)
                
    for mapping in mappings:
        iso = {"nodes":{}, "edges":{}}
        for key in mapping:
            iso["nodes"][mapping[key]] = key # reverse mapping for convenience      
        for edge in G_pat.edges(): # Add mapping between edges
            iso["edges"][edge] = (iso["nodes"][edge[0]], iso["nodes"][edge[1]])
        sub_iso.append(iso)
    
    output = [s for s in sub_iso if iso_filter(s)]
    
    return output

def find_sub_multi_iso(G, G_subgraphs, G_pat, node_match=None, edge_match=None, iso_filter=lambda x:True):
    """Returns the list of all the multigraph isomorphisms between one of the subgraphs of G in G_subgraphs and the graph pattern G_pat. 
    Each isomorphim is defined as a dictionary with keys "nodes" itself a dictionary mapping G_pat nodes to G nodes, and "edges" a dictionary mapping G_pat edges to G edges
    with edge noted as a triple (key, origin, target) 
    
    Args:
        - G (NetworkX.MultiDiGraph): The graph
        - G_subgraphs([NetworkX.MultiDiGraph]): List of subgraphs of G
        - G_pat(NetworkX.MultiDiGraph): The graph pattern
        - node_match (callable): node_match should be either "None" or networkx isomorphisms matching functions generated by node_iso_match().
        - edge_match (callable): edge_match should be either "None" or networkx isomorphisms matching functions generated by multi_edge_iso_match().
        - iso_filter (callable): a filter imposed on the isomorphisms that will be returned. Should go from sub_iso to BOOL
    """
    sub_iso = []
    mappings = []    
    for subgraph in G_subgraphs:
        MultDiGM = isomorphism.MultiDiGraphMatcher(subgraph, G_pat, node_match=node_match, edge_match=edge_match)
        if MultDiGM.is_isomorphic():
            mappings.append(MultDiGM.mapping)
            
    for mapping in mappings:
        iso = {"nodes":{}, "edges":{}}
        for key in mapping:
            iso["nodes"][mapping[key]] = key # reverse mapping for convenience (SemFrame -> SemRep)        
        for u1,v1,k1,attr1 in G_pat.edges(data=True, keys=True): # Add mapping between edges, I need to find all the edges that match.
            u2 = iso["nodes"][u1]
            v2 = iso["nodes"][v1]
            target_edges_dat = G.get_edge_data(u2,v2)
            name1 = attr1.get('name', None)
            iso["edges"][(u1, v1, k1, name1)] = []
            for k2,attr2 in target_edges_dat.iteritems():
                if not(edge_match) or  edge_match({'attr':attr1}, {'attr':attr2}): # not completely sure about that. I wish I could figure out how to have nx return directly the edge mapping...
                    name2 = attr2.get('name', None)
                    iso["edges"][(u1, v1, k1, name1)].append((u2, v2, k2, name2))
        sub_iso.append(iso)
      
    output = [s for s in sub_iso if iso_filter(s)]
    return output
    
def find_max_partial_iso(G, G_subgraphs, G_pat, G_pat_subgraphs, node_match=None, edge_match=None, iso_filter=lambda x:True):
    """Returns the list of all the max (partial) multigraph isomorphisms between one of the subgraphs of G in G_subgraphs and the graph pattern G_pat. 
    Each isomorphim is defined as a dictionary with keys "nodes" itself a dictionary mapping G_pat nodes to G nodes, and "edges" a dictionary mapping G_pat edges to G edges
    with edge noted as a triple (key, origin, target) 
    
    Args:
        - G (NetworkX.MultiDiGraph): The graph
        - G_subgraphs([NetworkX.MultiDiGraph]): List of subgraphs of G
        - G_pat(NetworkX.MultiDiGraph): The graph pattern
        - G_Pat_subgraphs([NetworkX.MultiDiGraph]): List of subgraphs of G_pat
        - node_match (callable): node_match should be either "None" or networkx isomorphisms matching functions generated by node_iso_match().
        - edge_match (callable): edge_match should be either "None" or networkx isomorphisms matching functions generated by multi_edge_iso_match().
        - iso_filter (callable): a filter imposed on the isomorphisms that will be returned. Should go from sub_iso to BOOL
    """
    sub_isos = {}
    for G_pat_sub in G_pat_subgraphs:
        G_subgraphs_sub = [g for g in G_subgraphs if len(g.nodes())==len(G_pat_sub.nodes()) and len(g.edges())==len(G_pat_sub.edges())]
        sub_iso = find_sub_multi_iso(G, G_subgraphs_sub, G_pat_sub, node_match, edge_match, iso_filter)
        if sub_iso: # none empty sub_isos
            if not(sub_isos):
                sub_isos[G_pat_sub] = sub_iso
            else:
                flag = False
                for g in sub_isos.copy():
                    if is_subgraph(g, G_pat_sub):
                        sub_isos.pop(g)
                        flag = True
                if flag:
                    sub_isos[G_pat_sub] = sub_iso
    output = []
    for iso in sub_isos.values():
        output.extend(iso)
        
    return output
    
def update_max_partial_iso(newG, newG_subgraphs, G_pat, G_pat_subgraphs, old_sub_iso, node_match=None, edge_match=None, iso_filter=lambda x:True):
    """For a partial iso mapping old_sub_iso, checks if it can be expanded on newG.
    Returns:
        List of max_partial_iso that expand old_sub_iso on newG
    """
    sub_iso = find_max_partial_iso(newG, newG_subgraphs, G_pat, G_pat_subgraphs, node_match, edge_match, iso_filter)
    new_sub_iso = []
    for a_sub_iso in sub_iso:
        if sub_multi_iso_include(a_sub_iso, old_sub_iso):
            new_sub_iso.append(a_sub_iso)
    return new_sub_iso

def sub_iso_include(sub_iso1, sub_iso2):
    """
    Compare two subgraph isomorphisms from a graph G1 onto a graph G2
    Returns True if sub_iso1 includes sub_iso2
    """ 
    nodes_map1 = sub_iso1['nodes']
    nodes_map2 = sub_iso2['nodes']
    node_flag = True
    for n,v in nodes_map2.iteritems():
        if not(n in nodes_map1) or nodes_map1[n] != v:
            node_flag = False
            break
    edges_map1 = sub_iso1['edges']
    edges_map2 = sub_iso2['edges']
    edge_flag = True
    for e,v in edges_map2.iteritems():
        if not(e in edges_map1) or edges_map1[e] != v:
            edge_flag = False
            break
        
    return node_flag and edge_flag   
                               
def sub_multi_iso_include(sub_iso1, sub_iso2):
    """
    Compare two sub mutltigraph isomorphisms from a graph G1 onto a graph G2
    Returns True if sub_iso1 includes sub_iso2
    """
    nodes_map1 = sub_iso1['nodes']
    nodes_map2 = sub_iso2['nodes']

    for n,v in nodes_map2.iteritems():
        if not(n in nodes_map1) or nodes_map1[n] != v:
            return False
    
    edges_map1 = sub_iso1['edges']
    edges_map2 = sub_iso2['edges']

    for e,v in edges_map2.iteritems():   
        if not(e in edges_map1):
            return False
        s1 = set(edges_map1[e])
        s2 = set(v)
        if not s2.issubset(s1):
            return False 
    return True
        
def is_subgraph(G1, G2):
    """
    Returns true if G1 is a subgraph of G2
    """
    nodes1 = set(G1.nodes())
    edges1 = set(G1.edges())
    nodes2 = set(G2.nodes())
    edges2 = set(G2.edges())
    return nodes1.issubset(nodes2) and edges1.issubset(edges2)
            
    
    
def build_subgraphs(G, induced='edge', subgraph_filter=lambda x:True):
    """
    Returns the list of subgraphs of G (DiGraph) filtered by subgraph_filter
    induced:
        -> 'edge': edge induced subgraphs + single nodes
        -> 'edge+': edges induced subgraphs + nodes powerset.
        -> 'node': node induced subgraphs.
        -> 'node*': only node powersets, no edges
        
    - subgraph_filter (callable): subgraph_filter should be a callable that takes on a subgraph and returns True or False. Only the subgraphs that return True
                                        are considered for subgraph isomorphism matching. By default returns always True.
    """
    if induced == 'node':
        node_power_set = list_powerset(G.nodes())
        subgraphs = [G.subgraph(nbunch) for nbunch in node_power_set if nbunch != []] # Builds all the node induced subgraphs (except empty graph).
    
    if induced == 'node*':
        node_power_set = list_powerset(G.nodes(data=True))
        subgraphs = []
        for n_list in [n for n in node_power_set if n !=[]]:
            subG = DiGraph()
            subG.add_nodes_from(n_list)
            subgraphs.append(subG)
    
    if induced == 'edge':
        edge_powerset = list_powerset(G.edges(data=True))
        subgraphs = []
        for e_list in [e for e in edge_powerset if e != []]: # Not creating empty graph
            subG = DiGraph(e_list) # Creating subraph from edges
            for n in subG.node.keys():
                subG.node[n] = G.node[n] # Transfering node attributes
            subgraphs.append(subG)
            
        # Adding single nodes
        for n, d in G.nodes(data=True):
            subG = DiGraph()
            subG.add_node(n,d)
            subgraphs.append(subG)
            
    if induced == 'edge+':
        edge_powerset = list_powerset(G.edges(data=True))
        subgraphs = []
        for e_list in [e for e in edge_powerset if e != []]: # Not creating empty graph
            subG = DiGraph(e_list) # Creating subraph from edges
            for n in subG.node.keys():
                subG.node[n] = G.node[n] # Transfering node attributes
            subgraphs.append(subG)
            
        node_powerset = list_powerset(G.nodes(data=True))
        for n_list in [n for n in node_powerset if n!=[]]:
            subG = DiGraph()
            subG.add_nodes_from(n_list)
            subgraphs.append(subG)
    
    # Filtering
    subgraphs = [sG for sG in subgraphs if subgraph_filter(sG)]

    return subgraphs
    
def build_submultigraphs(G, induced='edge', subgraph_filter=lambda x:True):
    """
    Returns the list of subgraphs of G (MutliDiGraph) filtered by subgraph_filter
    induced:
        -> 'edge': edge induced subgraphs + single nodes
        -> 'edge+': edges induced subgraphs + nodes powerset.
        -> 'node': node induced subgraphs.
    """
    if induced == 'node':
        node_power_set = list_powerset(G.nodes())
        subgraphs = [G.subgraph(nbunch) for nbunch in node_power_set if nbunch != []] # Builds all the node induced subgraphs (except empty graph).
    
    if induced == 'edge':
        edge_powerset = list_powerset(G.edges(data=True))
        subgraphs = []
        for e_list in [e for e in edge_powerset if e != []]: # Not creating empty graph
            subG = MultiDiGraph(e_list)# Creating subraph from edges
            for n in subG.node.keys():
                subG.node[n] = G.node[n] # Transfering node attributes
            subgraphs.append(subG)
            
        # Adding single nodes
        for n, d in G.nodes(data=True):
            subG = MultiDiGraph()
            subG.add_node(n,d)
            subgraphs.append(subG) 
            
    if induced == 'edge+':
        edge_powerset = list_powerset(G.edges(data=True))
        subgraphs = []
        for e_list in [e for e in edge_powerset if e != []]: # Not creating empty graph
            subG = MultiDiGraph(e_list)# Creating subraph from edges
            for n in subG.node.keys():
                subG.node[n] = G.node[n] # Transfering node attributes
            subgraphs.append(subG)
            
        node_powerset = list_powerset(G.nodes(data=True))
        for n_list in [n for n in node_powerset if n!=[]]:
            subG = MultiDiGraph()
            subG.add_nodes_from(n_list)
            subgraphs.append(subG)
    
    # Filtering
    subgraphs = [sG for sG in subgraphs if subgraph_filter(sG)]
                 
    return subgraphs
        
def list_powerset(lst):
    """
    Returns the powerset of all the elements in lst
    """
    result = [[]]
    for x in lst:
        result.extend([subset + [x] for subset in result])
    return result

def node_iso_match(attr, attr_default, op):
    """
    Returns an node_match function that can be used in find_sub_iso()
    
    Args: 
        - attr: the name (or list of names) of attributes to consider.
        - attr_default: default value (or list of values) for attributes
        - op: a callable boolean function.
    
    Note: This function in its current form is just a wrapper around networkx.isomorphism.generic_node_match()
    """
    nm = isomorphism.generic_node_match(attr, attr_default, op)
    return nm

def edge_iso_match(attr, attr_default, op):
    """
    Returns an edge_match function that can be used in find_sub_iso()
    
    Args:
        - attr: the name (or list of names) of attributes to consider.
        - attr_default: default value (or list of values) for attributes
        - op: a callable boolean function.
    
    Note: This function in its current form is just a wrapper around networkx.isomorphism.generic_edge_match()
    """
    em = isomorphism.generic_edge_match(attr, attr_default, op)
    return em

def multi_edge_iso_match(attr, attr_default, op):
    """
    Returns an edge_match function that can be used in find_sub_multi_iso()
    
    Args:
        - attr: the name of attribute to consider.
        - attr_default: default value
        - op: a callable boolean function.
    
    Note: This function in its current form is just a wrapper around networkx.isomorphism.generic_multiedge_match()
    """
    em = isomorphism.generic_multiedge_match(attr, attr_default, op)
    return em
    
    
def test1():
    """Test Digraph isomorphisms
    """
    import networkx as nx   
    import matplotlib.pyplot as plt
    
    # Main graph
    G = nx.DiGraph()
    
    G.add_node(0, attr=0)
    G.add_node(1, attr=0)
    G.add_node(2, attr=0)
    G.add_node(3, attr=0)
    
    G.add_edge(0,1, attr=-1)
    G.add_edge(1,2, attr=-1)
    G.add_edge(2,0, attr=-1)
    
#    nx.draw(G)
#    plt.show()
    
    # Graph pattern
    G_pat= nx.DiGraph()
    
    G_pat.add_node("a", attr=0)
    G_pat.add_node("b", attr=0)
    G_pat.add_node("c", attr=0)
    
    G_pat.add_edge("a","b", attr=-1)
    G_pat.add_edge("b","c", attr=-1)
#    
#    nx.draw(G_pat)
#    plt.show()
    
    G_subgraphs = build_subgraphs(G, induced='edge') # In this example, if induced = 'nodes' it won't find any isomorphisms.
    
    # Categorical match functions
    nm_cat = isomorphism.categorical_node_match("attr", 1)
    em_cat = isomorphism.categorical_edge_match("attr", 1)
    
    print find_sub_iso(G_subgraphs, G_pat, node_match = nm_cat, edge_match=em_cat)
    
    # Numerical match functions
    nm_num = isomorphism.numerical_node_match("attr", 0, atol=0.5, rtol=1e-05) # Matches if |x-y|<= atol + abs(y)*rtol
    print find_sub_iso(G_subgraphs, G_pat, node_match = nm_num, edge_match=None)
    
    # Generic match functions
    op = lambda x,y: x >= y
    nm_gen = isomorphism.generic_node_match("attr", 0, op)
    sub_iso = find_sub_iso(G_subgraphs, G_pat, node_match = nm_gen, edge_match=None)
    
    if sub_iso:
        print sub_iso[0]["nodes"].values()
        
def test2():
    """Test extension to MultiDiGraphs
    """
    import networkx as nx    
    
    # Main graph
    G = nx.MultiDiGraph()
    
    G.add_node(0, attr_dict={'val':1})
    G.add_node(1, attr_dict={'val':2})
    G.add_node(2, attr_dict={'val':3})
    G.add_node(3, attr_dict={'val':0})
    
    G.add_edge(0,1, attr_dict={'val':1})
    G.add_edge(0,1, attr_dict={'val':2})
    G.add_edge(0,1, attr_dict={'val':3})
    G.add_edge(1,2, attr_dict={'val':1})
    G.add_edge(1,2, attr_dict={'val':2})
    G.add_edge(2,0, attr_dict={'val':1})

    
    # Graph pattern
    G_pat= nx.MultiDiGraph()
    
    G_pat.add_node("a", attr_dict={'val':1})
    G_pat.add_node("b", attr_dict={'val':2})
    G_pat.add_node("c", attr_dict={'val':3})
    
    G_pat.add_edge("a","b", attr_dict={'val':1})
    G_pat.add_edge("b","c", attr_dict={'val':1})
    
    G_subgraphs = build_submultigraphs(G, induced='edge') # In this example, if induced = 'nodes' it won't find any isomorphisms.
    
    # Generic match functions
    op = lambda x,y: x == y
    nm_gen = node_iso_match("val", 0, op)
    em_gen = multi_edge_iso_match("val", 0, op)
    sub_iso = find_sub_multi_iso(G, G_subgraphs, G_pat, node_match = nm_gen, edge_match=em_gen)
    
    if sub_iso:
        print sub_iso
        
def test3():
    """Test extension to max partial isomorphism
    """
    import networkx as nx    
    
    # Main graph
    G = nx.MultiDiGraph()
    
    G.add_node(0, attr_dict={'val':1})
    G.add_node(1, attr_dict={'val':2})
    G.add_node(2, attr_dict={'val':3})
    G.add_node(3, attr_dict={'val':0})
    
    G.add_edge(0,1, attr_dict={'val':1})
    G.add_edge(0,1, attr_dict={'val':2})
    G.add_edge(0,1, attr_dict={'val':3})
    G.add_edge(1,2, attr_dict={'val':1})
    G.add_edge(1,2, attr_dict={'val':2})
    G.add_edge(2,0, attr_dict={'val':1})

    G_subgraphs = build_submultigraphs(G, induced='edge') # In this example, if induced = 'nodes' it won't find any isomorphisms.
    
    # Graph pattern
    G_pat= nx.MultiDiGraph()
    G_pat.add_node("a", attr_dict={'val':1})
    G_pat.add_node("b", attr_dict={'val':2})
    G_pat.add_node("c", attr_dict={'val':3})
    
    G_pat.add_edge("a","b", attr_dict={'val':1})
    G_pat.add_edge("b","c", attr_dict={'val':1})
    G_pat.add_edge("b","c", attr_dict={'val':2})
    
    G_pat_subgraphs = build_submultigraphs(G_pat, induced='edge+')
    
    # Generic match functions
    op = lambda x,y: x == y
    nm_gen = node_iso_match("val", 0, op)
    em_gen = multi_edge_iso_match("val", 0, op)
    sub_iso = find_max_partial_iso(G, G_subgraphs, G_pat, G_pat_subgraphs, node_match = nm_gen, edge_match=em_gen)
    
    if sub_iso:
        print sub_iso
    
###############################################################################
if __name__=="__main__":
    test3()

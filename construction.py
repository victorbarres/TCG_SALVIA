# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 15:48:47 2014

@author: Victor Barres

Define constructions related classes for TCG1.1
The Template Classes define all the basic template elements that are used to build a construction.

Uses NetworkX module to represent construction SemFrame graph.
"""
import networkx as nx

########################
### Template Classes ###
########################
class TP_ELEM:
    """
    Template element (base class).
    """
    # Element types
    UNDEFINED = 0
    NODE = 1
    RELATION = 2
    SLOT = 3
    PHONETICS = 4 
    SEMFRAME = 5
    SYNFORM = 6
    SYMLINKS = 7
    
    def __init__(self):
        self.type = self.UNDEFINED # Element type
        self.parent_cxn = None # Parent construction
    
class TP_SEM_ELEM(TP_ELEM):
    """
    Template Sem-Frame element.
    
    Data (inherited):
        - name (STR): Element's name.
        - concept (CONCEPT): Concept associated with the semantic element.
    
    Notes: 
        - Need to make sure that the link to synform is reciprocal.
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.name = ''
        self.concept = None # Representing concept
        
class TP_NODE(TP_SEM_ELEM):
    """
    Sem-Frame node.
    
    Data(inherited):
    Data:
        - type = TP_ELEM.NODE
        - head (BOOL): 
        - focus (BOOL):
    """
    def __init__(self):
        TP_SEM_ELEM.__init__(self)
        self.type = TP_ELEM.NODE
        self.head = False
        self.focus = False

class TP_REL(TP_SEM_ELEM):
    """
    Sem-Frame relation.
    
    Data(inherited):
    Data:
        - type = TP_ELEM.RELATION
        - pFrom (TP_NODE): 
        - pTo (TP_NODE):
    """
    def __init__(self):
        TP_SEM_ELEM.__init__(self)
        self.type = TP_ELEM.RELATION
        self.pFrom = None
        self.pTo = None

class TP_SYN_ELEM(TP_ELEM):
    """
    Template SynFrame element.
    
    Data(inherited):
    Data:
        - order (int): Syntactic order.
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.order = -1 
        
class TP_SLOT(TP_SYN_ELEM):
    """
    SynFrame slot.
    
    Data(inherited):
    Data:
        - type = TP_ELEM.SLOT
        - cxn_classes ([str]): Set of construction classes that can be accepted as filling this slot.
    
    Notes: 
        - Need to make sure that the link to SemFrame is reciprocal. 
    """
    def __init__(self):
        TP_SYN_ELEM.__init__(self)
        self.type = TP_ELEM.SLOT
        self.cxn_classes = [] # Construction classes that can fill this slot
        
class TP_PHON(TP_SYN_ELEM):
    """
    SynFrame phonetic notation.
    
    Data(inherited):
    Data:
        - type = TP_ELEM.PHONETICS
        - cxn_phonetics (str): the phonetic content.
        - num_syllables (int): number of syllables (used to measure utterance length)
    """
    def __init__(self):
        TP_SYN_ELEM.__init__(self)
        self.type = TP_ELEM.PHONETICS
        self.phonetics = ''
        self.num_syllables = 0

class TP_SEMFRAME(TP_ELEM):
    """
    SemFrame construction template element

    Data(inherited):
    Data:
        - type = TP_ELEM.SEMFRAME
        - nodes ([TP_NODES]): Set of template semantic nodes.
        - edges ([TP_REL]): Set of template semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
    
    The use of NetworkX graph allows the system to rely on NetworkX efficient python implementation of graph algorithms (in particular
    subgraph isomorphisms search).
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.type = TP_ELEM.SEMFRAME
        self.nodes = []
        self.edges = []
        self.graph = None
    
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node, concept=node.concept)
        for edge in self.edges:
            graph.add_edge(edge.pFrom, edge.pTo, concept= edge.concept)
        
        self.graph = graph
    
    def draw(self):
        node_labels = dict((n, d['concept'].meaning) for n,d in self.graph.nodes(data=True))
        edge_labels = dict(((u,v), d['concept'].meaning) for u,v,d in self.graph.edges(data=True))
        pos = nx.spring_layout(self.graph)        
        nx.draw_networkx(self.graph, pos=pos, with_labels= False)
        nx.draw_networkx_labels(self.graph, pos=pos, labels= node_labels)
        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)
        
        
class TP_SYNFORM(TP_ELEM):
    """
    SynForm construction template element
    Data (inherited):
    Data:
        - form ([TP_SYN_ELEM]): Form sequence.
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.type = TP_ELEM.SYNFORM
        self.form = []

class TP_SYMLINKS(TP_ELEM):
    """
    SymLinks construction template element.
    Data (inherited):
    Data:
        - SL (DICT): Map between SemFrame (TP_NODE) elements and SynForm (TP_SLOT) elements.
        
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.SL = {}
           
############################    
### Construction classes ###
############################     
class CXN:
    """
    Grammatical construction.
    
    Data:
        - name (str): construction name
        - clss (str): construction class
        - preference (int): construction preference
        - SemFrame (TP_SEMFRAME): cxn SemFrame.
        - SynForm (TP_SYNFORM): cxn SynForm.
        - SymLinks (TP_SYMLINKS): cxn SymLinks.
    """ 
    def __init__(self):
        self.name = ''
        self.clss = ''
        self.preference = 0 # construction preference
        self.SemFrame = TP_SEMFRAME() # Semantic frame
        self.SynForm = TP_SYNFORM() # Syntactic form
        self.SymLinks = TP_SYMLINKS() # Symbolic links
    
    def find_sem_elem(self, name):
        """
        Find and return SemFrame element with a given name (str).
        """
        for elem in self.SemFrame.nodes + self.SemFrame.edges:
            if elem.name == name:
                return elem
        return None
        
    def add_sem_elem(self, sem_elem):
        """
        Add sem_elem (TP_SEM_ELEM) to the SemFrame.
        If sem_elem is a NODE, it is added to SemFrame.nodes.
        If sem_elem is a RELATION, it is added to SemFrame.edges.
        
        OPTION: MAKE SURE THAT THE CONCEPTS DO BELONG TO THE CONCEPTUAL KNOWLEDGE, ELSE RETURN AN ERROR.
        """
        # Check for duplicate
        if self.find_sem_elem(sem_elem.name):
            return False
        
        # Set sem_elem variables
        sem_elem.parent_cxn = self
        
        # Add a new Sem-Frame element to either node or edge list.
        if sem_elem.type == TP_ELEM.NODE:
            self.SemFrame.nodes.append(sem_elem)
        elif sem_elem.type == TP_ELEM.RELATION:
            self.SemFrame.edges.append(sem_elem)
        else:
            return False
        
        # Update NetworkX graph
        self.SemFrame._create_NX_graph()
        return True
        
    def add_syn_elem(self, syn_elem):
        """
        Add syn_elem (TP_SYN_ELEM) to the SynForm.
        """          
        # Set syn_elem variable
        syn_elem.parent_cxn = self
        syn_elem.order = len(self.SynForm.form)
    
        # Add a new Syn-Form element
        self.SynForm.form.append(syn_elem)
        
        return True
    
    def add_sym_link(self, node, slot):
        """
        Adds a symbolic link  between the node (TP_NODE) and slot (TP_SLOT)
        """
        if (node.type != TP_ELEM.NODE) or (slot.type != TP_ELEM.SLOT):
            return False
        if self.SymLinks.SL.has_key(node) or (slot in self.SymLinks.SL.values()):
            return False
        self.SymLinks.SL[node] = slot
        return True
    
    
#    def __str__(self): # To rewrite
#        p = ''
#        p += "name: %s\n" % self.name
#        p += "class: %s\n" % self.clss
#        p += "preference: %i\n" % self.preference
#        p += "SEM-FRAME:\n"
#        for s in self.SemFrame:
#            p += "\tname: %s\n" % s.name
#            if s.type == TP_ELEM.NODE:
#                p += "\ttype: node\n"
#            elif s.type == TP_ELEM.RELATION:
#                p += "\ttype: relation\n"
#            else:
#                p += "\ttype: %s\n" % s.type
#            p += "\tconcept: %s\n" % s.concept.meaning
#            p += "\tshared: %s\n" % s.shared
#            p += "\thead: %s\n" % s.head
#            if s.type == TP_ELEM.NODE:
#                if s.linked_slot == None:
#                    p += "\tlinked slot order: None\n"
#                else:
#                    p += "\tlinked slot order: %i\n" % s.linked_slot.order 
#            if s.type == TP_ELEM.RELATION:
#                p += "\tfrom: %s\n" % s.pFrom.name
#                p += "\tto: %s\n" % s.pTo.name
#            if self.SemFrame.index(s)!=(len(self.SemFrame)-1):
#                p += '\n'
#        p += "SYN-FORM:\n"
#        for s in self.SynForm:
#            p += "\torder: %i\n" % s.order
#            if s.type == TP_ELEM.SLOT:
#                p += "\ttype: slot\n"
#                p += "\tlinked_node: %s\n" % s.linked_SemElem.name
#                p += "\tclasses: [%s]\n" % ' '.join(s.cxn_classes)
#            if s.type == TP_ELEM.PHONETICS:
#                p += "\ttype: phonetics\n"
#                p += "\tphon: %s\n" % s.phonetics
#                p += "\tnum_syllables: %i\n" % s.num_syllables
#            if self.SynForm.index(s)!=(len(self.SynForm)-1):
#                p += '\n'
#        
#        return p
        
####################################
### Grammar: set of construtions ###
####################################       
class GRAMMAR:
    """
    Grammar defined as a set of constructions ("constructicon")
    
    Data:
        - constructions ([CXN])
    """
    def __init__(self):
        self.constructions = []
    
    def find_construction(self, name):
        """
        Find construction in grammar for a given name.
        
        Args:
            - name (str)
        """
        for cxn in self.constructions:
            if cxn.name == name:
                return cxn
        return None
    
    def add_construction(self, construction):
        """
        Add construction (CXN) to grammar.
        """
        # Check for duplicate
        if self.find_construction(construction):
            return False
        
        # Add new construction
        self.constructions.append(construction)
        return True
    
    def clear(self):
        """
        Remove all constructions from grammar.
        """
        self.constructions = []
    
#    def __str__(self):
#        p = ''
#        p += "### TCG GRAMMAR ###\n\n"
#        for c in self.constructions:
#            p += str(c)
#            p += '\n\n'
#        
#        return p
#    
#    def print_cxn(self, cxn_name):
#        """
#        Print the cxn with name cxn_name (STR) if it is found in the grammar.
#        """        
#        cxn = self.find_construction(cxn_name)
#        if not(cxn):
#            print "%s not found..." % cxn_name
#        else:
#            print cxn     
###############################################################################

if __name__=='__main__':
    print "No test case implemented."
    
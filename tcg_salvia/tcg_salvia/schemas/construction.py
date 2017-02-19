# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define constructions related classes for TCG1.1
The Template Classes define all the basic template elements that are used to build a construction.

Uses NetworkX module to represent construction SemFrame graph and SynForm graph.
"""
from __future__ import division

import matplotlib.pyplot as plt
import networkx as nx

########################
### Template Classes ###
########################
class TP_ELEM(object):
    """
    Template element (base class).
    """
    
    ID_NEXT = 1 # GLOBAL TP_ELEM ID COUNTER
    
    def __init__(self):
        self.id = TP_ELEM.ID_NEXT
        TP_ELEM.ID_NEXT += 1
        self.name = ''
    
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
        self.concept = None # Representing concept
        
class TP_NODE(TP_SEM_ELEM):
    """
    Sem-Frame node.
    
    Data(inherited):
    Data:
        - head (BOOL): 
        - focus (BOOL):
        - frame (BOOL):
    """
    def __init__(self):
        TP_SEM_ELEM.__init__(self)
        self.head = False
        self.focus = False
        self.frame = False
    
    def copy(self):
        new_node = TP_NODE()
        new_node.name = '%s_%i' %(self.name, new_node.id)
        name_corr = (self.name, new_node.name)
        new_node.concept = self.concept
        new_node.head = self.head
        new_node.focus = self.focus
        new_node.frame = self.frame
        return (new_node, name_corr)

class TP_REL(TP_SEM_ELEM):
    """
    Sem-Frame relation.
    
    Data(inherited):
    Data:
        - pFrom (TP_NODE): 
        - pTo (TP_NODE):
    """
    def __init__(self):
        TP_SEM_ELEM.__init__(self)
        self.pFrom = None
        self.pTo = None
    
    def copy(self):
        new_rel = TP_REL()
        new_rel.name = '%s_%i' %(self.name, new_rel.id)
        name_corr = (self.name, new_rel.name)
        new_rel.concept = self.concept
        new_rel.pfrom = self.pFrom
        new_rel.pTo = self.pTo
        return (new_rel, name_corr)

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
        - cxn_classes ([str]): Set of construction classes that can be accepted as filling this slot.
    
    Notes: 
        - Need to make sure that the link to SemFrame is reciprocal. 
    """
    def __init__(self):
        TP_SYN_ELEM.__init__(self)
        self.cxn_classes = [] # Construction classes that can fill this slot
    
    def copy(self):
        new_slot = TP_SLOT()
        new_slot.name = '%s_%i' %(self.name, new_slot.id)
        name_corr = (self.name, new_slot.name)
        new_slot.order = self.order
        new_slot.cxn_classes = self.cxn_classes[:]
        return (new_slot, name_corr)
        
class TP_PHON(TP_SYN_ELEM):
    """
    SynFrame phonetic notation.
    
    Data(inherited):
    Data:
        - cxn_phonetics (str): the phonetic content.
        - num_syllables (int): number of syllables (used to measure utterance length)
    """
    def __init__(self):
        TP_SYN_ELEM.__init__(self)
        self.cxn_phonetics = ''
        self.num_syllables = 0
    
    def copy(self):
        new_phon = TP_PHON()
        new_phon.name = '%s_%i' %(self.name, new_phon.id)
        name_corr = (self.name, new_phon.name)
        new_phon.order = self.order
        new_phon.cxn_phonetics = self.cxn_phonetics
        new_phon.num_syllables = self.num_syllables
        return (new_phon, name_corr)

class TP_SEMFRAME(TP_ELEM):
    """
    SemFrame construction template element

    Data(inherited):
    Data:
        - nodes ([TP_NODES]): Set of template semantic nodes.
        - edges ([TP_REL]): Set of template semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
    
    The use of NetworkX graph allows the system to rely on NetworkX efficient python implementation of graph algorithms (in particular
    subgraph isomorphisms search).
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.nodes = []
        self.edges = []
        self.graph = None
    
    def get_head(self):
        """
        Return head node (NEED TO CHECK FOR THE CASE OF MULTIPLE HEAD NODES!!!!!!)
        """
        for node in self.nodes:
            if node.head:
                return node
    
    def find_elem(self, name):
        """
        Returns the element with name "name". Returns None if name is not found.
        """
        for elem in self.nodes + self.edges:
            if elem.name == name:
                return elem
        
        return None
    
    def _create_NX_graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node, concept=node.concept, frame=node.frame)
        for edge in self.edges:
            graph.add_edge(edge.pFrom, edge.pTo, concept=edge.concept)
        
        self.graph = graph
    
    def copy(self):
        """
        """
        new_semframe = TP_SEMFRAME()
        node_corr = {}
        name_corr = {}
        for node in self.nodes:
            (new_node, c) = node.copy()
            node_corr[node] = new_node
            name_corr[c[0]] = c[1]
            new_semframe.nodes.append(new_node)
        for edge in self.edges:
            (new_edge, c) = edge.copy()
            name_corr[c[0]] = c[1]
            new_edge.pFrom = node_corr[edge.pFrom]
            new_edge.pTo = node_corr[edge.pTo]
            new_semframe.edges.append(new_edge)
        new_semframe._create_NX_graph()
        
        return (new_semframe, name_corr)
    
    def draw(self):
        self._create_NX_graph()
        plt.figure(facecolor='white')
        plt.axis('off')
        title = 'SemFrame'
        plt.title(title)
        node_labels = dict((n, d['concept'].meaning) for n,d in self.graph.nodes(data=True))
        edge_labels = dict(((u,v), d['concept'].meaning) for u,v,d in self.graph.edges(data=True))
        pos = nx.spring_layout(self.graph)        
        nx.draw_networkx(self.graph, pos=pos, with_labels= False, node_color='g')
        nx.draw_networkx_labels(self.graph, pos=pos, labels= node_labels)
        nx.draw_networkx_edge_labels(self.graph, pos=pos, edge_labels=edge_labels)
    
    @staticmethod
    def unify(SF_p, node_p_name, SF_c, node_c_name):
        """
        Not commutative.
        """
        (SF_p_copy, c_p) = SF_p.copy()
        (SF_c_copy, c_c) = SF_c.copy()
        
        # Insert the child graph into the parent graph by substituting node_p by node_c.
        node_p = SF_p_copy.find_elem(c_p[node_p_name])
        SF_p_copy.nodes.remove(node_p)
        SF_p_copy.nodes += SF_c_copy.nodes
        
        node_c = SF_c_copy.find_elem(c_c[node_c_name])
        node_c.head = node_p.head
        for rel in SF_p_copy.edges:
            if rel.pFrom.name == c_p[node_p_name]:
                rel.pFrom = node_c
            if rel.pTo.name == c_p[node_p_name]:
                rel.pTo = node_c
        
        SF_p_copy.edges += SF_c_copy.edges
        SF_p_copy._create_NX_graph()
        
        new_SF = SF_p_copy
        
        name_corr = {}
        name_corr.update(c_p)
        name_corr[node_p_name] = node_c.name
        name_corr.update(c_c)

        u_map = dict([(k,[v]) for k,v in name_corr.iteritems()]) # Different format than name_corr to match with the SynForm version

        return (new_SF, name_corr, u_map)
        
class TP_SYNFORM(TP_ELEM):
    """
    SynForm construction template element
    Data (inherited):
    Data:
        - form ([TP_SYN_ELEM]): Form sequence.
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.form = []
    
    def add_syn_elem(self, elem):
        """
        """
        order = len(self.form)
        self.form.append(elem)
        elem.order = order
    
    def find_elem(self, name):
        """
        Returns the element with name "name". Returns None if name is not found.
        """
        for elem in self.form:
            if elem.name == name:
                return elem
        
        return None
    
    def copy(self):
        """
        """
        new_synform = TP_SYNFORM()
        name_corr = {}
        for f in self.form:
            (new_f, c) = f.copy()
            name_corr[c[0]] = c[1]
            new_synform.add_syn_elem(new_f)
        
        return (new_synform, name_corr)
    
    @staticmethod
    def unify(SF_p, slot_p_name, SF_c):
        """
        Not commutative.
        """
        new_synform = TP_SYNFORM()
        (SF_p_copy, c_p)  = SF_p.copy()
        (SF_c_copy, c_c) = SF_c.copy()
        slot_p = SF_p_copy.find_elem(c_p[slot_p_name])
        idx = SF_p_copy.form.index(slot_p)
        elems = SF_p_copy.form[:idx] + SF_c_copy.form + SF_p_copy.form[min(idx+1,len(SF_p_copy.form)):]
        for elem in elems:
            new_synform.add_syn_elem(elem)
            
        name_corr = {}
        name_corr.update(c_p)
        name_corr.pop(slot_p_name)
        name_corr.update(c_c)
        
        u_map = dict([(k,[v]) for k,v in name_corr.iteritems()])
        u_map[slot_p_name] = c_c.values()
            
        return (new_synform, name_corr, u_map)
    
class TP_SYMLINKS(TP_ELEM):
    """
    SymLinks construction template element.
    Data (inherited):
    Data:
        - SL (DICT): Map between SemFrame (TP_NODE) elements and SynForm (TP_SYNFORM) elements. The dictionary define a mapping between the names of the elements.
        
    """
    def __init__(self):
        TP_ELEM.__init__(self)
        self.SL = {}
    
    def form2node(self, form_name):
        """
        Returns the name of node associated with the form name "form_name"
        Returns None if the node name cannot be found.
        """
        res = [n for n,v in self.SL.iteritems() if v==form_name]
        output = res[0] if len(res) >0 else None 
        return output
        
    def node2form(self, node_name):
        """
        Returns the name of the form element associated with the node name "node_name"
        Returs None if the node_name cannot be found.
        """
        return self.SL.get(node_name, None)
        
############################    
### Construction classes ###
############################     
class CXN(object):
    """
    Grammatical construction.
    
    Data:
        - name (STR): construction name
        - clss (STR): construction class
        - preference (FLOAT): construction preference (usage preferences, optional)
        - group (INT): construction group (optional)
        - SemFrame (TP_SEMFRAME): cxn SemFrame.
        - SynForm (TP_SYNFORM): cxn SynForm.
        - SymLinks (TP_SYMLINKS): cxn SymLinks.
    """ 
    NEUTRAL_CLASS = "?"
    
    def __init__(self):
        self.name = ''
        self.clss = ''
        self.preference = None # construction preference
        self.group = None # construction group
        self.SemFrame = TP_SEMFRAME() # Semantic frame
        self.SynForm = TP_SYNFORM() # Syntactic form
        self.SymLinks = TP_SYMLINKS() # Symbolic links
    
    def cxn_signature(self):
        """
        Returns a construction signature that consists of:
            - its syntactic class
            - the semantic features of its head node.
        The signature combine syntactic and semantic features.
        """
        head_node = self.SemFrame.get_head()
        sem_feat = head_node.concept if head_node else None
        syn_feat = self.clss
        signature = {'syn_feat':syn_feat, 'sem_feat':sem_feat}
        return signature
        
    def class_match(self, slot):
        """
        Returns true iff the class of the construction matches the class requirements set up by slot.
        Args:
            - slot (TP_SLOT): a slot.
        """
        match = False
        # First check neutral class
        if (self.clss == CXN.NEUTRAL_CLASS) or (CXN.NEUTRAL_CLASS in slot.cxn_classes):
            match =  True
        else:
            match = self.clss in slot.cxn_classes
        
        return match
        
    def get_slot_constraints(self, slot):
        """
        Returns all the constraints associated with a slot:
            - syntactic constraints (cxn_classes)
            - semantic constraints (concepts associated with the slot)
        """
        node = self.form2node(slot)
        slot_constraints = {'syn_constraints':slot.cxn_classes, 'sem_constraints':[node.concept]}
        return slot_constraints
    
    def find_elem(self, name):
        """
        Find and return element with a given name (str).
        """
        for elem in self.SemFrame.nodes + self.SemFrame.edges + self.SynForm.form:
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
        if self.find_elem(sem_elem.name):
            return False
        
        # Add a new Sem-Frame element to either node or edge list.
        if isinstance(sem_elem, TP_NODE):
            self.SemFrame.nodes.append(sem_elem)
        elif isinstance(sem_elem, TP_REL):
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
        # Add a new Syn-Form element
        self.SynForm.add_syn_elem(syn_elem)        
        return True
    
    def add_sym_link(self, node_name, form_name):
        """
        Adds a symbolic link  between the node (TP_NODE) and form (TP_SLOT or TP_PHON)
        """
        if self.SymLinks.SL.has_key(node_name) or (form_name in self.SymLinks.SL.values()):
            return False
        self.SymLinks.SL[node_name] = form_name
        return True
    
    def form2node(self, form):
        """
        Returns the node associated with the form "form"
        """
        res = [n for n,v in self.SymLinks.SL.iteritems() if v==form.name]
        if not(res):
            return None
        node_name = res[0]
        node = self.find_elem(node_name)
        return node
    
    def node2form(self, node):
        """
        Returns the form associated with the node "node" if it exists. None otherwise.
        Args:
            - node (TP_NODE) or (STR): Node or Node's name
        """
        if isinstance(node, TP_NODE):
            node_name = node.name
        else:
            node_name = node
            
        form_name =  self.SymLinks.SL.get(node_name, None)
        if not(form_name):
            return None
        else:
            form_elem = self.find_elem(form_name)
        return form_elem
    
    def copy(self):
        """
        Returns a deep copy of the construction. Also returns coorespondence table.
        """
        new_cxn = CXN()
        new_cxn.name = self.name
        new_cxn.clss = self.clss
        new_cxn.preference = self.preference
        new_cxn.group = self.group
        
        (new_semframe, sem_corr) = self.SemFrame.copy()
        (new_synform, syn_corr) = self.SynForm.copy()
        for k, v in self.SymLinks.SL.iteritems():
            new_cxn.SymLinks.SL[sem_corr[k]] = syn_corr[v]

        new_cxn.SemFrame = new_semframe
        new_cxn.SynForm = new_synform
        
        name_corr = {}
        for n1, n2 in sem_corr.iteritems():
            name_corr[n1] = n2
        
        for n1, n2 in syn_corr.iteritems():
            name_corr[n1] = n2
        
        return (new_cxn, name_corr)
        
    @staticmethod
    def unify(cxn_p, slot_p, cxn_c):
        """
        Not commutative
        """
        node_p = cxn_p.form2node(slot_p)
        node_c = cxn_c.SemFrame.get_head()
        (new_semframe, sem_corr, u_map_sem) = TP_SEMFRAME.unify(cxn_p.SemFrame, node_p.name, cxn_c.SemFrame, node_c.name)
        (new_synform, syn_corr, u_map_syn) = TP_SYNFORM.unify(cxn_p.SynForm, slot_p.name, cxn_c.SynForm)
        
        new_cxn = CXN()
#        new_cxn.name = "[%s-U(%i)-%s]" %(cxn_p.name, slot_p.order, cxn_c.name)
        new_cxn.name = "%s__U__%s" %(cxn_p.name, cxn_c.name)
        new_cxn.clss = cxn_p.clss
        new_cxn.preference = None # For now does not need to be defined....
        new_cxn.group = None # For now does not need to be defined....
        new_cxn.SemFrame = new_semframe
        new_cxn.SynForm = new_synform
              
        for k,v in cxn_p.SymLinks.SL.iteritems():
            if v != slot_p.name:
                new_cxn.SymLinks.SL[sem_corr[k]]=syn_corr[v]
        
        for k,v in cxn_c.SymLinks.SL.iteritems():
            new_cxn.SymLinks.SL[sem_corr[k]]=syn_corr[v]
        
        name_corr = {}
        name_corr.update(sem_corr)
        name_corr.update(syn_corr)

        u_map = {'sem_map':u_map_sem, 'syn_map':u_map_syn}

        return (new_cxn, name_corr, u_map)
    
    def show(self):
        """
        Display the construction.
        Uses the display method defined in VIEWER class
        """
        from viewer import VIEWER
        VIEWER.display_cxn(self)
        
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
    from loader import TCG_LOADER
    
    # Loading data
    grammar_name = 'TCG_grammar_VB_main'
    
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics_main.json", "./data/semantics/")
    grammar_file = "%s.json" %grammar_name
    my_grammar = TCG_LOADER.load_grammar(grammar_file, "./data/grammars/", my_conceptual_knowledge)
    
    cxn = my_grammar.constructions[0]
    cxn2 = my_grammar.constructions[3]
    
    (cxn3, c, u_map) = CXN.unify(cxn, cxn.SynForm.form[0], cxn2)
#    cxn3.SemFrame.draw()
#    print [f.name for f in cxn3.SynForm.form]
#    print cxn3.SymLinks.SL
    
    cxn3.show()
    
    
    
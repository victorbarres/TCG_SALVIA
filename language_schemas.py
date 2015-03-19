# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:03:19 2015

@author: Victor Barres
Defines language schemas for TCG.

Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
"""
import networkx as nx

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM
##################################
### Language knowledge schemas ###
##################################
class CXN_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Construction schema
    
    Data:
        - KNOWEDGE SCHEMA data:
                    - id (int): Unique id
                    - name (str): schema name
                    - LTM (LTM): Associated long term memory.
                    - content (CXN):
                    - init_act (float): Initial activation value.        
    """
    def __init__(self,aCXN):
        KNOWLEDGE_SCHEMA.__init__(self, aCXN.name)
        self.content = aCXN

class CXN_SCHEMA_INST(SCHEMA_INST):
    """
    Construction instance
    
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activation (float): Current activation value of schema instance
            - schema (CXN_SCHEMA):
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
    """
    def __init__(self, cxn_schema, trace):
        SCHEMA_INST.__init__(self)
        self.instantiate(cxn_schema, trace)
    
    def set_port(self):
        """
        Defines the input and output port for the construction schema instance.
        Each instance has 1 input port.
        Each instance has an output port for each TP_SLOT element in the construction's SynForm.
        """
        SynForm = self.schema.content.SynForm
        for f in SynForm.form:
            if isinstance(f,TP_SLOT): # 1 output port per slot
                self.add_port('OUT', port_name=f.order)
    
        self.add_port('IN','input')

###################################
### Language procedural schemas ###
###################################
class CONCEPTUALIZER(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Phonological_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT', 'to_semantic_WM')
        self.brain_regions =[]
    
    def update(self):
        """
        """

class SEMANTIC_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Semantic_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_conceptualizer')
        self.add_port('OUT', 'to_grammatica_lWM')
        self.add_port('OUT', 'to_grammatical_LTM')
        self.SemRep = nx.DiGraph()
        self.brain_regions =['left_SFG', 'LIP', 'Hippocampus']
    
    def update(self):
        """
        """
        

class GRAMMATICAL_WM(WM):
    """
    """
    def __init__(self, name='Grammatical_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_grammatical_LTM')
        self.add_port('OUT', 'to_phonological_WM')
        self.brain_regions =['left_BA45', 'leftBA44']
    
    def update(self):
        """
        """

class GRAMMATICAL_LTM(LTM):
    """
    """
    def __init__(self, name='Grammatical_LTM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('OUT', 'to_grammatical_WM')
        self.brain_regions =['left_STG', 'left_MTG']
    
    def update(self):
        """
        """

class PHON_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Phonological_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_grammatical_WM')
        self.brain_regions =['left_BA6']
    
    def update(self):
        """
        """


        
            
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:03:19 2015

@author: Victor Barres
Defines language schemas for TCG.

Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
"""
import networkx as nx

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM, SCHEMA_SYSTEM, BRAIN_MAPPING
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
    def __init__(self, name='Conceptualizer'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT', 'to_semantic_WM')
        self.conceptualization = None
    
    def update(self):
        """
        """
        vis_input = self.get_input('from_visual_WM')
        self._conceptualize(vis_input)
        self.set_output('to_semantic_WM', self.conceptualization)
    
    def _conceptualize(self, vis_input):
        """
        """

class SEMANTIC_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Semantic_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_conceptualizer')
        self.add_port('OUT', 'to_grammatical_WM')
        self.add_port('OUT', 'to_cxn_retrieval')
        self.SemRep = nx.DiGraph()
    
    def update(self):
        """
        """
        conceptualization = self.get_input('from_conceptualizer')
        self._update_SemRep(conceptualization)
        self.set_output('to_grammatical_WM',self.SemRep)
        self.set_output('to_grammatical_LTM', self.SemRep)
    
    def _update_SemRep(self, conceptualiztion):
        """
        """

class GRAMMATICAL_WM(WM):
    """
    """
    def __init__(self, name='Grammatical_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_cxn_retrieval')
        self.add_port('OUT', 'to_phonological_WM')
    
    def update(self):
        """
        """
        SemRep = self.get_input('from_semantic_WM')
        cxn_instances = self.get_input('from_cxn_retrieval')
        # HERE NEED TO SET UP THE C2 COMPUTATION + POST THE OUTPUT.
        
class GRAMMATICAL_LTM(LTM):
    """
    """
    def __init__(self, name='Grammatical_LTM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('OUT', 'to_cxn_retrieval')

    def update(self):
        """
        """
        self.set_output('to_cxn_retrieval', self.schemas)

class CXN_RETRIEVAL(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name="Cxn_retrieval"):
        PROCEDURAL_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_grammatical_LTM')
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_WK_LTM')
        self.add_port('OUT', 'to_grammatical_WM')
        self.cxn_instances = []
    
    def update(self):
        """
        """
        SemRep = self.get_input('from_semantic_WM')
        gram = self.get_input('from_grammatical_LTM')
        WK = self.get_input('from_WK_LTM')
        self._instantiate_cxns(self,SemRep, gram, WK)
        self.set_output('to_grammatical_WM', self.cxn_instances)
    
    def _instantiate_cxns(self, SemRep, gram, WK):
        """
        """
        

class PHON_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Phonological_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_grammatical_WM')
        self.add_port('OUT', 'to_output')
    
    def update(self):
        """
        """


###############################################################################
if __name__=='__main__':
    ##############################
    ### Language schema system ###
    ##############################
    conceptualizer = CONCEPTUALIZER()
    grammaticalWM = GRAMMATICAL_WM()
    grammaticalLTM = GRAMMATICAL_LTM()
    cxn_retrieval = CXN_RETRIEVAL()
    semanticWM = SEMANTIC_WM()
    phonWM = PHON_WM()
    
    language_mapping = {'Conceptualizer':[], 
                        'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
                        'Grammatical_WM':['left_BA45', 'leftBA44'], 
                        'Grammatical_LTM':['left_STG', 'left_MTG'],
                        'Cxn_retrieval':[], 
                        'Phonological_WM':['left_BA6']}
                        
    language_schemas = [conceptualizer, grammaticalWM, grammaticalLTM, cxn_retrieval, semanticWM, phonWM]
    
    language_system = SCHEMA_SYSTEM('Language_system')
    language_system.add_schemas(language_schemas)
    
    language_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
    language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
    language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
    language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
    language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
    
    language_system.set_input_ports([conceptualizer._find_port('from_visual_WM')])
    language_system.set_output_port(phonWM._find_port('to_output'))
    
    language_brain_mapping = BRAIN_MAPPING()
    language_brain_mapping.schema_mapping = language_mapping
    language_system.brain_mapping = language_brain_mapping
    
    language_system.system2dot()






        
            
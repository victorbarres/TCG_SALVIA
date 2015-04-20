# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:03:19 2015

@author: Victor Barres
Defines language schemas for TCG.

Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
"""
import networkx as nx

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM, SCHEMA_SYSTEM, BRAIN_MAPPING
import construction
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
    def __init__(self,aCXN, init_act):
        KNOWLEDGE_SCHEMA.__init__(self, name=aCXN.name, content=aCXN, init_act=init_act)

class CXN_SCHEMA_INST(SCHEMA_INST):
    """
    Construction instance
    
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activation (INST_ACTIVATION): Current activation value of schema instance
            - schema (CXN_SCHEMA):
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
        
        - covers (DICT): maps SemRep element in trace to CXN.SemFrame elements
    """
    def __init__(self, cxn_schema, trace, t0, tau, mapping):
        SCHEMA_INST.__init__(self, schema=cxn_schema, trace=trace, t0=t0, tau=tau)
        self.covers = {}
        self.set_covers(mapping)
        self.set_port()
    
    def set_port(self):
        """
        Defines the input and output port for the construction schema instance.
        Each instance has 1 output port.
        Each instance has an input port for each TP_SLOT element in the construction's SynForm.
        """
        SynForm = self.schema.content.SynForm
        for f in SynForm.form:
            if isinstance(f,construction.TP_SLOT): # 1 intput port per slot
                self.add_port('IN', port_name=f.order)
    
        self.add_port('OUT','output')
    
    def set_covers(self, mapping):
        """
        Sets covers as mapping (DICT). Mapping should be of the form {t1:s1, t2:s2, ...} mapping each element of the trace to an element of the CXN.SemFrame
        """
        self.covers = mapping

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
        WM.__init__(self, name)
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
        LTM.__init__(self, name)
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
    
#    language_mapping = {'Conceptualizer':[], 
#                        'Semantic_WM':['left_SFG', 'LIP', 'Hippocampus'], 
#                        'Grammatical_WM':['left_BA45', 'leftBA44'], 
#                        'Grammatical_LTM':['left_STG', 'left_MTG'],
#                        'Cxn_retrieval':[], 
#                        'Phonological_WM':['left_BA6']}
#                        
#    language_schemas = [conceptualizer, grammaticalWM, grammaticalLTM, cxn_retrieval, semanticWM, phonWM]
#    
#    language_system = SCHEMA_SYSTEM('Language_system')
#    language_system.add_schemas(language_schemas)
#    
#    language_system.add_connection(conceptualizer, 'to_semantic_WM', semanticWM, 'from_conceptualizer')
#    language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
#    language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
#    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
#    language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
#    language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
#    
#    language_system.set_input_ports([conceptualizer._find_port('from_visual_WM')])
#    language_system.set_output_ports([phonWM._find_port('to_output')])
#    
#    language_brain_mapping = BRAIN_MAPPING()
#    language_brain_mapping.schema_mapping = language_mapping
#    language_system.brain_mapping = language_brain_mapping
#    
#    language_system.system2dot()
    
    ###########################################################################
    ### TEST GRAMMATICAL WM ###
    
    # Load grammar
    import random
    import loader as ld
    my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
    
    # Set up grammatical LTM content
    for cxn in my_grammar.constructions:
        new_cxn_schema = CXN_SCHEMA(cxn, 1)
        grammaticalLTM.add_schema(new_cxn_schema)
        
    # Select random cxn
    WM_size = 5
    idx = [random.randint(0,len(grammaticalLTM.schemas)-1) for i in range(WM_size)]
    
    # Instaniate constructions in WM
    for i in idx:
        cxn_inst = CXN_SCHEMA_INST(grammaticalLTM.schemas[i], trace=None, t0=0.0, tau=2.0)
        grammaticalWM.add_instance(cxn_inst)
    
    # Run WM
    max_step = 100
    for step in range(max_step):
        grammaticalWM.update_activations()
        
    grammaticalWM.plot_dynamics()
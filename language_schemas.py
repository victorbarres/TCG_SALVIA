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
import concept as cpt
import TCG_graph
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
            - activity = The current activity level of the schema.
            - activation (INST_ACTIVATION): Handles the activation dynamics.
            - schema (CXN_SCHEMA):
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace ({"nodes":[], "edge"=[]}): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
        
        - covers (DICT): maps CXN.SemFrame elements to SemRep elements in the trace
    """
    def __init__(self, cxn_schema, trace, mapping):
        SCHEMA_INST.__init__(self, schema=cxn_schema, trace=trace)
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
        self.SemRep = nx.DiGraph() ### NEED TO ADD A WAY TO KEEP TRACK OF WHICH SEMREP ELEMENTS HAVE BEEN OR HAVEN'T BEEN ALREADY PASSED THROUGH RETRIEVAL
    
    def update(self):
        """
        """
        conceptualization = self.get_input('from_conceptualizer')
        self._update_SemRep(conceptualization)
        self.set_output('to_grammatical_WM', self.SemRep)
        self.set_output('to_cxn_retrieval', self.SemRep)
    
    def _update_SemRep(self, conceptualiztion):
        """
        """
    
    def show_state(self):
        node_labels = dict((n, d['concept'].meaning) for n,d in self.SemRep.nodes(data=True))
        edge_labels = dict(((u,v), d['concept'].meaning) for u,v,d in self.SemRep.edges(data=True))
        pos = nx.spring_layout(self.SemRep)        
        nx.draw_networkx(self.SemRep, pos=pos, with_labels= False)
        nx.draw_networkx_labels(self.SemRep, pos=pos, labels= node_labels)
        nx.draw_networkx_edge_labels(self.SemRep, pos=pos, edge_labels=edge_labels)
    
        

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
        cxn_schemas = self.get_input('from_grammatical_LTM')
#        WK = self.get_input('from_WK_LTM')
        if cxn_schemas and SemRep:
            self._instantiate_cxns(SemRep, cxn_schemas)
            self.set_output('to_grammatical_WM', self.cxn_instances)
        self.cxn_instances = []
    
    def _instantiate_cxns(self, SemRep, cxn_schemas, WK=None):
        """
        """
        if not cxn_schemas:
            return
        for cxn_schema in cxn_schemas:
            sub_iso = self._SemMatch_cat(SemRep, cxn_schema)
            for a_sub_iso in sub_iso:
                match_qual = self._SemMatch_qual(a_sub_iso)
                trace = {"nodes":a_sub_iso["nodes"].values(), "edges":a_sub_iso["edges"].values()}
                new_instance = CXN_SCHEMA_INST(cxn_schema, trace, a_sub_iso) ### A few problem here: 1. I need to have access to sub_iso including node AND edge mapping. 2. I need to deal with the Trace better. 3. t0 and tau should be defined by the WM and set when the instances are added to the WM.??
                self.cxn_instances.append({"cxn_inst":new_instance, "match_qual":match_qual})
                    
    def _SemMatch_cat(self, SemRep, cxn_schema): ## NEED TO INCLUDE ASPECTS OF WORLD KNOWLEDGE.
        """
        IMPORTANT ALGORITHM
        Computes the categorical matches (match/no match) -> Returns the sub-graphs isomorphisms. This is the main filter for instantiation.
        """
        SemFrame_graph = cxn_schema.content.SemFrame.graph 
            
        node_concept_match = lambda cpt1,cpt2: cpt.CONCEPT.match(cpt1, cpt2, match_type="is_a")
        edge_concept_match = lambda cpt1,cpt2: cpt.CONCEPT.match(cpt1, cpt2, match_type="equal")
        nm = TCG_graph.node_iso_match("concept", "", node_concept_match)
        em = TCG_graph.edge_iso_match("concept", "", edge_concept_match)

        sub_iso = TCG_graph.find_sub_iso(SemRep, SemFrame_graph, node_match=nm, edge_match=em)        
        return sub_iso
    
    def _SemMatch_qual(self,a_sub_iso): ## NEEDS TO BE WRITTEN!! Need to add WK as an input?
        """
        Computes the quality of match?
        Returns a value between 0 and 1: 0 -> no match, 1 -> perfect match.
        """
        return 1

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
    ### TEST GRAMMATICAL WM 1 ###
    
#    # Load grammar
#    import random
#    import loader as ld
#    my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
#    
#    # Set up grammatical LTM content
#    for cxn in my_grammar.constructions:
#        new_cxn_schema = CXN_SCHEMA(cxn, random.random())
#        grammaticalLTM.add_schema(new_cxn_schema)
#        
#    # Select random cxn
#    WM_size = 10
#    idx = [random.randint(0,len(grammaticalLTM.schemas)-1) for i in range(WM_size)]
#    
#    # Instaniate constructions in WM
#    for i in idx:
#        cxn_inst = CXN_SCHEMA_INST(grammaticalLTM.schemas[i], trace=None, mapping=None)
#        grammaticalWM.add_instance(cxn_inst, act0=grammaticalLTM.schemas[i].init_act)
#    
#    # Run WM
#    max_step = 1000
#    for step in range(max_step):
#        grammaticalWM.update_activations()
#    
#    grammaticalWM.plot_dynamics()
    
    ###########################################################################
    ### TEST CXN RETRIEVAL ###
    
    import loader as ld
    my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
    my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
    cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
    
    # Set up grammatical LTM content
    act0 = 1
    for cxn in my_grammar.constructions:
        new_cxn_schema = CXN_SCHEMA(cxn, act0)
        grammaticalLTM.add_schema(new_cxn_schema)
    
    man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
    woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
    kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
    agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
    patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
    
    entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
    

    # Set up Semantic WM content
    semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt)
    semanticWM.SemRep.add_node("KICK", concept=kick_cpt)
    semanticWM.SemRep.add_node("MAN", concept=man_cpt)
    semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt)
    semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt)
    
    semanticWM.show_state()
            
    
    # Set up language system
    language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM]
    
    language_system = SCHEMA_SYSTEM('Language_system')
    language_system.add_schemas(language_schemas)
    language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
    language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
    
    language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
    language_system.set_output_ports([cxn_retrieval._find_port('to_grammatical_WM')])
    
    def print_output(value):
        if value:
            print [v["cxn_inst"].name for v in cxn_retrieval.out_ports[0].value]
        else:
            print "NOTHING!"
    
    print_output(cxn_retrieval.out_ports[0].value)
    language_system.update()
    print_output(cxn_retrieval.out_ports[0].value)
    language_system.update()
    print_output(cxn_retrieval.out_ports[0].value)
    language_system.update()
    print_output(cxn_retrieval.out_ports[0].value)

    
    
    
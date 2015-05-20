# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:03:19 2015

@author: Victor Barres
Defines language schemas for TCG.

Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
Uses pyttsx for the text to speech implementation (optional!)
"""
import random
import matplotlib.pyplot as plt

import networkx as nx
import pyttsx


from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM, ASSEMBLAGE, SCHEMA_SYSTEM, BRAIN_MAPPING
import construction
import concept as cpt
import TCG_graph

random.seed(1)
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
            - trace ({"nodes":[], "edge"=[]}): Pointer to the element that triggered the instantiation.
            - covers ({"nodes":{}, "edge"={}}): maps CXN.SemFrame nodes and edges to SemRep elements (in the trace)
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
        plt.figure(facecolor='white')
        plt.axis('off')
        title = '%s (state)' %self.name
        plt.title(title)
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
        self.dyn_params = {'tau':10.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0, 'noise_std':0.3}
        self.prune_threshold = 0.3
    
    def update(self):
        """
        """
        SemRep = self.get_input('from_semantic_WM')
        new_cxn_insts= self.get_input('from_cxn_retrieval')
        if new_cxn_insts:
            self._add_new_insts(new_cxn_insts)
        self.update_activations(coop_p=1, comp_p=1)
        self.prune()
        if not(self.comp_links) and self.coop_links:
            assemblages = self._assemble()
            activations = [a.activation for a in assemblages]
            winner_idx = activations.index(max(activations))
            phon_form = GRAMMATICAL_WM._read_out(assemblages[winner_idx])
            self.set_output('to_phonological_WM', phon_form)
            self.show_state()
            self._draw_assemblages()
            self.schema_insts = []
            self.coop_links = []
            self.comp_links = []
    
    def _add_new_insts(self, new_insts):
        """
        """
        for inst in new_insts:
            match_qual = inst["match_qual"]
            act = inst["cxn_inst"].activity
            new_inst = inst["cxn_inst"]
            self.add_instance(new_inst, act*match_qual)
            self._cooperate(new_inst)
            self._compete(new_inst)
            
    ###############################
    ### cooperative computation ###
    ###############################
    def _cooperate(self, new_inst):
       """
       """
       weight = 1
       for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM._match(new_inst, old_inst)
               if match["match"] == 1:
                   for link in match["links"]:
                       self.add_coop_link(inst_from=link["inst_from"], port_from=link["port_from"], inst_to=link["inst_to"], port_to=link["port_to"], weight=weight)
#                       self.add_coop_link(inst_from=link["inst_to"], port_from=link["port_to"], inst_to=link["inst_from"], port_to=link["port_from"], weight=1) # Now the f-link are bidirectional in the propagation of activation.
    
    def _compete(self, new_inst):
        """
        How to make it incremental....?
        Competition if they overlap on an edge.
        I want to avoid having to rebuild the assemblages all the time...-> Incrementality.
        """
        weight = -3.5
        for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM._match(new_inst, old_inst)
               if match["match"] == -1:
                   self.add_comp_link(inst_from=new_inst, inst_to=old_inst, weight=weight) # BOOSTEDD THE INHIBITION TO COMPENSATE FOR THE AMOUNT OF COOPERATION.
#                   self.add_comp_link(inst_from=old_inst, inst_to=new_inst, weight=-1)  # Now the f-link are bidirectional in the propagation of activation.
        
    
    @staticmethod
    def _overlap(inst1, inst2):
        """
        Returns the set of SemRep nodes and edges on which inst1 and inst2 overlaps.
        
        Args:
            - inst1 (CXN_SCHEMA_INST): A cxn instance
            - inst2 (CXN_SCHEMA_INST): A cxn instance
        """
        overlap = {}
        overlap["nodes"] = [n for n in inst1.trace["nodes"] if n in inst2.trace["nodes"]]
        overlap["edges"] = [e for e in inst1.trace["edges"] if e in inst2.trace["edges"]]
        return overlap
        
    @staticmethod    
    def _link(inst_p, inst_c, SR_node):
        """
        Args:
            - inst_p (CXN_SCHEMA_INST): A cxn instance (parent)
            - inst_c (CXN_SCHEMA_INST): A cxn instance (child)
            - SR_node (): SemRep node on which both instances overlap
        """
        cxn_p = inst_p.schema.content
        sf_p = [k for k,v in inst_p.covers["nodes"].iteritems() if v == SR_node][0] # Find SemFrame node that covers the SemRep node
        cxn_c = inst_c.schema.content
        sf_c = [k for k,v in inst_c.covers["nodes"].iteritems() if v==SR_node][0] # Find SemFrame node that covers the SemRep node
        
        cond1 = sf_p in cxn_p.SymLinks.SL # sf_p is linked to a slot in cxn_p
        cond2 = sf_c.head # sf_c is a head node
        if cond1 and cond2:
            slot_p = cxn_p.SymLinks.SL[sf_p]
            cond3 = cxn_c.clss in slot_p.cxn_classes
            if cond3:
                return {"inst_from": inst_c, "port_from":inst_c._find_port("output"), "inst_to": inst_p, "port_to":inst_p._find_port(slot_p.order)}
        return None
    
    @staticmethod
    def _match(inst1, inst2):
        """
        """
        match = 0
        links = []
        if inst1 == inst2:
           match = -1
        else:
            overlap = GRAMMATICAL_WM._overlap(inst1, inst2)
            if not(overlap["nodes"]) and not(overlap["edges"]):
                match = 0
            elif overlap["edges"]:
                match = -1
            else:
                for n in overlap["nodes"]:
                    link = GRAMMATICAL_WM._link(inst1, inst2, n)
                    if link:
                        links.append(link)
                        match = 1
                    link = GRAMMATICAL_WM._link(inst2, inst1, n)
                    if link:
                        match = 1
                        links.append(link)
                if not(links):
                    match = -1       
        return {"match":match, "links":links}
    
    ##################
    ### Assemblage ###
    ##################    
    def _assemble(self): # THIS IS VERY DIFFERENT FROM THE ASSEMBLE ALGORITHM OF TCG 1.0
        """
        WHAT ABOUT THE CASE WHERE THERE STILL IS COMPETITION GOING ON?
        
        NOTE THAT IN THE CASE OF MULTIPLE TREES GENERATED FROM THE SAME SET OF COOPERATION... THERE IS MAXIMUM SPANNING TREE. THIS IS THE ONE THA SHOULD BE CONSIDERED!!!
        """        
        inst_network = GRAMMATICAL_WM._build_instance_network(self.schema_insts, self.coop_links)
        
        tops = [(n,None) for n in inst_network.nodes() if not(inst_network.successors(n))]
        assemblages = []
        self._get_trees(tops, None, inst_network, assemblages)
        
        # Compute assemblage activation values
        for assemblage in assemblages:
            assemblage.update_activation()
            
        return assemblages
        
    @staticmethod
    def _build_instance_network(schema_insts, coop_links):
        """
        """
        graph = nx.DiGraph() # This could be built incrementally.....
        for inst in schema_insts:
            graph.add_node(inst, type="instance")
            for port in inst.in_ports:
                graph.add_node(port, type="port")
                graph.add_edge(port, inst, type="port2inst")
        for link in coop_links: # Does not requires the competition to be resolved (there could still be active competition links)
            graph.add_edge(link.inst_from, link.connect.port_to, type="inst2port")
        
        return graph

    def _get_trees(self, frontier, assemblage, graph, results):
        """
        Recursive function
        "Un-superpose" the trees!

        DOES NOT HANDLE THE CASE WHERE THERE STILL IS SOME COMPETITION GOING ON.
        """
        new_frontiers = [[]]
        for node, link in frontier:
            if assemblage == None:
                assemblage = ASSEMBLAGE()
            assemblage.add_instance(node)
            if link:
                assemblage.add_link(link)
            ports = graph.predecessors(node)
            for port in ports:
                children = graph.predecessors(port)
                updated_frontiers = []
                for child in children:
                    link = self.find_coop_links(inst_from=child, inst_to=node, port_from=child._find_port("output"), port_to=port)
                    for f in new_frontiers:
                        updated_frontiers.append(f[:] + [(child, link[0])])
                new_frontiers = updated_frontiers
        if new_frontiers == [[]]:
            results.append(assemblage)
        else:
            for a_frontier in new_frontiers:
                self._get_trees(a_frontier, assemblage.copy(), graph, results)
                
    @staticmethod                
    def _read_out(assemblage):
        """
        Left2right reading of the tree formed byt the assemblage.
        """
        def L2R_read(inst, graph, phon_form):
            """
            """
            cxn = inst.schema.content
            SynForm = cxn.SynForm.form
            for f in SynForm:
                if isinstance(f, construction.TP_PHON):
                    phon_form.append(f.cxn_phonetics)
                else:
                    port = inst._find_port(SynForm.index(f))
                    child  = graph.predecessors(port)
                    if not(child):
                        print "MISSING INFORMATION!"
                    else:
                        L2R_read(child[0], graph, phon_form)
        
        graph = GRAMMATICAL_WM._build_instance_network(assemblage.schema_insts, assemblage.coop_links)
        tops = [n for n in graph.nodes() if not(graph.successors(n))]
        phon_form = []
        L2R_read(tops[0], graph, phon_form)
        return phon_form

    @staticmethod
    def _draw_instance_network(graph, title=''):
        """
        """
        plt.figure(facecolor='white')
        plt.axis('off')
        plt.title(title)
        pos = nx.spring_layout(graph)
        nx.draw_networkx_nodes(graph, pos, nodelist=[n for n in graph.nodes() if graph.node[n]['type']=='instance'], node_color='b', node_shape='s', node_size=300)
        nx.draw_networkx_nodes(graph, pos, nodelist=[n for n in graph.nodes() if graph.node[n]['type']=='port'], node_color='r', node_shape='h', node_size=200)
        nx.draw_networkx_edges(graph, pos=pos, edgelist=[e for e in graph.edges() if graph.edge[e[0]][e[1]]['type'] == 'port2inst'], edge_color='k')
        nx.draw_networkx_edges(graph, pos=pos, edgelist=[e for e in graph.edges() if graph.edge[e[0]][e[1]]['type'] == 'inst2port'], edge_color='r')
        node_labels = dict((n, n.name) for n in graph.nodes())
        nx.draw_networkx_labels(graph, pos=pos, labels=node_labels)
        
    def _draw_assemblages(self):
        """
        """
        assemblages = self._assemble()
        i=0
        for assemblage in assemblages:
            graph = GRAMMATICAL_WM._build_instance_network(assemblage.schema_insts, assemblage.coop_links)
            title = 'Assemblage_%i' % i
            GRAMMATICAL_WM._draw_instance_network(graph, title)
            i += 1
        
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
        self.add_port('OUT', 'to_grammatical_WM')
        self.cxn_instances = []
    
    def update(self):
        """
        """
        SemRep = self.get_input('from_semantic_WM')
        cxn_schemas = self.get_input('from_grammatical_LTM')
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
                    
    def _SemMatch_cat(self, SemRep, cxn_schema):
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
    
    def _SemMatch_qual(self,a_sub_iso): ## NEEDS TO BE WRITTEN!! At this point the formalism does not support efficient quality of match.
        """
        Computes the quality of match.
        Returns a value between 0 and 1: 0 -> no match, 1 -> perfect match.
        
        NOTE: I NEED TO THINK ABOUT HOW TO INCORPORATE FOCUS ETC....
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
        phon_form = self.get_input('from_grammatical_WM')
        self.set_output('to_output', phon_form)

class TEXT2SPEECH:
    """
    """
    def __init__(self, rate_percent=100):
        self.rate_percent = float(rate_percent)/100
        self.utterance = None
        self.engine = pyttsx.init()
        engine_rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', engine_rate*self.rate_percent)
    
    def utter(self):
        if self.utterance:
            self.engine.say(self.utterance)
            self.engine.runAndWait()
            self.utterance = None
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
    
    prompt =  "1: TEST BUILD LANGUAGE SYSTEM; 2: TEST GRAMMATICAL WM; 3: TEST CXN RETRIEVAL; 4: TEST STATIC SEMREP; 5: TEST INCREMENTAL SEMREP"
    print prompt
    case = raw_input("ENTER CASE #: ")
    while case not in ['1','2','3','4','5']:
        print "INVALID CHOICE"
        print prompt
        case = raw_input("ENTER CASE #: ")
        
    if case == '1':
        ###########################################################################
        ### TEST BUILD LANGUAGE SYSTEM ###
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
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
        language_brain_mapping = BRAIN_MAPPING()
        language_brain_mapping.schema_mapping = language_mapping
        language_system.brain_mapping = language_brain_mapping
        
        language_system.system2dot()
    
    elif case == '2':
        ###########################################################################
        ### TEST GRAMMATICAL WM 1 ###
        
        # Load grammar
        import random
        import loader as ld
        my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
        
        # Set up grammatical LTM content
        for cxn in my_grammar.constructions:
            new_cxn_schema = CXN_SCHEMA(cxn, random.random())
            grammaticalLTM.add_schema(new_cxn_schema)
            
        # Select random cxn
        WM_size = 10
        idx = [random.randint(0,len(grammaticalLTM.schemas)-1) for i in range(WM_size)]
        
        # Instaniate constructions in WM
        for i in idx:
            cxn_inst = CXN_SCHEMA_INST(grammaticalLTM.schemas[i], trace=None, mapping=None)
            grammaticalWM.add_instance(cxn_inst, act0=grammaticalLTM.schemas[i].init_act)
        
        # Run WM
        max_step = 1000
        for step in range(max_step):
            grammaticalWM.update_activations()
        
        grammaticalWM.plot_dynamics()
    
    elif case == '3': 
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
        cxn_retrieval.out_ports[0].value = None
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)
        cxn_retrieval.out_ports[0].value = None
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)
        cxn_retrieval.out_ports[0].value = None
        semanticWM.SemRep.clear()
        language_system.update()
        print_output(cxn_retrieval.out_ports[0].value)

    elif case == '4':
        ###########################################################################
        ### TEST STATIC SEMREP ###
        
        
        import loader as ld
        my_grammar = ld.load_grammar("TCG_grammar_light.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        # Set up grammatical LTM content
        random.seed()
        act0 = 0.6
        for cxn in my_grammar.constructions:
            new_cxn_schema = CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, 0.2), grammaticalWM.prune_threshold))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")
        
        entity_cpt = cpt.CONCEPT(name="ENTITY", meaning="ENTITY")
        
    
        # Set up Semantic WM content
        semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt)
        semanticWM.SemRep.add_node("KICK", concept=kick_cpt)
        semanticWM.SemRep.add_node("MAN", concept=man_cpt)
        semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt)
        semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt)
        
        # A bit more info
        semanticWM.SemRep.add_node("BLUE", concept=blue_cpt)
        semanticWM.SemRep.add_edge("BLUE", "WOMAN", concept=modify_cpt)
        

        semanticWM.show_state()
                
        
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM]
        
        language_system = SCHEMA_SYSTEM('Language_system')
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
    
        language_system.update()
        language_system.update()
        semanticWM.SemRep.clear()
        language_system.update()
        language_system.update()
        language_system.update()
        grammaticalWM.show_state()
        
        max_step = 1000
        for step in range(max_step):
            language_system.update()
            if language_system.outputs['Phonological_WM:14']:
                print language_system.outputs['Phonological_WM:14']
            
        grammaticalWM.plot_dynamics()
     
    elif case == '5':
        ###########################################################################
        ### TEST STATIC SEMREP ###
        import loader as ld
        my_grammar = ld.load_grammar("TCG_grammar.json", "./data/grammars/")
        my_semnet = ld.load_SemNet("TCG_semantics.json", "./data/semantics/")
        cpt.CONCEPT.SEMANTIC_NETWORK = my_semnet
        
        # Set up grammatical LTM content
        random.seed()
        act0 = 0.6
        for cxn in my_grammar.constructions:
            new_cxn_schema = CXN_SCHEMA(cxn, max(act0 + random.normalvariate(0, 0.2), grammaticalWM.prune_threshold))
            grammaticalLTM.add_schema(new_cxn_schema)
        
        man_cpt = cpt.CONCEPT(name="MAN", meaning="MAN")
        woman_cpt = cpt.CONCEPT(name="WOMAN", meaning="WOMAN")
        kick_cpt = cpt.CONCEPT(name="KICK", meaning="KICK")
        blue_cpt = cpt.CONCEPT(name="BLUE", meaning="BLUE")
        big_cpt = cpt.CONCEPT(name="BIG", meaning="BIG")
        agent_cpt = cpt.CONCEPT(name="AGENT", meaning="AGENT")
        patient_cpt = cpt.CONCEPT(name="PATIENT", meaning="PATIENT")
        modify_cpt = cpt.CONCEPT(name="MODIFY", meaning="MODIFY")        
    
        # Set up Semantic WM content
        semanticWM.SemRep.add_node("WOMAN", concept=woman_cpt)
        semanticWM.SemRep.add_node("KICK", concept=kick_cpt)
        semanticWM.SemRep.add_node("MAN", concept=man_cpt)
        semanticWM.SemRep.add_edge("KICK", "WOMAN", concept=agent_cpt)
        semanticWM.SemRep.add_edge("KICK", "MAN", concept=patient_cpt)
        semanticWM.SemRep.add_node("BLUE", concept=blue_cpt)
        semanticWM.SemRep.add_node("BIG", concept=big_cpt) 
        semanticWM.SemRep.add_edge("BLUE", "WOMAN", concept=modify_cpt)
        semanticWM.SemRep.add_edge("BIG", "MAN", concept=modify_cpt)
            
        semanticWM.show_state()
                
        # Set up language system
        language_schemas = [grammaticalLTM, cxn_retrieval, semanticWM, grammaticalWM, phonWM]
        
        language_system = SCHEMA_SYSTEM('Language_system')
        language_system.add_schemas(language_schemas)
        language_system.add_connection(semanticWM,'to_cxn_retrieval', cxn_retrieval, 'from_semantic_WM')
        language_system.add_connection(grammaticalLTM, 'to_cxn_retrieval', cxn_retrieval, 'from_grammatical_LTM')
        language_system.add_connection(cxn_retrieval, 'to_grammatical_WM', grammaticalWM, 'from_cxn_retrieval')
        language_system.add_connection(semanticWM, 'to_grammatical_WM', grammaticalWM, 'from_semantic_WM')
        language_system.add_connection(grammaticalWM, 'to_phonological_WM', phonWM, 'from_grammatical_WM')
        
        language_system.set_input_ports([semanticWM._find_port('from_conceptualizer')])
        language_system.set_output_ports([phonWM._find_port('to_output')])
        
    
        language_system.update()
        language_system.update()
        semanticWM.SemRep.clear()
        language_system.update()
        language_system.update()
        language_system.update()
        grammaticalWM.show_state()
        
        
        # Set up text2speech
        text2speech = TEXT2SPEECH(rate_percent=80)
        max_step = 1000
        for step in range(max_step):
            language_system.update()
            if language_system.outputs['Phonological_WM:14']:
                output =  language_system.outputs['Phonological_WM:14']
                print output
                text2speech.utterance = ' '.join(output)
                text2speech.utter()
                
            
        grammaticalWM.plot_dynamics()
    
    else:
        print "ERROR"
        
    
    
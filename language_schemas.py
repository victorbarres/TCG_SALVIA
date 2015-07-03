# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines language schemas for TCG.

Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
Uses pyttsx for the text to speech implementation (optional!)
"""
import matplotlib.pyplot as plt

import networkx as nx
import pyttsx


from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM, ASSEMBLAGE
import construction
import TCG_graph

##################################
### Language knowledge schemas ###
##################################

##############################
# GRAMMAITCAL KNOWLEDGE SCHEMA
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
    
    If copy= True, carries a copy of the construction stored in LTM. 
    Trace contains pointers to both the SemRep subgraphs that triggered the instantiation and to the CXN_SCHEMA in LTM that was instantiated.
    
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activity = The current activity level of the schema.
            - activation (INST_ACTIVATION): Handles the activation dynamics.
            - content (CXN):
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace ({"SemRep":{"nodes":[], "edges"=[]}, "schemas":[CXN_SCHEMA]}): Pointer to the elements that triggered the instantiation.
            - covers ({"nodes":{}, "edges"={}}): maps CXN.SemFrame nodes and edges (in content) to SemRep elements (in the trace) (Maps the nodes and edges names to SemRep obj)
    """
    def __init__(self, cxn_schema, trace, mapping, copy=True):
        SCHEMA_INST.__init__(self, schema=cxn_schema, trace=trace)
        if copy:
                (cxn_copy, c) = cxn_schema.content.copy()
                self.content = cxn_copy
                if mapping:
                    new_node_mapping  = dict([(c[k], v) for k,v in mapping['nodes'].iteritems()])
                    new_edge_mapping  = dict([((c[k[0]], c[k[1]]), v) for k,v in mapping['edges'].iteritems()])
                    new_mapping= {'nodes':new_node_mapping, 'edges':new_edge_mapping}
                    self.covers = new_mapping
        else:
             self.covers = mapping
        self.set_ports()
    
    def set_ports(self, in_ports=None, out_ports=None):
        """
        Defines the input and output port for the construction schema instance.
        Each instance has 1 output port.
        Each instance has an input port for each TP_SLOT element in the construction's SynForm.
        """
        self.in_ports = []
        self.out_ports = []
        if in_ports == None:
            SynForm = self.content.SynForm
            for f in SynForm.form:
                if isinstance(f,construction.TP_SLOT): # 1 intput port per slot
                    self.add_port('IN', port_name=f.order, port_data=f)
        else:
            for port in in_ports:
                self.in_ports.append(port)
                port.schema=self
        
        if out_ports == None:
            self.add_port('OUT','output')
        else:
             for port in out_ports:
                self.out_ports.append(port)
                port.schema=self
                
############################
# CONCEPT KNOWLEDGE SCHEMAS
class CPT_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Concept schema
    Data:
    - KNOWEDGE SCHEMA data:
        - id (int): Unique id
        - name (str): schema name
        - LTM (LTM): Associated long term memory.
        - content ({'concept':CONCEPT): concept is a CONCEPT in SEMANTIC_NETWOR
        - init_act (float): Initial activation value.
    """
    def __init__(self, name, concept, init_act):
        """
        Args:
            - name (STR):
            - concept (CONCEPT):
            - init_act (FLOAT):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.set_content({'concept':concept})

class CPT_ENTITY_SCHEMA(CPT_SCHEMA):
    """
    Conceptual entity schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self ,name, concept, init_act)

class CPT_ACTION_SCHEMA(CPT_SCHEMA):
    """
    Conceptual action schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self ,name, concept, init_act)

class CPT_PROPERTY_SCHEMA(CPT_SCHEMA):
    """
    Conceptual property schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self ,name, concept, init_act)

class CPT_RELATION_SCHEMA(CPT_SCHEMA):
    """
    Conceptual relation schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self ,name, concept, init_act)
        self.content['pFrom'] = None 
        self.content['pTo'] = None

class CPT_SCHEMA_INST(SCHEMA_INST):
    """
    Concept schema instance. 
    """
    def __init__(self, cpt_schema, trace):
        SCHEMA_INST.__init__(self, schema=cpt_schema, trace=trace)
        content_copy = cpt_schema.content.copy()
        self.content = content_copy
        
    def match(self, cpt_inst, match_type = "is_a"):
        """
        Check if it;s concept matches that of cpt_inst. 
        Uses CONCEPTUAL_KNOWLEDGe.match() method.
            Type = "is_a":  concept1 matches concept2 if concept1 is a hyponym of concept2 (or equal to concept2)
            Type = "equal": concept1 matches concept2 if concept1 is equal to concept2.
        """
        return self.content['concept'].match(cpt_inst.content['concept'], match_type)
    
    def similarity(self, cpt_inst):
        """
        Returns a similarity score between it's concept and that of cpt_inst.
        Uses CONCEPTUAL_KNOWLEDGE.similarity() method.
        """
        return self.content['concept'].similarity(cpt_inst.content['concept'])

###################################
### Language procedural schemas ###
###################################
class CONCEPTUALIZER(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Conceptualizer'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_visual_WM')
        self.add_port('IN', 'from_concept_LTM')
        self.add_port('OUT', 'to_semantic_WM')
        self.conceptualization = None
    
    def initialize(self, conceptualization):
        """
        Args:
            - conceptualization (CONCEPTUALIZATION)
        """
        self.conceptualization = conceptualization
    
    def update(self):
        """
        """
        SceneRep = self.get_input('from_visual_WM')
        cpt_schemas = self.get_input('from_concept_LTM')
        if cpt_schemas and SceneRep:
            cpt_insts  = self.conceptualize(SceneRep, cpt_schemas)
            self.set_output('to_semantic_WM', cpt_insts)
        
            # Set all SceneRep elements to new=False
            for n in SceneRep.nodes_iter():
                SceneRep.node[n]['new'] = False
            for e in SceneRep.edges_iter():
                d = SceneRep.get_edge_data(e[0], e[1])
                d['new'] = False
    
    def conceptualize(self, SceneRep, cpt_schemas):
        """
        """
        cpt_insts  = []
        for n,d in SceneRep.nodes(data=True): # First process the nodes.
            if d['new']:
                per_name = d['percept'].name
                per_inst = d['per_inst']
                cpt_name = self.conceptualization.conceptualize(per_name)
                cpt_schema = [schema for schema in cpt_schemas if schema.name == cpt_name][0]
                cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'per_inst':per_inst, 'cpt_schema':cpt_schema})
                cpt_inst.set_activation(per_inst.activity) # THIS MIGHT NEED TO BE PARAMETRIZED!!
                per_inst.covers['cpt_inst'] = cpt_inst
                cpt_insts.append(cpt_inst)
        
        for u,v,d in SceneRep.edges(data=True): # Then the relations.
            if d['new']:
                per_name = d['percept'].name
                per_inst = d['per_inst']
                cpt_name = self.conceptualization.conceptualize(per_name)
                cpt_schema = [schema for schema in cpt_schemas if schema.name == cpt_name][0]
                cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'per_inst':per_inst, 'cpt_schema':cpt_schema})
                cpt_inst.set_activation(per_inst.activity) # THIS MIGHT NEED TO BE PARAMETRIZED!!
                pFrom = SceneRep.node[u]['per_inst'].covers['cpt_inst']
                pTo = SceneRep.node[v]['per_inst'].covers['cpt_inst']
                cpt_inst.content['pFrom'] = pFrom
                cpt_inst.content['pTo'] = pTo
                cpt_insts.append(cpt_inst)
                
        return cpt_insts

class CONCEPT_LTM(LTM):
    """
    """
    def __init__(self, name='Concept_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_conceptualizer')
        self.cpt_knowledge = None
        self.init_act = 1
        
    def initialize(self, cpt_knowledge):
        """
        Initilize the state of the CONCEPTUAL LTM with cpt_schema based on the content of cpt_knowledge
       
        Args:
            - cpt_knowledge (CONCEPTUAL_KNOWLEDGE):
        """
        self.cpt_knowledge = cpt_knowledge
        
        entity = cpt_knowledge.find_meaning('ENTITY')
        action = cpt_knowledge.find_meaning('ACTION')
        prop = cpt_knowledge.find_meaning('PROPERTY')
        rel = cpt_knowledge.find_meaning('RELATION')
        for concept in cpt_knowledge.concepts():
            new_schema = None
            if cpt_knowledge.match(concept, entity, match_type="is_a"):
                new_schema = CPT_ENTITY_SCHEMA(name=concept.name, concept=concept, init_act=self.init_act)
            elif cpt_knowledge.match(concept, action, match_type="is_a"):
                new_schema = CPT_ACTION_SCHEMA(name=concept.name, concept=concept, init_act=self.init_act)
            elif cpt_knowledge.match(concept, prop, match_type="is_a"):
                new_schema = CPT_PROPERTY_SCHEMA(name=concept.name, concept=concept, init_act=self.init_act)
            elif cpt_knowledge.match(concept, rel, match_type="is_a"):
                new_schema = CPT_RELATION_SCHEMA(name=concept.name, concept=concept, init_act=self.init_act)
            else:
                print "%s: unknown concept type" %concept.meaning
            
            if new_schema:
                self.add_schema(new_schema)
    
    def update(self):
        self.set_output('to_conceptualizer', self.schemas)
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(CONCEPT_LTM, self).get_info()
        data['init_act'] = self.init_act
        return data
        
class SEMANTIC_WM(WM):
    """
    """
    def __init__(self, name='Semantic_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_conceptualizer')
        self.add_port('OUT', 'to_grammatical_WM')
        self.add_port('OUT', 'to_cxn_retrieval')
        self.add_port('OUT', 'to_control')
        self.dyn_params = {'tau':1000.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0.0, 'noise_std':0.0}
        self.C2_params = {'coop_weight':0, 'comp_weight':0, 'prune_threshold':0.01, 'confidence_threshold':0} # C2 is not implemented in this WM.
        self.SemRep = nx.DiGraph() # Uses networkx to easily handle graph structure.
    
    def update(self):
        """
        """
        cpt_insts = self.get_input('from_conceptualizer')
        if cpt_insts:
            for inst in cpt_insts:
               self.add_instance(inst) # Does not deal with updating already existing nodes. Need to add that.
            self.set_output('to_control', True)
        self.update_activations()
        self.update_SemRep(cpt_insts)        
        self.prune()        
        self.set_output('to_grammatical_WM', self.SemRep)
        
        
        if cpt_insts:
#            self.show_SemRep()
            self.set_output('to_cxn_retrieval', self.SemRep)
    
    def update_SemRep(self, cpt_insts):
        """
        Updates the SemRep: Adds the nodes and edges needed based on the receivd concept instances.
        
        NOTE:
            - Does not handle the case of concept instance updating.
            - SemRep carreies the instance and the concept. The concept field is redundant, but is useful in order to be able to define
            SemMatch between SemRep graph and SemFrames (graphs needs to have same data key).
        """
        if cpt_insts:
            # First process all the instances that are not relations.
            for inst in [i for i in cpt_insts if not(isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA))]:
                self.SemRep.add_node(inst.name, cpt_inst=inst, concept=inst.content['concept'], new=True)
            
            # Then add the relations
            for rel_inst in [i for i in cpt_insts if isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA)]:
                node_from = rel_inst.content['pFrom'].name
                node_to = rel_inst.content['pTo'].name
                self.SemRep.add_edge(node_from, node_to, cpt_inst=rel_inst, concept=rel_inst.content['concept'],  new=True)
            
#            self.show_SemRep()
    
    def show_SemRep(self):
        node_labels = dict((n, '%s(%.1f)' %(n, d['cpt_inst'].activity)) for n,d in self.SemRep.nodes(data=True))
        edge_labels = dict(((u,v), '%s(%.1f)' %(d['concept'].meaning, d['cpt_inst'].activity)) for u,v,d in self.SemRep.edges(data=True))
        pos = nx.spring_layout(self.SemRep)  
        plt.figure(facecolor='white')
        plt.axis('off')
        title = '%s state (t=%i)' %(self.name,self.t)
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
        self.add_port('IN', 'from_control')
        self.dyn_params = {'tau':30.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0, 'noise_std':0.3}
        self.C2_params = {'coop_weight':1, 'comp_weight':-4, 'prune_threshold':0.3, 'confidence_threshold':0.8}  # BOOST THE INHIBITION TO COMPENSATE FOR THE AMOUNT OF COOPERATION.
    
    def update(self):
        """
        """
        SemRep = self.get_input('from_semantic_WM')
        new_cxn_insts= self.get_input('from_cxn_retrieval')
        produce = self.get_input('from_control')
        if new_cxn_insts:
            self._add_new_insts(new_cxn_insts)
        self.update_activations(coop_p=1, comp_p=1)
        self.prune()
        if produce:
            self.end_competitions()
        if not(self.comp_links):
            self._produce_form()
    
    def _add_new_insts(self, new_insts):
        """
        Args:
            new_insts ([{"cxn_inst":CXN_SCHEMA_INST, "match_qual":FLOAT}]): List of construction instances to be added to grammatical working memory.
        """
        for inst in new_insts:
            match_qual = inst["match_qual"]
            act = inst["cxn_inst"].activity
            new_inst = inst["cxn_inst"]
            self.add_instance(new_inst, act*match_qual)
            self._cooperate(new_inst)
            self._compete(new_inst)
    
    def _produce_form(self):
        """
        """
#        self.show_state()
#        self.end_competitions()
#        self.show_state()
        assemblages = self._assemble()
        if assemblages:
#            self._draw_assemblages()
            winner_assemblage = self._get_winner_assemblage(assemblages)
            if winner_assemblage.activation > self.C2_params['confidence_threshold']:
                print 'Production at time: %i' %self.t
                (phon_form, missing_info) = GRAMMATICAL_WM._read_out(winner_assemblage)
                self.set_output('to_phonological_WM', phon_form)
            
                # Option1: Replace the assemblage by it's equivalent instance
#                self.replace_assemblage(winner_assemblage)
                
                # Option2: Dismantle the assembalge by removing all the coop_link it involves and setting all composing instances activatoins to confidence_threshold.
#                self.dismantle_assemblage(winner_assemblage)
                
                 # Option3: Removes coop links + adds the equivalent instance.
#                self.dismantle_assemblage2(winner_assemblage)
                
                # Option4: Keeps all the coop_links but bumps down the activation values of all the isntances that are part of the winner assemblage.
#                self.reset_assemblage(winner_assemblage)
                
                #Option5: Sets all the instances in the winner assembalge to subthreshold activation. Sets all the coop_weightsto 0. So f-link remains but inst participating in assemblage decay unless they are reused.
                self.post_prod_state(winner_assemblage)

    def _get_winner_assemblage(self, assemblages):
        """
        Args: assemblages ([ASSEMBLAGE])
        Returns the winner assemblages and their equivalent instances.
        
        Note: Need to discuss the criteria that come into play in choosing the winner assemblages.
        As for the SemRep covered weight, the constructions should receive activation from the SemRep instances. This could help directly factoring in the SemRep covered factor.
        The formula is biased by the fact that not all variables have the same range. This needs to be accounted for.   
        
        NOTE: NEED TO SOMEHOW ACCOUNT FOR WEATHER OR NOT THE ASSEMBLAGE EXPRESSES NOVEL INFORMATION. Otherwise, I get the situation in which assemblage get reused
        because they are boosted by new construction while scoring higher that the novel assemblages.
        """
        w1 = 1 # Activation weight
        w2 = 0.2 # SemRep covered weight
        w3 = 0 # SynForm length weight
        
        winner = None
        max_score = None
        # Computing the equivalent instance for each assemblage.
        for assemblage in assemblages:
            eq_inst = self._assemblage2inst(assemblage)    
            sem_covered = len(eq_inst.content.SemFrame.nodes) + len(eq_inst.content.SemFrame.edges)
            form_len = len(eq_inst.content.SynForm.form)
            score = w1*eq_inst.activity + w2*sem_covered + w3*form_len # THIS NEEDS TO BE REVISED.
            if not(max_score):
                max_score = score
                winner = assemblage
            if score>max_score:
                max_score = score
                winner = assemblage
        return winner
 
#    def replace_assemblage(self, assemblage):
#        """
#        Replace all the construction instances contained in the assemblage by the assemblage equivalent cxn_inst.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        eq_inst = GRAMMATICAL_WM._assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.C2_params['confidence_threshold'])
#        for inst in assemblage.schema_insts:
#            inst.alive = False
#        self._add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
#        self.prune() # All the instances in the assemblage as well as all the f-links invovling them are removed.
#    
#    def dismantle_assemblage(self, assemblage):
#        """
#        Removes all the cooperation links involving instances that are part of the assemblages. Sets the activation of all the instances 
#        that are part of the assemblage to confidence_threshold.
#        Args:
#            - assemblage (ASSEMBLAGE)
#            
#        PB: When an assemblage is dismantled, some combinations of cxn instances might be necessary later on, but won't be possible to reconstruct.
#        E.g. "A man" once used will never be rebuilt since it will not involve novel semantic material.
#        The replace_assemblage policy would somewhat take care of this by including the equivalent instance. Same with dismantle assemblage2.
#        However, there is still an issue with removing the cooperation links. For example," There is a woman who is pretty" Then the system cannot utter,
#        given more semantic info, "A woman kicks a man" since it cannot rebuild "a woman" since this was dismantled following the previous utterance.
#        """
#        self.remove_coop_links(inst_from=assemblage.schema_insts, inst_to=assemblage.schema_insts)
#        for inst in assemblage.schema_insts:
#            inst.set_activation(self.C2_params['confidence_threshold'])
#    
#    def dismantle_assemblage2(self, assemblage):
#        """
#        Removes all the cooperation links involving instances that are part of the assemblages. Sets the activation of all the instances 
#        that are part of the assemblage to confidence_threshold.
#        Adds the assemblage equivalent cxn instance to the working memory.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        eq_inst = GRAMMATICAL_WM._assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.C2_params['confidence_threshold'])
#        
#        self.remove_coop_links(inst_from=assemblage.schema_insts, inst_to=assemblage.schema_insts)
#        for inst in assemblage.schema_insts:
#            inst.set_activation(self.C2_params['confidence_threshold'])
#        
#        self._add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
#    
#    def reset_assemblage(self, assemblage):
#        """
#        Resets the activation of all the instances that are part of the assemblage below confidence threshold.
#        Adds the assemblage equivalent cxn instance to the working memory.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        r = 0.9
#        eq_inst = GRAMMATICAL_WM._assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.C2_params['confidence_threshold']*r)
#
#        for inst in assemblage.schema_insts:
#            inst.set_activation(self.C2_params['confidence_threshold']*r)
#        
#        self._add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
    
    def post_prod_state(self, winner_assemblage):
        """
        Sets the grammatical state after production given a winner assemblage.
        """
        self._set_subthreshold(winner_assemblage.schema_insts)
        self._deactivate_coop_weigts()
        
    def _set_subthreshold(self, insts, r=1):
        """
        Sets the activation of all the instances in insts to r*confidence_threshold
        Args:
            - insts ([CXN_INST])
            - val (FLOAT)
        """
        for inst in insts:
            inst.set_activation(r*self.C2_params['confidence_threshold'])
            
    def _deactivate_coop_weigts(self, deact_weight=0):
        """
        Sets all the coop_links that in grammatial WM to weight = deact_weight
        Instances are also placed below confidence threshold.
        Args:
            - assemblage (ASSEMBLAGE)
        """
        for coop_links in self.coop_links:
            coop_links.weight = deact_weight

    ###############################
    ### cooperative computation ###
    ###############################
    def _cooperate(self, new_inst):
       """
       """
       for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM._match(new_inst, old_inst)
               if match["match_cat"] == 1:
                   for match_qual, link in match["links"]:
                       if match_qual > 0:
                           self.add_coop_link(inst_from=link["inst_from"], port_from=link["port_from"], inst_to=link["inst_to"], port_to=link["port_to"], qual=match_qual)
    
    def _compete(self, new_inst):
        """
        How to make it incremental....?
        Competition if they overlap on an edge.
        I want to avoid having to rebuild the assemblages all the time...-> Incrementality.
        """
        for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM._match(new_inst, old_inst)
               if match["match_cat"] == -1:
                   self.add_comp_link(inst_from=new_inst, inst_to=old_inst)
        
    
    @staticmethod
    def _overlap(inst1, inst2):
        """
        Returns the set of SemRep nodes and edges on which inst1 and inst2 overlaps.
        
        Args:
            - inst1 (CXN_SCHEMA_INST): A cxn instance
            - inst2 (CXN_SCHEMA_INST): A cxn instance
        """
        overlap = {}
        overlap["nodes"] = [n for n in inst1.trace["semrep"]["nodes"] if n in inst2.trace["semrep"]["nodes"]]
        overlap["edges"] = [e for e in inst1.trace["semrep"]["edges"] if e in inst2.trace["semrep"]["edges"]]
        if not(overlap['nodes']) and not(overlap['edges']):
            return None
        return overlap
        
    @staticmethod    
    def _link(inst_p, inst_c, SR_node):
        """
        Args:
            - inst_p (CXN_SCHEMA_INST): A cxn instance (parent)
            - inst_c (CXN_SCHEMA_INST): A cxn instance (child)
            - SR_node (): SemRep node on which both instances overlap
        NOTE:
            - NO LIGHT SEMANTICS!!!
        """
        cxn_p = inst_p.content
        sf_p = [cxn_p.find_elem(k) for k,v in inst_p.covers["nodes"].iteritems() if v == SR_node][0] # Find SemFrame node that covers the SemRep node
        cxn_c = inst_c.content
        sf_c = [cxn_c.find_elem(k) for k,v in inst_c.covers["nodes"].iteritems() if v==SR_node][0] # Find SemFrame node that covers the SemRep node
        
        cond1 = (sf_p.name in cxn_p.SymLinks.SL) and isinstance(cxn_p.node2form(sf_p), construction.TP_SLOT) # sf_p is linked to a slot in cxn_p
        cond2 = sf_c.head # sf_c is a head node
        if cond1 and cond2:
            slot_p = cxn_p.node2form(sf_p)
            cond3 = cxn_c.clss in slot_p.cxn_classes
            # NEED TO ADD A LIGHT_SEM CONDITION (cond4?)
            link = {"inst_from": inst_c, "port_from":inst_c._find_port("output"), "inst_to": inst_p, "port_to":inst_p._find_port(slot_p.order)}
            if cond3:
                match_qual = 1
            else:
                match_qual = 0
            return (match_qual, link)
        return None
    
    @staticmethod
    def _match(inst1, inst2):
        """
        IMPORTANT NOTE: IT IS NOT CLEAR WHY THE ABSCENSE OF LINK SHOULD NECESSARILY MEAN COMPETITION....
            Think about the case of a lexical cxn LEX_CXN linking to a Det_CXN itself linking to a SVO_CXN, we don't want LEX_CXN to enter in competition with
            SVO_CXN, even though they can't link since the LEX_CXN doesn't match the class restriction of SVO_CXN (LEX_CXN is N, not NP).
        
        For now I set the case not(links) to match=0. This is incorrect, since it does not allow to handle properly the case of lexical competition.
        """
        match_cat = 0
        links = []
        if inst1 == inst2:
           match_cat = -1 # CHECK THAAT
        else:
            overlap = GRAMMATICAL_WM._overlap(inst1, inst2)
            if not(overlap):
                match_cat = 0
            elif overlap["edges"]:
                match_cat = -1
            else:
                for n in overlap["nodes"]:
                    link = GRAMMATICAL_WM._link(inst1, inst2, n)
                    if link:
                        links.append(link)
                    link = GRAMMATICAL_WM._link(inst2, inst1, n)
                    if link:
                        links.append(link)
                if links:
                    match_cat = 1
                else:
                    match_cat = -1      
        return {"match_cat":match_cat, "links":links}
    
    ##################
    ### Assemblage ###
    ##################    
    def _assemble(self): # THIS IS VERY DIFFERENT FROM THE ASSEMBLE ALGORITHM OF TCG 1.0
        """
        WHAT ABOUT THE CASE WHERE THERE STILL IS COMPETITION GOING ON?
        
        NOTE THAT IN THE CASE OF MULTIPLE TREES GENERATED FROM THE SAME SET OF COOPERATION... THERE IS MAXIMUM SPANNING TREE. IS THIS IS THE ONE THA SHOULD BE CONSIDERED?
        """
        inst_network = GRAMMATICAL_WM._build_instance_network(self.schema_insts, self.coop_links)

        tops = [(n,None) for n in inst_network.nodes() if not(inst_network.successors(n))]
        assemblages = []
        for t in tops:
            results = []
            frontier = [t]
            assemblage = ASSEMBLAGE()
            self._get_trees(frontier, assemblage, inst_network, results)
            assemblages += results
        
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
        NOTE: I think it does...
        ALSO, it returns sub-optimal trees. (Not only the tree that contains all the cooperating instances in the WM).
        """
        new_frontiers = [[]]
        for node, link in frontier:
            assemblage.add_instance(node)
            if link:
                assemblage.add_link(link)
            ports = graph.predecessors(node)
            for port in ports:
                children = graph.predecessors(port)
                updated_frontiers = []
                for child in children:
                    flag =  child in assemblage.schema_insts
                    if not(flag):
                        link = self.find_coop_links(inst_from=[child], inst_to=[node], port_from=[child._find_port("output")], port_to=[port])
                        for f in new_frontiers:
                            updated_frontiers.append(f[:] + [(child, link[0])])
                new_frontiers = updated_frontiers
        if new_frontiers == [[]]:
            results.append(assemblage)
        else:
            for a_frontier in new_frontiers:
                self._get_trees(a_frontier, assemblage.copy(), graph, results)
                
    @staticmethod
    def _assemblage2inst(assemblage):
        """
        """
        new_assemblage = assemblage.copy()
        coop_links = new_assemblage.coop_links
        while len(coop_links)>0:
            new_assemblage = GRAMMATICAL_WM._reduce_assemblage(new_assemblage, new_assemblage.coop_links[0])
            coop_links = new_assemblage.coop_links
        eq_inst = new_assemblage.schema_insts[0]
        eq_inst.activity = new_assemblage.activation
        return eq_inst
      
    @staticmethod      
    def _reduce_assemblage(assemblage, coop_link):
        """
        Returns a new, reduced, assemblage in which the instances cooperating (as defined by 'coop_link') have been combined.
        """
        inst_p = coop_link.inst_to
        inst_c = coop_link.inst_from
        connect = coop_link.connect
        
        (new_cxn_inst, port_corr) = GRAMMATICAL_WM._combine_schemas(inst_p, inst_c, connect)
        
        new_assemblage = ASSEMBLAGE()
        new_assemblage.activation = assemblage.activation
        
        for inst in assemblage.schema_insts:
            if inst != inst_p and inst != inst_c:
                new_assemblage.add_instance(inst)
        new_assemblage.add_instance(new_cxn_inst)
        
        coop_links = assemblage.coop_links[:]
        coop_links.remove(coop_link)
        for coop_link in coop_links:
            new_link = coop_link.copy()
            if new_link.inst_to == inst_p:
                new_link.inst_to = new_cxn_inst
                new_link.connect.port_to = port_corr['in_ports'][coop_link.connect.port_to]
            if new_link.inst_to == inst_c:
                new_link.inst_to = new_cxn_inst
                new_link.connect.port_to = port_corr['in_ports'][coop_link.connect.port_to]
            if new_link.inst_from == inst_p:
                new_link.inst_from = new_cxn_inst
                new_link.connect.port_from = port_corr['out_ports'][coop_link.connect.port_from]
            if new_link.inst_from == inst_c:
                new_link.inst_to = new_cxn_inst
                new_link.connect.port_from = port_corr['out_ports'][coop_link.connect.port_from]
            new_assemblage.add_link(new_link)
        
        return new_assemblage
    
    @staticmethod
    def _combine_schemas(inst_to, inst_from, connect):
        """
        Returns a new cxn_instance and the mapping between inst_to and inst_from ports to new_cxn_inst ports.
        """
        inst_p = inst_to
        port_p = connect.port_to
        cxn_p = inst_p.content
        slot_p = port_p.data
        
        inst_c = inst_from
        cxn_c = inst_c.content        
        
        (new_cxn, c) = construction.CXN.unify(cxn_p, slot_p, cxn_c)
        new_cxn_schema = CXN_SCHEMA(new_cxn, init_act=0)
        
        # Define new_cxn trace
        new_trace = {'semrep':{'nodes':[], 'edges':[]}, "schemas":inst_p.trace["schemas"] + inst_c.trace["schemas"]} 
        nodes = list(set(inst_p.trace['semrep']['nodes'] + inst_c.trace['semrep']['nodes']))
        edges = list(set(inst_p.trace["semrep"]["edges"] + inst_c.trace["semrep"]["edges"]))
        new_trace['semrep']['nodes'] = nodes
        new_trace['semrep']['edges']= edges
        
        # Defines new_cxn mapping
        new_mapping = {'nodes':{}, 'edges':{}} # TO DEFINE
        for n,v in inst_p.covers['nodes'].iteritems():
                new_mapping['nodes'][c[n]] = v
        for e,v in inst_p.covers['edges'].iteritems():
            if (e[0] in c.keys()) and (e[1] in c.keys()):# Check the parent node hasn't been removed.
                new_mapping['edges'][(c[e[0]] , c[e[1]])] = v
            
        for n,v in inst_c.covers['nodes'].iteritems():
            new_mapping['nodes'][c[n]] = v
        for e,v in inst_c.covers['edges'].iteritems():
            new_mapping['edges'][(c[e[0]], c[e[1]])] = v
        
        new_cxn_inst = CXN_SCHEMA_INST(new_cxn_schema, trace=new_trace, mapping=new_mapping, copy=False)
        
        # Define port correspondence
        in_ports = [port for port in inst_p.in_ports if port.data != slot_p] + [port for port in inst_c.in_ports]
        new_cxn_inst.set_ports()
        
        port_corr = {'in_ports':{}, 'out_ports':{}}
        for port in in_ports:
            for new_port in new_cxn_inst.in_ports:
                if c[port.data.name] == new_port.data.name:
                    port_corr['in_ports'][port] = new_port
                    break
        port_corr['out_ports'][inst_p._find_port('output')] = new_cxn_inst._find_port('output')
      
        return (new_cxn_inst, port_corr)
            
#    @staticmethod                
#    def _read_out_LR(assemblage):
#        """
#        Left2right reading of the tree formed byt the assemblage.
#        
#        NOTE: SHOULD BE REPLACED BY ASSEMBLE
#        """
#        def L2R_read(inst, graph, phon_form):
#            """
#            """
#            cxn = inst.content
#            SynForm = cxn.SynForm.form
#            for f in SynForm:
#                if isinstance(f, construction.TP_PHON):
#                    phon_form.append(f.cxn_phonetics)
#                else:
#                    port = inst._find_port(f.order)
#                    child  = graph.predecessors(port)
#                    if not(child):
#                        print "MISSING INFORMATION!"
#                    else:
#                        L2R_read(child[0], graph, phon_form)
#        
#        graph = GRAMMATICAL_WM._build_instance_network(assemblage.schema_insts, assemblage.coop_links)
#        tops = [n for n in graph.nodes() if not(graph.successors(n))]
#        phon_form = []
#        L2R_read(tops[0], graph, phon_form)
#        return phon_form
        
    @staticmethod 
    def _read_out(assemblage):
        """
        Reads the phonlogical from generated by an assemblage by building the equivalent CXN INSTANCE.
        Returns: (phon_form, missing_info) with:
            - phon_form = the longest consecutive TP_PHON sequence that can be uttered.
            - missing_info = pointer to the SemRep node associated with the first TP_SLOT encountered, represented the missing information.
        """
        eq_inst = GRAMMATICAL_WM._assemblage2inst(assemblage)
        phon_form = []
        missing_info = None
        for form in eq_inst.content.SynForm.form:
            if isinstance(form, construction.TP_PHON):
                phon_form.append(form.cxn_phonetics)
            else:
                SemFrame_node = eq_inst.content.SymLinks.form2node(form)
                SemRep_node = eq_inst.covers['nodes'][SemFrame_node.name]
                missing_info = SemRep_node
                return (phon_form, missing_info)
      
        return (phon_form, missing_info)
        
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
    
    @staticmethod
    def _draw_assemblage(assemblage, title=''):
        """
        """
        graph = GRAMMATICAL_WM._build_instance_network(assemblage.schema_insts, assemblage.coop_links)
        GRAMMATICAL_WM._draw_instance_network(graph, title)
        
    def _draw_assemblages(self):
        """
        """
        assemblages = self._assemble()
        i=0
        for assemblage in assemblages:
            title = 'Assemblage_%i' % i
            GRAMMATICAL_WM._draw_assemblage(assemblage, title)
            i += 1
                  
class GRAMMATICAL_LTM(LTM):
    """
    """
    def __init__(self, name='Grammatical_LTM'):
        LTM.__init__(self, name)
        self.grammar = None
        self.add_port('OUT', 'to_cxn_retrieval')
        self.init_act = 0.5 #The initial activation value for cxn schema.
    
    def initialize(self, grammar):
        """
        Initilize the state of the GRAMMATICAL LTM with cxn_schema based on the content of grammar.
        Args:
            - grammar (GRAMMAR): A TCG grammar
        """
        self.grammar = grammar
        for cxn in grammar.constructions:
            new_cxn_schema = CXN_SCHEMA(cxn, self.init_act)
            self.add_schema(new_cxn_schema)

    def update(self):
        """
        """
        self.set_output('to_cxn_retrieval', self.schemas)
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(GRAMMATICAL_LTM, self).get_info()
        data['init_act'] = self.init_act
        return data

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
            # Set all SemRep elements to new=False
            for n in SemRep.nodes_iter():
                SemRep.node[n]['new'] = False
            for e in SemRep.edges_iter():
                d = SemRep.get_edge_data(e[0], e[1])
                d['new'] = False
        
        self.cxn_instances = []
    
    def _instantiate_cxns(self, SemRep, cxn_schemas, WK=None):
        """
        """
        if not cxn_schemas:
            return
        for cxn_schema in cxn_schemas:        
            sub_iso = self._SemMatch_cat(SemRep, cxn_schema)
            for a_sub_iso in sub_iso:
                match_qual = self._SemMatch_qual(SemRep, cxn_schema, a_sub_iso)
                trace = {"semrep":{"nodes":a_sub_iso["nodes"].values(), "edges":a_sub_iso["edges"].values()}, "schemas":[cxn_schema]}
                node_mapping  = dict([(k.name, v) for k,v in a_sub_iso['nodes'].iteritems()])
                edge_mapping  = dict([((k[0].name, k[1].name), v) for k,v in a_sub_iso['edges'].iteritems()])
                mapping = {'nodes':node_mapping, 'edges':edge_mapping}                
                new_instance = CXN_SCHEMA_INST(cxn_schema, trace, mapping)
                self.cxn_instances.append({"cxn_inst":new_instance, "match_qual":match_qual})
                    
    def _SemMatch_cat(self, SemRep, cxn_schema):
        """
        IMPORTANT ALGORITHM
        Computes the categorical matches (match/no match) -> Returns the sub-graphs isomorphisms. This is the main filter for instantiation.
        """
        SemFrame_graph = cxn_schema.content.SemFrame.graph 
            
        node_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a")
        edge_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="equal")
        nm = TCG_graph.node_iso_match("concept", "", node_concept_match)
        em = TCG_graph.edge_iso_match("concept", "", edge_concept_match)
        
        def subgraph_filter(subgraph):
            """
            Returns True only if at least one node or edge is tagged as new.
            """
            for n,d in subgraph.nodes(data=True):
                if d['new']:
                    return True
            for n1,n2,d in subgraph.edges(data=True):
                if d['new']:
                    return True
            return False

        sub_iso = TCG_graph.find_sub_iso(SemRep, SemFrame_graph, node_match=nm, edge_match=em, subgraph_filter=subgraph_filter)
        return sub_iso
    
    def _SemMatch_qual(self, SemRep, cxn_schema, a_sub_iso): ## NEEDS TO BE WRITTEN!! At this point the formalism does not support efficient quality of match.
        """
        Computes the quality of match.
        Returns a value between 0 and 1: 0 -> no match, 1 -> perfect match.
        
        NOTE: I NEED TO THINK ABOUT HOW TO INCORPORATE FOCUS ETC....
        """
        return 1
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(CXN_RETRIEVAL, self).get_state()
        data['cnx_instances'] = [inst.name for inst in self.cxn_instances]
        return data

class PHON_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Phonological_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_grammatical_WM')
        self.add_port('OUT', 'to_output')
        self.add_port('OUT', 'to_control')
        self.phon_form = []
    
    def update(self):
        """
        """
        phon_form = self.get_input('from_grammatical_WM')
        if phon_form:
            self.phon_form = phon_form
            self.set_output('to_output', phon_form)
            self.set_output('to_control', True)
        else:
            self.set_output('to_output', None)
            
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(PHON_WM, self).get_state()
        data['phon_form'] = self.phon_form
        return data
        
class CONTROL(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name="Control"):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_phonological_WM')
        self.add_port('OUT', 'to_grammatical_WM')
        self.task_params = {'time_pressure':100}
        self.state = {'last_prod_time':0, 'new_sem':False}
    
    def update(self):
        """
        """
        if ((self.t - self.state['last_prod_time']) > self.task_params['time_pressure']) and self.state['new_sem']:
            self.set_output('to_grammatical_WM', True)
            self.state['new_sem'] = False
        if self.get_input('from_phonological_WM'):
            self.state['last_prod_time'] = self.t
        if self.get_input('from_semantic_WM'):
            self.state['new_sem'] = True
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(CONTROL, self).get_info()
        data['task_params'] = self.task_params
        return data
    
    def get_state(self):
        """
        """
        data = super(CONTROL, self).get_state()
        data['state'] = self.state
        return data
        
class TEXT2SPEECH(object):
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
    from test_language_schemas import test
    test(seed=None)
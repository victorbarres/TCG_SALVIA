# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines language schemas for TCG.

Dependencies:
    - Uses NetworkX for the implementation of the content of the Semantic Working Memory (SemRep graph)
    - Uses Numpy for vectorial operations.
    - Uses pyttsx for the text to speech implementation (optional!)
    - Uses re for regular expression parsing of sem inputs
    
    - Uses schema_theory
    - Uses construction
    - Uses TCG_graph
"""
from __future__ import division
import re
import os
import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import pyttsx


from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, SYSTEM_SCHEMA, LTM, WM, ASSEMBLAGE
import construction
import TCG_graph

#######################################
##### LANGUAGE KNOWLEDGE SCHEMAS ######
#######################################

####################################
### GRAMMATICAL KNOWLEDGE SCHEMA ###
####################################
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
    def __init__(self, aCXN, init_act):
        KNOWLEDGE_SCHEMA.__init__(self, name=aCXN.name, content=aCXN, init_act=init_act)
    
    def get_initial_predictions(self):
        """
        Returns the list of initial prediction (syntactic classes or word forms)
        This is similar to getting the Left-Corner of the rule in the case of CFG.
        """
        init_preds = []
        init_form = self.content.SynForm.form[0]
        if isinstance(init_form, construction.TP_SLOT):
            init_preds = init_form.cxn_classes
        else:
            init_preds = [init_form.cxn_phonetics]
        return init_preds
            

class CXN_SCHEMA_INST(SCHEMA_INST):
    """
    (Production) construction instance
    
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
            - inputs (DICT): At each time steps stores the inputs
            - outputs (DICT): At each time steps stores the ouputs
            - alive (bool): status flag
            - done (bool): True if the instance is done with its function.
            - trace ({"SemRep":{"nodes":[], "edges"=[]}, "schemas":[CXN_SCHEMA]}): Pointer to the elements that triggered the instantiation.
        - covers ({"nodes":{}, "edges"={}}): maps CXN.SemFrame nodes and edges (in content) to SemRep elements (in the trace) (Maps the nodes and edges names to SemRep obj)
    """
    def __init__(self, cxn_schema, trace, mapping={"nodes":{}, "edges":{}}, copy=True):
        SCHEMA_INST.__init__(self, schema=cxn_schema, trace=trace)
        self.covers = {}
        if copy:
            (cxn_copy, c) = cxn_schema.content.copy()
            self.content = cxn_copy
            if mapping:
                new_node_mapping  = dict([(c[k], v) for k,v in mapping['nodes'].iteritems()])
                new_edge_mapping  = dict([((c[k[0]], c[k[1]]), v) for k,v in mapping['edges'].iteritems()])
                new_mapping= {'nodes':new_node_mapping, 'edges':new_edge_mapping}
                self.covers = new_mapping
            
            # Reset ports to get proper links to content copy.
            self.remove_ports()
            self.set_ports() 
        
        else:
             self.covers = mapping
    
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
            SemFrame_head = self.content.SemFrame.get_head()
            self.add_port('OUT','output', port_data=SemFrame_head)
        else:
             for port in out_ports:
                self.out_ports.append(port)
                port.schema=self
            
class CXN_SCHEMA_INST_C(CXN_SCHEMA_INST):
    """
    Comprehension construction instance.
    
    Added:
        - form_sequence
        - form_state
        - has_predicted
        - expressed
    Notes:
        - Here covers defines a mapping from SynForm to Phon_Inst
    """
    def __init__(self, cxn_schema, trace, mapping={}, copy=True):
        CXN_SCHEMA_INST.__init__(self, cxn_schema=cxn_schema, mapping=mapping, trace=trace, copy=copy)
        self.form_sequence = self.content.SynForm.form[:]
        self.form_sequence.reverse() # Simply so that the sequence can be used as stack in python.
        self.form_state = self.form_sequence.pop()
        self.chart_pos = [] # Should be reorganized with covers. Mapping should also be introduced by reworking the relations with constructions instances used for production.
        self.has_predicted = False
        self.expressed = False
    
    def cxn_predictions(self):
        """
        Return the set of cxn classes that are predicted by this construction given its current form_state. 
        Classes that are predicted are those that fit the constraints of next(state) if it is a slot.
        No predictions are issued if instance is in COMPLETE state or if next(state) is not a slot.
        Notes:
            - This should include the semantic features of the node the slot is symbolically linked to.
        """
        predictions = []
        if self.form_state and (isinstance(self.form_state, construction.TP_SLOT)):
            predictions.extend(self.form_state.cxn_classes)
        self.has_predicted = True
        return predictions
    
    def phon_prediction(self):
        """
        Return, if the form_state is a TP_PHON, the word_form the cxn is expecting.
        """
        word_form = None
        if self.form_state and(isinstance(self.form_state, construction.TP_PHON)):
            word_form =  self.form_state.cxn_phonetics
        return word_form
        
    def next_state(self):
        """
        Move to next state along the form sequence (defined by the SynForm).
        """
        if self.form_sequence:
            self.form_state = self.form_sequence.pop()
            self.has_predicted = False
        else:
            self.form_state = None
            
#################################
### CONCEPT KNOWLEDGE SCHEMAS ###
#################################      
class CPT_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Concept schema
    Data:
    - KNOWEDGE SCHEMA data:
        - id (int): Unique id
        - name (str): schema name
        - LTM (LTM): Associated long term memory.
        - content ({'concept':CONCEPT): concept is a CONCEPT in SEMANTIC_NETWORK
        - init_act (float): Initial activation value.
    """
    def __init__(self, name, concept, init_act):
        """
        Args:
            - name (STR):
            - concept (CONCEPT):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.set_content({'concept':concept})

class CPT_ENTITY_SCHEMA(CPT_SCHEMA):
    """
    Conceptual entity schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self, name, concept, init_act)

class CPT_ACTION_SCHEMA(CPT_SCHEMA):
    """
    Conceptual action schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self, name, concept, init_act)

class CPT_PROPERTY_SCHEMA(CPT_SCHEMA):
    """
    Conceptual property schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self, name, concept, init_act)

class CPT_EVENT_SCHEMA(CPT_SCHEMA):
    """
    Conceptual event schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self, name, concept, init_act)

class CPT_RELATION_SCHEMA(CPT_SCHEMA):
    """
    Conceptual relation schema
    """
    def __init__(self, name, concept, init_act):
        CPT_SCHEMA.__init__(self, name, concept, init_act)
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
        self.unbound = False
        self.frame = False
        
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
        
#############################
### PHON KNOWLEDGE SCHEMA ###
#############################
class PHON_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Phonological form schemas.
    NOTE:
        - For now the model only deals with word level phonological form, ignoring phoneme level processes.
        - For now, there is no distinction between PHON_SCHEMA used during production and those used during comprehension.
    """
    def __init__(self, name, word_form, init_act):
        """
        Args:
            - name (STR):
            - word_form (STR):
            - init_act (FLOAT):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.set_content({'word_form':word_form})

class PHON_RELATION_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    UNUSED! For now the PhonologicalWM contains a sequence of PHONS_SCHEMA_INST that define word_forms.
    Temporal relation between phonological form schemas.
    NOTE:
         For now only 'next' is implemented.
    """
    def __init__(self, name, phon_rel, init_act):
        """
        Args:
            - name (STR):
            - phon_rel (STR):
            - init_act (FLOAT):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.set_content({'phon_rel':phon_rel})
        self.content['pFrom'] = None 
        self.content['pTo'] = None

class PHON_SCHEMA_INST(SCHEMA_INST):
    """
    Phonological schema instances.
    """
    def __init__(self, phon_schema, trace):
        SCHEMA_INST.__init__(self, schema=phon_schema, trace=trace)
        content_copy = phon_schema.content.copy()
        self.content = content_copy

###################################
##### LANGUAGE SYSTEM SCHEMAS #####
###################################

#################
### SEMANTICS ###
#################
class CONCEPTUALIZER(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name='Conceptualizer'):
        SYSTEM_SCHEMA.__init__(self, name)
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
    
    def process(self):
        """
        """
        SceneRep = self.inputs['from_visual_WM']
        cpt_schemas = self.inputs['from_concept_LTM']
        if cpt_schemas and SceneRep:
            cpt_insts  = self.conceptualize(SceneRep, cpt_schemas)
            self.outputs['to_semantic_WM'] =  cpt_insts
        
            # Set all SceneRep elements to new=False
            for n in SceneRep.nodes_iter():
                SceneRep.node[n]['new'] = False
            for e in SceneRep.edges_iter():
                d = SceneRep.get_edge_data(e[0], e[1])
                d['new'] = False
    
    def conceptualize(self, SceneRep, cpt_schemas):
        """
        For a given SceneRep, returns the set of CPT_SCHEMA_INSTS that conceptualize the SceneRep

        Args:
            - SceneRep ()
            - cpt_schemas ()
            
        Notes:
            - For now the conceptualization scheme is trivial: many-to-one mapping.
        """
        FRAMES  = ['ENTITY_SCENE', 'ACTION_SCENE', 'EVENT_SCENE']
        
        cpt_insts  = []
        for n,d in SceneRep.nodes(data=True): # First process the nodes.
            if d['new']:
                per_name = d['percept'].name
                per_inst = d['per_inst']
                cpt_name = self.conceptualization.conceptualize(per_name)
                cpt_schema = [schema for schema in cpt_schemas if schema.name == cpt_name][0]
                cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'per_inst':per_inst, 'cpt_schema':cpt_schema})
                cpt_inst.frame = per_name in FRAMES
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
        self.add_port('OUT', 'to_semantic_WM')
        self.cpt_knowledge = None
        self.params['init_act'] = 1
        
    def initialize(self, cpt_knowledge):
        """
        Initilize the state of the CONCEPTUAL LTM with cpt_schemas based on the content of cpt_knowledge
       
        Args:
            - cpt_knowledge (CONCEPTUAL_KNOWLEDGE):
        """
        self.cpt_knowledge = cpt_knowledge
        
        entity_name = 'ENTITY'
        action_name = 'ACTION'
        property_name = 'PROPERTY'
        relation_name = 'RELATION'  
        event_name = 'EVENT'
        
        entity = cpt_knowledge.find_meaning(entity_name)
        action = cpt_knowledge.find_meaning(action_name)
        prop = cpt_knowledge.find_meaning(property_name)
        rel = cpt_knowledge.find_meaning(relation_name)
        event = cpt_knowledge.find_meaning(event_name)

        for concept in cpt_knowledge.concepts():
            new_schema = None
            if concept.name == 'CONCEPT':
                pass
            elif cpt_knowledge.match(concept, event, match_type="is_a"):
                new_schema = CPT_EVENT_SCHEMA(name=concept.name, concept=concept, init_act=self.params['init_act'])
            elif cpt_knowledge.match(concept, entity, match_type="is_a"):
                new_schema = CPT_ENTITY_SCHEMA(name=concept.name, concept=concept, init_act=self.params['init_act'])
            elif cpt_knowledge.match(concept, action, match_type="is_a"):
                new_schema = CPT_ACTION_SCHEMA(name=concept.name, concept=concept, init_act=self.params['init_act'])
            elif cpt_knowledge.match(concept, prop, match_type="is_a"):
                new_schema = CPT_PROPERTY_SCHEMA(name=concept.name, concept=concept, init_act=self.params['init_act'])
            elif cpt_knowledge.match(concept, rel, match_type="is_a"):
                new_schema = CPT_RELATION_SCHEMA(name=concept.name, concept=concept, init_act=self.params['init_act'])
            else:
                print "%s: unknown concept type" %concept.meaning
            
            if new_schema:
                self.add_schema(new_schema)
    
    def process(self):
        self.outputs['to_conceptualizer'] =  self.schemas
        self.outputs['to_semantic_WM'] = self.schemas
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(CONCEPT_LTM, self).get_info()
        data['params'] = self.params
        return data
                
class SEMANTIC_WM(WM):
    """
    Notes:
        - to_output is defined differently for production and comprehension. Need to unify that.
        - Not sure that it is best for C2 in comprehension to have a single SemanticWM. to see.
    """
    def __init__(self, name='Semantic_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_conceptualizer')
        self.add_port('IN', 'from_concept_LTM')
        self.add_port('IN', 'from_grammatical_WM_C')
        self.add_port('IN', 'from_grammatical_WM_P')
        self.add_port('IN', 'from_control')
        self.add_port('OUT', 'to_grammatical_WM_P')
        self.add_port('OUT', 'to_cxn_retrieval_P')
        self.add_port('OUT', 'to_control')
        self.add_port('OUT', 'to_visual_WM')
        self.add_port('OUT', 'to_output')
        self.params['dyn'] = {'tau':1000.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.SemRep = nx.MultiDiGraph() # Uses networkx to easily handle graph structure.
    
    def reset(self):
        """
        """
        super(SEMANTIC_WM, self).reset()
        self.SemRep = nx.DiGraph()
    
    def process(self):
        """
        """
        mode = self.inputs['from_control']
        
        if mode == 'produce':
            self.subprocess_prod()
        if mode == 'listen':
            self.subprocess_comp()
                            
        self.update_activations()       
        self.prune()
    
    def subprocess_comp(self, init_val = 0.2):
        """Comprehension subprocess
        """
        cpt_insts = None        
        gram_activations = {}
        gram_input = self.inputs['from_grammatical_WM_C']
        if gram_input:
            gram_activations = gram_input['activations']
            instance_data  = gram_input.get('instances', None)
            if instance_data:
                SemFrame = instance_data['SemFrame']
                sem_map = instance_data['sem_map']
                cpt_schemas = self.inputs['from_concept_LTM']
                if cpt_schemas and SemFrame and sem_map:
                    cpt_insts  = self.instantiate_cpts(SemFrame, sem_map, cpt_schemas)
   
        if cpt_insts:
            for inst in cpt_insts:
                self.add_instance(inst, init_val)   
        
        self.convey_gram_activations(gram_activations) # NEED TO DEFINE WEIGHT IF THERE IS COMPETITION. DO THAT USING THE CONNECT WEIGHT
        self.update_SemRep(cpt_insts)
        
    def subprocess_prod(self):
        """ Production subprocess
        """
        cpt_insts = self.inputs['from_conceptualizer']            
        if cpt_insts:
            for inst in cpt_insts:
                self.add_instance(inst)
        
        self.update_SemRep(cpt_insts) 
                
        if self.inputs['from_grammatical_WM_P']: # This should be done on the instances directly...
            # Note nodes and edges as expressed
            for name in self.inputs['from_grammatical_WM_P']['nodes']:
                self.SemRep.node[name]['expressed'] = True
            for name in self.inputs['from_grammatical_WM_P']['edges']:
                d = self.SemRep.get_edge_data(name[0], name[1])
                d['expressed'] = True
        
        self.outputs['to_grammatical_WM_P'] = self.gram_WM_P_output()
        
        # TD request for missing info
        self.outputs['to_visual_WM'] = self.vis_WM_output()
        
        if self.has_new_sem():
            self.outputs['to_cxn_retrieval_P'] = self.SemRep
        
        self.outputs['to_control'] = self.has_unexpressed_sem()
        
    
    def update_SemRep(self, cpt_insts):
        """
        Updates the SemRep: Adds the nodes and edges needed based on the receivd concept instances.
        
        NOTE:
            - Does not handle the case of concept instance updating. Concepts cannot be updated (Monotonous growth of the SemRep)
            - SemRep carries the instance and the concept. The concept field is redundant, but is useful in order to be able to define
            SemMatch between SemRep graph and SemFrames (graphs needs to have same data key).
        """
        if cpt_insts:
            # First process all the instances that are not relations.
            for inst in [i for i in cpt_insts if not(isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA))]:
                if self.SemRep.has_node(inst.name):
                    continue
                self.SemRep.add_node(inst.name, cpt_inst=inst, concept=inst.content['concept'], frame=inst.frame, new=True, expressed=False)
            
            # Then add the relations
            for rel_inst in [i for i in cpt_insts if isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA)]:
                node_from = rel_inst.content['pFrom'].name
                node_to = rel_inst.content['pTo'].name
                if self.SemRep.has_edge(node_from, node_to):
                    continue
                self.SemRep.add_edge(node_from, node_to, cpt_inst=rel_inst, concept=rel_inst.content['concept'], frame=inst.frame,  new=True, expressed=False)
            
#            # Update concept frames
#            self.update_cpt_frames()
    
#    def update_cpt_frames(self):
#        """
#        For all the concept frames instances. If they have an 'IS' relation, propagate is_concept to frame.
#        """
#        cpt_rel_name = 'IS'
#        for u,v,d in [edge for edge in self.SemRep.edges(data=True)]:
#            if d['concept'].name == cpt_rel_name:
#                self.SemRep.node[u]['cpt_inst'].content = self.SemRep.node[v]['cpt_inst'].content.copy()
#                self.SemRep.node[u]['concept'] = self.SemRep.node[v]['concept']
    
    #########################
    ### COMPREHENSION METHODS
    def instantiate_cpts(self, SemFrame, sem_map, cpt_schemas):
        """
        Builds SemRep based on the received SemFrame.
        
        Args:
            - SemFrame (TP_SEMFRAME)
            - cpt_schemas ([CPT_SCHEMAS])
        """
        def find_cpt_schema(cpt_schemas, cpt_name):
            """Returns, if it exists, the cpt_schema whose name matches cpt_name
            """
            output = [schema for schema in cpt_schemas if schema.name == cpt_name]
            if len(output)>1:
                error_msg = 'There is more than one cpt_schema matches the concept name %s' %cpt_name
                raise ValueError(error_msg)
            elif not(output):
                error_msg = 'There are is cpt_schema that matches the concept name %s' %cpt_name
                raise ValueError(error_msg)
            else:
                return output[0]
            
        def find_cpt_inst(sem_frame_insts):
            """ Returns, if it exists, the cpt_inst whose sem_frame trace already contains one of the sem_frame_insts.
            """
            output = [inst for inst in self.schema_insts if not(inst.trace['sem_frame_insts'].isdisjoint(sem_frame_insts))]
            if len(output)>1:
                print self.t
                error_msg = 'There is more than one cpt_inst that map onto the same SemFrame element! %s' %str([o.name for o in output])
                raise ValueError(error_msg)
            elif len(output)==1:
                return output[0]
            else:
                return None
        cpt_insts = []
        name_table = {}
        
        for node in SemFrame.nodes:
            cpt_schema = find_cpt_schema(cpt_schemas, node.concept.name)
            sem_frame_insts = set([k for k,v in sem_map.iteritems() if node.name in v])
            old_cpt_inst = find_cpt_inst(sem_frame_insts)
            if old_cpt_inst:
                old_cpt_inst.trace['sem_frame_insts'].update(sem_frame_insts)
                name_table[node] = old_cpt_inst
            else:
                new_cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'cpt_schema':cpt_schema, 'sem_frame_insts':sem_frame_insts})
                name_table[node] = new_cpt_inst
                cpt_insts.append(new_cpt_inst)
        
        for edge in SemFrame.edges:
            cpt_schema = find_cpt_schema(cpt_schemas, edge.concept.name)
            sem_frame_insts = set([k for k,v in sem_map.iteritems() if edge.name in v])
            old_cpt_inst = find_cpt_inst(sem_frame_insts)
            if old_cpt_inst:
                old_cpt_inst.trace['sem_frame_insts'].update(sem_frame_insts)
            else:
                new_cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'cpt_schema':cpt_schema, 'sem_frame_insts':sem_frame_insts})
                new_cpt_inst.content['pFrom'] = name_table[edge.pFrom]
                new_cpt_inst.content['pTo'] = name_table[edge.pTo]
                cpt_insts.append(new_cpt_inst)
        return cpt_insts
    
    def convey_gram_activations(self, gram_activations):
        """
        SemRep instances receives external activations from the construction instances they are linked to.
        Notes:
            - This imposes that (1) the cpt_inst start with low activations. (2) the cxn instances are not deactivated once they are expressed (symmetric coop_links.)
        """
        if not(gram_activations):
            return
        for inst in self.schema_insts:
            for k, val in gram_activations.iteritems():
                act = 0
                if k in inst.trace['sem_frame_insts']:
                    act += val
                inst.activation.E += act # No normalization
    
    ######################
    ### PRODUCTION METHODS       
    def gram_WM_P_output(self):
        """
        Returns the output to send to gram_WM_P.
        The signal sent to gram_WM_P contains the activation levels of the node and edge instance that so far have not been expressed.
        """
        output = {'nodes':{}, 'edges':{}}
        for n,d in self.SemRep.nodes(data=True):
            if not(d['expressed']):
                output['nodes'][n] = d['cpt_inst'].activity
        for u,v,d in self.SemRep.edges(data=True):
            if not(d['expressed']):
                output['edges'][(u,v)] = d['cpt_inst'].activity
        return output
    
    def vis_WM_output(self):
        """
        Returns the output to send to vis_WM. This output contains the TD attentional signal that can bias the 
        BU saliency.
        """
        output = None
        if not(self.inputs['from_grammatical_WM_P']) or not(self.inputs['from_grammatical_WM_P']['missing_info']):
            return output
        
        missing_info = self.inputs['from_grammatical_WM_P']['missing_info']
        
        cpt_schema_inst = self.find_instance(missing_info)
        var_name = cpt_schema_inst.trace.get('ref', '')
        self.outputs['to_output'] = {'missing_info':missing_info, 'var_name':var_name}
        output = cpt_schema_inst.trace['per_inst']
        return output
        
    def has_new_sem(self):
        """
        Returns true if there is at least 1 new element in the SemRep. False otherwise.
        """
        for n,d in self.SemRep.nodes(data=True):
            if d['new']:
                return True
        
        for u,v,d in self.SemRep.edges(data=True):
            if d['new']:
                return True
        return False
    
    def has_unexpressed_sem(self):
        """
        Returns true if there is at least 1 unexpresed node or relation in the SemRep. False otherwise. 
        """
        for n,d in self.SemRep.nodes(data=True):
            if not(d['expressed']):
                return True
        return False
        
        for u,v,d in self.SemRep.edges(data=True):
            if d['expressed']:
                return True
        return False
        
    ###################
    ### DISPLAY METHODS 
    def show_state(self):
        from viewer import TCG_VIEWER
        TCG_VIEWER.display_semWM_state(self, file_type='png', show=True)

class SEMANTIC_WM_P(WM):
    """
    """
    def __init__(self, name='Semantic_WM_P'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_conceptualizer')
        self.add_port('IN', 'from_concept_LTM')
        self.add_port('IN', 'from_grammatical_WM_P')
        self.add_port('IN', 'from_control')
        self.add_port('OUT', 'to_grammatical_WM_P')
        self.add_port('OUT', 'to_cxn_retrieval_P')
        self.add_port('OUT', 'to_control')
        self.add_port('OUT', 'to_visual_WM')
        self.add_port('OUT', 'to_output')
        self.params['dyn'] = {'tau':1000.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.SemRep = nx.DiGraph() # Uses networkx to easily handle graph structure.
    
    def reset(self):
        """
        """
        super(SEMANTIC_WM_P, self).reset()
        self.SemRep = nx.MultiDiGraph()
    
    def process(self):
        """
        """
        cpt_insts = self.inputs['from_conceptualizer']            
        if cpt_insts:
            for inst in cpt_insts:
                self.add_instance(inst)
        
        self.update_SemRep(cpt_insts) 
                
        if self.inputs['from_grammatical_WM_P']: # This should be done on the instances directly...
            # Note nodes and edges as expressed
            for name in self.inputs['from_grammatical_WM_P']['nodes']:
                self.SemRep.node[name]['expressed'] = True
            for name in self.inputs['from_grammatical_WM_P']['edges']:
                d = self.SemRep.get_edge_data(name[0], name[1])
                d['expressed'] = True
        
        self.outputs['to_grammatical_WM_P'] = self.gram_WM_P_output()
        
        # TD request for missing info
        self.outputs['to_visual_WM'] = self.vis_WM_output()
        if self.has_new_sem():
            self.outputs['to_cxn_retrieval_P'] = self.SemRep
        
        self.outputs['to_control'] = self.has_unexpressed_sem()
        
        self.update_activations()      
        self.prune()                    
            
    def update_SemRep(self, cpt_insts):
        """
        Updates the SemRep: Adds the nodes and edges needed based on the received concept instances.
        
        NOTE:
            - Does not handle the case of concept instance updating. Concepts cannot be updated (Monotonous growth of the SemRep)
            - SemRep carries the instance and the concept. The concept field is redundant, but is useful in order to be able to define
            SemMatch between SemRep graph and SemFrames (graphs needs to have same data key).
        """
        if cpt_insts:
            # First process all the instances that are not relations.
            for inst in [i for i in cpt_insts if not(isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA))]:
                if self.SemRep.has_node(inst.name):
                    continue
                self.SemRep.add_node(inst.name, cpt_inst=inst, concept=inst.content['concept'], frame=inst.frame, new=True, processed=[], expressed=False)
            
            # Then add the relations
            for rel_inst in [i for i in cpt_insts if isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA)]:
                node_from = rel_inst.content['pFrom'].name
                node_to = rel_inst.content['pTo'].name
                if self.SemRep.has_edge(node_from, node_to):
                    continue
                self.SemRep.add_edge(node_from, node_to, cpt_inst=rel_inst, concept=rel_inst.content['concept'], frame=inst.frame,  new=True, processed=[], expressed=False)
            
#            # Update concept frames
#            self.update_cpt_frames()
    
#    def update_cpt_frames(self):
#        """
#        For all the concept frames instances. If they have an 'IS' relation, propagate is_concept to frame.
#        """
#        cpt_rel_name = 'IS'
#        for u,v,d in [edge for edge in self.SemRep.edges(data=True)]:
#            if d['concept'].name == cpt_rel_name:
#                self.SemRep.node[u]['cpt_inst'].content = self.SemRep.node[v]['cpt_inst'].content.copy()
#                self.SemRep.node[u]['concept'] = self.SemRep.node[v]['concept']
            
    def gram_WM_P_output(self):
        """
        Returns the output to send to gram_WM_P.
        The signal sent to gram_WM_P contains the activation levels of the node and edge instance that so far have not been expressed.
        """
        output = {'nodes':{}, 'edges':{}}
        for n,d in self.SemRep.nodes(data=True):
            if not(d['expressed']):
                output['nodes'][n] = d['cpt_inst'].activity
        for u,v,d in self.SemRep.edges(data=True):
            if not(d['expressed']):
                output['edges'][(u,v)] = d['cpt_inst'].activity
        return output
    
    def vis_WM_output(self):
        """
        Returns the output to send to vis_WM. This output contains the TD attentional signal that can bias the 
        BU saliency.
        """
        output = None
        if not(self.inputs['from_grammatical_WM_P']) or not(self.inputs['from_grammatical_WM_P']['missing_info']):
            return output
        
        missing_info = self.inputs['from_grammatical_WM_P']['missing_info']
        
        cpt_schema_inst = self.find_instance(missing_info)
        var_name = cpt_schema_inst.trace.get('ref', '')
        self.outputs['to_output'] = {'missing_info':missing_info, 'var_name':var_name}
        output = cpt_schema_inst.trace['per_inst']
        return output
        
    def has_new_sem(self):
        """
        Returns true if there is at least 1 new element in the SemRep. False otherwise.
        """
        for n,d in self.SemRep.nodes(data=True):
            if d['new']:
                return True
        
        for u,v,d in self.SemRep.edges(data=True):
            if d['new']:
                return True
        return False
    
    def has_unexpressed_sem(self):
        """
        Returns true if there is at least 1 unexpresed node or relation in the SemRep. False otherwise.
        
        """
        for n,d in self.SemRep.nodes(data=True):
            if not(d['expressed']):
                return True
        return False
        
        for u,v,d in self.SemRep.edges(data=True):
            if d['expressed']:
                return True
        return False
        
    #######################
    ### DISPLAY METHODS ###
    #######################
    def show_state(self):
        from viewer import TCG_VIEWER
        TCG_VIEWER.display_semWM_state(self, file_type='png', show=True)
        
class SEMANTIC_WM_C(WM):
    """
    Comprehension version of the Semantic_WM.
    Testing some comprehension specific issues.
    Notes:
        - Testing the SemRep being a MutliDiGraph instead of simply a DiGraph.
        Might need to support multi-edges (competing edges).
    """
    def __init__(self, name='Semantic_WM_C'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_concept_LTM')
        self.add_port('IN', 'from_grammatical_WM_C')
        self.add_port('IN', 'from_control')
        self.add_port('OUT', 'to_WK_frame_WM')
        self.add_port('OUT', 'to_grammatical_WM_C')
        self.add_port('OUT', 'to_control')
        self.add_port('OUT', 'to_output')
        self.params['dyn'] = {'tau':1000.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.SemRep = nx.MultiDiGraph() # Uses networkx to easily handle graph structure.
    
    def reset(self):
        """
        """
        super(SEMANTIC_WM_C, self).reset()
        self.SemRep = nx.MultiDiGraph()
    
    def process(self):
        """
        """   
        cpt_insts = None        
        gram_activations = {}
        gram_input = self.inputs['from_grammatical_WM_C']
        if gram_input:
            gram_activations = gram_input['activations']
            instance_data  = gram_input.get('instances', None)
            if instance_data:
                SemFrame = instance_data['SemFrame']
                sem_map = instance_data['sem_map']
                cpt_schemas = self.inputs['from_concept_LTM']
                if cpt_schemas and SemFrame and sem_map:
                    cpt_insts  = self.instantiate_gram_cpts(SemFrame, sem_map, cpt_schemas)
   
        if cpt_insts:
            for inst in cpt_insts:
                self.add_instance(inst, 0.2)   
        
        self.convey_gram_activations(gram_activations) # NEED TO DEFINE WEIGHT IF THERE IS COMPETITION. DO THAT USING THE CONNECT WEIGHT
#        self.convey_WK_activations(WK_activations)
        self.update_activations()
        self.update_SemRep(cpt_insts)        
        self.prune()
    
    def instantiate_gram_cpts(self, SemFrame, sem_map, cpt_schemas):
        """
        Builds SemRep based on the received SemFrame.
        
        Args:
            - SemFrame (TP_SEMFRAME)
            - cpt_schemas ([CPT_SCHEMA])
        """            
        def find_cpt_inst(sem_frame_insts):
            """ Returns, if it exists, the cpt_inst whose sem_frame trace already contains one of the sem_frame_insts.
            """
            output = [inst for inst in self.schema_insts if not(inst.trace['sem_frame_insts'].isdisjoint(sem_frame_insts))]
            if len(output)>1:
                print self.t
                error_msg = 'There is more than one cpt_inst that map onto the same SemFrame element! %s' %str([o.name for o in output])
                raise ValueError(error_msg)
            elif len(output)==1:
                return output[0]
            else:
                return None
        cpt_insts = []
        name_table = {}

        """
        I need to recheck the mapping (here there is no mapping) since this is not production. So mapping is None. But
        there will be a mapping if I had feebback
        Expand the mapping: Given a frame and a preliminary mapping, can I find bigger mappings that contains the initial mapping.
        If so, expand mapping, move on with adding concept schemas.
        """
        def build_mapping(SemFrame, sem_map):
            """
            Find ways in wich the SemFrame can map onto the SemRep.
            For each ways, it adds to the SemRep the portion of its graph that is not contained in the SemRep.
            """
            pass
        
        for node in SemFrame.nodes:
            cpt_schema = self._find_cpt_schema(cpt_schemas, node.concept.name)
            sem_frame_insts = set([k for k,v in sem_map.iteritems() if node.name in v])
            old_cpt_inst = find_cpt_inst(sem_frame_insts)
            if old_cpt_inst:
                old_cpt_inst.trace['sem_frame_insts'].update(sem_frame_insts)
                name_table[node] = old_cpt_inst
            else:
                new_cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'cpt_schema':cpt_schema, 'sem_frame_insts':sem_frame_insts})
                name_table[node] = new_cpt_inst
                cpt_insts.append(new_cpt_inst)
        
        for edge in SemFrame.edges:
            cpt_schema = self._find_cpt_schema(cpt_schemas, edge.concept.name)
            sem_frame_insts = set([k for k,v in sem_map.iteritems() if edge.name in v])
            old_cpt_inst = find_cpt_inst(sem_frame_insts)
            if old_cpt_inst:
                old_cpt_inst.trace['sem_frame_insts'].update(sem_frame_insts)
            else:
                new_cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'cpt_schema':cpt_schema, 'sem_frame_insts':sem_frame_insts})
                new_cpt_inst.content['pFrom'] = name_table[edge.pFrom]
                new_cpt_inst.content['pTo'] = name_table[edge.pTo]
                cpt_insts.append(new_cpt_inst)
        return cpt_insts
        
    def instantiate_wk_cpts(self, wk_inputs, cpt_schemas):
        """
        Builds SemRep based on a wk_inputs.
        
        Args:
            - wk_inputs ([(WK_FRAME, mapping)])
            - cpt_schemas ([CPT_SCHEMA])
        """
        
        """
        I need to recheck the mapping. 
        Expand the mapping: Given a frame and a preliminary mapping, can I find bigger mappings that contains the initial mapping.
        If so, expand mapping, move on with adding concept schemas.
        """
        pass
    
    def convey_gram_activations(self, gram_activations):
        """
        SemRep instances receives external activations from the construction instances they are linked to.
        Notes:
            - This imposes that (1) the cpt_insts start with low activations. (2) the cxn instances are not deactivated once they are expressed (symmetric coop_links.)
        """
        if not(gram_activations):
            return
        for inst in self.schema_insts:
            for k, val in gram_activations.iteritems():
                act = 0
                if k in inst.trace['sem_frame_insts']:
                    act += val
                inst.activation.E += act # No normalization
    
    def convey_WK_activation(self, WK_activations):
        """SemRep instances receive external activations from the WK_frames instances they are linked to.
        Notes:
            - This imposes that (1) the cpt_insts start with low activations. (2) the Wk_frame are not deactivated once they are expressed.
        """
        pass

    def update_SemRep(self, cpt_insts):
        """
        Updates the SemRep: Adds the nodes and edges needed based on the receivd concept instances.
        
        NOTE:
            - Does not handle the case of concept instance updating. Concepts cannot be updated (Monotonous growth of the SemRep)
            - SemRep carries the instance and the concept. The concept field is redundant, but is useful in order to be able to define
            SemMatch between SemRep graph and SemFrames (graphs needs to have same data key).
        """
        if cpt_insts:
            # First process all the instances that are not relations.
            for inst in [i for i in cpt_insts if not(isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA))]:
                if self.SemRep.has_node(inst.name):
                    continue
                self.SemRep.add_node(inst.name, cpt_inst=inst, concept=inst.content['concept'], frame=inst.frame, new=True, processed=[], expressed=False)
            
            # Then add the relations
            for rel_inst in [i for i in cpt_insts if isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA)]:
                node_from = rel_inst.content['pFrom'].name
                node_to = rel_inst.content['pTo'].name
                if self.SemRep.has_edge(node_from, node_to):
                    continue
                self.SemRep.add_edge(node_from, node_to, cpt_inst=rel_inst, concept=rel_inst.content['concept'], frame=inst.frame,  new=True, processed=[], expressed=False)
            
            #Send the new state to output.
            self.outputs['to_output'] = True

    def update_mapping(self, sem_input_frame, sem_input_mapping):
        """
        Updates the mapping of a sem_input to take into account the possible change of state
        that took place in Semantic_WM.
        """
        pass
        

    def _find_cpt_schema(self, cpt_schemas, cpt_name):
            """Returns, if it exists, the cpt_schema whose name matches cpt_name
            """
            output = [schema for schema in cpt_schemas if schema.name == cpt_name]
            if len(output)>1:
                error_msg = 'There is more than one cpt_schema matches the concept name %s' %cpt_name
                raise ValueError(error_msg)
            elif not(output):
                error_msg = 'There are is cpt_schema that matches the concept name %s' %cpt_name
                raise ValueError(error_msg)
            else:
                return output[0]
        
    #######################
    ### DISPLAY METHODS ###
    #######################
    def show_state(self):
        from viewer import TCG_VIEWER
        TCG_VIEWER.display_semWM_state(self, file_type='png', show=True)

###################
### GRAMMAR LTM ###
###################
class GRAMMATICAL_LTM(LTM):
    """
    """
    def __init__(self, name='Grammatical_LTM'):
        LTM.__init__(self, name)
        self.grammar = None
        self.add_port('OUT', 'to_cxn_retrieval_P')
        self.add_port('OUT', 'to_cxn_retrieval_C')
        self.params['init_act'] = 0.5 #The initial activation value for cxn schema.
    
    def initialize(self, grammar):
        """
        Initilize the state of the GRAMMATICAL LTM with cxn_schema based on the content of grammar.
        Args:
            - grammar (GRAMMAR): A TCG grammar
        """
        self.grammar = grammar
        for cxn in grammar.constructions:
            preference = 1
            if cxn.preference:
                preference = cxn.preference
            new_cxn_schema = CXN_SCHEMA(cxn, self.params['init_act']*preference)
            self.add_schema(new_cxn_schema)

    def process(self):
        """
        """
        self.outputs['to_cxn_retrieval_P'] =  self.schemas
        self.outputs['to_cxn_retrieval_C'] =  self.schemas
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(GRAMMATICAL_LTM, self).get_info()
        data['params'] = self.params
        return data
        
##################
### PRODUCTION ###
##################
class GRAMMATICAL_WM_P(WM):
    """
    TO DO!!
    
        - I AM NOT USING CXN GROUPS!...
    """
    def __init__(self, name='Grammatical_WM_P'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_cxn_retrieval_P')
        self.add_port('IN', 'from_control')
        self.add_port('IN', 'from_phonological_WM_P')
        self.add_port('OUT', 'to_semantic_WM')
        self.add_port('OUT', 'to_phonological_WM_P')
        self.add_port('OUT', 'to_output')
        self.params['dyn'] = {'tau':30.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.3}
        self.params['C2'] = {'coop_weight':1.0, 'comp_weight':-4.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0, 'deact_weight':0.0, 'prune_threshold':0.3, 'confidence_threshold':0.8, 'sub_threshold_r':0.8, 'refractory_period':10}
        self.params['style'] = {'activation':1.0, 'sem_length':0, 'form_length':0, 'continuity':0} # Default value, updated by control. 
        self.refractory_period = 10
        self.time_to_next_prod = 0
        
    def reset(self):
        """
        """
        super(GRAMMATICAL_WM_P, self).reset()
        self.refractory_period = 10
        self.time_to_next_prod = 0    
        
    #####################
    ### STATE UPDATE  ###
    #####################   
    def process(self):
        """
        """
        sem_input = self.inputs['from_semantic_WM'] # I need to tie the activity of the cxn_instances to that of the SemRep. (Would be nicer to have coop-links across WMs.)
        new_cxn_insts= self.inputs['from_cxn_retrieval_P']
        ctrl_input = self.inputs['from_control']
        phon_input = self.inputs['from_phonological_WM_P']
        if new_cxn_insts:
            self.add_new_insts(new_cxn_insts)            
                
        self.convey_sem_activations(sem_input)
        self.update_activations()
        self.prune()

        # Apply memory limitations
        wm_limit = self.limit_memory()
        
        if ctrl_input and ctrl_input['produce']:
            self.params['style'] = ctrl_input['params_style']
            try_produce = self.apply_pressure(ctrl_input['pressure'], option=1)
            if try_produce or wm_limit: # If the limit in wm has been reached the system tries to produce.
                if self.time_to_next_prod<=0:
                    output = self.produce_form(sem_input, phon_input)
                    self.time_to_next_prod = self.params['C2']['refractory_period']
                
                    if output:
                        self.outputs['to_phonological_WM_P'] = output['phon_WM_output']
                        self.outputs['to_semantic_WM'] =  output['sem_WM_output']
                        self.outputs['to_output'] = output['to_output']
                    else:
                        self.outputs['to_phonological_WM_P'] = []
                else:
                    self.time_to_next_prod -= 1
    
    def add_new_insts(self, new_insts):
        """
        Args:
            new_insts ([{"cxn_inst":CXN_SCHEMA_INST, "match_qual":FLOAT}]): List of construction instances to be added to grammatical working memory.
        """
        for inst in new_insts:
            match_qual = inst["match_qual"]
            act = inst["cxn_inst"].activity
            new_inst = inst["cxn_inst"]
            self.add_instance(new_inst, act*match_qual)
            self.cooperate(new_inst)
            self.compete(new_inst)
    
    def convey_sem_activations(self, sem_input, normalization=True, use_groups=[1]):
        """
        Args:
            - sem_input (DICT): Unexpressed semantic nodes and relations. Used to compute sem_length score.
            - normalization (BOOL): If True, the propagation of the activation is normalized by the number of nodes and edges covered.
            - use_groups ([INT]): only convey activations to cxn instnaces of group in use_groups.
        
        If use_groups = []
            A construction receives activations from semantic working memory if :
                - 1. It's semframe covers at least one semrep node that has not yet been 
            expressed. 
                - 2. The SemFrame node that covers is linked to a TP_PHON
            This can be modified by changing the formula for 
            
        """
        for inst in self.schema_insts:
            cover_nodes = inst.covers['nodes']
            cover_edges = inst.covers['edges']
            
            act_node_phon = 0.0
            act_node_slot = 0.0
            act_node_none = 0.0
            act_edge = 0.0
            count_node_phon = 0
            count_node_slot = 0
            count_node_none = 0
            count_edge = 0
            # Compute semantic node activation
            for node in sem_input['nodes']:
                inst_node = next((k for k,v in cover_nodes.items() if v==node), None) # Instances covers the node through sf_node
                if inst_node:
                    inst_form = inst.content.node2form(inst_node)
                    if isinstance(inst_form, construction.TP_PHON): # sf_node is linked to a TP_PHON form or does not have a symlink.. (formalization)                      
                        act_node_phon += sem_input['nodes'][node]
                        count_node_phon += 1
                    elif inst_form == None: # sf_node does not have a symlink.. (formalization)    
                        act_node_none += sem_input['nodes'][node]
                        count_node_none += 1
                    else: # sf_node linked to a slot.
                        act_node_slot += sem_input['nodes'][node]
                        count_node_slot += 1
                        
            # Compute semantic relation activation
            for edge in sem_input['edges']:
                inst_edge = next((k for k,v in cover_edges.items() if v==edge), None)
                if inst_edge:
                    act_edge += sem_input['edges'][edge] # Edge always propagate their activation since they are obligatory formalized in a TCG cxn.
                    count_edge +=1
            
            # Propagate activation
            if use_groups:
                W_1 = 1.0 # Weight of activation propagation to in groups
                W_2 = 1.0 # Weight of activation propagation to out groups
                if inst.content.group in use_groups:
                    node_weight = 1.0
                    edge_weight = 1.0
                    act_node = act_node_phon + act_node_none + act_node_slot # I propagate everything
                    count_node = count_node_phon + count_node_none + count_node_slot
                    act = node_weight*act_node + edge_weight*act_edge
                    act *= W_1
                    count = node_weight*count_node + edge_weight*count_edge
                else:
                    node_weight = 1.0
                    edge_weight = 1.0
                    act_node = act_node_phon + act_node_none + act_node_slot # I propagate everything
                    count_node = count_node_phon + count_node_none + count_node_slot
                    act = (node_weight*act_node + edge_weight*act_edge)*W_2
                    act *= W_2
                    count = node_weight*count_node + edge_weight*count_edge
            else:
                #######################################
                ### CHANGE IF WANT TO USE OTHER POLICY.
                node_weight = 1.0
                edge_weight = 0.0
                act_node = act_node_phon + act_node_none # I propagate activation to lexicalized nodes.
                count_node = count_node_phon + count_node_none
                act = node_weight*act_node + edge_weight*act_edge
                count = node_weight*count_node + edge_weight*count_edge
            
            # Normalization
            if normalization and count>0:
                act = act/count # normalizing removes advantage for constructions that cover more content.
            inst.activation.E += act
            
    ###############################
    ### COOPERATIVE COMPUTATION ###
    ###############################
    def cooperate(self, new_inst):        
       """
       For each cxn instance already active in GrammaticalWM, checks whether it can enter in cooperation with the new_inst.
       
       Args:
           - new_inst (CXN_SCHEMA_INST): A cxn schema instance (that was just instantiated in GrammaticalWM)
          
       Notes:
           - For now, the match quality (match_qual) is still binary so it is used to define or not a cooperative functional link.
           - This should be updated to use match_qual to account for the strength of the cooperative functional link created.
       """
       for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM_P.match(new_inst, old_inst)
               if match["match_cat"] == 1:
                   for match_qual, link in match["links"]:
                       if match_qual > 0:
                           self.add_coop_link(inst_from=link["inst_from"], port_from=link["port_from"], inst_to=link["inst_to"], port_to=link["port_to"], qual=match_qual)
    
    def compete(self, new_inst):
        """
        For each cxn instance already active in GrammaticalWM, checks whether it competes with the new_inst
        
        Args:
           - new_inst (CXN_SCHEMA_INST): A cxn schema instance (that was just instantiated in GrammaticalWM)
        """
        for old_inst in self.schema_insts:
           if new_inst != old_inst:
               match = GRAMMATICAL_WM_P.match(new_inst, old_inst)
               if match["match_cat"] == -1:
                   self.add_comp_link(inst_from=new_inst, inst_to=old_inst)
        
#        # Possible addition...
#        # Construction that correspond to 2 different hypotheses regarding which slot the new isnt should link to compete. 
#        # This is might be problematic. See my notes in notebook.
#        for inst1 in self.schema_insts:
#            for inst2 in self.schema_insts:
#                if inst1 != inst2:
#                    link1 = [l for l in self.coop_links if (l.inst_from == new_inst) and (l.inst_to == inst1)]
#                    link2 = [l for l in self.coop_links if (l.inst_from == new_inst) and (l.inst_to == inst2)]
#                    if link1 and link2:
#                        self.add_comp_link(inst_from=inst1, inst_to=inst2)
    
    @staticmethod
    def overlap(inst1, inst2):
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
    def comp_link(inst_1, inst_2, SR_node):
        """
        Checks whether inst1 and inst2 are in competition if they overlap on a SemRep node.
        
        Args:
            - inst1 (CXN_SCHEMA_INST): A cxn instance
            - inst2 (CXN_SCHEMA_INST): A cxn instance
            - SR_node (): SemRep node on which both instances overlap
        
        Notes:
            The case of an overlap on an edge is handled directly by the match function.
        """
        competition = False
        cxn_1 = inst_1.content
        sf_1 = [cxn_1.find_elem(k) for k,v in inst_1.covers["nodes"].iteritems() if v == SR_node][0] # Find SemFrame node that covers the SemRep node
        cxn_2 = inst_2.content
        sf_2 = [cxn_2.find_elem(k) for k,v in inst_2.covers["nodes"].iteritems() if v==SR_node][0] # Find SemFrame node that covers the SemRep node
        
        cond1 = (sf_1.name not in cxn_1.SymLinks.SL) or isinstance(cxn_1.node2form(sf_1), construction.TP_PHON) # cxn_1 formalizes the node entity
        cond2 = (sf_2.name not in cxn_2.SymLinks.SL) or isinstance(cxn_2.node2form(sf_2), construction.TP_PHON) # cxn_2 formalizes the node entity
        
        if cond1 and cond2:
            competition = True
        return competition
        
    @staticmethod    
    def coop_link(inst_p, inst_c, SR_node):
        """
        Returns functional link between cooperating construction if it exists as well as quality of match (match_qual).
        
        Args:
            - inst_p (CXN_SCHEMA_INST): A cxn instance (parent)
            - inst_c (CXN_SCHEMA_INST): A cxn instance (child)
            - SR_node (): SemRep node on which both instances overlap
        
        Notes:
            - For now match_qual is actualy categorical!
        """
        cxn_p = inst_p.content
        sf_p = [cxn_p.find_elem(k) for k,v in inst_p.covers["nodes"].iteritems() if v == SR_node][0] # Find SemFrame node that covers the SemRep node
        cxn_c = inst_c.content
        sf_c = [cxn_c.find_elem(k) for k,v in inst_c.covers["nodes"].iteritems() if v==SR_node][0] # Find SemFrame node that covers the SemRep node
             
        
        # Type constraints (Obligatory)
        syn1 = (sf_p.name in cxn_p.SymLinks.SL) and isinstance(cxn_p.node2form(sf_p), construction.TP_SLOT) # sf_p is linked to a slot in cxn_p
        sem1 = sf_c.head # sf_c is a head node
        
        # Metric constraints (Qualitative)
        if syn1 and sem1:
            slot_p = cxn_p.node2form(sf_p)
            syn2 = cxn_c.class_match(slot_p) # Syntactic match
            sem2 = sf_c.concept.match(sf_p.concept) # Semantic match (Light semantics)
            link = {"inst_from": inst_c, "port_from":inst_c.find_port("output"), "inst_to": inst_p, "port_to":inst_p.find_port(slot_p.order)}
            # For now syn2 and sem2 are treated as categorical, but should be anlalogical.
            if syn2 and sem2:
                match_qual = 1
            else:
                match_qual = 0
            return (match_qual, link)
        return None
    
    @staticmethod
    def match(inst1, inst2):
        """
        Args:
            - inst1 (CXN_SCHEMA_INST): A cxn instance
            - inst2 (CXN_SCHEMA_INST): A cxn instance
            
        IMPORTANT NOTE: IT IS NOT CLEAR WHY THE ABSENCE OF LINK SHOULD NECESSARILY MEAN COMPETITION....
            Think about the case of a lexical cxn LEX_CXN linking to a Det_CXN itself linking to a SVO_CXN, we don't want LEX_CXN to enter in competition with
            SVO_CXN, even though they can't link since the LEX_CXN doesn't match the class restriction of SVO_CXN (LEX_CXN is N, not NP).
        
        """
        match_cat = 0
        links = []
        if inst1 == inst2:
           match_cat = 0 # CHECK THAT
           return {"match_cat":match_cat, "links":links}
         
        overlap = GRAMMATICAL_WM_P.overlap(inst1, inst2)
        
        #Check that relation exists
        if not(overlap):
            match_cat = 0
            return {"match_cat":match_cat, "links":links}
        
        #Check competition
        if overlap["edges"]: # Syntactic competition
            match_cat = -1
            return {"match_cat":match_cat, "links":links}
        else:
            for n in overlap["nodes"]:
                competition = GRAMMATICAL_WM_P.comp_link(inst1, inst2, n)
                if competition:
                    match_cat = -1
                    return {"match_cat":match_cat, "links":links}
        
        #Check cooperation
        flag1 = False
        flag2 = False
        for n in overlap["nodes"]:
            link = GRAMMATICAL_WM_P.coop_link(inst1, inst2, n)
            if link:
                flag1 = link[0]==1
                links.append(link)
            link = GRAMMATICAL_WM_P.coop_link(inst2, inst1, n)
            if link:
                flag2  = link[0]==1
                links.append(link)
        
        if flag1 and flag2:
            print "LOOP %s %s" %(inst1.name, inst2.name) # Warns that there are direct loops.
            
        if links:
            match_cat = 1
        else: 
            match_cat = 0 # since we have already ruled out the possibilities of competition
        return {"match_cat":match_cat, "links":links}
        
    ##################################
    ### LINGUISTIC FORM PRODUCTION ###
    ##################################
    def produce_form(self, sem_input, phon_input):
        """
        Generates the meanining to form transduction based on the current C2 state.
        
        Args:
            - sem_input (DICT): Unexpressed semantic nodes and relations. Used to compute sem_length score.
            - phon_input ([STR]): Sequence of phon content. Used to compute continuity score
       
       Notes: 
            - There is an issue with the fact that it takes 2 steps for the fact that part of the SemRep has been expressed gets
        registered by the semantic_WM. This leads to the repetition of the same assemblage twice.
            - Need to clarify how the score_threshold is defined.
            - Note that the only reason I don't just take the 1 winner above threshold is because of the issue of having multiple none overlapping assemblages.
            A better solution might be to return all the assemblages that have a different TOP instance (but then this would only work if I terminate all the competition at the read-out time.)
            - Might want to revisit assemble.
            - Need to think about whether or not read-out means terminating all the competitions.
            Make sure to revisit all the different options below.
        """  
#        score_threshold = self.params['style']['activation']*self.params['C2']['confidence_threshold'] + self.params['style']['sem_length'] + self.params['style']['form_length'] + self.params['style']['continuity'] # Uncomment to use confidence threshold

#        self.end_competitions() #When production is triggered, a decision is forced for all the competitions.
        assemblages = self.assemble()
        data = []
        winner_found = False
        if assemblages:
            phon_WM_output = []
            sem_WM_output = {'nodes':[], 'edges':[], 'missing_info':None}
            winner_dat, score = self.get_winner_assemblage(assemblages, sem_input, phon_input)
            if winner_dat: # LOOK INTO THIS!!! THIS IS AN IMPORTANT STEP
                self.set_winners(winner_dat[0])

#            while winner_dat and score >= score_threshold: # Uncomment to use confidence threshold and recursive reading
#            if winner_dat and score >= score_threshold: # Uncomment to use confidence threshold without recursive reading
                winner_found = True
                (winner_assemblage, phon_form, missing_info, expressed, eq_inst, a2i_map, insts_used) = winner_dat
                phon_WM_output.extend(phon_form)
                sem_WM_output['nodes'].extend(expressed['nodes'])
                sem_WM_output['edges'].extend(expressed['edges'])
                sem_WM_output['missing_info'] = missing_info
                for inst in insts_used:
                    inst.done = True # REMOVE NOT NECESSARY ANYMORE
#                assemblages.remove(winner_assemblage)
                
                # Save winner assemblage to state
                partial_readout = False if missing_info == None else True
                data.append({'t':self.t, 'assemblage':winner_assemblage.copy(), 'phon_form':phon_form[:], 'eq_inst':eq_inst.content.copy()[0], 'a2i_map':a2i_map.copy(), 'expressed':expressed.copy(), 'partial_readout':partial_readout, 'insts_used':insts_used})
                
                # Option1: Replace the assemblage by it's equivalent instance
#                self.replace_assemblage(winner_assemblage)
                
                # Option2: Dismantle the assemblage by removing all the coop_link it involves and setting all composing instances activatoins to confidence_threshold.
#                self.dismantle_assemblage(winner_assemblage)
                
                 # Option3: Removes coop links + adds the equivalent instance.
#                self.dismantle_assemblage2(winner_assemblage)
                
                # Option4: Keeps all the coop_links but bumps down the activation values of all the instances that are part of the winner assemblage.
#                self.reset_assemblage(winner_assemblage)
                
#                #Option5: Sets all the instances in the winner assembalge to subthreshold activation. Sets all the coop_weightsto 0. So f-link remains but inst participating in assemblage decay unless they are reused.
#                self.post_prod_state(winner_assemblage)
                
                #Option6: Sets all the coop_weights to 0. So f-link remains but inst participating in assemblage decay unless they are reused.
#                self.deactivate_coop_weigts()
                
#                for assemblage in assemblages:
#                    assemblage.update_activation()
#                    
#                if assemblages and not(missing_info): # For now I added the caveat that if one read-out an incomplete assemblage then no other assemblage could be read afterwards. THIS SHOULD BE MODIFIED
#                    winner_dat, score = self.get_winner_assemblage(assemblages, sem_input, phon_input)
#                else:
#                    winner_dat = None
            
            if winner_found:
                return {'phon_WM_output':phon_WM_output, 'sem_WM_output':sem_WM_output, 'to_output':data}
            else:
                return None
        
        return None

    def get_winner_assemblage(self, assemblages, sem_input, phon_input):
        """
        Returns the winner assemblage and its equivalent instances.
        
        Args: 
            - assemblages ([ASSEMBLAGE])
            - sem_input (DICT): Unexpressed semantic nodes and relations. Used to compute sem_length score.
            - phon_input ([STR]): Sequence of phon content. Used to compute continuity score
        
        Return:
            - (assemblage_dat, score) if a winner if found, None otherwise.
            
        Notes:
            - Need to discuss the criteria that come into play in choosing the winner assemblages.
            - As for the SemRep covered weight, the constructions should receive activation from the SemRep instances. 
            This could help directly factoring in the SemRep covered factor.   
            - For the continuity, this requires an access to what was posted to phonWM. Cannot be done simply by reactivating assemblages, at least
            in their current form, since they could be expanded by adding elements that would change the order of phons.
        
        """
        w1 = self.params['style']['activation'] # Activation weight
        w2 = self.params['style']['sem_length'] # SemRep covered weight
        w3 = self.params['style']['form_length'] # SynForm length weight  
        w4 = self.params['style']['continuity'] # Utterance continuity weight  
        winner_dat = None
        scores = {'sem_length':[], 'form_length':[], 'utterance_continuity': [], 'continuity': [], 'eq_insts':[]}
            
        # Computing the equivalent instance for each assemblage.
        # For each assemblage stores the values of relevant scores.
        assemblages_dat = [] 
        for assemblage in assemblages:
            (phon_form, missing_info, expressed, eq_inst, a2i_map, insts_used) = GRAMMATICAL_WM_P.form_read_out(assemblage) # In order to test for continuity, I have to read_out every assemblage. 
            assemblages_dat.append((assemblage, phon_form, missing_info, expressed, eq_inst, a2i_map, insts_used))               
            sem_length_nodes = len([sf_node for sf_node, semrep_node in eq_inst.covers['nodes'].iteritems() if (semrep_node in sem_input['nodes'])]) # Only counts nodes that have NOT already been expressed.
            sem_length_edges = len([sf_edge for sf_edge, semrep_edge in eq_inst.covers['edges'].iteritems() if semrep_edge in sem_input['edges']]) # Only counts edges that have NOT already been expressed. 

            sem_length = sem_length_nodes + sem_length_edges          
            form_length = len(phon_form)         
            continuity = 0
            for i in range(1, min(len(phon_form)+1, len(phon_input)+1)):
                if phon_form[:i] == phon_input[-1*i:]:
                    continuity = len(phon_form[:i])
                    
            scores['sem_length'].append(sem_length)
            scores['form_length'].append(form_length)
            scores['continuity'].append(continuity)
            scores['eq_insts'].append(eq_inst)
            
        # Normalize the scores
        max_sem_length = max(scores['sem_length'])
        max_form_length = max(scores['form_length'])
        max_continuity = max(scores['continuity'])
        if max_sem_length==0: # Doesn't return anything if the assemblage doesn't cover unexpressed info.
            output = (None, None)
            return output
        else:
            scores['sem_length'] = [s/max_sem_length for s in scores['sem_length']]
        
        if max_form_length == 0:
            scores['form_length'] = [0 for s in scores['form_length']]
        else:
            scores['form_length'] = [s/max_form_length for s in scores['form_length']]
        
        if max_continuity == 0:
            scores['continuity'] = [0 for s in scores['continuity']]
        else:
            scores['continuity'] = [s/max_continuity for s in scores['continuity']]
        
        # Finding winner assemblage
#        score_threshold = self.params['style']['activation']*self.params['C2']['confidence_threshold'] + self.params['style']['sem_length'] + self.params['style']['form_length'] + self.params['style']['continuity']
        winner_score = None
        
        for i in range(len(assemblages)):
            score = w1*assemblages[i].activation + w2*scores['sem_length'][i] + w3*(1-scores['form_length'][i]) + w4*scores['continuity'][i] # Scoring assemblage
            # change if winner needs to express a form.
            has_form = True #scores['form_length'][i] != 0
            if has_form: # An assembalge is considered only if it has a form to produce.
                if not(winner_score):
                    winner_score = score
                    winner_dat = assemblages_dat[i]
                if score>winner_score:
                    winner_score = score
                    winner_dat = assemblages_dat[i]
#        if winner_score < score_threshold:
#            return (None, None)
        output = (winner_dat, winner_score)
        return output
 
#    def replace_assemblage(self, assemblage):
#        """
#        Replace all the construction instances contained in the assemblage by the assemblage equivalent cxn_inst.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        eq_inst = GRAMMATICAL_WM_P.assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.params['C2']['confidence_threshold'])
#        for inst in assemblage.schema_insts:
#            inst.alive = False
#        self.add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
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
#            inst.set_activation(self.params['C2']['confidence_threshold'])
#    
#    def dismantle_assemblage2(self, assemblage):
#        """
#        Removes all the cooperation links involving instances that are part of the assemblages. Sets the activation of all the instances 
#        that are part of the assemblage to confidence_threshold.
#        Adds the assemblage equivalent cxn instance to the working memory.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        eq_inst = GRAMMATICAL_WM_P.assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.params['C2']['confidence_threshold'])
#        
#        self.remove_coop_links(inst_from=assemblage.schema_insts, inst_to=assemblage.schema_insts)
#        for inst in assemblage.schema_insts:
#            inst.set_activation(self.params['C2']['confidence_threshold'])
#        
#        self.add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
#    
#    def reset_assemblage(self, assemblage):
#        """
#        Resets the activation of all the instances that are part of the assemblage below confidence threshold.
#        Adds the assemblage equivalent cxn instance to the working memory.
#        Args:
#            - assemblage (ASSEMBLAGE)
#        """
#        r = 0.9
#        eq_inst = GRAMMATICAL_WM_P.assemblage2inst(assemblage)
#        # Sets the activation below confidence threshold so that it is not re-used right away. 
#        eq_inst.set_activation(self.params['C2']['confidence_threshold']*r)
#
#        for inst in assemblage.schema_insts:
#            inst.set_activation(self.params['C2']['confidence_threshold']*r)
#        
#        self.add_new_insts([{"cxn_inst":eq_inst, "match_qual":1}])
    
    def post_prod_state(self, winner_assemblage):
        """
        Sets the grammatical state after production given a winner assemblage.
        If I use the option to not produce a winner if no assemblage covers any new SemRep nodes, don't need to set_subthreshold.
        Except for the fact that if I don't there is repetition due to the lag between production of assemblage and registering in semWM that some elements have been expressed.
        In the new version where winner assemblages are read recursively until  there are no more winners, I need to use set_subthreshold, otherwise the same winner will be picke again.
        """
        self.set_subthreshold(winner_assemblage.schema_insts)
        self.set_winners(winner_assemblage)
        self.deactivate_coop_weigts()
#        self.deactivate_coop_weigts2(winner_assemblage)
#        self.end_competitions()
        
    def set_subthreshold(self, insts):
        """
        Sets the activation of all the instances in insts to r*confidence_threshold where r= self.params['C2']['sub_threshold_r']
        
        Args:
            - insts ([CXN_INST])
            
        Notes:
            - If the score of the assemblage is not just the avereage cxn inst activation, the value needs to be place low enough
            so that the system does not repeat the same utterance twice. 
        """
        r= self.params['C2']['sub_threshold_r']
        for inst in insts:
            inst.set_activation(r*self.params['C2']['confidence_threshold'])
            
    def deactivate_coop_weigts(self):
        """
        Sets all the coop_links to weight = self.params['C2']['deact_weight']
        """
        for coop_link in self.coop_links:
            coop_link.weight = self.params['C2']['deact_weight']
                
    def deactivate_coop_weigts2(self, assemblage, deact_weight=0.0):
        """
        Sets all the coop_links that are associated with an instance in assemblage to weight = deact_weight
        
        Args:
            - assemblage (ASSEMBLAGE)
            - deact_weight (FLOAT)
        """
        for coop_link in self.coop_links:
            if (coop_link.inst_from in assemblage.schema_insts) or (coop_link.inst_to in assemblage.schema_insts):
                coop_link.weight = deact_weight
    
    def set_winners(self, winner_assemblage):
        """
        Kills all the instances that are in competition with an instances that has been chosen in a winner assemblage.
        """
        winner_insts = winner_assemblage.schema_insts
        for link in self.comp_links:
            if link.inst_from in winner_insts:
                link.inst_to.alive = False
            if link.inst_to in winner_insts:
                link.inst_from.alive = False
        self.prune()
    
    def apply_pressure(self, pressure, option=0):
        """
        Tests various ways to apply time pressure.
        """
        if option==0: # Do nothing
            try_produce = True
        elif option == 1: # Simply trigger production when pressure reaches 1.
            try_produce = pressure>=1
        elif option == 2: #Applies pressure by ramping up C2
            for link in [l for l in self.coop_links if l.weight != 0]: # Make sure not to reactivate old weights.
                link.update_weight(self.params['C2']['coop_weight'] + self.params['C2']['coop_weight']*pressure)
            for link in self.comp_links:
                link.update_weight(self.params['C2']['comp_weight'] + self.params['C2']['comp_weight']*pressure)  
            try_produce = True     
        else:
            error_msg = 'Invalid apply pressure option'
            raise ValueError(error_msg)
        
        return try_produce
    
    ##################
    ### ASSEMBLAGE ###
    ##################    
    def assemble(self):
        """
        Returns the set of all the assemblages ([ASSEMBLAGE]) that can be built given the current state of the GrammaticalWM.
        
        Notes:
            - WHAT ABOUT THE CASE WHERE THERE STILL IS COMPETITION GOING ON?
            - NOTE THAT IN THE CASE OF MULTIPLE TREES GENERATED FROM THE SAME SET OF COOPERATION... THERE IS MAXIMUM SPANNING TREE. IS THIS IS THE ONE THAT SHOULD BE CONSIDERED?
        
        """
        inst_network = GRAMMATICAL_WM_P.build_instance_network(self.schema_insts, self.coop_links)
        tops = [(n,None) for n in inst_network.nodes() if not(inst_network.successors(n))]
        
        assemblages = []
        for t in tops:
            results = []
            frontier = [t]
            assemblage = ASSEMBLAGE()
            self.get_trees(frontier, assemblage, inst_network, results)
            assemblages += results
        
        # Compute assemblage activation values
        for assemblage in assemblages:
            assemblage.update_activation()
        
        return assemblages
        
    @staticmethod
    def build_instance_network(schema_insts, coop_links):
        """
        Creates a NetworkX directed graph whose nodes are of the instances (type='instance') and their ports (type='port'), 
        and the edges link the instances to the ports (type='inst2port') or the ports to the instances (coop_link) (type='port2inst')
    
        Args:
            - schema_insts ([SCHEMA_INST]): Set of schema instances
            - coop_links ([COOP_LINK]): Set of cooperation links defined between the schema instants
        
        Requires:
            - NetworkX
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

    def get_trees(self, frontier, assemblage, graph, results):
        """
        For a given instance network (generated by build_instance_network) defined as a directed graph, returns all the sub-trees each sub-tree
        defining an assemblage.
        (Recursive function)
        
        Args:
            - frontier (): Frontier of the search space.
            - assemblage (ASSEMBLAGE): 
            - graph (NetworkX Digraph): Generated by build_instance_network
            - results ([ASSEMBLAGE]): Recursively stores the assemblages (sub-trees)
        
        Notes:
            - "Un-superpose" the trees!
            - DOES NOT HANDLE THE CASE WHERE THERE STILL IS SOME COMPETITION GOING ON.
                NOTE: I think it does...
            - ALSO, it returns also sub-optimal trees. (Not only the tree that contains all the cooperating instances in the WM).
        """
        new_frontiers = [[]] # Each frontier correspond to a possible choice between multiple cooperation options to a same port.
        
        for node, link in frontier:
            # Update assemblage
            assemblage.add_instance(node)
            if link:
                assemblage.add_link(link)
            
            # For each element in the frontier, try to expand the tree.
            ports = graph.predecessors(node)
            for port in ports:
                children = graph.predecessors(port) # A port can be linked to multiple children, each representing a different hypothesis.
                updated_frontiers = []
                if not(children):
                    pass
                else:
                    for child in children:
                        flag =  child in assemblage.schema_insts
                        if not(flag):
                            link = self.find_coop_links(inst_from=child, inst_to=node, port_from=child.find_port("output"), port_to=port)
                            for f in new_frontiers:
                                updated_frontiers.append(f[:] + [(child, link[0])])
                    new_frontiers = updated_frontiers # Wrong indentation. Not handling frontiers properly.
        if new_frontiers == [[]]:
            results.append(assemblage)
        else:
            for a_frontier in new_frontiers:
                self.get_trees(a_frontier, assemblage.copy(), graph, results)
                
    @staticmethod
    def assemblage2inst(assemblage):
        """
        For a given construction instance assemblage, returns 
            (1) the instance equivalent to the assemblage by Unification.
            (2) a DICT mapping the name of the TP_ELEM of the assemblage onto the TP_ELEM of the eq_inst.
            This mapping allows to compute direct relations between the structure of the assemblage and the compact equivalent instance form.
            The dictionary also provides (for convenience) the names of the TP_ELEM for each instance in the assemblage.
        
        Args:
            - assemblage (ASSEMBLAGE): An construction instance assemblage
        """
        new_assemblage = assemblage.copy()
        coop_links = new_assemblage.coop_links
        a2i_map = {'sem_map':{}, 'syn_map':{}}
        if coop_links: # not a trivial assemblage composed of a single instance.
            while len(coop_links)>0:
                (new_assemblage, new_cxn_inst, a2i_map) = GRAMMATICAL_WM_P.reduce_assemblage(new_assemblage, new_assemblage.coop_links[0], a2i_map)
                coop_links = new_assemblage.coop_links
            eq_inst = new_assemblage.schema_insts[0]
        else:
            inst = new_assemblage.schema_insts[0] #It would be best to make a copy(?)
            #Trivial mapping onto itself
            a2i_map['sem_map'] = dict([(sem_elem.name, sem_elem.name) for sem_elem in inst.content.SemFrame.nodes + inst.content.SemFrame.edges])
            a2i_map['syn_map'] = dict([(syn_elem.name, syn_elem.name) for syn_elem in inst.content.SynForm.form])
            eq_inst = inst
        eq_inst.activity = assemblage.activation
        return (eq_inst, a2i_map)
      
    @staticmethod      
    def reduce_assemblage(assemblage, coop_link, a2i_map):
        """
        Returns a new, reduced, assemblage in which the instances cooperating (as defined by 'coop_link') have been combined.
        
        Args:
            - assemblage (ASSEMBLAGE): A construction instance assemblage.
            - coop_link (COOP_LINK): A cooperation link belonging to the assemblage.
            - a2i_map (DICT): assemblage2instance name mapping to be updated
        """
        inst_p = coop_link.inst_to
        inst_c = coop_link.inst_from
        connect = coop_link.connect
        
        (new_cxn_inst, port_corr, a2i_map) = GRAMMATICAL_WM_P.combine_schemas(inst_p, inst_c, connect, a2i_map)
        
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
        
        return (new_assemblage, new_cxn_inst, a2i_map)
    
    @staticmethod
    def combine_schemas(inst_to, inst_from, connect, a2i_map):
        """
        Returns a new cxn_instance and the mapping between inst_to and inst_from ports to new_cxn_inst ports.
        
        Args:
            - inst_to (CXN_SCHEMA_INST):
            - inst_from (CXN_SCHEMA_INST):
            - connect (CONNECT): A CONNECT object associated with a cooperation link between inst_to and inst_from.
            - a2i_map (DICT): assemblage2instance name mapping to be updated.
        """
        inst_p = inst_to
        port_p = connect.port_to
        cxn_p = inst_p.content
        slot_p = port_p.data
        
        inst_c = inst_from
        cxn_c = inst_c.content        
        
        (new_cxn, c, u_map) = construction.CXN.unify(cxn_p, slot_p, cxn_c)
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
        
        port_corr = {'in_ports':{}, 'out_ports':{}}
        for port in in_ports:
            for new_port in new_cxn_inst.in_ports:
                if c[port.data.name] == new_port.data.name:
                    port_corr['in_ports'][port] = new_port
                    break
        port_corr['out_ports'][inst_p.find_port('output')] = new_cxn_inst.find_port('output')
      
        # Update a2i_map
        for map_type in ['sem_map', 'syn_map']: # There must be a cleaner way to do that! Rethink the data structure used.
            new = {} 
            to_remove = set([])
            my_map = u_map[map_type]
            for k,v in a2i_map[map_type].iteritems():
                new[k] = []
                for i in v:
                    if my_map.has_key(i):
                        new[k].extend(my_map[i])
                        to_remove.add(i)
                    else:
                        new[k].extend([i])
            for i in to_remove:
                my_map.pop(i)
            new.update(my_map)
            a2i_map[map_type] = new
        
        return (new_cxn_inst, port_corr, a2i_map)
            
#    @staticmethod                
#    def form_read_out_LR(assemblage):
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
#                    port = inst.find_port(f.order)
#                    child  = graph.predecessors(port)
#                    if not(child):
#                        print "MISSING INFORMATION!"
#                    else:
#                        L2R_read(child[0], graph, phon_form)
#        
#        graph = GRAMMATICAL_WM_P.build_instance_network(assemblage.schema_insts, assemblage.coop_links)
#        tops = [n for n in graph.nodes() if not(graph.successors(n))]
#        phon_form = []
#        L2R_read(tops[0], graph, phon_form)
#        return phon_form
        
    @staticmethod 
    def form_read_out(assemblage):
        """
        Reads the phonological from generated by an assemblage by building the equivalent CXN INSTANCE.
        
        Args:
            - assemblage (ASSEMBLAGE): A construction instance assemblage.
        
        Returns: (phon_form, missing_info, expressed) with:
            - phon_form = the longest consecutive TP_PHON sequence that can be uttered.
            - missing_info (STR) = Name of the SemRep node associated with the first TP_SLOT encountered, represented the missing information.
            - expressed = the semrep that the assemblage expresses (nodes and relations) as defined in the trace of the instances that have been used.
            - a2i_map = TP_ELEMs name mapping between assemblage instances and eq_inst
            - insts_used = the list of cxn_instances that have been fully used.
        """
        (eq_inst, a2i_map) = GRAMMATICAL_WM_P.assemblage2inst(assemblage)
            
        
        phon_list = []
        missing_info = None
        for form in eq_inst.content.SynForm.form:
            if isinstance(form, construction.TP_PHON): # Deal with lexicalized info
                phon_list.append(form)
            else: # find what is the missing info and stop
                SemFrame_node_name = eq_inst.content.SymLinks.form2node(form.name)
                SemRep_node_name = eq_inst.covers['nodes'][SemFrame_node_name]
                missing_info = SemRep_node_name
                break
        
        phon_form = [phon.cxn_phonetics for phon in phon_list]
        
        insts_used = []
        # Define the semantic content expressed
        if not(missing_info): # Everything has been expressed.
            expressed = {'nodes':eq_inst.trace['semrep']['nodes'][:], 'edges':eq_inst.trace['semrep']['edges'][:]} # Deep copy
            insts_used = assemblage.schema_insts[:]
        else:
            nodes = set([])
            edges = set([])
            phon_set = set([phon.name for phon in phon_list])
            for inst in assemblage.schema_insts:
                syn_names = set([])
                for f in inst.content.SynForm.form:
                    mapped_names = a2i_map['syn_map'][f.name]
                    syn_names.update(mapped_names)
                shared = syn_names.intersection(phon_set)
                # Case 1: None of the SynForm has been expressed
                if not(shared):
                    continue
                # Case 2: The whole SynForm has been expressed
                if shared == syn_names:
                    nodes.update(inst.trace['semrep']['nodes'][:])
                    edges.update(inst.trace['semrep']['edges'][:])
                    insts_used.append(inst)
                # Case 3: The SynForm has been partially expressed
                else:
                    for form_name in shared:
                        SemFrame_node_name = eq_inst.content.SymLinks.form2node(form_name)
                        if SemFrame_node_name:
                            SemRep_node_name = eq_inst.covers['nodes'][SemFrame_node_name]
                            nodes.add(SemRep_node_name)
                
            expressed = {'nodes':list(nodes), 'edges':list(edges)}
          
        return (phon_form, missing_info, expressed, eq_inst, a2i_map, insts_used)
    
    ###############
    ### DISPLAY ###
    ###############
    def draw_assemblages(self):
        """
        Draws all the assemblages currently defined by the working memory.
        """
        assemblages = self.assemble()
        i=0
        for assemblage in assemblages:
            title = 'Assemblage_%i' % i
            GRAMMATICAL_WM_P.draw_assemblage(assemblage, title)
            i += 1
            
    @staticmethod
    def draw_instance_network(graph, title=''):
        """
        Draws the instance network.
        
        Args:
            - graph (NetworkX digraph): Generated by build_instance_network()
            - title (STR): Title of the figure.
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
    def draw_assemblage(assemblage, title=''):
        """
        Draws a given assemblage
        
        Args:
            - assemblage (ASSEMBLAGE): A construction instance assemblage
            - title (STR): Title of the figure.
        """
        graph = GRAMMATICAL_WM_P.build_instance_network(assemblage.schema_insts, assemblage.coop_links)
        GRAMMATICAL_WM_P.draw_instance_network(graph, title)
                  

class CXN_RETRIEVAL_P(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name="Cxn_retrieval_P"):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_grammatical_LTM')
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('OUT', 'to_grammatical_WM_P')
        self.cxn_instances = []
    
    def reset(self):
        """
        """
        super(CXN_RETRIEVAL_P, self).reset()
        self.cxn_instances = []
    
    def process(self):
        """
        """
        SemRep = self.inputs['from_semantic_WM']
        cxn_schemas = self.inputs['from_grammatical_LTM']
        if cxn_schemas and SemRep:
            self.instantiate_cxns(SemRep, cxn_schemas)
            self.outputs['to_grammatical_WM_P'] = self.cxn_instances
            # Marked all SemRep elements as processed by gram_WM_C
            for n, d in SemRep.nodes(data=True):
                d['processed'].append('gram_WM_P')
            for u,v,d in SemRep.edges(data=True):
                d['processed'].append('gram_WM_P')
        self.cxn_instances = []
    
    def instantiate_cxns(self, SemRep, cxn_schemas):
        """
        """
        if not cxn_schemas:
            return
            
        def subgraph_filter(subgraph):
            """
            Returns True only if at least one node or edge is tagged as new.
            """
            for n,d in subgraph.nodes(data=True):
                if 'gram_WM_P' not in d['processed']:
                    return True
            for n1,n2,d in subgraph.edges(data=True):
                if 'gram_WM_P' not in d['processed']:
                    return True
            return False
        
        # Build SemRep subgraphs
        SemRep_subgraphs = TCG_graph.build_subgraphs(SemRep, induced='edge', subgraph_filter=subgraph_filter)
        
        for cxn_schema in cxn_schemas:
            sub_iso = self.SemMatch_cat(SemRep_subgraphs, cxn_schema)
            for a_sub_iso in sub_iso:
                match_qual = self.SemMatch_qual(SemRep, cxn_schema, a_sub_iso)
                trace = {"semrep":{"nodes":a_sub_iso["nodes"].values(), "edges":a_sub_iso["edges"].values()}, "schemas":[cxn_schema]}     
                new_instance = CXN_SCHEMA_INST(cxn_schema, trace, a_sub_iso)
                self.cxn_instances.append({"cxn_inst":new_instance, "match_qual":match_qual})
                    
    def SemMatch_cat(self, SemRep_subgraphs, cxn_schema):
        """
        IMPORTANT ALGORITHM
        Computes the categorical matches (match/no match) -> Returns the sub-graphs isomorphisms. This is the main filter for instantiation.
        """
        SemFrame_graph = cxn_schema.content.SemFrame.graph 
            
        node_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a")
        node_frame_match = lambda frame1, frame2: (frame1 == frame2) # Frame values have to match
        edge_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a") # "equal" for strict matching
       
        nm = TCG_graph.node_iso_match(["concept", "frame"], ["", False], [node_concept_match, node_frame_match])
        em = TCG_graph.edge_iso_match("concept", "", edge_concept_match)

        sub_iso = TCG_graph.find_sub_iso(SemRep_subgraphs, SemFrame_graph, node_match=nm, edge_match=em)
        return sub_iso
    
    def SemMatch_qual(self, SemRep, cxn_schema, a_sub_iso): ## NEEDS TO BE WRITTEN!! At this point the formalism does not support efficient quality of match.
        """
        Computes the quality of match.
        Returns a value between 0 and 1: 0 -> no match, 1 -> perfect match.
        
        NOTE: I NEED TO THINK ABOUT HOW TO INCORPORATE FOCUS ETC....
            - In the current version of focus, it only looks at the focus node for the quality of match. 
                But focus should be defined as contrasts within consructions (and between constructions.)
                Move from focus as boolean value to focus as value attached to each node.
            - Still need to incorporate light sem. For this, need to switch to vector space representaiton of concept. 
            This could be added on top of the is-a ontology.
        """
        # Compute match qual value based on focus values.
        focus_match = 1
#        for cxn_node, sem_node_name in a_sub_iso['nodes'].iteritems():
#            sem_node_act = SemRep.node[sem_node_name]['cpt_inst'].activity
#            if cxn_node.focus:
#                focus = 1
#                focus_match -= focus - sem_node_act # This is much too simple. But placeholder for now.            
        return focus_match
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(CXN_RETRIEVAL_P, self).get_state()
        data['cnx_instances'] = [inst.name for inst in self.cxn_instances]
        return data

class PHON_WM_P(WM):
    """
    """
    def __init__(self, name='Phonological_WM_P'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_grammatical_WM_P')
        self.add_port('OUT', 'to_utter')
        self.add_port('OUT', 'to_grammatical_WM_P')
        self.add_port('OUT', 'to_control')
        self.add_port('OUT', 'to_output')
        self.params['dyn'] = {'tau':2, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.phon_sequence = []
        self.needs_filler = False
        self.filler = '....'
    
    def reset(self):
        """
        """
        super(PHON_WM_P, self).reset()
        self.phon_sequence = []
        self.needs_filler = False
        self.filler = '....'
        
    def process(self):
        """
        """
        phon_sequence = self.inputs['from_grammatical_WM_P']
        if phon_sequence:
            new_phon_sequence = []
            for phon_form in phon_sequence:
                phon_schema = PHON_SCHEMA(name=phon_form, word_form=phon_form, init_act=0.6)
                phon_inst = PHON_SCHEMA_INST(phon_schema, trace = {'phon_schema':phon_schema})
                self.add_instance(phon_inst)
                new_phon_sequence.append(phon_inst)
            self.phon_sequence.extend(new_phon_sequence)
            self.outputs['to_utter'] = [inst.content['word_form'] for inst in new_phon_sequence]
            self.outputs['to_control'] = True
            self.outputs['to_output'] = [inst.content['word_form'] for inst in new_phon_sequence]
        else:
            self.outputs['to_utter'] =  None
        
        # Add pause fillers to outputs.
        self.add_fillers(phon_sequence)
        
        self.update_activations()
        self.prune()
        self.outputs['to_grammatical_WM_P'] =  [inst.content['word_form'] for inst in self.phon_sequence]
        
    def add_fillers(self, phon_sequence):
        """
        Simple method to have pause filler placed in utter outputs.
        """
        if phon_sequence == [] and self.needs_filler:
            self.outputs['to_utter'] = [self.filler]
            self.needs_filler = False
        elif phon_sequence == None:
            self.needs_filler = True
        elif phon_sequence:
            self.needs_filler = False

    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(PHON_WM_P, self).get_state()
        data['phon_sequence'] = [phon_inst.content['word_form'] for phon_inst in self.phon_sequence]
        return data

class UTTER(SYSTEM_SCHEMA):
    """
    Simple algorithmic implementation of a proxy for the language motor system realizing the
    phonological plan sequence stored in PHON_WM_P into a temporal sequence of words.
    """
    def __init__(self, name='Utter'):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_phonological_WM_P')
        self.add_port('OUT', 'to_output')
        self.params = {'speech_rate':10}
        self.utterance_stack = []
    
    
    def reset(self):
        """
        """
        super(UTTER, self).reset()
        self.utterance_stack = []
        
    def process(self):
        """
        """
        new_utterance =  self.inputs['from_phonological_WM_P']
        if self.utterance_stack and (self.t % self.params['speech_rate']) == 0:
            word_form = self.utterance_stack.pop()
            self.outputs['to_output'] =  word_form
        if new_utterance:
            new_utterance.reverse()
            self.utterance_stack =  new_utterance + self.utterance_stack

    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(UTTER, self).get_state()
        data['utterance_stack'] = self.utterance_stack[:]
        return data
            
#####################
### COMPREHENSION ###
#####################                   
class PHON_WM_C(WM):
    """
    Receives input one word at a time.
    """
    def __init__(self, name='Phonological_WM_C'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_grammatical_WM_C')
        self.add_port('OUT', 'to_grammatical_WM_C')
        self.add_port('OUT', 'to_cxn_retrieval_C')
        self.add_port('OUT', 'to_control')
        self.params['dyn'] = {'tau':2, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.phon_sequence = []

    def reset(self):
        """
        """
        super(PHON_WM_C, self).reset()
        self.phon_sequence = []
    
    def process(self):
        """
        """
        phon_form = self.inputs['from_input']
        gram_input = self.inputs['from_grammatical_WM_C']
        if gram_input: # Marked all expressed phon elements
            for phon in [phon for phon in self.phon_sequence if phon['inst'].name in gram_input]:
                phon['expressed'] = True

        self.outputs['to_grammatical_WM_C'] =  self.gram_WM_C_output()
        if phon_form:
            phon_schema = PHON_SCHEMA(name=phon_form, word_form=phon_form, init_act=1.0)
            phon_inst = PHON_SCHEMA_INST(phon_schema, trace = {'phon_schema':phon_schema})
            self.add_instance(phon_inst)
            self.phon_sequence.append({'inst':phon_inst, 'expressed':False})
            self.outputs['to_cxn_retrieval_C'] = phon_inst
            self.outputs['to_control'] =  True
        else:
            self.outputs['to_cxn_retrieval_C'] =  None
        
        self.update_activations()     
        self.prune()
    
    def gram_WM_C_output(self):
        """
        Returns the output to send to gram_WM_C.
        The signal sent to gram_WM_C contains the activation levels of the phon instance that so far have not been expressed.
        """
        output = {}
        for inst in [phon['inst'] for phon in self.phon_sequence]:
            output[inst.name] = inst.activity
        return output
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(PHON_WM_C, self).get_state()
        data['phon_sequence'] = [[phon['inst'].content['word_form'], phon['expressed']] for phon in self.phon_sequence]
        return data

class GRAMMATICAL_WM_C(WM):
    """
    """
    def __init__(self, name='Grammatical_WM_C'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_phonological_WM_C')
        self.add_port('IN', 'from_control')
        self.add_port('IN', 'from_cxn_retrieval_C')
        self.add_port('OUT', 'to_cxn_retrieval_C')
        self.add_port('OUT', 'to_semantic_WM')
        self.add_port('OUT', 'to_phonological_WM_C')
        self.params['dyn'] = {'tau':30.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.3}
        self.params['C2'] = {'coop_weight':1.0, 'comp_weight':-4.0, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'max_capacity':None, 'P_comp':1.0, 'P_coop':1.0, 'deact_weight':0.0, 'prune_threshold':0.3, 'confidence_threshold':0.8, 'sub_threshold_r':0.8}
        self.params['parser'] = {'pred_init':{'S':[1]}, 'parser_type':'Left-Corner'}  # S is used to initialize the set of predictions. This is not not really in line with usage based... but for now I'll keep it this way.
        self.state = -1
        self.pred_init = None
          
    def reset(self):
        """
        """
        super(GRAMMATICAL_WM_C, self).reset()
        self.state = -1
        self.pred_init = None
    
    #####################
    ### STATE UPDATE  ###
    ##################### 
    def process(self):
        """
        NOTES:
            - NEED TO BE CAREFUL ABOUT THE TIME DELAY BETWEEN WM AND CXN RETRIEVAL.
            - Might be worth adding a refractory period here again?
        """
        if  self.params['parser']['parser_type'] == 'Earley':
            print "Sorry! Earley parser has been removed in this version. Use Left-Corner. But top-down filtering will come back soon!"
            
        ctrl_input = self.inputs['from_control']
        if ctrl_input and ctrl_input['listen'] and self.state==-1:
                self.state = 0
                self.set_pred_init()
            
        phon_activations = self.inputs['from_phonological_WM_C']

        inst_inputs = self.inputs['from_cxn_retrieval_C']
        if inst_inputs:
            (pred_cxn_insts, phon_inst) = inst_inputs
            # Add new instances
            for inst in pred_cxn_insts:
                self.add_instance(inst, inst.activity)
            # Update Grammatical WM C2 and instance state
            self.Left_Corner_parser(phon_inst, pred_cxn_insts)
        
        self.convey_phon_activations(phon_activations)
        self.update_activations()
        self.prune()
        self.outputs['to_cxn_retrieval_C'] = self.TD_predictor()
        activations = self.sem_WM_output()
        self.outputs['to_semantic_WM'] = {'activations':activations}
        
        # Define when meaning read-out should take place
#        if ctrl_input and ctrl_input['produce'] == self.t:
        if self.t in [100*t for t in range(1, 10)]:
            output = self.produce_meaning()
            if output:
                self.outputs['to_phonological_WM_C'] = output['phon_WM_output']
                self.outputs['to_semantic_WM']['instances'] = output['sem_WM_output']

    def convey_phon_activations(self, phon_activations):
        """
        Propagates activations from PhonWM to GramWM.
        """
        if not(phon_activations):
            return
        for inst in self.schema_insts:
            act = 0
            for f,p in inst.covers.iteritems():
                val = phon_activations.get(p, 0)
                act += val
            inst.activation.E += act # No normalization
            
    def sem_WM_output(self):
        """ Defines the activation output to semantic_WM.
        Returns a dictionary mapping SemFrame elements names of expressed constructions instances onto the respective constrution's activity.
        """
        output = {}
        insts = [i for i in self.schema_insts if i.expressed] # only look at expressed insts
        for cxn_inst in insts:
            activity = cxn_inst.activity
            sem_frame_names = [s.name for s in cxn_inst.content.SemFrame.nodes + cxn_inst.content.SemFrame.edges]
            for name in sem_frame_names:
                output[name] = activity
        return output
            
        
    
    def Left_Corner_parser(self, phon_inst, pred_cxn_insts):
        """
        TCG version of Left-Corner chart parser.
        Note that the work of the parser is spread on both the grammatical WM and the cxn_retrieval sub_system.
        
        Notes:
            - Dont' forget that constructions do not define only slots but also word forms. 
            This requires checking that a phon_inst can match onto an existing construction (scanner)..
        """
        for inst in pred_cxn_insts:
            inst.chart_pos = [self.state, self.state]
        self.state += 1
        self.scanner(phon_inst)
        self.completer()
        
    def TD_predictor(self):
        """
        Top-Down grammatical predictions.
        Returns the classes of constructions expected based on the current status of the GrammaticalWM.
        
        Return:
            - predictions (DICT) : {syn_class:[activities of cxn_inst that predict this syn_class]}
        
        Notes: 
            - I need to incorporate better class and head semantic features (construction signature = sem_feat and syn_feat)
        """

        if self.state==0 and self.pred_init:
             pred_classes = self.pred_init
             self.pred_init = {}
        else:
            if not(self.pred_init):
                self.set_pred_init() # Reset initial predictions.
            pred_classes = {}
            for inst in [i for i in self.schema_insts if not(i.has_predicted)]:
                inst_pred = inst.cxn_predictions()
                for clss in inst_pred:
                    if pred_classes.has_key(clss):
                        pred_classes[clss].append(inst.activity)
                    else:
                        pred_classes[clss] = [inst.activity]
        if pred_classes:
            predictions = {'chart_pos':[self.state, self.state], 'cxn_classes':pred_classes}
        else:
            predictions = None
        return predictions
    
    def scanner(self, phon_inst):
        """
        TCG version of the Earley chart parsing scanner.
        
        NOTES: 
            - Check the existing instances whose form match the phon_inst.content['word_form']. If there is a match, move dot.
            - This is when the competitions are taking place.
            - Covers, to fit with production, should be a mapping between SynForm and PhonRep, while Trace is the part that only keeps track of the element that triggered the instantiation.
            - A key step is to reset the activation of the instance that is confirmed by an input to that of the Phon instance. Right now it is just set to the value of the phone instance. 
            But it should be clamped to it or receive a constant input from it.
        """
        matching_insts = []
        for inst in self.schema_insts:
            phon_prediction = inst.phon_prediction()
            if phon_prediction:
                if phon_prediction == phon_inst.content['word_form']:
                    inst.covers[inst.form_state.name] = phon_inst.name
                    inst.next_state()
                    inst.chart_pos[1] = self.state # Keep track of chart
                    matching_insts.append(inst)
                else:
                    inst.alive = False # Here a cxn whose form is directly disproved by the input is directly removed. Need to revisit this deisgn choice.
        self.compete(matching_insts) # Competing hypotheses.
    
    def completer(self):
        """
        TCG version of the Earley chart parsing completer. (Where cooperations are defined)
        NOTES:
            -  Recursively check all the "completed" cxn (dot all the way to the right) and make the appropriate coop links.
            - I HAVE ADDED COMPETITION HERE... BUT I AM NOT SURE THAT THIS IS THE WAY TO GO.
                This has to be wrong in some way because their could be loops in the tree (think of an example), and in addition
                one wants to be able to maintain multiple possible predictions alive in terms of incomplete instances.
        """
        completed_insts = [inst for inst in self.schema_insts if not(inst.form_state)]
        while completed_insts:
            incomplete_insts = [inst for inst in self.schema_insts if inst.form_state]
            for inst1 in completed_insts:
                competing_insts = []
                for inst2 in incomplete_insts:
                    coop = self.cooperate(inst2, inst1) # Attempt cooperation. If possible, both create coop_link AND update instance states.  
                    if coop:
                        competing_insts.append(inst2)
                # Sets up competition between incompleted cxn that try to map onto the same compeleted cxn.
                self.compete(competing_insts)
               
            completed_insts = [inst for inst in incomplete_insts if not(inst.form_state)]       
    
    def set_pred_init(self):
        """
        Sets the stack of TD initial predictions pred_init.
        The stacks is refilled as soon a state != 0.
        Reinitialize state to state == 0 will then trigger the init predictions.
        """
        self.pred_init = self.params['parser']['pred_init'].copy()

    ###############################
    ### COOPERATIVE COMPUTATION ###
    ###############################
    def cooperate(self, inst1, inst2):
        """
        Notes:
            - Check match between inst1 and inst2
            - If there is a match: create a coop link
            - Update inst1.chart_pos[1] to self.state.
            - Compare to production, here C2 operations cannot simply be applied only once to new instances. this is due to the fact that the state of the instances changes. 
            The state change is required by the fact that production includes predictions, predictions which are absent from production.
        """
        match = GRAMMATICAL_WM_C.match(inst1, inst2)
        flag = False
        if match["match_cat"] == 1:
            for match_qual, link in match["links"]:
                if match_qual > 0:
                    self.add_coop_link(inst_from=link["inst_from"], port_from=link["port_from"], inst_to=link["inst_to"], port_to=link["port_to"], qual=match_qual)
                    link["inst_to"].chart_pos[1] = self.state
                    link["inst_to"].next_state()
                    flag = True
        return flag
    
    def compete(self, insts):
        """
        Adds competition links between each pair of instances in comp_insts [CXN_SCHEMA_INST_C] for which self.match() returns -1.
        
        Args:
            - comp_insts [CXN_SCHEMA_INST_C]:
            
        NOTE:
            - For now it is used in way that all the constructions in insts should be competing.
        """
        for i in range(len(insts)-1):
            inst1 = insts[i]
            for j in range(i+1, len(insts)):
                inst2 = insts[j]
                match = GRAMMATICAL_WM_C.match(inst1, inst2)
                if match['match_cat'] == -1:
                    self.add_comp_link(inst1, inst2)
    
    @staticmethod
    def overlap(inst1, inst2):
        """
        Returns the set of PHON_SCHEMA_INST on which the instances overlap.
        
        Args:
            - inst1 (CXN_SCHEMA_INST_C): A cxn instance
            - inst2 (CXN_SCHEMA_INST_C): A cxn instance
       
       NOTES:
            - Overlap should define the set of constraints that are expressed by both constructions. It should allow to determine whether or not they
            compete
            - I need to clean up the notion of trace and cover in both production and comprehension. In particular, it is important to note that a cxn can cover both semantic instances
            (SemRep) AND phon instances. The notion of trace changes also when cxn can be instantiated on the bases of predictions from other constructions. Should those constructions
            be part of the trace?
            - With respect to the previous point, in production, trace contains only pointers to what triggered the instantiation, covers contains a mappping!
            - Since we are dealing with CFG, one way to define overal, given the notion of chart_pos (as [state1, state2]) can just be the intersection of two such segments, and the competition
            would occur as soon as the overlap is not null (no crossing branches in CFGs).
        """
        s1 = set(range(inst1.chart_pos[0], inst1.chart_pos[1]))
        s2 = set(range(inst2.chart_pos[0], inst2.chart_pos[1]))
        overlap = list(s1.intersection(s2))
        return overlap
    
    @staticmethod    
    def link(inst_p, inst_c):
        """
        Args:
            - inst_p (CXN_SCHEMA_INST_C): An incomplete cxn instance (parent)
            - inst_c (CXN_SCHEMA_INST_C): A completed cxn instance (child)
            
        NOTE:
            - Light semantics is required to limit for example the possibility of an intransitive verb to link into an SV cxn.
        """
        cxn_c = inst_c.content
        form_elem_p = inst_p.form_state

        cond1 = isinstance(form_elem_p, construction.TP_SLOT)
        if cond1:
            cond2 = cxn_c.clss in form_elem_p.cxn_classes
            sem_elem_p = inst_p.content.form2node(form_elem_p)
            sem_elem_c = inst_c.content.SemFrame.get_head()
            cond3 = sem_elem_c.concept.match(sem_elem_p.concept, match_type = "is_a") # CHECK LIGHT_SEM MATCH. NEED TO HAVE QUALITATIVE MATCH (NOT BOOLEAN MATCH)
                                
            link = {"inst_from": inst_c, "port_from":inst_c.find_port("output"), "inst_to": inst_p, "port_to":inst_p.find_port(form_elem_p.order)}
            if cond2 and cond3:
                match_qual = 1
            else:
                match_qual = 0
            return (match_qual, link)
        return None
    
    @staticmethod
    def match(inst1, inst2):
        """
         Args:
            - inst1 (CXN_SCHEMA_INST_C): An incomplete cxn instance (parent)
            - inst2 (CXN_SCHEMA_INST_C): A completed cxn instance (child)
            
        NOTE:
            - Not sure that this method is really necessary.
            - IS THERE NOT AN ISSUE HERE? SEEMS LIKE THE CODE TREATS SUCCESSIVELY EACH CXN INST AS PARENT AND CHILD?
        """            
        match_cat = 0
        links = []
        if inst1 == inst2:
           match_cat = 0 # CHECK THAT (This should not be allowed to happen1)
           return {"match_cat":match_cat, "links":links}
        
        overlap = GRAMMATICAL_WM_C.overlap(inst1, inst2)
        
        # Check competition
        if overlap: 
            match_cat = -1
            return {"match_cat":match_cat, "links":links}
            
        # Check for cooperation
        flag1 = False
        flag2 = False
        if inst1.form_state and not(inst2.form_state):
            if inst1.chart_pos[1] == inst2.chart_pos[0]: 
                link = GRAMMATICAL_WM_C.link(inst1, inst2)
                if link:
                    links.append(link)
                    flag1 = True
                        
        if inst2.form_state and not(inst1.form_state):
            if inst2.chart_pos[1] == inst1.chart_pos[0]:
                link = GRAMMATICAL_WM_C.link(inst2, inst1)
                if link:
                    links.append(link)
                    flag2 = True
          
        if flag1 and flag2:
            print "LOOP %s %s" %(inst1.name, inst2.name) # Warns that there are direct loops.
        
        if links:
            match_cat = 1
        else: 
            match_cat = 0 # since we have already ruled out the possibilities of competition
        return {"match_cat":match_cat, "links":links}               
                               
                              
    ##########################
    ### MEANING PRODUCTION ###
    ##########################                       
    def produce_meaning(self):
        """
        Notes:
            - I might want to revisit the expressed tag used in cxn_inst_c.
            In particular the mapping between constructions and SemRep might need to be going both ways.
        """
        assemblages = self.assemble()
        if assemblages:
            sem_WM_output = {'SemFrame':None, 'sem_map':{}}
            (winner_assemblage, eq_inst, a2i_map) = self.get_winner_assemblage(assemblages)
            if winner_assemblage.activation > self.params['C2']['confidence_threshold']:
                sem_WM_output['SemFrame'] = eq_inst.content.SemFrame
                sem_WM_output['sem_map'] = a2i_map['sem_map']
                phon_WM_output = eq_inst.covers.values()
                for cxn_inst in winner_assemblage.schema_insts:
                    cxn_inst.expressed = True # For now I mark all the cxn_insts that have sent their SemFrame to SemanticWM as done 
                
                #Option5: Sets all the instances in the winner assembalge to subthreshold activation. Sets all the coop_weightsto 0. So f-link remains but inst participating in assemblage decay unless they are reused.
#                self.post_prod_state(winner_assemblage) # Needed if cooperation links are symmetrical
                
                return {'phon_WM_output':phon_WM_output, 'sem_WM_output':sem_WM_output}
        return None
        
    def get_winner_assemblage(self, assemblages):
        """
        Args: assemblages ([ASSEMBLAGE])
        Notes: 
            - Need to discuss the criteria that come into play in choosing the winner assemblages.
            - Check how this should be udpated on the basis of the method used for production.
        """
        winner = None
        max_score = None
        # Computing the equivalent instance for each assemblage.
        for assemblage in assemblages:
            (eq_inst, a2i_map) = self.assemblage2inst(assemblage)
            assemblage_dat = (assemblage, eq_inst, a2i_map)
            score = assemblage.activation
            if not(max_score):
                max_score = score
                winner = assemblage_dat
            if score>max_score:
                max_score = score
                winner = assemblage_dat
        return winner
    
    def post_prod_state(self, winner_assemblage):
        """
        Sets the grammatical state after production given a winner assemblage.
        
        NOTE directly taken from the production model
        """
        self.deactivate_coop_weigts()
    
    def set_subthreshold(self, insts):
        """
        Sets the activation of all the instances in insts to r*confidence_threshold where r= self.params['C2']['sub_threshold_r']
        Args:
            - insts ([CXN_INST])
        
        NOTE: directly taken from the production model.
        """
        r= self.params['C2']['sub_threshold_r']
        for inst in insts:
            inst.set_activation(r*self.params['C2']['confidence_threshold'])
            
    def deactivate_coop_weigts(self):
        """
        Sets all the coop_links to weight = self.params['C2']['deact_weight']
        
        NOTE: directly taken from the production model.
        """
        for coop_link in self.coop_links:
            coop_link.weight = self.params['C2']['deact_weight']
    
    ##################
    ### ASSEMBLAGE ###
    ##################    
    def assemble(self):
        """
        Returns the set of all the assemblages ([ASSEMBLAGE]) that can be built given the current state of the GrammaticalWM.
        
        
        Notes:
            - THIS IS COPIED FROM GRAMMATICAL_WM_P.
            - WHAT ABOUT THE CASE WHERE THERE STILL IS COMPETITION GOING ON?
            - NOTE THAT IN THE CASE OF MULTIPLE TREES GENERATED FROM THE SAME SET OF COOPERATION... THERE IS MAXIMUM SPANNING TREE. IS THIS IS THE ONE THAT SHOULD BE CONSIDERED?
        
        """
        inst_network = GRAMMATICAL_WM_C.build_instance_network(self.schema_insts, self.coop_links)
        tops = [(n,None) for n in inst_network.nodes() if not(inst_network.successors(n))]
        
        assemblages = []
        for t in tops:
            results = []
            frontier = [t]
            assemblage = ASSEMBLAGE()
            self.get_trees(frontier, assemblage, inst_network, results)
            assemblages += results
        
        # Compute assemblage activation values
        for assemblage in assemblages:
            assemblage.update_activation()
        
        return assemblages
        
        
    @staticmethod
    def build_instance_network(schema_insts, coop_links):
        """
        Creates a NetworkX directed graph whose nodes are of the instances (type='instance') and their ports (type='port'), 
        and the edges link the instances to the ports (type='inst2port') or the ports to the instances (coop_link) (type='port2inst')
    
        Args:
            - schema_insts ([SCHEMA_INST]): Set of schema instances
            - coop_links ([COOP_LINK]): Set of cooperation links defined between the schema instants
        
        Requires:
            - NetworkX
        
        Notes:
            - Directly copied from GrammaticalWM_P
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

    def get_trees(self, frontier, assemblage, graph, results):
        """
        For a given instance network (generated by build_instance_network) defined as a directed graph, returns all the sub-trees each sub-tree
        defining an assemblage.
        (Recursive function)
        
        Args:
            - frontier (): Frontier of the search space.
            - assemblage (ASSEMBLAGE): 
            - graph (NetworkX Digraph): Generated by build_instance_network
            - results ([ASSEMBLAGE]): Recursively stores the assemblages (sub-trees)
        
        Notes:
            - THIS IS COPIED FROM GRAMMATICAL_WM_P!!
            - "Un-superpose" the trees!
            - DOES NOT HANDLE THE CASE WHERE THERE STILL IS SOME COMPETITION GOING ON.
                NOTE: I think it does...
            - ALSO, it returns also sub-optimal trees. (Not only the tree that contains all the cooperating instances in the WM).
        """
        new_frontiers = [[]] # Each frontier correspond to a possible choice between multiple cooperation options to a same port.
        
        for node, link in frontier:
            # Update assemblage
            assemblage.add_instance(node)
            if link:
                assemblage.add_link(link)
            
            # For each element in the frontier, try to expand the tree.
            ports = graph.predecessors(node)
            for port in ports:
                children = graph.predecessors(port) # A port can be linked to multiple children, each representing a different hypothesis.
                updated_frontiers = []
                if not(children):
                    pass
                else:
                    for child in children:
                        flag =  child in assemblage.schema_insts
                        if not(flag):
                            link = self.find_coop_links(inst_from=child, inst_to=node, port_from=child.find_port("output"), port_to=port)
                            for f in new_frontiers:
                                updated_frontiers.append(f[:] + [(child, link[0])])
                    new_frontiers = updated_frontiers # Wrong indentation. Not handling frontiers properly.
        if new_frontiers == [[]]:
            results.append(assemblage)
        else:
            for a_frontier in new_frontiers:
                self.get_trees(a_frontier, assemblage.copy(), graph, results)
           
    @staticmethod
    def assemblage2inst(assemblage):
        """
        For a given construction instance assemblage, returns 
            (1) the instance equivalent to the assemblage by Unification.
            (2) a DICT mapping the name of the TP_ELEM of the assemblage onto the TP_ELEM of the eq_inst.
            This mapping allows to compute direct relations between the structure of the assemblage and the compact equivalent instance form.
            The dictionary also provides (for convenience) the names of the TP_ELEM for each instance in the assemblage.
        
        Args:
            - assemblage (ASSEMBLAGE): An construction instance assemblage
        
        Notes:
            - Copied from GrammaticalWM_P!
        """
        new_assemblage = assemblage.copy()
        coop_links = new_assemblage.coop_links
        a2i_map = {'sem_map':{}, 'syn_map':{}}
        if coop_links: # not a trivial assemblage composed of a single instance.
            while len(coop_links)>0:
                (new_assemblage, new_cxn_inst, a2i_map) = GRAMMATICAL_WM_C.reduce_assemblage(new_assemblage, new_assemblage.coop_links[0], a2i_map)
                coop_links = new_assemblage.coop_links
            eq_inst = new_assemblage.schema_insts[0]
        else:
            inst = new_assemblage.schema_insts[0] #It would be best to make a copy(?)
            #Trivial mapping onto itself
            a2i_map['sem_map'] = dict([(sem_elem.name, sem_elem.name) for sem_elem in inst.content.SemFrame.nodes + inst.content.SemFrame.edges])
            a2i_map['syn_map'] = dict([(syn_elem.name, syn_elem.name) for syn_elem in inst.content.SynForm.form])
            eq_inst = inst
        eq_inst.activity = new_assemblage.activation
        return (eq_inst, a2i_map)
       
    @staticmethod      
    def reduce_assemblage(assemblage, coop_link, a2i_map):
        """
        Returns a new, reduced, assemblage in which the instances cooperating (as defined by 'coop_link') have been combined.
        
        Args:
            - assemblage (ASSEMBLAGE): A construction instance assemblage.
            - coop_link (COOP_LINK): A cooperation link belonging to the assemblage.
            - a2i_map (DICT): assemblage2instance name mapping to be updated
        
        Notes:
            - Copied froM GrammaticalWM_P
        """
        inst_p = coop_link.inst_to
        inst_c = coop_link.inst_from
        connect = coop_link.connect
        
        (new_cxn_inst, port_corr, a2i_map) = GRAMMATICAL_WM_C.combine_schemas(inst_p, inst_c, connect, a2i_map)
        
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
        
        return (new_assemblage, new_cxn_inst, a2i_map)
    
    
#    @staticmethod
#    def combine_schemas_old(inst_to, inst_from, connect):
#        """
#        Returns a new cxn_instance and the mapping between inst_to and inst_from ports to new_cxn_inst ports.
#        
#        NOTE: Only minor changes from the production method related to the difference in trace and mapping, and chart_pos.
#        """
#        inst_p = inst_to
#        port_p = connect.port_to
#        cxn_p = inst_p.content
#        slot_p = port_p.data
#        
#        inst_c = inst_from
#        cxn_c = inst_c.content        
#        
#        (new_cxn, c) = construction.CXN.unify(cxn_p, slot_p, cxn_c)
#        new_cxn_schema = CXN_SCHEMA(new_cxn, init_act=0.0)
#        
#        # Define new_cxn trace
#        new_trace = {"schemas":inst_p.trace["schemas"] + inst_c.trace["schemas"]} 
#        
#        # Defines new_cxn mapping
#        new_mapping = {} 
#        for n,v in inst_p.covers.iteritems():
#                new_mapping[c[n]] = v
#        for n,v in inst_c.covers.iteritems():
#            new_mapping[c[n]] = v       
#        
#        new_cxn_inst = CXN_SCHEMA_INST_C(new_cxn_schema, trace=new_trace, mapping=new_mapping, copy=False)
#        new_cxn_inst.chart_pos = inst_p.chart_pos
#        
#        # Define port correspondence
#        in_ports = [port for port in inst_p.in_ports if port.data != slot_p] + [port for port in inst_c.in_ports]
#        
#        port_corr = {'in_ports':{}, 'out_ports':{}}
#        for port in in_ports:
#            for new_port in new_cxn_inst.in_ports:
#                if c[port.data.name] == new_port.data.name:
#                    port_corr['in_ports'][port] = new_port
#                    break
#        port_corr['out_ports'][inst_p.find_port('output')] = new_cxn_inst.find_port('output')
#      
#        return (new_cxn_inst, port_corr)
        
        
    @staticmethod
    def combine_schemas(inst_to, inst_from, connect, a2i_map):
        """
        Returns a new cxn_instance and the mapping between inst_to and inst_from ports to new_cxn_inst ports.
        
        Args:
            - inst_to (CXN_SCHEMA_INST):
            - inst_from (CXN_SCHEMA_INST):
            - connect (CONNECT): A CONNECT object associated with a cooperation link between inst_to and inst_from.
            - a2i_map (DICT): assemblage2instance name mapping to be updated.
            
        Notes:
             NOTE: Only minor changes from the production method related to the difference in trace and mapping, and chart_pos.
        """
        inst_p = inst_to
        port_p = connect.port_to
        cxn_p = inst_p.content
        slot_p = port_p.data
        
        inst_c = inst_from
        cxn_c = inst_c.content        
        
        (new_cxn, c, u_map) = construction.CXN.unify(cxn_p, slot_p, cxn_c)
        new_cxn_schema = CXN_SCHEMA(new_cxn, init_act=0)
        
        # Define new_cxn trace
        new_trace = {"schemas":inst_p.trace["schemas"] + inst_c.trace["schemas"]} 
            
        # Defines new_cxn mapping
        new_mapping = {} 
        for n,v in inst_p.covers.iteritems():
                new_mapping[c[n]] = v
        for n,v in inst_c.covers.iteritems():
            new_mapping[c[n]] = v
        
        new_cxn_inst = CXN_SCHEMA_INST_C(new_cxn_schema, trace=new_trace, mapping=new_mapping, copy=False)
        new_cxn_inst.chart_pos = inst_p.chart_pos[:]
    
        # Define port correspondence
        in_ports = [port for port in inst_p.in_ports if port.data != slot_p] + [port for port in inst_c.in_ports]
        
        port_corr = {'in_ports':{}, 'out_ports':{}}
        for port in in_ports:
            for new_port in new_cxn_inst.in_ports:
                if c[port.data.name] == new_port.data.name:
                    port_corr['in_ports'][port] = new_port
                    break
        port_corr['out_ports'][inst_p.find_port('output')] = new_cxn_inst.find_port('output')
      
        # Update a2i_map
        for map_type in ['sem_map', 'syn_map']: # There must be a cleaner way to do that! Rethink the data structure used.
            new = {} 
            to_remove = set([])
            my_map = u_map[map_type]
            for k,v in a2i_map[map_type].iteritems():
                new[k] = []
                for i in v:
                    if my_map.has_key(i):
                        new[k].extend(my_map[i])
                        to_remove.add(i)
                    else:
                        new[k].extend([i])
            for i in to_remove:
                my_map.pop(i)
            new.update(my_map)
            a2i_map[map_type] = new
        
        return (new_cxn_inst, port_corr, a2i_map)
    
    @staticmethod 
    def meaning_read_out(assemblage):
        """
        Reads the semantic representation generated by an assemblage by building the equivalent CXN INSTANCE.
        Returns:
            - sem_frame = the SemFrame of the equivalent instance.
        """
        (eq_inst, a2i_map) = GRAMMATICAL_WM_C.assemblage2inst(assemblage)
        sem_frame = eq_inst.content.SemFrame     
        print "HERE"
        return sem_frame
    
    #######################
    ### DISPLAY METHODS ###
    #######################
    def draw_assemblages(self):
        """
        NOTE: COPIED  FROM GRAMMATICAL_WM_P AND USE THE GRAMMATICAL_WM_P method!!
        """
        assemblages = self.assemble()
        i=0
        for assemblage in assemblages:
            title = 'Assemblage_%i' % i
            GRAMMATICAL_WM_P.draw_assemblage(assemblage, title)
            i += 1
        
class CXN_RETRIEVAL_C(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name="Cxn_retrieval_C"):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_grammatical_LTM')
        self.add_port('IN', 'from_phonological_WM_C')
        self.add_port('IN', 'from_grammatical_WM_C')
        self.add_port('OUT', 'to_grammatical_WM_C')
        self.cxn_instances = []

    def reset(self):
        """
        """
        super(CXN_RETRIEVAL_C, self).reset()
        self.cxn_instances = []
    
    def process(self):
        """
        """
        cxn_schemas = self.inputs['from_grammatical_LTM']
        TD_pred_input = self.inputs['from_grammatical_WM_C'] # unused here since I have removed Earley parser for now.
        phon_inst = self.inputs['from_phonological_WM_C']
        if cxn_schemas and phon_inst:
            (lexical_cxn_instances, BU_predictions) = self.instantiate_lexical_cxns(phon_inst, cxn_schemas)
            self.cxn_instances.extend(lexical_cxn_instances)
            self.instantiate_cxns(BU_predictions, cxn_schemas)
            self.outputs['to_grammatical_WM_C'] = (self.cxn_instances, phon_inst)
        self.cxn_instances = []
    
    def instantiate_lexical_cxns(self, phon_inst, cxn_schemas):
        """
        Instantiates the construcitons whose left-corner matches phon_inst content.
        Returns instances and the set of their classes that form the basis of Bottom-up grammatial predictions
        used in left-corner instantiation in instantiate_cxns()
        """
        lexical_cxn_instances = []
        BU_predictions = set([])
        BU_data = set([phon_inst.content['word_form']])
        for cxn_schema in cxn_schemas:
            left_corner = set(cxn_schema.get_initial_predictions())
            if not(left_corner.isdisjoint(BU_data)): # Left corner matches lexical bottom-up data.
                trace = {'schemas':[cxn_schema]}
                cxn_inst = CXN_SCHEMA_INST_C(cxn_schema, trace=trace, mapping={})
                lexical_cxn_instances.append(cxn_inst)
                pred = cxn_inst.content.clss
                BU_predictions.add(pred)
        return (lexical_cxn_instances, BU_predictions)
                    
    def instantiate_cxns(self, predictions, cxn_schemas):
        """
        Generate the set of construction instances to be invoked in GrammaticalWM.
        Left-Corner based instantiation.
        
        Args:
            - Predictions: List of syntactic classes on which the instantiation should be based.
            - cxn_schemas: Direct access to the GrammaticalLTM knowledge.
        """
        pred_classes = predictions
        old_pred_classes = pred_classes
        while pred_classes: # Recursively instantiate the constructions.
            new_pred_classes = set([])
            for cxn_schema in cxn_schemas:
                left_corner = set(cxn_schema.get_initial_predictions())
                if not(left_corner.isdisjoint(pred_classes)): # Left corner matches a prediction.
                    trace = {'schemas':[cxn_schema]}
                    cxn_inst = CXN_SCHEMA_INST_C(cxn_schema, trace=trace, mapping={})
                    self.cxn_instances.append(cxn_inst)
                    # Recursively add the instances predicted by the newly instantiated cxns.
                    pred = cxn_inst.content.clss
                    if pred not in old_pred_classes:
                        new_pred_classes.add(pred)
            old_pred_classes = old_pred_classes.union(new_pred_classes)
            pred_classes = new_pred_classes
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(CXN_RETRIEVAL_C, self).get_state()
        data['cnx_instances'] = [inst.name for inst in self.cxn_instances]
        return data
        
####################
### TASK CONTROL ###
####################
class CONTROL(SYSTEM_SCHEMA):
    """
    This needs to be reformatted to better handle comprehension.
    """
    def __init__(self, name="Control"):
        SYSTEM_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('IN', 'from_phonological_WM_P')
        self.add_port('OUT', 'to_semantic_WM')
        self.add_port('OUT', 'to_grammatical_WM_P')
        self.add_port('OUT', 'to_grammatical_WM_C')
        self.params['task'] = {'time_pressure':100, 'start_produce':1000}
        self.params['style'] = {'activation':1.0, 'sem_length':0, 'form_length':0, 'continuity':0}
        self.state = {'last_prod_time':0, 'unexpressed_sem':False, 'mode':'produce', 'produce': False}
    
    def reset(self):
        """
        """
        super(CONTROL, self).reset()
        self.state = {'last_prod_time':0, 'unexpressed_sem':False, 'mode':'produce', 'produce': False}
    
    def set_mode(self, mode):
        """
        """
        self.state['mode'] = mode
        if mode =='produce':
            self.state['last_prod_time'] = self.t
            self.state['produce'] = False
            self.state['unexpressed_sem'] = False
            self.params['task']['start_produce'] += self.t
    
    def process(self):
        """
        """
        # Communicating with semantic_WM
        self.outputs['to_semantic_WM'] =  self.state['mode']
        
        # Communicating with grammatical_WM_P
        if self.state['mode'] == 'produce':
            if self.inputs['from_phonological_WM_P']:
                self.state['last_prod_time'] = self.t
                
            self.state['unexpressed_sem'] = self.inputs['from_semantic_WM']
            
            if self.t == self.params['task']['start_produce']:
                self.state['last_prod_time'] = self.t #pressure only starts building up once the start_produce time has been reached.
                
            if self.t >= self.params['task']['start_produce'] and self.state['unexpressed_sem']:
                self.state['produce'] = True
            else:
                self.state['produce'] = False
            
            if self.t < self.params['task']['start_produce'] or not(self.state['unexpressed_sem']):
                pressure = 0
                self.state['last_prod_time'] = self.t # This option allows to have the pressure start to ramp up only once a new sem element has been introduced in semWM.
            else:
                pressure = min((self.t - self.state['last_prod_time'])/self.params['task']['time_pressure'], 1) #Pressure ramps up linearly to 1

            output = {'produce':self.state['produce'], 'pressure':pressure, 'params_style':self.params['style'].copy()}
            self.outputs['to_grammatical_WM_P'] = output
        else:
            self.outputs['to_grammatical_WM_P'] =  None
                
        # Communicating with grammatical_WM_C
        if self.state['mode'] == 'listen':
            gram_output = {'listen':True, 'produce':self.params['task']['start_produce']}
            self.outputs['to_grammatical_WM_C'] = gram_output
            
        else:
            gram_output = {'listen':False}
            self.outputs['to_grammatical_WM_C'] =  gram_output
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(CONTROL, self).get_info()
        data['params'] = self.params
        return data
    
    def get_state(self):
        """
        """
        data = super(CONTROL, self).get_state()
        data['state'] = self.state
        return data
        
###############################
##### INPUT-OUPUT CLASSES #####
###############################
class TEXT2SPEECH(object):
    """
    Simple TTS system.
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
            
class ISRF_INTERPRETER(object):
    """
    Interprets ISRF expressions.
    """
    def __init__(self, conceptLTM):
        self.conceptLTM = conceptLTM
        self.name_table = {}

    def reset(self):
        """
        Resets the interpeter
        """
        self.name_table = {}
    
    def prop_interpreter(self, proposition):
        """
        For a given proposition defined as a list of terms (STR), 
        returns the associated set of concept schema instances
        
        Args:
            - proposition ([STR]) or (STR): An array of ISRF defined terms (or string with terms separated by '&'))

        Notes:
            - A concept is only interpreted into an instance once. Following interpretations are skipped.
        """
        connector = '&'
        if isinstance(proposition, str):
            proposition = [s.strip() for s in proposition.split(connector)]
                           
        # For reference.
#        func_pattern = r"(?P<operator>\w+)\((?P<args>.*)\)"
#        cpt_name_pattern = r"[A-Z0-9_]+"
#        var_name_pattern = r"[a-z0-9]+"
#        frame_flag_pattern = r"F"
#        act_pattern = r"[0-9]*\.[0-9]+|[0-9]+"
#        cpt_var_flag_pattern = r"\?"
        
        # More directly specialized pattern. Works since I limit myself to two types of expressions CONCEPT(var, F, act) - act and F optional -  or var1(var2, var3) (and ?CONCEPT(var))
        func_pattern_cpt = r"(?P<cpt_var>\??)(?P<operator>[A-Z0-9_]+)\(\s*(?P<var>[a-z0-9]+)((\s*,\s*)(?P<frame>F))?((\s*,\s*)(?P<act>[0-9]*\.[0-9]+|[0-9]+))?\s*\)" # Concept definition with activation and frame flag
        func_pattern_rel = r"(?P<operator>[a-z0-9]+)\(\s*(?P<var1>[a-z0-9]+)(\s*,\s*)(?P<var2>[a-z0-9]+)\s*\)" # Relation activation is defined alongside the relation concept.
        
        instances = []
        
        cpts_match = []
        rels_match = []
        for term in proposition:
            match1 = re.search(func_pattern_cpt, term)
            match2 = re.search(func_pattern_rel, term)
            if match1:
                cpts_match.append(match1)
            elif match2:
                rels_match.append(match2)
            else:
                error_msg = "Unknown formula %s" %term
                raise ValueError(error_msg)
                
        for match in cpts_match: #First process define concept schemas
            dat = match.groupdict()
            cpt_var = dat['cpt_var'] == '?'
            concept = dat['operator']
            var = dat['var']
            if self.name_table.has_key(var): # Do not reinterpret a schema inst that has already been interpreted.
                cpt_inst = self.name_table[var]
                instances.append(cpt_inst)
                continue
            cpt_schema = self.conceptLTM.find_schema(name=concept)
            cpt_frame = dat.get('frame', None)
            cpt_act = dat.get('act', None)
                
            cpt_inst = CPT_SCHEMA_INST(cpt_schema, trace={'per_inst':None, 'cpt_schema':cpt_schema, 'ref':var}) # 'ref' is used to track referent.
            cpt_inst.trace['per_inst'] = cpt_inst.name # Trick to facilitate bypassing visualWM when necessary.
            if cpt_frame:
                cpt_inst.frame = True
            if cpt_act:
                cpt_inst.set_activation(float(cpt_act))
            if cpt_var:
                cpt_inst.unbound = True
            self.name_table[var] = cpt_inst
            instances.append(cpt_inst)
        
        for match in rels_match: # Then build the relations
            dat = match.groupdict()
            rel = dat['operator']
            arg1 = dat['var1']
            arg2 = dat['var2']
            if not((rel in self.name_table) and (arg1 in self.name_table) and (arg2 in self.name_table)):
                error_msg = "ISRF variable used before it is defined."
                raise ValueError(error_msg)
            else:
                rel_inst = self.name_table[rel]
                rel_inst.content['pFrom'] = self.name_table[arg1]
                rel_inst.content['pTo'] = self.name_table[arg2]
                    
        return instances
    
    def get_instance(self, var_name):
        """
        Returns the instance associated with the variable name var_name.
        """
        return self.name_table[var_name]


class ISRF_WRITER(object):
    """ Translates SemanticWM state into ISRF format
    """
    def __init__(self, SemanticWM): 
        self.SemanticWM = SemanticWM
        self.var_table = {}
        self.data = {}
        self.var_id = 0
        self.connector = '&'
    def reset(self):
        """ Resets writer.
        """
        self.var_table = {}
        self.data = {}
        self.var_id = 0
    
    def cpt_2_ISRF(self, cpt_inst):
        """
        """
        var_name = self.var_table.get(cpt_inst.name, None)
        cpt_name = str(cpt_inst.trace['cpt_schema'].name)
        if not var_name:        
            var_name = "%s_%i" %(str.lower(cpt_name), self.var_id)
            self.var_table[cpt_inst.name] = var_name
            self.var_id +=1
        cpt_ISRF = "%s(%s, " %(cpt_name, var_name)
        if cpt_inst.frame:
            cpt_ISRF += "F, "
        cpt_ISRF += ".%2f)" %cpt_inst.activity
        return (cpt_ISRF, var_name)
        
    def write_ISRF(self):
        """ Defines, stores, and returns the ISRF format associated with the
        current state of the associated, self.SemanticWM.
        """
        t = self.SemanticWM.t
        dat = []
        cpt_insts = self.SemanticWM.schema_insts
        for cpt_inst in [i for i in cpt_insts if not(isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA))]: # Start with nodes.
            (cpt_ISRF, var_name) = self.cpt_2_ISRF(cpt_inst)
            dat.append(cpt_ISRF)
        for rel_inst in [i for i in cpt_insts if isinstance(i.trace['cpt_schema'], CPT_RELATION_SCHEMA)]: # Then move on to relations
            (cpt_ISRF, var_name) = self.cpt_2_ISRF(rel_inst)
            dat.append(cpt_ISRF)
            p_from = rel_inst.content['pFrom']
            p_to = rel_inst.content['pTo']
            cpt_ISRF_rel = "%s(%s, %s)" %(var_name, self.var_table[p_from.name], self.var_table[p_to.name])
            dat.append(cpt_ISRF_rel)
            self.data[t] = dat
        
        return (t,dat)

class SEM_GENERATOR(object):
    """
    Serves to generate incremental semantic inputs to the SemanticWM as defined by ISRF format.
    
    Data:
        - sem_inputs (DICT): Dictionary of all inputs in text form
        - conceptLTM (CONCEPT_LTM): Direct access to the conceptual long term memory
        - speed_param (FLOAT): speed_param >0. Factor applied to the timing of the input to slow it down (<1) or speed it up (>1).
        - is_macro (BOOL): True if the input is a sem_gen macro.
        - ground_truths (DICT): Dictionary associating sem_inputs to an array of utterances each providing a ground-truth linguistic expression of the semantic content.
    
    Notes: 
        - Does not allow for verbal guidance. Designed for purely serial update of semanticWM state.
    """
    def __init__(self, sem_inputs, conceptLTM, speed_param=1, std=0, is_macro=False, ground_truths=None):
        """
        Args:
            - sem_inputs: a semantic input dict loaded using TCG_LOADER.load_sem_input()
            - conceptLTM (CONCEPT_LTM): Contains concept schemas.
            - speed_param (FLOAT): speed_param >0. Factor applied to the timing of the input.
            - std (FLOAT): defines standard deviation of uniform distribution centered on a timing t0 around which the time of utterance is chosen (introduces stochasticity in the input timing)
            - is_macro (BOOL): True if the input is a sem_gen macro.
            - ground_truths (DICT): Dictionary associating sem_inputs to an array of utterances each providing a ground-truth linguistic expression of the semantic content.
        """ 
        self.sem_inputs = sem_inputs
        self.interpreter = ISRF_INTERPRETER(conceptLTM)
        self.speed_param = speed_param
        self.std = std
        self.is_macro = is_macro
        self.ground_truths = ground_truths
        self.preprocess_inputs()
    
    def preprocess_inputs(self):
        """
        Adds timing sequence for the based on input rate if only sem_rate has been provided.
        """
        for name, sem_input in self.sem_inputs.iteritems():
            sem_rate = float(sem_input['sem_rate'])*self.speed_param
            sequence = sem_input['sequence']
            timing = [t*self.speed_param for t in sem_input['timing']]
            get_time = lambda i, rate, std: max(random.uniform(i*sem_rate-std, i*sem_rate+std), 0)
            if sem_rate and not(timing):
                if sem_rate<2*self.std:
                    error_msg = "Input sequence order compromised. Sem_Rate=%.2f < 2*std=%.2f. SemRate should be > 2*std" %(sem_rate, 2*self.std)
                    raise ValueError(error_msg)
                sem_input['timing'] = [get_time(i, sem_rate, self.std) for i in range(len(sequence))]
            if not(timing) and not(sem_rate):
                print "PREPROCESSING ERROR: Provide either timing or rate for %s" %name
                
    def show_options(self, verbose=False):
        """
        Print the input names.
        If verbose, show the content of each input.
        """
        for name, sem_input in self.sem_inputs.iteritems():
            print name
            if verbose:
                self.show_input(name)
                
    def show_input(self, input_name):
        """
        Show the content of input "input_name".
        
        Args:
            - input_name (STR): name of the sem_input to show
        """
        sem_input = self.sem_inputs.get(input_name, None)
        if sem_input:
            propositions = sem_input['propositions']
            sequence = sem_input['sequence']
            timing = sem_input['timing']
            for i in range(len(sequence)):
                print 't: %.1f, prop: %s' %(timing[i], ' , '.join(propositions[sequence[i]]))
                               
    def sem_generator(self, input_name, verbose=False):
        """
        Creates a generator based on a semantic_data loaded by TCG_LOADER.load_sem_input().
        Each time next() function is called, returns a set of concept instances as well as the next time at which the generator should be called.
        
        Args:
            - input_name (STR): name of the sem_input to be loaded in the generator.
            - verbose (BOOL): Flag
        
        Yields:
            - next_input ([INST], INT, STR): array of concept instances, the next time at which the generator should be called, the proposition in text format.
        """
        sem_input = self.sem_inputs[input_name]
        propositions = sem_input['propositions']
        sequence = sem_input['sequence']
        timing = sem_input['timing']
        
        next_timing = timing[0]
        yield ([], next_timing, '')
            
        for idx in range(len(sequence)):          
            prop_name = sequence[idx]
            proposition = propositions[prop_name]
            if verbose:
                print 'sem_input <- t: %.1f, prop: %s' %(timing[idx], ' , '.join(proposition))
            instances = self.interpreter.prop_interpreter(proposition)
            
            next_idx = idx + 1       
            if next_idx<len(timing):
                next_time = timing[next_idx]
            else:
                next_time = None
            
            yield (instances, next_time, ' , '.join(proposition))
        
        self.interpreter.reset()
    
    def save(self, file_name, file_path):
        """
        Saves its content as json.
        """
        my_file = file_path + file_name + '_speed_' + str(self.speed_param)
        if not(os.path.exists(file_path)):
            os.mkdir(file_path)
        with open(my_file, 'wb') as f:
            json.dump(self.sem_inputs, f, sort_keys=True, indent=4, separators=(',', ': '))

class UTTER_GENERATOR(object):
    """
    """
    def __init__(self, ling_inputs, speed_param=1, offset=10):
        self.ling_inputs = ling_inputs
        self.speed_param = speed_param
        self.offset = offset
        self.preprocess_inputs()
    
    def preprocess_inputs(self):
        """
        """
        for name, ling_input in self.ling_inputs.iteritems():
            utter_rate = ling_input['utter_rate']*self.speed_param
            utterance = ling_input['utterance']
            timing = [t*self.speed_param for t in ling_input['timing']]
            if utter_rate and not(timing):
                ling_input['timing'] = [i*utter_rate + self.offset for i in range(len(utterance))]
            if not(timing) and not(utter_rate):
                print "PREPROCESSING ERROR: Provide either timing or rate for %s" %name
    
    def show_options(self, verbose = False):
        """
        Print the input names.
        If verbose, show the content of each input.
        """
        for name, ling_input in self.ling_inputs.iteritems():
            print name
            if verbose:
                self.show_input(name)
                
    def show_input(self, input_name):
        """
        Show the content of input "input_name".
        """
        ling_input = self.ling_inputs.get(input_name, None)
        if ling_input:
            utterance = ling_input['utterance']
            timing = ling_input['timing']
            for i in range(len(utterance)):
                print 't: %.1f, word-form: %s' %(timing[i], utterance[i])
    
    def utter_generator(self, input_name, verbose=False):
        """
        Creates a generator based on a linguistic_data loaded by TCG_LOADER.load_ling_input().
        Eeach time next() function is called, returns a word-form (STRING) as well as the next time at which the generator should be called.
        Args:
            - ling_input: a linguistic input dict loaded using load_ling_input()
        
        Yields:
            - next_input (STR, INT): word form input and the next time at which the generator should be called.
        """        
        ling_input = self.ling_inputs[input_name]
        utterance = ling_input['utterance']
        timing = ling_input['timing']
        
        next_timing = timing[0]
        yield ('', next_timing)
            
        for idx in range(len(utterance)):          
            word_form = utterance[idx]
            if verbose:
                print 'ling_input <- t: %.1f, word_form: %s' %(timing[idx], word_form)
            
            next_idx = idx + 1       
            if next_idx<len(timing):
                next_time = timing[next_idx]
            else:
                next_time = None
            
            yield (word_form, next_time)
            
###############################################################################
if __name__=='__main__':
#    print "No test case implemented"
    test_sentence = "Your work is done"
    TTS = TEXT2SPEECH(rate_percent=80)
    TTS.utterance = test_sentence
    TTS.utter()
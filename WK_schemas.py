# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines World knowledge schemas for TCG.

"""
from __future__ import division

from schema_theory import SYSTEM_SCHEMA, KNOWLEDGE_SCHEMA, SCHEMA_INST, LTM, WM
#import TCG_graph

####################################
##### WORLD KNOWLEDGE SCHEMAS ######
####################################
class WK_FRAME_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    World knowledge Frame knowledge schema
    Data:
    - KNOWEDGE SCHEMA data:
        - id (int): Unique id
        - name (str): schema name
        - LTM (LTM): Associated long term memory.
        - content (WK_FRAME): WK_FRAME object
        - init_act (float): Initial activation value.
    - trigger = (CPT))
    """
    def __init__(self, name, frame, init_act):
        """
        Args:
            - name (STR):
            - frame (WK_FRAME):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=frame.name, content=frame, init_act=init_act)
        self.trigger = frame.trigger
    
    def is_triggered(self, concept):
        """
        Returns true if the concept triggers the instantiation of the WK_FRAME_SCHEMA.
        """
        return concept.match(self.trigger.concept, match_type = "is_a")
    
#    def FrameMatch(self, SemRep, SemRep_subgraphs, wk_frame_schema, trigger_sem_node_name):
#        """
#        Defines the condition of instantiation of the WK_FRAME_SCHEMA based on the state of Semantic Representation (SemRep).
#        
#        Notes:
#            - Here the trigger is given. This is is mostly for running efficiency.
#        """
#        sub_iso = self.FrameMatch_cat(SemRep, SemRep_subgraphs, wk_frame_schema, trigger_sem_node_name)
#        return sub_iso
#    
#    def FrameMatch_cat(self, SemRep, SemRep_subgraphs, wk_frame_schema, trigger_sem_node_name):
#        """
#        Computes the categorical matches (match/no match) -> Returns the sub-graphs isomorphisms. This is the main filter for instantiation.
#        """
#        wk_frame_graph = self.content.graph 
#        trigger_name = self.trigger.name
#        # Build wk_frame_graph subgraphs. 
#        def subgraph_filter(subgraph): # Only the subgraph that contain the trigger are considered as legal for partial match.
#            return trigger_name in subgraph.nodes()
#                
#        wk_frame_subgraphs = TCG_graph.build_submultigraphs(wk_frame_graph, induced='edge', subgraph_filter=subgraph_filter)
#        
#        node_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a")
#    #        node_frame_match = lambda frame1, frame2: (frame1 == frame2) # Frame values have to match
#        edge_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a") # "equal" for strict matching
#       
#        nm = TCG_graph.node_iso_match("concept", "", node_concept_match)
#        em = TCG_graph.edge_iso_match("concept", "", edge_concept_match)
#    
#        def iso_filter(iso, trigger_sem_node_name):
#            sem_node_name = iso['nodes'].get(trigger_name, None)
#            if not(sem_node_name) or (sem_node_name != trigger_sem_node_name):
#                return False
#            return True
#            
#        sub_iso = TCG_graph.find_max_partial_iso(SemRep, SemRep_subgraphs, wk_frame_graph, wk_frame_subgraphs, node_match=nm, edge_match=em)
#        sub_iso = [s for s in sub_iso if iso_filter(s, trigger_sem_node_name)]
#        
#        return sub_iso

class WK_FRAME_SCHEMA_INST(SCHEMA_INST):
    """
    World knowledge frame schema instance. 
     - expressed
     - covers ({"nodes":{}, "edges"={}}): maps WK_FRAME nodes and edges (in content) to SemRep elements (in the trace) (Maps the nodes and edges names to SemRep obj)
    """
    def __init__(self, wk_frame_schema, trace, mapping={"nodes":{}, "edges":{}}, copy=True):
        SCHEMA_INST.__init__(self, schema=wk_frame_schema, trace=trace)
        self.expressed = False
        self.covers = {}
        if copy:
            (wk_frame_copy, c) = wk_frame_schema.content.copy()
            self.content = wk_frame_copy
            if mapping:
                new_node_mapping  = dict([(c[k], v) for k,v in mapping['nodes'].iteritems()])
                new_edge_mapping  = dict([((c[k[0]], c[k[1]]), v) for k,v in mapping['edges'].iteritems()])
                new_mapping= {'nodes':new_node_mapping, 'edges':new_edge_mapping}
                self.covers = new_mapping
        
        else:
             self.covers = mapping
        
##########################################
##### WORLD KNOWLEDGE SYSTEM SCHEMAS #####
##########################################
class WK_FRAME_LTM(LTM):
    """
     Initilize the state of the FRAME LTM with WK_frame_schemas based on the content of frame_knowledge
       
    Args:
        - frame_knowledge (FRAME_KNOWLEDGE):
    """
    def __init__(self, name='WK_frame_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_wk_frame_retrieval')
        self.frame_knowledge = None
        self.params['init_act'] = 1
        
    def initialize(self, frame_knowledge):
        """
        Initilize the state of the FRAME LTM with frame_schemas based on the content of frame_knowledge
       
        Args:
            - frame_knowledge (FRAME_KNOWLEDGE):
        """
        self.frame_knowledge = frame_knowledge
        
        for frame in frame_knowledge.frames:
            new_schema = WK_FRAME_SCHEMA(name=frame.name, frame=frame, init_act=self.params['init_act'])
            self.add_schema(new_schema)
    
    def process(self):
        self.outputs['to_wk_frame_retrieval'] = self.schemas
       
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(WK_FRAME_LTM, self).get_info()
        data['params'] = self.params
        return data

class WK_FRAME_WM(WM):
    """
    """
    def __init__(self, name='WK_frame_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_phonological_WM_C')
        self.add_port('IN', 'from_wk_frame_retrieval')
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('OUT', 'to_semantic_WM')
        
    def reset(self):
        """
        """
        super(WK_FRAME_WM, self).reset()
        
    def process(self):
        """
        """
#        sem_input = self.inputs['from_semantic_WM']
        phon_activations = self.inputs['from_phonological_WM_C']
        new_wk_frame_insts= self.inputs['from_wk_frame_retrieval']

        if new_wk_frame_insts:
            # Add new instances
            for inst in new_wk_frame_insts:
                self.add_instance(inst, inst.activity) 
            wk_output = self.apply_WK()
            if wk_output:
                self.outputs['to_semantic_WM']['instances'] =  wk_output
        
        activations = self.sem_WM_output()
        self.outputs['to_semantic_WM']['activations'] = activations
            
        self.convey_phon_activations(phon_activations)
        self.update_activations()
        self.prune()
    
    def apply_WK(self):
        """
        """
        wk_frame_insts = [i for i in self.schema_insts if not i.expressed]
        wk_output = []
        for inst in wk_frame_insts:
            #Send their wk_frame to SemWM.
            if inst.activity > self.params['C2']['confidence_threshold']:
                wk_output.append((inst.content, inst.name))
                inst.expressed = True
        return wk_output
        
    def sem_WM_output(self):
        """ Defines the activation output to semantic_WM.
        Returns a dictionary mapping wk_frame elements names of used wk_frame instances onto the respective frame activity.
        """
        output = {}
        insts = [i for i in self.schema_insts if i.expressed] # only look at expressed insts
        for wk_frame_inst in insts:
            activity = wk_frame_inst.activity
            wk_frame_names = [s.name for s in wk_frame_inst.content.nodes + wk_frame_inst.content.edges]
            for name in wk_frame_names:
                output[name] = activity
        return output
    
    def convey_phon_activations(self, phon_activations):
        """
        Propagates activations from PhonWM to wk_frame_WM.
        """
        if not(phon_activations):
            return
        for inst in self.schema_insts:
            val = phon_activations.get(inst.trace['trigger'], 0)
            inst.activation.E += val # No normalization
            
class WK_FRAME_RETRIEVAL(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name="WK_frame_retrieval"):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_wk_frame_LTM')
        self.add_port('IN', 'from_cxn_retrieval_C')
        self.add_port('OUT', 'to_wk_frame_WM')
        self.wk_frame_instances = []
    
    def reset(self):
        """
        """
        super(WK_FRAME_RETRIEVAL, self).reset()
        self.wk_frame_instances = []
    
    def process(self):
        """
        """
        phon_input = self.inputs['from_cxn_retrieval_C']
          
        wk_frame_schemas = self.inputs['from_wk_frame_LTM']
        if wk_frame_schemas and phon_input and phon_input['instances']:
            self.instantiate_wk_frames(phon_input, wk_frame_schemas)
            self.outputs['to_wk_frame_WM'] = self.wk_frame_instances

        self.wk_frame_instances = []
    
    def instantiate_wk_frames(self, phon_input, wk_frame_schemas):
        """
        """
        if not wk_frame_schemas or not phon_input or not phon_input['instances']:
            return
        phon_inst = phon_input['phon_inst']
        lex_instances = phon_input['instances']
        concepts = set([])
        for lex_instance in lex_instances:
            inst_concepts = [n.concept for n in lex_instance.content.SemFrame.nodes]
            concepts.update(inst_concepts)
            
        # Find triggers:   
        for concept in concepts:
            triggered_schemas = [schema for schema in wk_frame_schemas if schema.is_triggered(concept)]
            for wk_frame_schema in triggered_schemas:
                trace = trace = {"trigger":phon_inst.name, "schemas":[wk_frame_schema]}  
                new_instance = WK_FRAME_SCHEMA_INST(wk_frame_schema, trace)
                self.wk_frame_instances.append(new_instance)
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(WK_FRAME_RETRIEVAL, self).get_state()
        data['wk_frame_instances'] = [inst.name for inst in self.wk_frame_instances]
        return data
            
###############################################################################
if __name__=='__main__':
    print "No test case implemented"

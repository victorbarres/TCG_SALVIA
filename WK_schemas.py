# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines World knowledge schemas for TCG.

"""
from __future__ import division

from schema_theory import SYSTEM_SCHEMA, KNOWLEDGE_SCHEMA, SCHEMA_INST, LTM, WM
import TCG_graph

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
        - trigger_dict ({trigger_cpt:[FRAME_SCHEMA]})
    """
    def __init__(self, name='WK_frame_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_wk_frame_WM')
        self.frame_knowledge = None
        self.trigger_dict = {}
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
        self.set_trigger_dict()
    
    def process(self):
        self.outputs['to_wk_frame_WM'] = self.trigger_dict
    
    def set_trigger_dict(self):
        for wk_frame_schema in self.schemas:
            trig = wk_frame_schema.trigger.concept
            if trig not in self.trigger_dict:
                self.trigger_dict[trig] = [wk_frame_schema]
            else:
                self.trigger_dict[trig].append(wk_frame_schema)
       
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
        self.add_port('IN', 'from_wk_frame_LTM')
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('OUT', 'to_semantic_WM')
        
    def reset(self):
        """
        """
        super(WK_FRAME_WM, self).reset()
        
    def process(self):
        """
        """
        sem_input = self.inputs['from_semantic_WM']
        new_wk_frame_insts= self.inputs['from_cxn_retrieval_P']
        self.outputs['to_semantic_WM'] = {}
        if new_wk_frame_insts:
            self.add_new_insts(new_wk_frame_insts) 
            output = self.apply_WK(new_wk_frame_insts,sem_input)
            if output:
                self.outputs['to_semantic_WM']['instances'] =  output['sem_WM_output']
        
        activations = self.sem_WM_output()
        self.outputs['to_semantic_WM']['activations'] = activations
            
        self.convey_sem_activations(sem_input)
        self.update_activations()
        self.prune()
        
        """
        TO DO:
            - find the WK_FRAME that should be instantiated.
            - For this I need to allow for partial match
            - So I need largest subgraphs of SemRep that partially map onto frames.
            - Then I instantiate the Frames and link it to SemRep + send info to SemRep that is
            can be updated if it is a partial match.
            - The activation of the Frames supports some aspects of the SemRep.
            - In SemRep, edges between same nodes in multigraph compete.
            - Question: Are the frames triggered by the SemRep or by the lexical items?
            - I can simply force the posting of the lexical item content onto SemWM directly as they are 
            recovered (any element construction marked as done might need to be automatically expressed in SemRep.)
            - On the other hand, it might be worth it considering the fact that lexical items directly tie to WK.
            - They could trigger the recovery of any frames that matches them. (simple).
            - Then those would project onto the SemRep where the lexical content should serve as the way to link the two (hinges).
            - The difficult part is that now, the GrammaticalWM needs to check whether or not the information it wants to post is already there,
            which means graph iso matching from Sem to GramWM
        """
    
    def apply_WK(self, sem_input):
        """
        """
        wk_frame_insts = [i for i in self.schema_insts if not i.expressed]
        wk_output = []
        for inst in wk_frame_insts:
            #Send their wk_frame to SemWM.
            wk_output.append((inst.content, inst.covers))
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
    
    def convey_sem_activations(self, sem_input):
        """
        """
        pass
            
class WK_FRAME_RETRIEVAL(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name="WK_frame_retrieval"):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_wk_frame_LTM')
        self.add_port('IN', 'from_semantic_WM')
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
        SemRep = self.inputs['from_semantic_WM']
          
        wk_frame_dict = self.inputs['from_wk_frame_LTM']
        if wk_frame_dict and SemRep:
            self.instantiate_wk_frames(SemRep, wk_frame_dict)
            self.outputs['to_wk_frame_WM'] = self.wk_frame_instances
            
            # Marked all SemRep elements as processed by WK_WM
            for n, d in SemRep.nodes(data=True):
                d['processed'].append('wk_WM')
            for u,v,d in SemRep.edges(data=True):
                d['processed'].append('wk_WM')
        self.wk_frame_instances = []
    
    def instantiate_wk_frame(self, SemRep, wk_frame_dict):
        """
        """
        if not wk_frame_dict:
            return
            
        # Build SemRep subgraphs
        def subgraph_filter(subgraph): # I NEED TO FIX THAT TO HANDLE MULTIGRAPHS!
            """
            Returns True only if at least one node or edge is tagged as new.
            """
            for n,d in subgraph.nodes(data=True):
                if 'wk_WM' not in d['processed']:
                    return True
            for n1,n2,d in subgraph.edges(data=True):
                if 'wk_WM' not in d['processed']:
                    return True
            return False
        SemRep_subgraphs = TCG_graph.build_submultigraphs(SemRep, induced='edges', subgraph_filter=subgraph_filter)
        
        # Find triggers:
        for trigger_sem_node in [n for n in SemRep.nodes() if (n.concept in wk_frame_dict) and ('wk_WM' not in n.processed)]:
            wk_frame_schemas = wk_frame_dict[trigger_sem_node.concept]
            for wk_frame_schema in wk_frame_schemas:
                sub_iso = self.FrameMatch_cat(SemRep, SemRep_subgraphs, wk_frame_schema, trigger_sem_node.name)
                for a_sub_iso in sub_iso:
                    trace = trace = {"trigger":trigger_sem_node, "semrep":{"nodes":a_sub_iso["nodes"].values(), "edges":a_sub_iso["edges"].values()}, "schemas":[wk_frame_schema]}
                    node_mapping  = dict([(k.name, v) for k,v in a_sub_iso['nodes'].iteritems()])
                    edge_mapping  = dict([((k[0].name, k[1].name), v) for k,v in a_sub_iso['edges'].iteritems()])
                    mapping = {'nodes':node_mapping, 'edges':edge_mapping}    
                    new_instance= WK_FRAME_SCHEMA_INST(wk_frame_schema, trace, mapping)
                    self.wk_frame_instances.append(new_instance)
                    
    def FrameMatch_cat(self, SemRep, SemRep_subgraphs, wk_frame_schema, trigger_sem_node_name):
        """
        Computes the categorical matches (match/no match) -> Returns the sub-graphs isomorphisms. This is the main filter for instantiation.
        """
        wk_frame_graph = wk_frame_schema.content.graph 
        trigger_name = wk_frame_schema.trigger.name
        # Build wk_frame_graph subgraphs. 
        def subgraph_filter(subgraph): # Only the subgraph that contain the trigger are considered as legal for partial match.
            return trigger_name in subgraph.nodes()
                
        wk_frame_subgraphs = TCG_graph.build_submultigraphs(wk_frame_graph, induced='edges', subgraph_filter=subgraph_filter)
        
        node_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a")
#        node_frame_match = lambda frame1, frame2: (frame1 == frame2) # Frame values have to match
        edge_concept_match = lambda cpt1,cpt2: cpt1.match(cpt2, match_type="is_a") # "equal" for strict matching
       
        nm = TCG_graph.node_iso_match("concept", "", node_concept_match)
        em = TCG_graph.edge_iso_match("concept", "", edge_concept_match)

        def iso_filter(iso, trigger_sem_node_name):
            sem_node_name = iso['nodes'].get(trigger_name, None)
            if not(sem_node_name) or (sem_node_name != trigger_sem_node_name):
                return False
            return True
            
        sub_iso = TCG_graph.find_max_partial_iso(SemRep, SemRep_subgraphs, wk_frame_graph, wk_frame_subgraphs, node_match=nm, edge_match=em)
        sub_iso = [s for s in sub_iso if iso_filter(s, trigger_sem_node_name)]
        
        return sub_iso
    
    
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

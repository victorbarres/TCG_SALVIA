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
    - trigger = ([FRAME_NODE]))
    """
    def __init__(self, name, frame, init_act):
        """
        Args:
            - name (STR):
            - frame (WK_FRAME):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=frame.name, content=frame, init_act=init_act)
        self.trigger = frame.trigger
    
    def has_trigger(self, concept):
        """
        If the concept is a trigger of the WK_FRAME_SCHEMA, returns the corresponding trigger.
        Else returns None
        """
        for trig in self.trigger:
            if concept.match(trig.concept, match_type = "is_a"):
                return True
        return False
    

class WK_FRAME_SCHEMA_INST(SCHEMA_INST):
    """
    World knowledge frame schema instance. 
     - expressed
     - covers (STR): name of the PHON_INST that triggered the instantatiation
    """
    def __init__(self, wk_frame_schema, trace, covers):
        old_frame =  wk_frame_schema.content
        (new_frame, name_corr) = old_frame.copy()
#        new_name = "%s_%s" %(old_frame.name, trigger_concept.name)
#        new_frame.name = new_name
#        new_frame.trigger.concept = trigger_concept
        new_frame._create_graph()
        new_wk_frame_schema = WK_FRAME_SCHEMA(new_frame.name, new_frame, wk_frame_schema.init_act)
        SCHEMA_INST.__init__(self, schema=new_wk_frame_schema, trace=trace)
        self.expressed = False
        self.covers = covers
        self.trigger = new_wk_frame_schema.trigger
        
    def has_trigger(self, concept):
        """
        If the concept is a trigger of the WK_FRAME_SCHEMA, returns the corresponding trigger.
        Else returns None
        """
        for trig in self.trigger:
            if concept.match(trig.concept, match_type = "is_a"):
                return True
        return False
        
    def got_trigger(self, concept):
        """
        """
        trig = next((t for t in self.trigger if concept.match(t.concept, match_type = "is_a") ), None)
        trig.concept = concept
        self.content._create_graph()
        self.trigger.remove(trig)
        
    def is_triggered(self):
        """
        """
        return self.trigger == []
        
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
        self.outputs['to_semantic_WM'] = {}
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
            val = phon_activations.get(inst.covers, 0)
            inst.activation.E += val # No normalization
            
class WK_FRAME_RETRIEVAL(SYSTEM_SCHEMA):
    """
    """
    def __init__(self, name="WK_frame_retrieval"):
        SYSTEM_SCHEMA.__init__(self,name)
        self.add_port('IN', 'from_wk_frame_LTM')
        self.add_port('IN', 'from_lex_cxn_retrieval_C')
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
        phon_input = self.inputs['from_lex_cxn_retrieval_C']
          
        wk_frame_schemas = self.inputs['from_wk_frame_LTM']
        if wk_frame_schemas and phon_input and phon_input['instances']:
            self.instantiate_wk_frames(phon_input, wk_frame_schemas)
            self.outputs['to_wk_frame_WM'] = []
        for inst in [inst for inst in self.wk_frame_instances if inst.is_triggered()]:
            print inst.name
            self.outputs['to_wk_frame_WM'].append(inst)
            self.wk_frame_instances.remove(inst)
    
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
        names = []
        for wk_frame_inst in self.wk_frame_instances:
            for concept in concepts:
                if wk_frame_inst.has_trigger(concept):
                    wk_frame_inst.got_trigger(concept)
                    names.append(wk_frame_inst.content.name)
                    print "%i: %s by %s" %(self.t, wk_frame_inst.content.name, concept.name)

        for wk_frame_schema in [s for s in wk_frame_schemas if s.name not in names]:
            new_instance = None
            for concept in concepts:
                if wk_frame_schema.has_trigger(concept):
                    if not(new_instance):
                        trace = {"trigger":[concept], "schemas":[wk_frame_schema]}  
                        new_instance = WK_FRAME_SCHEMA_INST(wk_frame_schema, trace, phon_inst.name)
                        new_instance.got_trigger(concept)
                        print "%i: %s by %s" %(self.t, new_instance.content.name, concept.name)
                    else:
                        new_instance.got_trigger(concept)
                        print "%i: %s by %s" %(self.t, new_instance.content.name, concept.name)
            if new_instance:
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

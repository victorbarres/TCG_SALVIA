# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines World knowledge schemas for TCG.

"""
from __future__ import division

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, LTM, WM

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
    """
    def __init__(self, name, frame, init_act):
        """
        Args:
            - name (STR):
            - frame (WK_FRAME):
        """
        KNOWLEDGE_SCHEMA.__init__(self, name=frame.name, content=frame, init_act=init_act)

class WK_FRAME_SCHEMA_INST(SCHEMA_INST):
    """
    World knowledge frame schema instance. 
    """
    def __init__(self, frame_schema, trace):
        SCHEMA_INST.__init__(self, schema=frame_schema, trace=trace)
        content_copy = frame_schema.content.copy()
        self.content = content_copy    
        
##########################################
##### WORLD KNOWLEDGE SYSTEM SCHEMAS #####
##########################################
class FRAME_LTM(LTM):
    """
     Initilize the state of the FRAME LTM with WK_frame_schemas based on the content of frame_knowledge
       
    Args:
        - frame_knowledge (FRAME_KNOWLEDGE):
    """
    def __init__(self, name='Frame_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_frame_WM')
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
        self.outputs['to_frame_WM'] =  self.schemas
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(FRAME_LTM, self).get_info()
        data['params'] = self.params
        return data

class FRAME_WM(WM):
    """
    """
    def __init__(self, name='Frame_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_frame_LTM')
        self.add_port('OUT', 'to_semantic_WM')
        self.add_port('IN', 'from_semantic_WM')
        
    def reset(self):
        """
        """
        super(FRAME_WM, self).reset()
        
    def process(self):
        """
        """
        pass
            
###############################################################################
if __name__=='__main__':
    print "No test case implemented"

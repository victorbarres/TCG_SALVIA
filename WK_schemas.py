# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines World knowledge schemas for TCG.

"""
from __future__ import division

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, LTM, WM
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
class WK_FRAME_LTM(LTM):
    """
     Initilize the state of the FRAME LTM with WK_frame_schemas based on the content of frame_knowledge
       
    Args:
        - frame_knowledge (FRAME_KNOWLEDGE):
    """
    def __init__(self, name='WK_frame_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_wk_frame_WM')
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
        self.outputs['to_wk_frame_WM'] = self.schemas
        
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
        pass
            
###############################################################################
if __name__=='__main__':
    print "No test case implemented"

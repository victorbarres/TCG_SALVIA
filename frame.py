# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define semantic network related classes for TCG.
"""
from __future__ import division
from knowledge_rep import FRAME

class WK_FRAME(FRAME):
    """ Defines a WK_Frame object  
    Data (inherited):
        - name (STR): WK frame name
        - preference (FLOAT): WK frame preference (usage preferences, optional)
        - nodes ([FRAME_NODES]): Set of WK FRAME nodes.
        - edges ([FRAME_REL]): Set of WK FRAME relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
     - conceptual_knowledge (CONCEPTUAL_KNOWLEDGE): The conceptual knowledge instance the WK frame is part of.
    """
    def __init__(self, name='',  frame_knowledge=None):
        FRAME.__init__(self, name=name)
        self.frame_knowledge = frame_knowledge
        
class FRAME_KNOWLEDGE(object):
    """Frame knowledge. Simply defined as a set of WK_Frames.
    """
    def __init__(self):
        self.frames = []
    
    def add_frame(self, frame):
        """Add a frame (WK_FRAME) to Frame knowledge while linking the WK_frame to back to the Frame_knowledge.
        """
        if frame.name in [f.name for f in self.frames]:
            error_msg = "Frame %s already defined in frame knowledge" % frame.name
            raise ValueError(error_msg)
        self.frames.add(frame)
        frame.frame_knowledge = self

###############################################################################
if __name__=='__main__':
    print "No test case implemented"
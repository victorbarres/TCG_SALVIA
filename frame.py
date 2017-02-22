# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines semantic network related classes for TCG.
"""
from __future__ import division
from knowledge_rep import FRAME, FRAME_NODE, FRAME_REL

class WK_FRAME_NODE(FRAME_NODE):
    """Define WK_FRAME_NODE
    
    Data:
        - trigger (BOOL) = True if the node is the WK_FRAME trigger
    """
    def __init__(self):
        FRAME_NODE.__init__(self)
        self.trigger = False
    
class WK_FRAME_REL(FRAME_REL):
    """ now doesn't add anythong to the FRAME_REL class
    """
    def __init__(self):
        FRAME_REL.__init__(self)
    
class WK_FRAME(FRAME):
    """ Defines a WK_Frame object  
    Data (inherited):
        - name (STR): WK frame name
        - preference (FLOAT): WK frame preference (usage preferences, optional)
        - nodes ([FRAME_NODES]): Set of WK FRAME nodes.
        - edges ([FRAME_REL]): Set of WK FRAME relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
     - frame_knowledge (FRAME_KNOWLEDGE): The frame knowledge instance the WK frame is part of.
     - trigger (FRAME_NODE): The frame node whose concept serve as a trigger for the WK_FRAME
    """
    def __init__(self, name='',  frame_knowledge=None):
        FRAME.__init__(self, name=name)
        self.frame_knowledge = frame_knowledge
        self.trigger = None
        
    def show(self):
        """
        Display the WK_FRAME.
        Uses the display method defined in TCG_VIEWER class
        """
        from viewer import TCG_VIEWER
        TCG_VIEWER.display_wk_frame(self, file_type='png', show=True)
        
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
        self.frames.append(frame)
        frame.frame_knowledge = self

###############################################################################
if __name__=='__main__':
    print "No test case implemented"
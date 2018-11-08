# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines semantic network related classes for TCG.
"""
from knowledge_rep import FRAME, FRAME_NODE, FRAME_REL
import networkx as nx


class WK_FRAME_NODE(FRAME_NODE):
    """Define WK_FRAME_NODE
    
    Data:
        - trigger (BOOL) = True if the node is the WK_FRAME trigger
        - frame (BOOL) (similar as the use in SemRep and SemFrame. To be replaced by ref)
    """

    def __init__(self):
        FRAME_NODE.__init__(self)
        self.trigger = False
        self.frame = False

    def copy(self):
        new_node = WK_FRAME_NODE()
        new_node.name = '{}_{}'.format(self.name, new_node.id)
        new_node.frame = self.frame
        name_corr = (self.name, new_node.name)
        new_node.concept = self.concept
        return (new_node, name_corr)


class WK_FRAME_REL(FRAME_REL):
    """ now doesn't add anythong to the FRAME_REL class
    """

    def __init__(self):
        FRAME_REL.__init__(self)

    def copy(self):
        new_rel = WK_FRAME_REL()
        new_rel.name = '{}_{}'.format(self.name, new_rel.id)
        name_corr = (self.name, new_rel.name)
        new_rel.concept = self.concept
        new_rel.pfrom = self.pFrom
        new_rel.pTo = self.pTo
        return (new_rel, name_corr)


class WK_FRAME(FRAME):
    """ Defines a WK_Frame object  
    Data (inherited):
        - name (STR): WK frame name
        - nodes ([FRAME_NODES]): Set of WK FRAME nodes.
        - edges ([FRAME_REL]): Set of WK FRAME relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the graph.
            Each node and edge have the additional 'concept' attribute derived from their respective node.concept and edge.concept
     - preference (FLOAT): WK frame preference (usage preferences, optional)
     - frame_knowledge (FRAME_KNOWLEDGE): The frame knowledge instance the WK frame is part of.
     - trigger ([FRAME_NODE]): The frame nodes whose concept serve as a trigger for the WK_FRAME
    """

    def __init__(self, name='', frame_knowledge=None):
        FRAME.__init__(self, name=name)
        self.preference = 1.0
        self.frame_knowledge = frame_knowledge
        self.trigger = []

    def copy(self):
        """
        """
        new_frame = WK_FRAME()
        new_frame.name = self.name
        new_frame.preference = self.preference
        new_frame.frame_knowledge = self.frame_knowledge
        node_corr = {}
        name_corr = {}
        for node in self.nodes:
            (new_node, c) = node.copy()
            node_corr[node] = new_node
            name_corr[c[0]] = c[1]
            new_frame.nodes.append(new_node)
        for edge in self.edges:
            (new_edge, c) = edge.copy()
            name_corr[c[0]] = c[1]
            new_edge.pFrom = node_corr[edge.pFrom]
            new_edge.pTo = node_corr[edge.pTo]
            new_frame.edges.append(new_edge)
        new_frame.trigger = [node_corr[t] for t in self.trigger]
        new_frame._create_graph()

        return (new_frame, name_corr)

    def _create_graph(self):
        graph = nx.MultiDiGraph()
        for node in self.nodes:
            graph.add_node(node.name, concept=node.concept, frame=node.frame, dat=(node.concept, node.frame))
        for edge in self.edges:
            pFrom = edge.pFrom.name if edge.pFrom else None
            pTo = edge.pTo.name if edge.pTo else None
            graph.add_edge(pFrom, pTo, name=edge.name, concept=edge.concept)

        self.graph = graph

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
            error_msg = "Frame {} already defined in frame knowledge".format(frame.name)
            raise ValueError(error_msg)
        self.frames.append(frame)
        frame.frame_knowledge = self


###############################################################################
if __name__ == '__main__':
    print("No test case implemented")

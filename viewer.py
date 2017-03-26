# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 16:13:10 2015

@author: Victor Barres

Defines the TCG_VIEWER class that allows to view a certain dataset into the TCG viewer.

Can be also be use in command line: python viewer.py
"""
from __future__ import division
import os, shutil
import SimpleHTTPServer
import SocketServer
import webbrowser
import subprocess
import pydot


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

from construction import TP_PHON, TP_SLOT
from percept import PERCEPT_CAT
from perceptual_schemas import PERCEPT_SCHEMA_REL

class TCG_VIEWER:
    """
    Connects the simulation to the the TCG viewer.
    
    Data:
        - SERVER_PORT (INT): Server port value, default 8080.
        - VIEWER_PATH (STR): path to the viewer main directory: "viewer/"
        - data_path (STR): Path to the data folder that needs to be displayed.
        - tmp (STR): Temp folder.
    """

    def __init__(self, data_path, viewer_path="viewer/"):
        """
        Requires the path (data_path) to the folder that contains the data to be diplayed in the viewer.
        """
        self.SERVER_PORT = 8000
        self.VIEWER_PATH = "viewer/"
        self.VIEWER_TMP = self.VIEWER_PATH + "tmp/"
        self.data_path = data_path
        self.conceptual_knowledge = None
        self.perceptual_knowledge = None
        self.conceptualization = None
        self.grammar = None
        self.scene = None
    ######################
    ### Server methods ###   
    def start_viewer(self):
        """
        Starts the viewer.
        """
        self._load_data()
        self._start_server()
        
    def _start_server(self):
        """
        Setting up server at port PORT serving the viewer folder defined by viewer_path
        and opens default browser to "http://localhost:PORT"
        """
        PORT = self.SERVER_PORT
    
        os.chdir(self.VIEWER_PATH)
    
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    
        httpd = SocketServer.TCPServer(("", PORT), Handler)
    
        print "serving at port", PORT
        webbrowser.open_new("http://localhost:" + str(PORT))
        httpd.serve_forever()
        
    def _load_data(self):
        """
        Copies and creates all the required data in viewer/tmp directory.
        """
        from loader import TCG_LOADER
        if os.path.exists(self.VIEWER_TMP):
            shutil.rmtree(self.VIEWER_TMP)
        print os.getcwd()
        shutil.copytree(self.data_path, self.VIEWER_TMP)
        
        self.conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", self.VIEWER_TMP)
        self.perceptual_knowledge = TCG_LOADER.load_perceptual_knowledge("TCG_semantics.json", self.VIEWER_TMP)
        self.conceptualization = TCG_LOADER.load_conceptualization("TCG_semantics.json", self.VIEWER_TMP, self.conceptual_knowledge, self.perceptual_knowledge)
        self.grammar = TCG_LOADER.load_grammar("TCG_grammar.json", self.VIEWER_TMP, self.conceptual_knowledge)
        self.scene = TCG_LOADER.load_scene("TCG_scene.json", self.VIEWER_TMP)
        
        self._create_cxn_imgs()
        self._create_concept_img()
        self._create_percept_img()
        self._create_conceptualizer_img()

    #####################################
    ### LTM knowledge display methods ###   
    def _create_concept_img(self):
        """
        Create graph image for the conceptual knowledge.
        Uses graphviz with pydot implementation.
        """        
        prog = 'neato'
        file_type = 'svg'
        
        cpt_folder = self.VIEWER_TMP + 'cpt/'        
        
        if os.path.exists(cpt_folder):
            shutil.rmtree(cpt_folder)
        
        os.mkdir(cpt_folder)
        
        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'RL'
        
        if not(self.conceptual_knowledge):
            "Conceptual knowledge was not loaded."
            return
        
        cpt_graph = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth, overlap='false')
        cpt_graph.set_rankdir(rankdir)
        cpt_graph.set_fontname(font_name)
        
        cluster_cpt = TCG_VIEWER._create_concepts_cluster(self.conceptual_knowledge)
        cpt_graph.add_subgraph(cluster_cpt)
        
        file_name = cpt_folder + "TCG_concepts" + ".gv"
        cpt_graph.write(file_name)
        
        # This is a work around becauses dot.write or dot.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
    
    def _create_percept_img(self):
        """
        Create graph image for the percetual knowledge.
        Uses graphviz with pydot implementation.
        """  
        prog = 'neato'
        file_type = 'svg'
        
        per_folder = self.VIEWER_TMP + 'per/'        
        
        if os.path.exists(per_folder):
            shutil.rmtree(per_folder)
        
        os.mkdir(per_folder)
        
        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'RL'
        
        if not(self.perceptual_knowledge):
            "Perceptual knowledge was not loaded."
            return
        
        per_graph = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth, overlap='false')
        per_graph.set_rankdir(rankdir)
        per_graph.set_fontname(font_name)
        
        cluster_per = TCG_VIEWER._create_percepts_cluster(self.perceptual_knowledge)
        per_graph.add_subgraph(cluster_per)
        
        
        file_name = per_folder + 'TCG_percepts' + ".gv"
        per_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        return per_graph
    
    def _create_conceptualizer_img(self, show_cpt=True):
        """
        Create graph image for the conceputalizer.
        Uses graphviz with pydot implementation.
        """        
        prog = 'dot'
        file_type = 'svg'
        
        czer_folder = self.VIEWER_TMP + 'czer/'        
        
        if os.path.exists(czer_folder):
            shutil.rmtree(czer_folder)
        
        os.mkdir(czer_folder)
        
        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'RL'
        
        if not(self.conceptualization):
            print "Conceptualization was not loaded."
            return
        
        if show_cpt and not(self.conceptual_knowledge):
            print "conceptual knowledge not loaded"
            return
        
        czer_graph = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth, overlap='false')
        czer_graph.set_rankdir(rankdir)
        czer_graph.set_fontname(font_name)

        cpt_knowledge=None
        if show_cpt:
            cpt_knowledge = self.conceptual_knowledge
        
        cluster_czer = TCG_VIEWER._create_conceptualizer_cluster(self.conceptualization, cpt_knowledge=cpt_knowledge)
        czer_graph.add_subgraph(cluster_czer)
        
        file_name = czer_folder + 'TCG_conceptualizer' + ".gv"
        czer_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
    
    def _create_cxn_imgs(self):
        """
        Create graph images for all the constructions.
        Uses graphviz with pydot implementation.
        
        Obsolete, check format of display_cxn
        """        
        prog = 'dot'
        file_type = 'svg'
        
        cxn_folder = self.VIEWER_TMP + 'cxn/'  
        
        if os.path.exists(cxn_folder):
            shutil.rmtree(cxn_folder)
        
        os.mkdir(cxn_folder)

        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'LR'
        
        if not(self.grammar):
            "Grammar was not loaded."
            return
        
        for cxn in self.grammar.constructions:
            cxn_graph = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth)
            cxn_graph.set_rankdir(rankdir)
            cxn_graph.set_fontname(font_name)
            
            cluster_cxn = TCG_VIEWER._create_cxn_cluster(cxn)
            cxn_graph.add_subgraph(cluster_cxn)
            
            file_name = cxn_folder + cxn.name + ".gv"
            cxn_graph.write(file_name)
            
        cxn_graphs = os.listdir(cxn_folder)
        for cxn_file in cxn_graphs:
            cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, cxn_folder + cxn_file, cxn_folder + cxn_file, file_type)
            subprocess.call(cmd, shell=True)
    
    ##############################
    ### Static display methods ###   
    @staticmethod
    def _obj_to_color(my_obj):
        """
        Takes and object and returns a color value in RGB deterministically defined from object hash.
        """
        char_len = 2
        max_val = (2**8 -1) #8bit
        h = hash(my_obj)
        int1= h % max_val
        int2 =  hash(str(int1)) % max_val
        int3 =  hash(str(int2)) % max_val
        
        get_hex = lambda i : hex(i)[2:] # get hex value striped the initial '0x'
        pad_hex = lambda i : '0'*(char_len - len(get_hex(i))) + get_hex(i)
        rgb_str = '#' + pad_hex(int1) + pad_hex(int2) + pad_hex(int3)
        return rgb_str
        
    @staticmethod
    def _create_concepts_cluster(cpt_knowledge, name=None):
        """
        Returns a DOT cluster containing all the information regarding the conceptual knowledge.
        """
        font_name = 'consolas'
        font_size = '16'
        color = 'black'
        node_shape = 'box'
        style = 'rounded'
        fill_color = 'white'
        
        if not(name):
            name = "conceptual_knowledge"
        
        cluster_name = name
        cluster_cpt = pydot.Cluster(cluster_name)
        
        for concept in cpt_knowledge.nodes:
            label = '<<FONT FACE="%s">%s</FONT>>' %(font_name, concept.name)
            new_node = pydot.Node(concept.name, label=label, color=color, style=style, shape=node_shape, fillcolor=fill_color, fontsize=font_size)
            cluster_cpt.add_node(new_node)
        
        for sem_rel in cpt_knowledge.edges:
            label = ''
#           label = sem_rel.type
            new_edge = pydot.Edge(sem_rel.pFrom.name, sem_rel.pTo.name, label=label, fontsize=font_size)
            cluster_cpt.add_edge(new_edge)
        
        return cluster_cpt
    
    @staticmethod
    def _create_percepts_cluster(per_knowledge, name=None):
        """
        Returns a DOT cluster containing all the information regarding the perceptual knowledge.
        """
        font_name = 'consolas'
        font_size = '16'
        color = 'black'
        node_shape1 = 'box'
        node_shape2 = 'octagon'
        style = 'filled'
        fill_color = 'white'
        
        if not(name):
            name = "perceptual_knowledge"
        
        cluster_name = name
        cluster_per = pydot.Cluster(cluster_name)
        
        for per in per_knowledge.nodes:
            label = '<<FONT FACE="%s">%s</FONT>>' %(font_name, per.name)
            if isinstance(per, PERCEPT_CAT):
                node_shape=node_shape1
            else:
                node_shape=node_shape2
            new_node = pydot.Node(per.name, label=label, color=color, style=style, shape=node_shape, fillcolor=fill_color, fontsize=font_size)
            cluster_per.add_node(new_node)
        
        for sem_rel in per_knowledge.edges:
            label = ''
#           label = sem_rel.type
            new_edge = pydot.Edge(sem_rel.pFrom.name, sem_rel.pTo.name, label=label, fontsize=font_size)
            cluster_per.add_edge(new_edge)
        
        return cluster_per
    
    @staticmethod
    def _create_conceptualizer_cluster(conceptualization, cpt_knowledge=None, name=None):
        """
        Returns a DOT cluster containing all the information regarding the conceptualization.
        """
        font_name = 'consolas'
        font_size = '16'
        color = 'black'
        edge_color = 'red'
        node_shape1 = 'box'
        node_shape2 = 'octagon'
        style = 'filled'
        fill_color = 'white'
        
        if not(name):
            name = "conceptualization"
        
        cluster_name = name
        cluster_czer = pydot.Cluster(cluster_name)
        
        if not(cpt_knowledge):
            cluster_cpt = pydot.cluster('conceptual_knowledge')
            for cpt in conceptualization.per2cpt.values():
                label = '<<FONT FACE="%s">%s</FONT>>' %(font_name, cpt)
                node_shape=node_shape1
                new_node = pydot.Node(cpt, label=label, color=color, style=style, shape=node_shape, fillcolor=fill_color, fontsize=font_size)
                cluster_cpt.add_node(new_node)
            cluster_czer.add_subgraph(cluster_cpt)
        else:
            cluster_cpt = TCG_VIEWER._create_concepts_cluster(cpt_knowledge)
            cluster_czer.add_subgraph(cluster_cpt)
            
        cluster_per = pydot.Cluster('perceptual_knowledge')
        for per in conceptualization.per2cpt.keys():
            label = '<<FONT FACE="%s">%s</FONT>>' %(font_name, per)
            node_shape=node_shape2
            new_node = pydot.Node(per, label=label, color=color, style=style, shape=node_shape, fillcolor=fill_color, fontsize=font_size)
            cluster_per.add_node(new_node)
        
        cluster_czer.add_subgraph(cluster_per)
          
        
        for per, cpt in conceptualization.per2cpt.iteritems():
            label = ''
#           label = 'conceptualization'
            new_edge = pydot.Edge(per, cpt, label=label, fontsize=font_size, color=edge_color)
            cluster_czer.add_edge(new_edge)
       
        return cluster_czer
    
    @staticmethod
    def _create_wk_frame_cluster(wk_frame, name=None):
        """Returns a DOT cluster containing all the information regarding the wk_frame.
        """
        font_size = '16'
        font_name = 'consolas'

        node_style = 'filled'
        edge_style = 'solid'
        
        frame_color = 'white'
        frame_bg_color = 'lightgrey'
        
        WK_frame_color = 'black'
        WK_frame_bg_color = 'white'
        WK_frame_node_shape = 'circle'
        WK_frame_node_color = 'grey'
        WK_frame_trigger_shape = 'doublecircle'
        WK_frame_node_fill_color = 'grey'
        
        if not(name):
            name = wk_frame.name
            
        label = '<<FONT FACE="%s"><TABLE BORDER="0" ALIGN="LEFT"><TR><TD ALIGN="LEFT">name: %s</TD></TR><TR><TD ALIGN="LEFT">preference: %s</TD></TR></TABLE></FONT>>' %(font_name, wk_frame.name, wk_frame.preference)
        cluster_name = name
        cluster_frame = pydot.Cluster(cluster_name, label=label, color=frame_color)
        cluster_frame.set_bgcolor(frame_bg_color)
        
        label = '<<FONT FACE="%s">WK_Frame</FONT>>' %font_name
        cluster_WK_frame = pydot.Cluster(name + '_WK_frame', label=label, color=WK_frame_color)
        cluster_WK_frame.set_bgcolor(WK_frame_bg_color)
        for node in wk_frame.nodes:
            label = "%s"%node.concept.meaning
            new_node = pydot.Node(node.name, label=label, color=WK_frame_node_color, fillcolor=WK_frame_node_fill_color, shape=WK_frame_node_shape, style=node_style, fontsize=font_size, fontname=font_name)
            cluster_WK_frame.add_node(new_node)
        for edge in wk_frame.edges:
            new_edge = pydot.Edge(edge.pFrom.name, edge.pTo.name, style=edge_style, label=edge.concept.meaning)
            cluster_WK_frame.add_edge(new_edge)
        
        cluster_frame.add_subgraph(cluster_WK_frame)
        return cluster_frame
        
    @staticmethod
    def _create_cxn_cluster(cxn, name=None):
        """
        Returns a DOT cluster containing all the information regarding the construction.
        """
        font_size = '16'
        font_name = 'consolas'
        
        cxn_color = 'white'
        cxn_bg_color = 'lightgray'

        node_style = 'filled'
        edge_style = 'solid'
        
        SemFrame_color = 'black'
        SemFrame_bg_color = 'white'
        SemFrame_node_shape = 'circle'
        SemFrame_head_shape = 'doublecircle'
        SemFrame_node_color = 'grey'
        SemFrame_node_fill_color = 'grey'
        
        SynForm_color = 'black'
        SynForm_bg_color = 'white'
        SynForm_shape = 'box'
        SynForm_node_color = 'grey'
        SynForm_node_fill_color = 'grey'
        
        SymLinks_color = 'black'
        SymLinks_width = '1'
        SymLinks_style = 'dashed'
        
        if not(name):
            name = cxn.name
            
        label = '<<FONT FACE="%s"><TABLE BORDER="0" ALIGN="LEFT"><TR><TD ALIGN="LEFT">name: %s</TD></TR><TR><TD ALIGN="LEFT">class: %s</TD></TR></TABLE></FONT>>' %(font_name, cxn.name, cxn.clss)
        cluster_name = name
        cluster_cxn = pydot.Cluster(cluster_name, label=label, color=cxn_color)
        cluster_cxn.set_bgcolor(cxn_bg_color)
        
        label = '<<FONT FACE="%s">SemFrame</FONT>>' %font_name
        cluster_SemFrame = pydot.Cluster(name + '_SemFrame', label=label, color=SemFrame_color)
        cluster_SemFrame.set_bgcolor(SemFrame_bg_color)
        for node in cxn.SemFrame.nodes:
            if node.head:
                node_shape = SemFrame_head_shape
            else:
                node_shape = SemFrame_node_shape
            if node.focus:
                label = "%s%s"%(node.concept.meaning, '(F)')
            else:
                label = "%s"%node.concept.meaning
                
            new_node = pydot.Node(node.name, label=label, color=SemFrame_node_color, fillcolor=SemFrame_node_fill_color, shape=node_shape, style=node_style, fontsize=font_size, fontname=font_name)
            cluster_SemFrame.add_node(new_node)
        for edge in cxn.SemFrame.edges:
            new_edge = pydot.Edge(edge.pFrom.name, edge.pTo.name, style=edge_style, label=edge.concept.meaning)
            cluster_SemFrame.add_edge(new_edge)
        
        cluster_cxn.add_subgraph(cluster_SemFrame)
        
        label = '<<FONT FACE="%s">SynForm</FONT>>' %font_name
        cluster_SynForm = pydot.Cluster(name + '_SynForm', label=label, color=SynForm_color)
        cluster_SynForm.set_bgcolor(SynForm_bg_color)
        pre_form = None
        for form in cxn.SynForm.form:
            if isinstance(form, TP_SLOT):
                new_node = pydot.Node(str(form), label ="[" +  ", ".join(form.cxn_classes) +"]", shape=SynForm_shape, style=node_style, color=SynForm_node_color, fillcolor=SynForm_node_fill_color, fontsize=font_size, fontname=font_name)
                cluster_SynForm.add_node(new_node)
            elif isinstance(form, TP_PHON):
                new_node = pydot.Node(str(form), label = form.cxn_phonetics, shape=SynForm_shape, style=node_style, color=SynForm_node_color, fillcolor=SynForm_node_fill_color, fontsize=font_size, fontname=font_name)
                cluster_SynForm.add_node(new_node)
            if not(pre_form):
                pre_form = form
            else:
                new_edge = pydot.Edge(str(pre_form), str(form), style=edge_style, label='next')
                cluster_SynForm.add_edge(new_edge)
                pre_form = form
        
        cluster_cxn.add_subgraph(cluster_SynForm)
        
        for k, v in cxn.SymLinks.SL.iteritems():
            node = cxn.find_elem(k)
            form = cxn.find_elem(v)
            new_edge = pydot.Edge(str(form), node.name, color=SymLinks_color , dir='none', penwidth=SymLinks_width, style=SymLinks_style)
            cluster_cxn.add_edge(new_edge)
        
        return cluster_cxn
        
    @staticmethod
    def _create_cxn_inst_cluster(cxn_inst):
        """
        Returns a DOT cluster containing all the information regarding the construction instance
        """
        label = '<<FONT FACE="%s"><TABLE BORDER="0" ALIGN="LEFT"><TR><TD ALIGN="LEFT">name: %s</TD></TR><TR><TD ALIGN="LEFT">activity: %.2f</TD></TR></TABLE></FONT>>' %('consolas', cxn_inst.name, cxn_inst.activity)
        cluster_name = cxn_inst.name        
        inst_cluster = pydot.Cluster(cluster_name, label=label, color='black', fill='white')
        for port in cxn_inst.out_ports:
            port_node = pydot.Node(name=str(port), label=str(port.name), shape='point', height='0.2', color='white')
            inst_cluster.add_node(port_node)
        
        #Node use to draw competition links.
        comp_node = pydot.Node(name=cxn_inst.name, shape='point', color='white')
        inst_cluster.add_node(comp_node)
        
        cxn_cluster = TCG_VIEWER._create_cxn_cluster(cxn_inst.content, cxn_inst.name + '_content')
        inst_cluster.add_subgraph(cxn_cluster)
        
        #For now I'll remove the input ports. Too much cluter.
#        for port in cxn_inst.in_ports:
#            port_node = pydot.Node(name=str(port), label=str(port.name), shape='point', height='0.2')
#            inst_cluster.add_node(port_node)
#            edge = pydot.Edge(str(port), str(port.data), style='dashed', dir='none', splines='spline')
#            inst_cluster.add_edge(edge)
        
        
        return inst_cluster
    
    @staticmethod
    def _create_inst_C2_cluster(insts, coop_links, comp_links):
        """
        Returns a DOT cluster containing the C2 graph, with the instances as nodes without display instances content.
        """
        font_size = '14'
        font_name = 'consolas'
        inst_shape = 'box'
        style = 'filled, rounded'
        
        C2_cluster = pydot.Cluster('C2_cluster', label='', color='white', fill='white')
        for inst in insts:
            label = '<<FONT FACE="%s">%s (%.2f)</FONT>>' %(font_name, inst.name, inst.activity)
            inst_fill_color = TCG_VIEWER._obj_to_color(inst.name)
            inst_color = inst_fill_color
            new_node = pydot.Node(inst.name, label=label, shape=inst_shape, style=style, color=inst_color, fillcolor=inst_fill_color, fontsize=font_size, fontname=font_name)
            C2_cluster.add_node(new_node)
        
        for coop_link in coop_links:
             coop_edge = pydot.Edge(coop_link.inst_from.name, coop_link.inst_to.name, splines='spline', color='green', penwidth='3', dir='both', arrowhead='box', arrowtail='box')
             C2_cluster.add_edge(coop_edge)
            
        for comp_link in comp_links:
            comp_edge = pydot.Edge(comp_link.inst_from.name, comp_link.inst_to.name, splines='spline', color='red', penwidth='3', dir='both', arrowhead='dot', arrowtail='dot')
            C2_cluster.add_edge(comp_edge)
        
        return C2_cluster
            
            
    @staticmethod
    def _create_cxn_inst_C2_cluster(cxn_insts, coop_links, comp_links):
        """
        Returns a DOT cluster containing all the information regarding the C2 between cxn instances.
        """
        
        C2_cluster = pydot.Cluster('C2_cluster', label='', color='white', fill='white')
        splines='splines' # I am not sure that this works...
        
        for cxn_inst in cxn_insts:
            cxn_inst_cluster = TCG_VIEWER._create_cxn_inst_cluster(cxn_inst)
            C2_cluster.add_subgraph(cxn_inst_cluster)
        for coop_link in coop_links:
            connect = coop_link.connect
#            coop_edge = pydot.Edge(str(connect.port_from), str(connect.port_to.data), color='green', penwidth='3', dir='both', arrowhead='box', arrowtail='box', ltail='cluster_' + coop_link.inst_from.name)
            coop_edge = pydot.Edge(connect.port_from.data.name, str(connect.port_to.data), splines=splines, color='green', penwidth='3', dir='both', arrowhead='box', arrowtail='box')

            C2_cluster.add_edge(coop_edge)
        for comp_link in comp_links:
            comp_edge = pydot.Edge(comp_link.inst_from.name, comp_link.inst_to.name, splines=splines, color='red', penwidth='3', dir='both', arrowhead='dot', arrowtail='dot', ltail='cluster_' + comp_link.inst_from.name, lhead='cluster_' + comp_link.inst_to.name)
            C2_cluster.add_edge(comp_edge)
        
        return C2_cluster
        
    @staticmethod   
    def _create_semrep_cluster(semrep, name=''):
        """
        Returns a DOT cluster containing all the SemRep information.
        Args:
            - SemRep (Networkx.DiGraph): State of semWM.
        """
        node_font_size = '14'
        edge_font_size = '12'
        style_unexpressed = 'filled'
        style_expressed = 'dashed'
        node_fill_color = 'lightgrey'
        node_color = 'lightgrey'
        node_shape = 'oval'
        font_name = 'consolas'
        semrep_cluster = pydot.Cluster(name, label='', color='white', fillcolor='white')
        
        
        for n, d in semrep.nodes(data=True):
            style = style_expressed if d['expressed'] else style_unexpressed
            label = '<<FONT FACE="%s">%s (%.2f)</FONT>>' %(font_name, d['cpt_inst'].content['concept'].name, d['cpt_inst'].activity)
            new_node = pydot.Node(n, label=label, shape=node_shape, style=style, color=node_color, fillcolor=node_fill_color, fontsize=node_font_size, fontname=font_name)
            semrep_cluster.add_node(new_node)
            
        for u,v, d in semrep.edges(data=True):
            style = style_expressed if d['expressed'] else style_unexpressed
            label = '<<FONT FACE="%s">%s (%.2f)</FONT>>' %(font_name, d['cpt_inst'].content['concept'].name, d['cpt_inst'].activity)
            new_edge = pydot.Edge(u, v, label=label, style = style, fontsize=edge_font_size, fontname=font_name, penwidth='2')
            semrep_cluster.add_edge(new_edge)
        
        return semrep_cluster
    
    
    @staticmethod        
    def _create_lingWM_cluster(semWM, gramWM, concise=False):
        """
        Returns a DOT cluster containing all the linguisticWM (semanticWM + grammaticamWM)
        Uses graphviz with pydot implementation.
        
        NOTE: would need to add phonological WM
        """        
        font_name = 'consolas'
        cover_style = 'dashed'
        edge_color = 'grey'
        
        lingWM_cluster = pydot.Cluster('linguisticWM')
        
        # Add SemanticWM cluster
        label = '<<FONT FACE="%s">Semantic WM (t:%.2f)</FONT>>' %(font_name, semWM.t)
        semWM_cluster = pydot.Cluster('semWM', label=label)
        semrep_cluster = TCG_VIEWER._create_semrep_cluster(semWM.SemRep, 'SemRep')
        semWM_cluster.add_subgraph(semrep_cluster)
        lingWM_cluster.add_subgraph(semWM_cluster)
        
        # Add GrammaticalWM cluster
        label = '<<FONT FACE="%s">Grammatical WM (t:%.2f)</FONT>>' %(font_name, gramWM.t)
        gramWM_cluster = pydot.Cluster('gramWM', label=label)
        if not(concise):
            cxn_inst_C2_cluster = TCG_VIEWER._create_cxn_inst_C2_cluster(gramWM.schema_insts, gramWM.coop_links, gramWM.comp_links)
        else:
            cxn_inst_C2_cluster = TCG_VIEWER._create_inst_C2_cluster(gramWM.schema_insts, gramWM.coop_links, gramWM.comp_links)
        gramWM_cluster.add_subgraph(cxn_inst_C2_cluster)
        lingWM_cluster.add_subgraph(gramWM_cluster)
        
        #Add covers links
        for cxn_inst in gramWM.schema_insts:
            node_covers = cxn_inst.covers['nodes'] # I am only going to show the node covers for simplicity
            for n1, n2 in node_covers.iteritems():
                if not(concise):
                    new_edge = pydot.Edge(n1, n2, dir='both', color=edge_color, style=cover_style, splines='spline')
                else:
                    edge_color = TCG_VIEWER._obj_to_color(cxn_inst.name)
                    new_edge = pydot.Edge(cxn_inst.name, n2, dir='both', color=edge_color, style=cover_style, splines='spline')
                lingWM_cluster.add_edge(new_edge)
        
        return lingWM_cluster
    
    @staticmethod
    def _create_scenerep_cluster(scenerep, name=''):
        """
        Returns a DOT cluster containing all the SceneRep information.
        
        Args:
            - SceneRep (Networkx.DiGraph): State of visWM.
            
        Note:
            - Node position is defined by instances position.
        """
        node_font_size = '14'
        edge_font_size = '12'
        style = 'filled'
        cluster_fill_color = '#%s%s%s%s' %('00', '00', '00', '11') #RGBA format
        node_fill_color = '#%s%s%s%s' %('00', '00', '00', '44') #RGBA format
        node_color = 'white'
        node_shape = 'box'
        font_name = 'consolas'
        
        scenerep_cluster = pydot.Cluster(name, label='', color='white', fillcolor=cluster_fill_color)
        
        for n, d in scenerep.nodes(data=True):
            pos = d['per_inst'].content['area'].center()
            w = d['per_inst'].content['area'].w
            h = d['per_inst'].content['area'].h
            
            label = '<<FONT FACE="%s"><TABLE BORDER="0" ALIGN="LEFT"><TR><TD ALIGN="LEFT">%s (%.2f)</TD></TR><TR><TD ALIGN="LEFT">area_%i: (x:%.1f,y:%.1f,w:%.1f,h:%.1f)</TD></TR></TABLE></FONT>>' %(font_name, d['per_inst'].name, d['per_inst'].activity, d['per_inst'].content['area'].id, pos[0], pos[1], w, h)
#            label = '<<FONT FACE="%s">%s (%.1f)</FONT>>' %(font_name, d['per_inst'].name, d['per_inst'].activity)
            scale = 1
            pos = "%f,%f" %(d['pos'][0]*scale, d['pos'][1]*scale)
#            width = "%f" %(d['per_inst'].content['area'].w*scale*0.01) # This is annoying! width is defined in inches, and pos is interpreted in points.....
#            height = "%f" %(d['per_inst'].content['area'].h*scale*0.01)
            new_node = pydot.Node(n, pos=pos, label=label, shape=node_shape, style=style, color=node_color, fillcolor=node_fill_color, fontsize=node_font_size, fontname=font_name)
            scenerep_cluster.add_node(new_node)
            
        for u,v, d in scenerep.edges(data=True):
            label = '<<FONT FACE="%s">%s (%.2f)</FONT>>' %(font_name, d['per_inst'].name, d['per_inst'].activity)
            new_edge = pydot.Edge(u, v, label=label,  fontsize=edge_font_size, fontname=font_name, penwidth='2')
            scenerep_cluster.add_edge(new_edge)
        
        return scenerep_cluster
    
    @staticmethod        
    def _create_WMs_cluster(visWM, semWM, gramWM, concise=True):
        font_name = 'consolas'
        cover_color = 'grey'
        cover_style = 'dashed'
        
        WMs_cluster = pydot.Cluster('WMs')
        
        # Add visWM cluster
        label = '<<FONT FACE="%s">Visual WM (t:%.1f)</FONT>>' %(font_name, visWM.t)
        visWM_cluster = pydot.Cluster('visWM', label=label)
        scenerep_cluster = TCG_VIEWER._create_scenerep_cluster(visWM.SceneRep)
        visWM_cluster.add_subgraph(scenerep_cluster)
        WMs_cluster.add_subgraph(visWM_cluster)
        
        # Add LingWM cluster
        lingWM_cluster = TCG_VIEWER._create_lingWM_cluster(semWM, gramWM, concise)
        WMs_cluster.add_subgraph(lingWM_cluster)
        
        #Add conceptualization links
        for per_inst in visWM.schema_insts:
            if not(isinstance(per_inst.content, PERCEPT_SCHEMA_REL)):
                cpt_inst = per_inst.covers['cpt_inst'] # I am only going to show the node covers for simplicity
                if cpt_inst:
                    new_edge = pydot.Edge(cpt_inst.name, per_inst.name, dir='both', color=cover_color, style=cover_style, splines='spline')
                    WMs_cluster.add_edge(new_edge)
        
        return WMs_cluster
    
    @staticmethod
    def display_wk_frame(frame, folder='./tmp/', file_type='png', show=True):
        """Create graph images for the wk_frame 'frame'.
        Uses graphviz with pydot implementation.
        
        Args:
            - frame (WK_FRAME): the frame object to be displayed.
        """
        tmp_folder = folder   
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)

        prog = 'dot'
        
        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'LR'
        
        dot_frame = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth)
        dot_frame.set_rankdir(rankdir)
        dot_frame.set_fontname(font_name)
        
        cluster_frame = TCG_VIEWER._create_wk_frame_cluster(frame)
        dot_frame.add_subgraph(cluster_frame)
        
        file_name = tmp_folder + frame.name + ".gv"
        dot_frame.write(file_name)
            
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)          
            plt.figure(facecolor='white')
            plt.axis('off')
            title = "%s\n pref: %.2f"%(frame.name, frame.preference)
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
        
    @staticmethod
    def display_cxn(cxn, folder='./tmp/', file_type='png', show=True):
        """
        Create graph images for the construction 'cxn'.
        Uses graphviz with pydot implementation.
        
        Args:
            - cxn (CXN): the construction object to be displayed.
        """        
        tmp_folder = folder   
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)

        prog = 'dot'

        font_name = 'consolas'
        labeljust='l'
        penwidth = '2'
        rankdir = 'LR'
        
        dot_cxn = pydot.Dot(graph_type='digraph', labeljust=labeljust, penwidth=penwidth)
        dot_cxn.set_rankdir(rankdir)
        dot_cxn.set_fontname(font_name)
        
        cluster_cxn = TCG_VIEWER._create_cxn_cluster(cxn)
        dot_cxn.add_subgraph(cluster_cxn)
        
        file_name = tmp_folder + cxn.name + ".gv"
        dot_cxn.write(file_name)
            
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)          
            plt.figure(facecolor='white')
            plt.axis('off')
            title = cxn.name  + '\n class:' + cxn.clss
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_cxn_instance(cxn_inst, name='', folder='./tmp/', file_type='png', show=True):
        """
        Display a construction instance.
        """
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
            
        prog = 'dot'
        
        font_name ='consolas'

        inst_cluster = TCG_VIEWER._create_cxn_inst_cluster(cxn_inst)
        
        inst_graph = pydot.Dot(graph_type='digraph', rankdir='LR', labeljust='l' ,fontname=font_name)
        inst_graph.add_subgraph(inst_cluster)
        
        name = cxn_inst.name
        file_name = tmp_folder + name + ".gv"
        inst_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_cxn_assemblage(cxn_assemblage, name='cxn_assembalge', concise=False, folder='./tmp/', file_type='svg', show=False):
        """
        Nicer display for assemblage.
        Should have a concise=True/False option (concise does not show the inside of cxn. Ideally, clicking on a cxn would expand it)
        """
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
            
        prog = 'dot'
        
        if not(concise):
            C2_cluster = TCG_VIEWER._create_cxn_inst_C2_cluster(cxn_assemblage.schema_insts, cxn_assemblage.coop_links,[])
        else:
            C2_cluster = TCG_VIEWER._create_inst_C2_cluster(cxn_assemblage.schema_insts, cxn_assemblage.coop_links,[])
            name='%s_concise' %name
        
        assemblage_graph = pydot.Dot('"%s"' %name, graph_type='digraph', rankdir='LR', labeljust='l', compound='true', style='rounded')
        
        C2_cluster = TCG_VIEWER._create_cxn_inst_C2_cluster(cxn_assemblage.schema_insts, cxn_assemblage.coop_links, [])
        assemblage_graph.add_subgraph(C2_cluster)

        
        file_name = tmp_folder + name + ".gv"
        assemblage_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_gramWM_state(WM, concise=False, folder='./tmp/', file_type='svg', show=False):
        """
        Nicer display for wm state.
        """
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
            
        prog = 'dot'
        
        if not(concise):
            C2_cluster = TCG_VIEWER._create_cxn_inst_C2_cluster(WM.schema_insts, WM.coop_links,WM.comp_links)
            name = WM.name
        else:
            C2_cluster = TCG_VIEWER._create_inst_C2_cluster(WM.schema_insts, WM.coop_links,WM.comp_links)
            name='%s_concise' %WM.name
        
        gram_WM_state_graph = pydot.Dot(name, graph_type='digraph', rankdir='LR', labeljust='l', compound='true', style='rounded')
        gram_WM_state_graph.add_subgraph(C2_cluster)
        
        
#        file_name = '%s%s%.1f.gv' %(tmp_folder, name, WM.t)        
        file_name = '%s%s%05d.gv' %(tmp_folder, name, WM.t)
        gram_WM_state_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_semWM_state(semWM, folder='./tmp/', file_type='svg', show=False):
        """
        Create graph images for the semanic working memory
        Uses graphviz with pydot implementation.
        """        
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        
        prog = 'dot'
    
        name = 'semanticWM'
        
        semWM_graph = pydot.Dot(name, graph_type = 'digraph', rankdir='LR', labeljust='l', compound='true', style='rounded', penwidth ='2')
        
        semrep_cluster = TCG_VIEWER._create_semrep_cluster(semWM.SemRep, 'SemRep')
        semWM_graph.add_subgraph(semrep_cluster)
        
#        file_name = '%s%s%.1f.gv' %(tmp_folder, semWM.name, semWM.t)
        file_name = '%s%s%05d.gv' %(tmp_folder, semWM.name, semWM.t)
        semWM_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_lingWM_state(semWM, gramWM, concise=False, folder='./tmp/', file_type='pdf', show=False):
        """
        Create graph images for the ling working memory (semantic WM + grammatical WM)
        Uses graphviz with pydot implementation.
        """        
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        
        prog = 'dot'
        
        if not(concise):
            name='LinguisticWM'
        else:
            name='LinguisticWM_concise'
        
        lingWM_graph = pydot.Dot(name, graph_type = 'digraph', rankdir='LR', labeljust='l', compound='true', style='rounded', penwidth ='2')

        lingWM_cluster = TCG_VIEWER._create_lingWM_cluster(semWM, gramWM, concise=concise)
        lingWM_graph.add_subgraph(lingWM_cluster)
        
#        file_name = '%s%s%.1f.gv' %(tmp_folder, name, semWM.t)
        file_name = '%s%s%05d.gv' %(tmp_folder, name, semWM.t)
        lingWM_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_visWM_state(visWM, folder='./tmp/', file_type='svg', show=False):
        """
        Create graph images for the visual working memory.
        Uses graphviz with pydot implementation.
        """
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        
        prog = 'neato' # Need to use neato or fdp to make use of node positions in rendering
        
        name = 'visualWM'
        
        visWM_graph = pydot.Dot(name, graph_type= 'digraph', rankdir='LR', labeljust='L', compound='true', style='rounded', penwidth = '2', dpi='72')
        scenerep_cluster = TCG_VIEWER._create_scenerep_cluster(visWM.SceneRep, 'SceneRep')
        visWM_graph.add_subgraph(scenerep_cluster)
        
        file_name = '%s%s%.1f.gv' %(tmp_folder, visWM.name, visWM.t)
        visWM_graph.write(file_name)
        
        cmd = "%s -T%s -Gdpi=300 -n2 %s > %s.%s" %(prog, file_type, file_name, file_name, file_type) # For neato flag -n or n2: assumes that positions have been set up by layout and are given in points.
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_WMs_state(visWM, semWM, gramWM, concise=True, folder='./tmp/', file_type='svg', show=False):
        """
        Create graph images for including both visual and linguisitc working memory.
        """
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        
        
        prog = 'dot' # Need to use neato or fdp to make use of node positions in rendering

        if not(concise):
            name='WMs '
        else:
            name='WMs_concise'
        
        WMs_graph = pydot.Dot(name, graph_type = 'digraph', rankdir='LR', labeljust='l', compound='true', style='rounded', penwidth ='2')
        
        WMs_cluster = TCG_VIEWER._create_WMs_cluster(visWM, semWM, gramWM, concise)
        WMs_graph.add_subgraph(WMs_cluster)
        
        file_name = '%s%s%.1f.gv' %(tmp_folder, name, semWM.t)
        WMs_graph.write(file_name)
        
        cmd = "%s -T%s  -Gdpi=300 -s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type) # For neato flag -n or n2: assumes that positions have been set up by layout and are given in points.
        subprocess.call(cmd, shell=True)
        if show:
            img_name = '%s.%s' %(file_name,file_type)
            plt.figure(facecolor='white')
            plt.axis('off')
            title = name
            plt.title(title)
            img = plt.imread(img_name)
            plt.imshow(img)
            plt.show()
            
    @staticmethod
    def display_scene(scene, img_file):
        """
        """
        # Load scene image
        imgPIL = Image.open(img_file)
        
        # Convert to nparray
        img = np.asarray(imgPIL)
        
        # Drawing figure
        fig = plt.figure(facecolor='white')
        title = 'Scene'
        plt.title(title)
        plt.imshow(img)
        fig = plt.gcf()
        ax = fig.gca()
        
        color_dict = {'OBJECT':'g', 'ACTION':'r' , 'QUALITY':'b', 'SCENE':'y'}
        
        # Display perceptual schemas and area
        for per_schema in scene.schemas:
            if not(isinstance(per_schema.trace, PERCEPT_SCHEMA_REL)):
                area = per_schema.content['area']
                pos = (area.y, area.x)
                rectangle = patches.Rectangle((pos[0], pos[1]), width=area.w, height=area.h, alpha=0.2,color=color_dict[per_schema.trace.type])
                ax.add_patch(rectangle)
                info = '%s (%.1f)' %(per_schema.name, per_schema.content['saliency'])
                plt.text(area.y, area.x + 10, info, fontsize=10)
            else:
                schema_from = per_schema.content['pFrom']
                schema_to = per_schema.content['pTo']
                pos_from = schema_from.content['area'].center()
                pos_to = schema_to.content['area'].center()
                head_size = 10
                pos_start = (pos_from[1], pos_from[0])
                d_pos = (pos_to[1] - pos_from[1], pos_to[0] - pos_from[0])
                if d_pos == (0,0):
                    err_message = "Cannot draw arrow between %s and %s for relation %s since they have the same area center" %(schema_from.name, schema_to.name, per_schema.name)
                    raise ValueError(err_message)
                plt.arrow(pos_start[0], pos_start[1], d_pos[0], d_pos[1], length_includes_head=True, head_width=head_size/2, head_length=head_size, fc='k', ec='k')
                info = '%s (%.1f)' %(per_schema.name, per_schema.content['saliency'])
                plt.text(pos_start[0] + d_pos[0]/2, pos_start[1] + d_pos[1]/2, info, fontsize=10)
        
        # Display subscenes
        for subscene in scene.subscenes:
            margin = 20
            lw = 3
            area = subscene.area            
            pos = (area.y - margin, area.x - margin)
            w = area.w + 2*margin
            h = area.h + 2*margin
            rectangle = patches.Rectangle((pos[0], pos[1]), width=w, height=h, fc='none', ec='r', lw=lw)
            ax.add_patch(rectangle)
            info = 'SS_%s (%.1f, %i)' %(subscene.name, subscene.saliency, subscene.uncertainty)
            plt.text(pos[0]+lw, pos[1]+lw+10, info, fontsize=10, color='r')
            
        plt.show()
    
    @staticmethod
    def display_saccades(fixations, img_file, ss_radius=False):
        """
        Args:
            - fixation [DICT]. Format {'time':FLOAT, 'pos':(FLOAT, FLOAT), 'subscene':{'name':STR, 'radius':FLOAT}}
            - img_file
            - ssradius (BOOL): If True, fixtion radius is set to the value of the fixated subscene's radius.
        """
        HEAD_SIZE = 20
        RADIUS_FIX = 80.0
        COLOR_FIX = 'b'
        ALPHA_FIX = 0.3
        FONT_SIZE = 12
        # Load scene image
        imgPIL = Image.open(img_file)
        
        # Convert to nparray
        img = np.asarray(imgPIL)
        
        # Drawing figure
        fig = plt.figure(facecolor='white')
        plt.title('Saccades')
        plt.imshow(img)
        fig = plt.gcf()
        ax = fig.gca()
        
        
        prev_pos = None
        for fix in fixations:
            pos = fix['pos']
            radius = fix['subscene']['radius'] if ss_radius else RADIUS_FIX
            fixation = plt.Circle((pos[1],pos[0]), radius , color=COLOR_FIX, alpha=ALPHA_FIX)
            ax.add_patch(fixation)
            info = 't:%.1f' %fix['time']
            plt.text(pos[1] + radius/10, pos[0] + radius/10, info, fontsize=FONT_SIZE)
            if prev_pos:
                plt.arrow(prev_pos[1], prev_pos[0], pos[1]-prev_pos[1], pos[0]-prev_pos[0], length_includes_head=True, head_width=HEAD_SIZE/2, head_length=HEAD_SIZE, fc='k', ec='k')
            prev_pos = pos
        
        plt.show()
    
    @staticmethod
    def display_saliencymap(saliency_map):
        """
        """
        plt.figure()
        plt.title('saliency map')
        plt.plot(saliency_map)
        plt.show()
###############################################################################
if __name__ == '__main__':
    data_folder = './output/'
    
    data_list = os.listdir(data_folder)
    print "Available data:\n"
    for d in data_list:
        print "\t" + d
    
    filename = raw_input('Enter a file name: ')
    
    data_path = data_folder + filename
    
    myViewer = TCG_VIEWER(data_path)
    myViewer.start_viewer()
    
        

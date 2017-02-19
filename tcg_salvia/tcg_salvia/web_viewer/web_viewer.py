# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 16:13:10 2015

@author: Victor Barres

Defines the WEB_VIEWER classes.

Can be also be use in command line: python web_viewer.py
"""
from __future__ import division
import os, shutil
import SimpleHTTPServer
import SocketServer
import webbrowser
import subprocess
import pydot

from schemas.loader import LOADER
from schemas.viewer import VIEWER

class WEB_VIEWER:
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
        if os.path.exists(self.VIEWER_TMP):
            shutil.rmtree(self.VIEWER_TMP)
        print os.getcwd()
        shutil.copytree(self.data_path, self.VIEWER_TMP)
        
        self.conceptual_knowledge = LOADER.load_conceptual_knowledge("TCG_semantics.json", self.VIEWER_TMP)
        self.perceptual_knowledge = LOADER.load_perceptual_knowledge("TCG_semantics.json", self.VIEWER_TMP)
        self.conceptualization = LOADER.load_conceptualization("TCG_semantics.json", self.VIEWER_TMP, self.conceptual_knowledge, self.perceptual_knowledge)
        self.grammar = LOADER.load_grammar("TCG_grammar.json", self.VIEWER_TMP, self.conceptual_knowledge)
        self.scene = LOADER.load_scene("TCG_scene.json", self.VIEWER_TMP)
        
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
        
        cluster_cpt = VIEWER._create_concepts_cluster(self.conceptual_knowledge)
        cpt_graph.add_subgraph(cluster_cpt)
        
        file_name = cpt_folder + "TCG_concepts" + ".gv"
        cpt_graph.write(file_name)
        
        # This is a work around becauses dot.write or dot.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
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
        
        cluster_per = VIEWER._create_percepts_cluster(self.perceptual_knowledge)
        per_graph.add_subgraph(cluster_per)
        
        
        file_name = per_folder + 'TCG_percepts' + ".gv"
        per_graph.write(file_name)
        
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
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
        
        cluster_czer = VIEWER._create_conceptualizer_cluster(self.conceptualization, cpt_knowledge=cpt_knowledge)
        czer_graph.add_subgraph(cluster_czer)
        
        file_name = czer_folder + 'TCG_conceptualizer' + ".gv"
        czer_graph.write(file_name)
        
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
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
            
            cluster_cxn = VIEWER._create_cxn_cluster(cxn)
            cxn_graph.add_subgraph(cluster_cxn)
            
            file_name = cxn_folder + cxn.name + ".gv"
            cxn_graph.write(file_name)
            
        cxn_graphs = os.listdir(cxn_folder)
        for cxn_file in cxn_graphs:
            cmd = "%s -T%s %s > %s.%s" %(prog, file_type, cxn_folder + cxn_file, cxn_folder + cxn_file, file_type)
            subprocess.call(cmd, shell=True)
    
        
        

###############################################################################
if __name__ == '__main__':
    data_folder = './output/'
    
    data_list = os.listdir(data_folder)
    print "Available data:\n"
    for d in data_list:
        print "\t" + d
    
    filename = raw_input('Enter a file name: ')
    
    data_path = data_folder + filename
    
    myViewer = WEB_VIEWER(data_path)
    myViewer.start_viewer()
    
        

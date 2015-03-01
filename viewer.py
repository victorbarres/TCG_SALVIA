# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 16:13:10 2015

@author: Victor Barres

Defines the TCG_VIEWER class that allows to view a certain dataset into the TCG viewer.

Can be also be use in command line: python viewer.py
"""
class TCG_VIEWER:
    """
    Connects the simulation to the the TCG viewer.
    
    Data:
        - server_port (INT): Server port value, default 8080.
        - viewer_path (STR): path to the viewer main directory.
        - data_path (STR): Path to the data folder that needs to be displayed.
        - tmp (STR): Temp folder.
    """

    def __init__(self, data_path, PORT=8080, viewer_path="viewer/"):
        """
        Requires the path (data_path) to the folder that contains the data to be diplayed in the viewer.
        """
        self.server_port = PORT
        self.viewer_path = viewer_path
        self.data_path = data_path
        self.tmp = "tmp/"
    
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
        import os
        import SimpleHTTPServer
        import SocketServer
        
        import webbrowser
        PORT = self.server_port
    
        os.chdir(self.viewer_path)
    
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    
        httpd = SocketServer.TCPServer(("", PORT), Handler)
    
        print "serving at port", PORT
        webbrowser.open_new("http://localhost:" + str(PORT))
        httpd.serve_forever()
        
    def _load_data(self):
        """
        Copies and creates all the required data in viewer/tmp directory.
        """
        import os, shutil
        if os.path.exists(self.viewer_path + self.tmp):
            shutil.rmtree(self.viewer_path + self.tmp)
        print os.getcwd()
        shutil.copytree(self.data_path, self.viewer_path + self.tmp)
        self._create_cxn_imgs()
        dot_cpt = self._create_concept_img()
        dot_sem= self._create_semrels_img()
        self._create_percept_img()
        self._create_conceptualizer_img(dot_cpt, dot_sem)
    
    def _create_cxn_imgs(self):
        """
        Create graph images for all the constructions.
        Uses graphviz with pydot implementation.
        """
        import os, shutil
        import subprocess        
        import json
        import pydot
        
        prog = 'dot'
        file_type = 'svg'
        
        cxn_folder = self.viewer_path + self.tmp + 'cxn/'        
        
        if os.path.exists(cxn_folder):
            shutil.rmtree(cxn_folder)
        
        os.mkdir(cxn_folder)
        
        grammar_file = 'TCG_grammar.json'
        with open(self.viewer_path + self.tmp + grammar_file, 'r') as f:
            json_data = json.load(f)
        
        grammar = json_data['grammar']
        
        font_size = '10'
        style = 'filled'
        fill_color = 'white'
        
        for cxn in grammar:
            dot_cxn = pydot.Dot(graph_type = 'digraph')
            dot_cxn.set_rankdir('LR')
            dot_cxn.set_fontname('consolas')

            
            cluster_SemFrame = pydot.Cluster('SemFrame', label='SemFrame')
            cluster_SemFrame.set_bgcolor('lightcoral')
            for node in cxn['SemFrame']['nodes']:
                if node['head'] == True:
                    node_shape = 'doublecircle'
                else:
                    node_shape = 'circle'
                cluster_SemFrame.add_node(pydot.Node(node['name'], label=node['concept'], color='black', shape=node_shape, style=style, fillcolor=fill_color, fontsize=font_size))
            for edge in cxn['SemFrame']['edges']:
                cluster_SemFrame.add_edge(pydot.Edge(edge['from'], edge['to'], label=edge['concept']))
            
            dot_cxn.add_subgraph(cluster_SemFrame)
            
            cluster_SynForm = pydot.Cluster('SynForm', label='SynForm')
            cluster_SynForm.set_bgcolor('lightblue')
            pre_form = None
            for form in cxn['SynForm']:
                if form['type'] == "SLOT":
                    cluster_SynForm.add_node(pydot.Node(form['name'], label ="[" +  ", ".join(form['classes']) +"]", shape="box", style=style, fillcolor=fill_color, fontsize=font_size))
                elif form['type'] == 'PHON':
                    cluster_SynForm.add_node(pydot.Node(form['name'], label = form['phon'], shape="box", style=style, fillcolor=fill_color, fontsize=font_size))
                if not(pre_form):
                    pre_form = form['name']
                else:
                    cluster_SynForm.add_edge(pydot.Edge(pre_form, form['name'], label='next'))
                    pre_form = form["name"]
            
            dot_cxn.add_subgraph(cluster_SynForm)
            
            for k in cxn['SymLinks'].keys():
                dot_cxn.add_edge(pydot.Edge(k, cxn['SymLinks'][k], color='red', dir='none', penwidth='1'))
            
            file_name = cxn_folder + cxn['name'] + ".gv"
            dot_cxn.write(file_name)
            
        # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cxn_dots = os.listdir(cxn_folder)
        for cxn_file in cxn_dots:
            cmd = "%s -T%s %s > %s.%s" %(prog, file_type, cxn_folder + cxn_file, cxn_folder + cxn_file, file_type)
            subprocess.call(cmd, shell=True)
    
    def _create_concept_img(self):
        """
        Create graph image for the conceptual knowledge.
        Uses graphviz with pydot implementation.
        """
        import os, shutil
        import subprocess        
        import json
        import pydot
        
        prog = 'dot'
        file_type = 'svg'
        
        cpt_folder = self.viewer_path + self.tmp + 'cpt/'        
        
        if os.path.exists(cpt_folder):
            shutil.rmtree(cpt_folder)
        
        os.mkdir(cpt_folder)
        
        cpt_file = 'TCG_semantics.json'
        with open(self.viewer_path + self.tmp + cpt_file, 'r') as f:
            json_data = json.load(f)
        
        cpt = json_data['CONCEPTUAL_KNOWLEDGE']
        edge_type = 'is_a'
        dot_cpt = pydot.Dot(graph_type='digraph')
        dot_cpt.set_rankdir('BT')
        dot_cpt.set_fontname('consolas')
        font_size = '10'
        color = 'black'
        node_shape = 'box'
        style = 'filled'
        fill_color = 'white'
        
        def _add_rel(sup_node, cpt_data, dot_cpt):
            for concept in cpt_data:
                dot_cpt.add_node(pydot.Node(concept, label=concept, color=color, shape=node_shape, style=style, fillcolor=fill_color, fontsize=font_size))
                if sup_node != None:
                    dot_cpt.add_edge(pydot.Edge(concept, sup_node, label=edge_type, fontsize=font_size))
                
                _add_rel(concept, cpt_data[concept], dot_cpt)
        
        _add_rel('CONCEPTUAL_KNOWLEDGE', cpt, dot_cpt)
        
        file_name = cpt_folder + 'TCG_concepts' + ".gv"
        dot_cpt.write(file_name)
        # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        return dot_cpt
    
    def _create_semrels_img(self):
        """
        Create graph image for the semantic relations knowledge.
        Uses graphviz with pydot implementation.
        """
        import os, shutil
        import subprocess        
        import json
        import pydot
        
        prog = 'dot'
        file_type = 'svg'
        
        sem_folder = self.viewer_path + self.tmp + 'sem/'        
        
        if os.path.exists(sem_folder):
            shutil.rmtree(sem_folder)
        
        os.mkdir(sem_folder)
        
        sem_file = 'TCG_semantics.json'
        with open(self.viewer_path + self.tmp + sem_file, 'r') as f:
            json_data = json.load(f)
        
        sem = json_data['SEM_RELATIONS']
        edge_type = 'is_a'
        dot_sem = pydot.Dot(graph_type='digraph')
        dot_sem.set_rankdir('BT')
        dot_sem.set_fontname('consolas')
        font_size = '10'
        color = 'black'
        node_shape = 'box'
        style = 'filled'
        fill_color = 'white'
        
        def _add_rel(sup_node, sem_data, dot_sem):
            for concept in sem_data:
                dot_sem.add_node(pydot.Node(concept, label=concept, color=color, shape=node_shape, style=style, fillcolor=fill_color, fontsize=font_size))
                if sup_node != None:
                    dot_sem.add_edge(pydot.Edge(concept, sup_node, label=edge_type, fontsize=font_size))
                
                _add_rel(concept, sem_data[concept], dot_sem)
        
        _add_rel('SEMANTIC_RELATIONS', sem, dot_sem)
        
        file_name = sem_folder + 'TCG_semrels' + ".gv"
        dot_sem.write(file_name)
        # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        return dot_sem
    
    def _create_percept_img(self):
        """
        Create graph image for the percetual knowledge.
        Uses graphviz with pydot implementation.
        """
        import os, shutil
        import subprocess        
        import json
        import pydot
        
        prog = 'dot'
        file_type = 'svg'
        
        per_folder = self.viewer_path + self.tmp + 'per/'        
        
        if os.path.exists(per_folder):
            shutil.rmtree(per_folder)
        
        os.mkdir(per_folder)
        
        per_file = 'TCG_semantics.json'
        with open(self.viewer_path + self.tmp + per_file, 'r') as f:
            json_data = json.load(f)
        
        per = json_data['PERCEPTUAL_KNOWLEDGE']
        edge_type = 'is_a'
        dot_per = pydot.Dot(graph_type='digraph')
        dot_per.set_rankdir('BT')
        dot_per.set_fontname('consolas')
        font_size = '10'
        color = 'black'
        node_shape = 'box'
        style = 'filled'
        fill_color = 'white'
        id_next = [0] # Just so that it's pass by name and not by value...
        
        def _add_rel(sup_node, sup_id, per_data, dot_per, id_next):
            for concept in per_data:
                if concept!= 'FEATURE':  
                    concept_id = id_next[0]
                    id_next[0] +=1
                    dot_per.add_node(pydot.Node(str(concept_id), label=concept, color=color, shape=node_shape, style=style, fillcolor=fill_color, fontsize=font_size))
                    if sup_node != None:
                        dot_per.add_edge(pydot.Edge(str(concept_id), str(sup_id), label=edge_type, fontsize=font_size))
                    
                    _add_rel(concept, concept_id, per_data[concept], dot_per, id_next)
        
        _add_rel('PERCEPTUAL_KNOWLEDGE', 0, per, dot_per, id_next)
        
        file_name = per_folder + 'TCG_percepts' + ".gv"
        dot_per.write(file_name)
        # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        return dot_per
    
    def _create_conceptualizer_img(self, dot_cpt, dot_sem):
        """
        Create graph image for the conceputalizer.
        Uses graphviz with pydot implementation.
        """
        import os, shutil
        import subprocess        
        import json
        import pydot
        
        prog = 'dot'
        file_type = 'svg'
        
        czer_folder = self.viewer_path + self.tmp + 'czer/'        
        
        if os.path.exists(czer_folder):
            shutil.rmtree(czer_folder)
        
        os.mkdir(czer_folder)
        
        czer_file = 'TCG_conceptualizer.json'
        with open(self.viewer_path + self.tmp + czer_file, 'r') as f:
            json_data = json.load(f)
        
        czer = json_data['CONCEPTUALIZATIONS']
        dot_czer = pydot.Dot(graph_type = 'digraph')
        dot_czer.set_rankdir('BT')
        dot_czer.set_fontname('consolas')
        font_size = '10'
        color = 'black'
        node_shape = 'box'
        style = 'filled'
        fill_color = 'white'
        edge_color = 'red'
        
        def _create_subgraph(graph):
            sbg = pydot.Subgraph('')
            for node in graph.get_nodes():
                sbg.add_node(node)
            for edge in graph.get_edges():
                sbg.add_edge(edge)
            return sbg
        
        cluster_concepts = pydot.Cluster('concepts', label='concepts')
        cpt_sbg = _create_subgraph(dot_cpt)
        cluster_concepts.add_subgraph(cpt_sbg)
        
        cluster_semrels = pydot.Cluster('semrels', label='semrels')
        sem_sbg = _create_subgraph(dot_sem)
        cluster_semrels.add_subgraph(sem_sbg)
        
        abstract_sbg = pydot.Subgraph()
        abstract_sbg.add_subgraph(cluster_concepts)
        abstract_sbg.add_subgraph(cluster_semrels)
        
        cluster_abstract = pydot.Cluster('abstract_knowlege', label='abstract_knowledge')
        cluster_abstract.add_subgraph(abstract_sbg)
        cluster_percepts = pydot.Cluster('percepts', label='percepts')
        
        dot_czer.add_subgraph(cluster_abstract)
        dot_czer.add_subgraph(cluster_percepts)
        
        for target in czer:
            for source in czer[target]['TOKENS']:
                cluster_percepts.add_node(pydot.Node(source, label=source, color=color, shape=node_shape, style=style, fillcolor=fill_color, fontsize=font_size))
                dot_czer.add_edge(pydot.Edge(source, target, color=edge_color))
        
        file_name = czer_folder + 'TCG_conceptualizer' + ".gv"
        dot_czer.write(file_name)
        # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
            
###############################################################################
if __name__ == '__main__':
    import os
    data_folder = './output/'
    
    data_list = os.listdir(data_folder)
    print "Available data:\n"
    for d in data_list:
        print "\t" + d
    
    filename = raw_input('Enter a file name: ')
    
    data_path = data_folder + filename
    
    myViewer = TCG_VIEWER(data_path)
    myViewer.start_viewer()
    
        

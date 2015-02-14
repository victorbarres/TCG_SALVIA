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
        import os, shutil
        if os.path.exists(self.viewer_path + self.tmp):
            shutil.rmtree(self.viewer_path + self.tmp)
        print os.getcwd()
        shutil.copytree(self.data_path, self.viewer_path + self.tmp)
        self._create_cxn_imgs()
    
    def _create_cxn_imgs(self):
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
        for cxn in grammar:
            dot_cxn = pydot.Dot(graph_type = 'digraph')
            dot_cxn.set_rankdir('LR')
            dot_cxn.set_fontname('consolas')

            
            cluster_SemFrame = pydot.Cluster('SemFrame', label='SemFrame')
            cluster_SemFrame.set_bgcolor('lightcoral')
            for node in cxn['SemFrame']['nodes']:
                cluster_SemFrame.add_node(pydot.Node(node['name'], label=node['concept'], style='filled', fillcolor='white'))
            for edge in cxn['SemFrame']['edges']:
                cluster_SemFrame.add_edge(pydot.Edge(edge['from'], edge['to'], label=edge['concept']))
            
            dot_cxn.add_subgraph(cluster_SemFrame)
            
            cluster_SynForm = pydot.Cluster('SynForm', label='SynForm')
            cluster_SynForm.set_bgcolor('lightblue')
            pre_form = None
            for form in cxn['SynForm']:
                if form['type'] == "SLOT":
                    cluster_SynForm.add_node(pydot.Node(form['name'], label ="[" +  ", ".join(form['classes']) +"]", shape="box", style='filled', fillcolor='white'))
                elif form['type'] == 'PHON':
                    cluster_SynForm.add_node(pydot.Node(form['name'], label = form['phon'], shape="box", style='filled', fillcolor='white'))
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
    
        

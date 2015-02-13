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
        self._create_cxn_svgs()
    
    def _create_cxn_svgs(self):
        import os, shutil        
        import json
        from graphviz import Digraph

        cxn_folder = self.viewer_path + self.tmp + 'cxn/'        
        
        if os.path.exists(cxn_folder):
            shutil.rmtree(cxn_folder)
        
        os.mkdir(cxn_folder)
        
        grammar_file = 'TCG_grammar.json'
        with open(self.viewer_path + self.tmp + grammar_file, 'r') as f:
            json_data = json.load(f)
        
        grammar = json_data['grammar']
        for cxn in grammar:
            dot = Digraph(comment=cxn['name'])
            for node in cxn['SemFrame']['nodes']:
                dot.node(node['name'], node['concept'])
            for edge in cxn['SemFrame']['edges']:
                dot.edge(edge['from'], edge['to'], label=edge['concept'])
            dot.format = 'svg'
            file_name = cxn_folder + cxn['name'] + '.gv'
            dot.render(file_name, view=False)
            
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
    
        

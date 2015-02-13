# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 16:13:10 2015

@author: Victor Barres

Defines the functions required to set up the TCGviewer
"""

class TCG_VIEWER:

    def __init__(self, data_path, PORT=8080, viewer_path="./viewer/"):
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
        import shutil
        shutil.rmtree(self.viewer_path + self.tmp)
        shutil.copytree(self.data_path, self.viewer_path + self.tmp)
    
        

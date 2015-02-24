# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 11:57:27 2015

@author: Victor Barres
Defines the classes used to set up a brain system model
"""

############################    
### Brain system classes ###
############################   
class SYSTEM:
    """
    Defines a whole brain system
    Data:
        - name (str):
        - modules ([MODULES]):
        - connections ([CONNECT]):
    """
    def __init__(self,name):
        self.name = name
        self.modules = []
        self.connections = []
    
    def add_modules(self, modules):
        """
        Add all the modules in "modules" ([MODULES]) in the system.
        """
        self.modules += modules
        
    def add_connections(self, connections):
        """
        Add all the connections in "connections" ([CONNECT]) in the system.
        """
        self.connections += connections
        
    def update(self):
        """
        """
    
class MODULE:
    """
    A module could be an LTM or a WM or made of submodules?
    A module should be linked to brain regions? (possibly a set of brain regions?)
    Data:
        - id (int): Unique id
        - name (str): Module name
        - function (WM, LTM)
        - in_ports ([int]):
        - out_ports ([int]):
        - brain_regions([str]):
    """
    ID_next = 0
    PO_next = 0
    PI_next = 0
    def __init__(self, name, function = None, brain_regions = []):
        self.id = MODULE.ID_next
        MODULE.ID_next +=1
        self.name = name
        self.function = function
        self.in_ports = []
        self.out_ports = []
        self.brain_regions = brain_regions
    
    def set_function(self, function):
        """
        """
        self.function = function
    
    def add_port(self,port_type, port_name):
        """
        """

class CONNECT:
    """
    Data:
        - port_in ({"module":MODULE, "port":port_id}):
        - port_out ({"module":MODULE, "port":port_id}):
        - weight (float):
        - delay (float):
    """
    def __init__(self):
        """
        """
        self.port_in = {"module":None, "port":None}
        self.port_out = {"module":None, "port":None}
        self.weight = 0
        self.delay = 0
    
    def set_port_in(self, module, port_id):
        """
        """
        self.port_in["module"] = module
        self.port_in["port"] = port_id
        
    def set_port_out(self, module, port_id):
        """
        """
        self.port_out["module"] = module
        self.port_out["port"] = port_id
    
    def set_weight(self, weight):
        """
        """
        self.weight = weight
    
    def set_delay(self, delay):
        """
        """
        self.delay = delay

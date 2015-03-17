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
        Each class that inherit from this base class need to define its update procedure.
        """
    
class MODULE:
    """
    A module could be an LTM or a WM or made of submodules?
    A module should be linked to brain regions? (possibly a set of brain regions?)
    Data:
        - id (int): Unique id
        - name (str): Module name
        - function (PROCEDURAL_SCHEMA)
        - in_ports ([{'id':port_id, 'name':port_name, 'value':value}]):
        - out_ports ([{'id':port_id, 'name':port_name, 'value':value}]):
        - brain_regions([str]):
    """
    ID_next = 0 # Global module ID counter
    PI_next = 0 # Global module input port counter
    PO_next = 0 # Global module output port counter
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
        Adds a new port to the module. Port_type (str) ['in' or 'out'], port_name (str).
        """
        if port_type == 'in':
            new_port = {'id':MODULE.PI_next, 'name':port_name, 'value':None}
            MODULE.PI_next +=1
            self.in_ports.append(new_port)
            return True
        elif port_type == 'out':
            new_port = {'id':MODULE.PO_next, 'name':port_name, 'value':None}
            MODULE.PO_next +=1
            self.out_ports.append(new_port)
            return True
        else:
            return False

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

class LESION:
    """
    """

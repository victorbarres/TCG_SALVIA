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
        return
        
    def connect(self, module1, module2, weight=1, delay=0):
        """
        Adds a directed connection between module1 and module2.
        """
        outport_name = 'to_%s' % module2.name
        inport_name = 'from_%s' % module1.name
        id_out = module1.add_port('out', outport_name)
        id_in = module2.add_port('in', inport_name)
        if id_in and id_out:
            new_connect = CONNECT()
            new_connect.set_from(module1, id_out)
            new_connect.set_to(module2, id_in)
            new_connect.set_weight(weight)
            new_connect.set_delay(delay)
            self.add_connections([new_connect])
            return True
        else:
            return False
    
    def system2dot(self):
        return
            
        
    
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
    ID_next = 1 # Global module ID counter
    PI_next = 1 # Global module input port counter
    PO_next = 1 # Global module output port counter
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
        Return new port id if the creation successful, None otherwise.
        """
        if port_type == 'in':
            new_port = {'id':MODULE.PI_next, 'name':port_name, 'value':None}
            MODULE.PI_next +=1
            self.in_ports.append(new_port)
            return new_port['id']
        elif port_type == 'out':
            new_port = {'id':MODULE.PO_next, 'name':port_name, 'value':None}
            MODULE.PO_next +=1
            self.out_ports.append(new_port)
            return new_port['id']
        else:
            return None

class CONNECT:
    """
    Data:
        - pFrom ({"module":MODULE, "port":port_id}):
        - pTo ({"module":MODULE, "port":port_id}):
        - weight (float):
        - delay (float):
    """
    def __init__(self):
        """
        """
        self.pFrom = {"module":None, "port":None}
        self.pTo = {"module":None, "port":None}
        self.weight = 0
        self.delay = 0
    
    def set_from(self, module, port_id):
        """
        """
        self.pFrom["module"] = module
        self.pFrom["port"] = port_id
        
    def set_to(self, module, port_id):
        """
        """
        self.pTo["module"] = module
        self.pTo["port"] = port_id
    
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

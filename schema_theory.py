# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines the based schema theory classes.

Dependencies:
    - abc to define abstract classes
    - time only to provide execution timing for procedural schema updating.
    - random
    - numpy to implement the schema instances activation values.
    - matplotlib.plt to visualize WM state dynamics
    - networkx to visualize WM state
    - json to save simulation data in json format.
    - pickle to save schema_systems.
    - pprint for printing data
"""
import abc
import time
import os
import random
import numpy as np
import matplotlib.pyplot as plt
import pickle
import pprint

import networkx as nx
import json

###################
##### SCHEMAS #####
###################
class SCHEMA(object):
    """
    Schema (base class)
    
    Data:
        - id (int): Unique id
        - name (str): schema name
        - schema_system (SCHEMA_SYSTEM): Schema system to which the schema belongs.
    """
    ID_next = 1 # Global schema ID counter
    def __init__(self, name=""):
        self.id = SCHEMA.ID_next
        SCHEMA.ID_next += 1
        self.name = name
        self.schema_system = None

class PORT(object):
    """
    Port class defining inputs and outputs connections.
    Data:
        - id (int): unique port id.
        - name (str): optional port name.
        - data (): optional port data
        - schema (SCHEMA): the schema the port is associated with.
        - type ('IN' or 'OUT'): type of port (input or output port)
        - value(): current value at the port.
    """
    TYPE_IN = 'IN'
    TYPE_OUT = 'OUT'
    ID_NEXT = 1 # Global port counter
    
    def __init__(self, port_type, port_schema = None, port_name='', port_data = None, port_value=None):
        self.name = port_name
        self.data = port_data
        self.value = port_value
        self.id = PORT.ID_NEXT
        PORT.ID_NEXT += 1
        self.type = port_type
        self.schema = port_schema
    
    def reset(self):
        """
        Reset port state.
        """
        self.port_data = None
        self.port_value = None

class CONNECT(SCHEMA):
    """
    Defines connections and message passing between ports (input_port -> output_port)
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
    Data:
        - port_from (PORT)
        - port_to (PORT)
        - weight (float)
        - delay (float)
    """
    def __init__(self, name="",  port_from=None, port_to=None, weight=0, delay=0):
        """
        """
        SCHEMA.__init__(self, name)
        self.port_from = port_from
        self.port_to = port_to
        self.weight = weight
        self.delay = delay
        
    def reset(self):
        """
        Reset the set of each connected port.
        """
        self.port_from.reset()
        self.port_to.reset()
    
    def update(self):
        """
        For now does not involve weight or delay!
        Sets the value of port_rom to the value of port_to.
        Resets the port_from value to None.
        """
        self.port_to.value = self.port_from.value
        self.port_from.value = None
    
    def set_from(self, port):
        """
        """
        if port.type == PORT.TYPE_OUT:
            self.port_from = port
            return True
        else:
            return False
        
    def set_to(self, port):
        """
        """
        if port.type == PORT.TYPE_IN:
            self.port_to = port
            return True
        else:
            return False
    
    def set_weight(self, weight):
        """
        """
        self.weight = weight
    
    def set_delay(self, delay):
        """
        """
        self.delay = delay
    
    def copy(self):
        """
        """
        new_connect = CONNECT(name=self.name, port_from = self.port_from, port_to = self.port_to, weight=self.weight, delay=self.delay)
        return new_connect
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {"id":self.id, "name":self.name, "port_from":self.port_from.name, "port_to":self.port_to.name, "weight":self.weight, "delay":self.delay}
        return data
        
##############################  
##### PROCEDURAL SCHEMAS #####
##############################
class PROCEDURAL_SCHEMA(SCHEMA):
    """
    Procedural schema base class
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
    Data:
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - params (DICT): Stores the process parameters
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - activity (float): The activity level of the schema.
        - t (FLOAT): Time.
        - dt (FLOAT): Time step.
    """
    def __init__(self, name=""):
        SCHEMA.__init__(self, name)
        self.in_ports = []
        self.out_ports = []
        self.params = {}
        self.inputs = {}
        self.outputs = {}
        self.activity = 0.0
        self.t = 0.0
        self.dt = 1.0
    
    def reset(self):
        """
        Reset procedural schema state.
        
        Note:
            - For any extention of the class, if new instance state variables are introduced, the method should be overriden!
        """
        for k in self.inputs:
            self.inputs[k] = None
        for k in self.outputs:
            self.outputs[k] = None
        self.activity = 0
        self.t = 0
        self.dt = 1.0
    
    def get(self):
        """
        Get all inputs and store them in the local self.inputs DICT. 
        """
        for input_name in self.inputs.keys():
            self.get_input(input_name)
    
    def post(self):
        """
        Post all the process outputs.
        """
        for output_name, val in self.outputs.iteritems():
            self.post_output(output_name, val)
    
    @abc.abstractmethod    
    def process(self):
        """
        This function should be specified for every specific PROCEDURAL_SCHEMA class.
        When called the function updates the state of the procedural schema 
        based on the values stored in inputs and sets the output values in outputs.
        """
        return
    
    def update(self):
        """
        Gathers the input, update the state, posts the outputs, resets inputs and outputs namespaces.
        """
        self.get()
        self.process()
        self.post()
        
        # Reset input and output namespace values.
        for input_name in self.inputs.keys():
            self.inputs[input_name] = None
        
        for output_name in self.outputs.keys():
            self.outputs[output_name] = None
    
    def add_port(self, port_type, port_name='', port_data=None, port_value=None):
        """
        Adds a new port to the procedural schema. Port_type (str) ['IN' or 'OUT'], port_name (str), and a value port_value for the port.
        Updates the input and output dictionary to hanlde the data receives or posted from input ports or to output ports respectively.
        If sucessessful, returns the port id. Else returns None.
        """
        new_port = PORT(port_type, port_schema=self, port_name=port_name, port_data=port_data, port_value=port_value)
        
        if port_type == PORT.TYPE_IN:
            if self.inputs.has_key(new_port.name):
                error_msg = "Already exising input port name %s. Cannot add the port to schema %s." %(new_port.name, self.name)
                raise ValueError(error_msg)
            else:
                self.in_ports.append(new_port)
                self.inputs[new_port.name] = None
            return new_port.id
        elif port_type == PORT.TYPE_OUT:
            if self.outputs.has_key(new_port.name):
                error_msg = "Already existing output port name %s. Cannot add the port to schema %s." %(new_port.name, self.name)
                raise ValueError(error_msg)
            else:
                self.out_ports.append(new_port)
                self.outputs[new_port.name] = None
            return new_port.id
        else:
            error_msg = "Unknown port type: %s" %port_type
            raise ValueError(error_msg)
    
    def remove_ports(self):
        """
        Removes all the input and output ports and resets the inputs and outputs namespaces.
        """
        self.in_ports = []
        self.out_ports = []
        self.inputs = {}
        self.outputs = {}
    
    def set_params(self, params):
        """
        Set the procedural schemas parameters to params (DICT)
        
        Args:
            - params (DICT): contains all the parameters.
        """
        self.params = params
    
    def update_param(self, param_path, param_value):
        """
        Update the parameter value defined by the param_path to param_value.
        
        Args:
            - param_path (str): String giving the path to the param using . chain (e.g. "dynamics.activation' would set the path to params['dynamics']['activation'])
            - param_value (): New value of the parameter
        """
        path_list = param_path.split('.')
        param_name = path_list.pop()
        parent = self.params
        for key in path_list:
            parent = parent[key]
        
        if param_name in parent.keys():
            parent[param_name] = param_value
        
    def get_input(self, port_name):
        """
        Return the current value of the port with name 'port_name', stores the value in the inputs namesapce, and resets the port value to None. If the port is not an input port, if multiple ports shared the same name or if the port is 
        not found, returns None.
        """
        port = self.find_port(port_name)
        if port and (port.type == PORT.TYPE_IN):
            if self.inputs.has_key(port.name):
                val = port.value
                self.inputs[port.name] = val # Stores value in inputs namespace
                port.value = None # Reset port value
                return val
        elif port and (port.type == PORT.TYPE_OUT):
            error_msg = "Port %s refers to an output port" % port_name
            raise ValueError(error_msg)
        else:
            error_msg = "port %s does not exist or could refer to multiple ports" % port_name
            raise ValueError(error_msg)
    
    def post_output(self, port_name, val):
        """
        Sets the value of the output port with name 'port_name' to 'val'. If the port is not an output port, if multiple ports shared the same name or if the port is 
        not found, returns False, else returns True.
        """
        port = self.find_port(port_name)
        if port and (port.type == PORT.TYPE_OUT):
            port.value = val
            return True
        elif port and (port.type == PORT.TYPE_IN):
            error_msg = "Port %s refers to an output port" % port_name
            raise ValueError(error_msg)
        else:
            return False
    
    def find_port(self, port_name):
        """
        Looks for port with name 'port_name'. 
        Returns the port if a single port with this name is found. Else returns None.
        """
        found = []
        for port in self.in_ports + self.out_ports:
            if port.name == port_name:
                found.append(port)
        
        if len(found)!= 1:
            error_msg = "Port %s does not exist or could refer to multiple ports" % port_name
            raise ValueError(error_msg)
            
        return found[0]
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        Returns a JSON formated string containing the schema's description info.
        """
        data = {"name":self.name, "type":self.__class__.__name__, "params":{"dt":self.dt}, 
                     "in_ports":[p.name for p in self.in_ports], "out_ports":[p.name for p in self.out_ports]}
        return data
        
    def get_state(self):
        """
        Returns a JSON formated string containing schema's current state's information.
        """
        data = {"name":self.name, "t":self.t, "activity":self.activity}
        return data

class SYSTEM_SCHEMA(PROCEDURAL_SCHEMA):
    """
    Brain anchored procedural schema. Defines the schema system as nodes in the fixed system's topology.
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - params (DICT)
        - activity (float):
    
    Data:
        - brain_regions(LIST): List of brain regions associated with the system schema.
    """
    def __init__(self, name=""):
        PROCEDURAL_SCHEMA.__init__(self, name)
        brain_mapping = BRAIN_MAPPING()

class FUNCTION_SCHEMA(PROCEDURAL_SCHEMA):
    """
    Functional schemas, not anchored to a specific brain regions but participating in the processes ocurring within a given
    system schema.
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - params (DICT)
        - activity (float):
    
    Data:
        - system (SYSTEM_SCHEMA): the system_schema within which the function schema operates.
    """
    def __init__(self, name=""):
        PROCEDURAL_SCHEMA.__init__(self,name)
        self.system = None
 
################################
### KNOWLEDGE SCHEMA CLASSES ###
################################        

class KNOWLEDGE_SCHEMA(SCHEMA):
    """
    Knowledge schema base class (Declarative schema)
    Those schemas can be instantiated.
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
    Data:
        - LTM (LTM): Associated long term memory.
        - content (): Procedural or semantic content of the schema.
        - init_act (float): Initial activation value.
    """    
    def __init__(self, name="", LTM=None, content=None, init_act=0):
        SCHEMA.__init__(self, name)
        self.content = content
        self.LTM = LTM
        self.init_act = init_act
    
    def set_name(self, name):
        self.name = name

    def set_init(self, init_act):
        self.init_act = init_act
    
    def set_content(self, content):
        self.content = content
    
    def set_LTM(self, LTM):
        self.LTM = LTM
        
#####################################
##### PROCEDURAL SCHEMA CLASSES #####
#####################################  
        

###############################
### FUNCTION SCHEMA CLASSES ###
###############################       
        
class SCHEMA_INST(FUNCTION_SCHEMA):
    """
    Schema instance
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - params (DICT)
        - activity (float):
        - system (SYSTEM_SCHEMA): the system_schema within which the function schema operates.
    Data:
        - content (KNOWLEDGE_SCHEMA)
        - alive (bool): status flag
        - trace (): Pointer to the element that triggered the instantiation.
        - activity (FLOAT): activity value for schema instance
        - params: {'act':{t0:FLOAT, act0: FLOAT, dt:FLOAT, tau:FLOAT, int_weight:FLOAT, ext_weight:FLOAT, sact_rest:FLOAT, k:FLOAT, noise_mean:FLOAT, noise_std:FLOAT}}
        - activation (INST_ACTIVATION): Activation object of schema instance
        - act_port_in (PORT): Stores the vector of all the input activations.
        - act_port_out (PORT): Sends as output the activation of the instance.
    """    
    def __init__(self,schema=None, trace=None):
        FUNCTION_SCHEMA.__init__(self,name="")
        self.content = None      
        self.alive = False
        self.trace = None
        self.activity = 0
        self.params['act'] = {'t0':0.0, 'act0': 1.0, 'dt':0.1, 'int_weight': 1.0, 'ext_weight': 1.0, 'tau':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.0}
        self.activation = None
        self.act_port_in = PORT("IN", port_schema=self, port_name="act_in", port_value=[]);
        self.act_port_out = PORT("OUT", port_schema=self, port_name="act_out", port_value=0);
        self.instantiate(schema, trace)
     
    def initialize_activation(self):
        """
        Set activation parameters
        """
        self.activation = INST_ACTIVATION(t0=self.params['act']['t0'], act0=self.params['act']['act0'], dt=self.params['act']['dt'], tau=self.params['act']['tau'],
                                          int_weight=self.params['act']['int_weight'], ext_weight=self.params['act']['ext_weight'],
                                          act_rest=self.params['act']['act_rest'], k=self.params['act']['k'],
                                          noise_mean=self.params['act']['noise_mean'], noise_std=self.params['act']['noise_std'])
        
        self.activation.save_vals["t"].append(self.params['act']['t0'])
        self.activation.save_vals["act"].append(self.params['act']['act0'])
        self.activity = self.params['act']['act0']
        self.act_port_out.value = self.activity
    
    def set_activation(self, value):
        """
        Sets the activation to value (FLOAT).
        Args:
            - value (FLOAT)
        """
        self.activation.act = value
        self.activity = value
    
    @abc.abstractmethod
    def set_ports(self):
        """
        THIS FUNCTION NEEDS TO BE DEFINED FOR EACH SPECIFIC SUBCLASS OF SCHEMA_INST.
        """
        return
    
    def instantiate(self, schema, trace, system=None):
        """
        Sets up the state of the schema instance at t0 of instantiation with tau characteristic time for activation dynamics.
        """
        self.content = schema.content
        self.name = "%s_%i" %(schema.name, self.id)
        self.system = system
        self.alive = True
        self.trace = trace
        self.set_ports()
        self.params['act']['act0'] = float(schema.init_act)
        self.initialize_activation()
    
    def update_activation(self):
        """
        Gathers all values from activation input port; reset value to []; update activation value based on INST_ACTIVATION dynamics; post new activation value to activation output port.
        """
        I = 0
        for v in self.act_port_in.value:
            I+= v
        self.act_port_in.value = [];
        
        self.activation.update(I)
        self.activity = self.activation.act
        self.act_port_out.value = self.activity
    
    @abc.abstractmethod
    def process(self):
        """
        This function should be specified for every specific SCHEMA_INST class.
        When called, this function should read the value at the input ports and based on the state of the procedure, update the state of the instance and 
        post values at the output ports.
        """
        return
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(SCHEMA_INST, self).get_state()
        data['alive'] = self.alive
        data['content'] = {}
        data['trace'] = {}
        
        return data

class INST_ACTIVATION(object):
    """
    Note: Having dt and Tau is redundant... dt should be defined at the system level.
    I have added E to gather external inputs (not carried through ports. Useful for activations across WMs.)
    """
    def __init__(self, t0=0.0, act0=1.0, dt=0.1, tau=1.0, int_weight=1.0, ext_weight=1.0, act_rest=0.001, k=10.0, noise_mean=0.0, noise_std=0.0):
        self.t0 = float(t0)
        self.act0 = float(act0)
        self.tau = float(tau)
        self.act_rest = float(act_rest)
        self.W = {'W_I':int_weight, 'W_E':ext_weight, 'W_self':0.0}
        self.k = float(k)
        self.dt = float(dt) 
        self.t = self.t0
        self.act = self.act0
        self.noise_mean = float(noise_mean)
        self.noise_std = float(noise_std)
        self.save_vals = {"t":[], "act":[]}
        self.E = 0.0
        
    def update(self, Int):
        """
        Int: total internal input
        """
        alpha = (1.0 - 1.0/self.tau) # Time constant (leak rate)
        noise =  random.normalvariate(self.noise_mean, self.noise_std) # noise value
        act_int = self.W['W_I']*Int + self.W['W_self']*self.act # Weighted internal input
        act_ext = self.W['W_E']*self.E #  Weighted external input
        Input = act_int + act_ext # Total input before noise (linear summation option)
#        Input = act_ext + act_int*act_ext # Total input before noise (modulation option 1)

        
        new_act = alpha*self.act + (1.0 - alpha)*self.logistic(Input + noise) # Updated activation
        self.act = new_act
        self.t += self.dt
        self.save_vals["t"].append(self.t)
        self.save_vals["act"].append(self.act)
        self.E = 0.0
    
    
    def logistic(self, x):
        """
        Activation function.
        """
        if self.act_rest == 0.0:
            err_msg = "logistic function undefined for sigma(0) = act_rest = 0"
            raise ValueError(err_msg)
            
        x0 = np.log(1.0/self.act_rest - 1)/self.k     # Compute x0 so that sigma(0) = act_rest    
        output = 1.0/(1.0 + np.exp(-1.0*self.k*(x-x0)))
        return output
        
#############################
### SYSTEM SCHEMA CLASSES ###
#############################  

########################        
### LONG TERM MEMORY ###
########################
class LTM(SYSTEM_SCHEMA):
    """
    Long term memory. 
    Stores the set of schemas associated with this memory.
    In addition, weighted connection can be defined betweens schemas to set up the LTM as a schema network. NOT USED IN TCG1.1!
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - activity (float): The activity level of the schema.
    Data:
        - schemas ([SCHEMA]): Schema content of the long term memory
        - connections ([{from:schema1, to:schema2, weight:w}]): List of weighted connections between schemas (for future use if LTM needs to be defined as schema network)
    """
    def __init__(self, name=''):
        SYSTEM_SCHEMA.__init__(self,name)
        self.schemas = []
        self.connections = []

    def add_schema(self, schema):
        if schema.LTM != self:
            schema.set_LTM(self) # Link the schema to this LTM object
        self.schemas.append(schema)
    
    def add_connection(self, from_schema, to_schema, weight):
        self.connections.append({'from':from_schema, 'to':to_schema, 'weight':weight})
    
    def find_schema(self, name):
        """
        Returns the list of schemas with name = name(STR)
        """
        res = [schema for schema in self.schemas if schema.name == name]
        if not(res):
            return None
        else:
            if len(res)==1:
                return res[0]
            else:
                error_msg = "%s: Ambiguous schema name" %name
                raise ValueError(error_msg)
                
######################        
### WORKING MEMORY ###
######################
class WM(SYSTEM_SCHEMA):
    """
    Working memory
    Stores the currently active schema instances and the functional links through which they enter in cooperative computation.
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - params (DICT):
        - activity (float): The activity level of the schema.
    Data:
        - schema_insts ([SCHEMA_INST]):
        - coop_links ([COOP_LINK]):
        - comp_links ([COMP_LINK]):
        - params (DICT): {'dyn': {'tau':FLOAT, 'int_weight':FLOAT, 'ext_weight':FLOAT,'act_rest':FLOAT,'k':FLOAT, 'noise_mean':FLOAT, 'noise_var':FLOAT},
                          'C2': {'coop_weight':FLOAT, 'comp_weight':FLOAT, 'prune_threshold':FLOAT, 'confidence_threshold':FLOAT, 'coop_asymmetry':FLOAT, 'comp_asymmetry':FLOAT, 'P_comp':FLOAT, 'P_coop':FLOAT}}
            Note:
            - coop_weight (FLOAT): weight of cooperation f-links
            - comp_weight (FLOAT): weight of competition f-links
            - int_weight (FLOAT): weight given to internal effects on C2
            - ext_weight (FLOAT): weight given to external effects on C2
            - prune_threshold (FLOAT): Below this threshold the instances are considered inactive (Alive=False)
        - save_state (DICT): Saves the history of the WM states. DOES NOT SAVE THE F_LINKS!!! NEED TO FIX THAT.
    """
    def __init__(self, name=''):
        SYSTEM_SCHEMA.__init__(self,name)
        self.schema_insts = []
        self.coop_links = []
        self.comp_links = []
        self.params['dyn'] = {'tau':10.0, 'int_weight':1.0, 'ext_weight':1.0, 'act_rest':0.001, 'k':10.0, 'noise_mean':0.0, 'noise_std':0.1}
        self.params['C2'] = {'coop_weight':1.0, 'comp_weight':-4.0, 'prune_threshold':0.3, 'confidence_threshold':0.8, 'coop_asymmetry':1.0, 'comp_asymmetry':0.0, 'P_comp':1.0, 'P_coop':1.0}
        self.save_state = {'insts':{}, 
                           'WM_activity': {'t':[], 'act':[], 'comp':[], 'coop':[], 
                                           'c2_network':{'num_insts':[], 'num_coop_links':[], 'num_comp_links':[]}}}
    def reset(self):
        """
        Reset state of the schema
        """
        super(WM, self).reset()
        self.schema_insts = []
        self.coop_links = []
        self.comp_links = []
        self.save_state = {'insts':{}, 
                           'WM_activity': {'t':[], 'act':[], 'comp':[], 'coop':[], 
                                           'c2_network':{'num_insts':[], 'num_coop_links':[], 'num_comp_links':[]}}}
    
    ########################
    ### INSTANCE METHODS ###
    ########################
    def add_instance(self, schema_inst, act0=None):
        if schema_inst in self.schema_insts:
            return False
            
        self.schema_insts.append(schema_inst)
        schema_inst.system = self
        
        if not(act0):
            act0 = schema_inst.activity # Uses the init_activation defined by the associated schema.
        act_params = {'t0':self.t, 'act0': act0, 'dt':self.dt, 'tau':self.params['dyn']['tau'], 
                      'int_weight':self.params['dyn']['int_weight'], 'ext_weight':self.params['dyn']['ext_weight'], 'act_rest':self.params['dyn']['act_rest'],
                      'k':self.params['dyn']['k'], 'noise_mean':self.params['dyn']['noise_mean'], 'noise_std':self.params['dyn']['noise_std']}
        schema_inst.params['act'] = act_params
        schema_inst.initialize_activation()
        
        # Save inst activation values.
        self.save_state['insts'][schema_inst.name] = schema_inst.activation.save_vals.copy()
        
        return True
    
    def remove_instance(self, schema_inst):
        """
        To do: Remove the C2-links...
        """
        self.schema_insts.remove(schema_inst)
                
    def find_instance(self, schema_inst_name):
        """
        Returns the schema instance with name schema_inst_name if it exists.
        Args:
            schema_inst_name (STR): name of a schema instance.
        """
        schema_inst = next((inst for inst in self.schema_insts if inst.name == schema_inst_name), None)
        return schema_inst
        
    def add_coop_link(self, inst_from, port_from, inst_to, port_to, qual=1.0, weight=None):
        """
        Add a cooperation link between two instances.
        A cooperation link can only be added if the two instances are not already in competition.
        """
        if (inst_from not in self.schema_insts) or (inst_to not in self.schema_insts):
            raise ValueError("Cannot add cooperation link. Either %s or %s are not in WM." %(inst_from.name, inst_to.name))            
            
        result_1 = self.find_comp_links(inst_from=inst_from, inst_to=inst_to)
        result_2 = self.find_comp_links(inst_from=inst_to, inst_to=inst_from) # Directionality does not matter.
        
        if result_1 or result_2:
            raise ValueError("Cannot add cooperation link. %s and %s are already in competition!" %(inst_from.name, inst_to.name))
            
        if weight == None:
            weight=self.params['C2']['coop_weight']
        new_link = COOP_LINK(inst_from, inst_to, weight*qual, self.params['C2']['coop_asymmetry'])
        new_link.set_connect(port_from, port_to)
        self.coop_links.append(new_link)

    def find_coop_links(self, inst_from='any', inst_to='any', port_from='any', port_to='any'):
        """
        Returns a list of coop_links that match the criteria.
        By default, it returns al the coop_links (no criteria specified)
        
        Args:
            - inst_from (SCHEMA_INST or 'any')
            - inst_to (SCHEMA_INST or 'any')
            - port_from (PORT or 'any')
            - port_to (PORT or 'any')
        """        
        results = []
        for flink in self.coop_links:
            if inst_from!='any' and (flink.inst_from != inst_from):
                continue
            if inst_to!='any' and (flink.inst_to != inst_to):
                continue
            if port_from !='any' and (flink.connect.port_from != port_from):
                continue
            if port_to !='any' and (flink.connect.port_to != port_to):
                continue
            
            results.append(flink)
        results = list(set(results))
        return results
                   
    def remove_coop_links(self, inst_from, inst_to, port_from='any', port_to='any'):
        """
        Remove the coop_links from working memory that satisfy the criteria.
        """
        f_links = self.find_coop_links(inst_from=inst_from, inst_to=inst_to, port_from=port_from, port_to=port_to)
        for f_link in f_links:
            self.coop_links.remove(f_link)
        
    def add_comp_link(self, inst_from, inst_to, weight=None):
        """
        Add a competition link between two instances.
        A competition link can only be added if the two instances are not already in cooperation.
        
        """
        if (inst_from not in self.schema_insts) or (inst_to not in self.schema_insts):
            raise ValueError("Cannot add competition link. Either %s or %s are not in WM." %(inst_from.name, inst_to.name))
            
        result_1 = self.find_coop_links(inst_from=inst_from, inst_to=inst_to)
        result_2 = self.find_coop_links(inst_from=inst_to, inst_to=inst_from) # Directionality does not matter.
        
        if result_1 or result_2:
            raise ValueError("Cannot add competition link. %s and %s are already in cooperation!" %(inst_from.name, inst_to.name))        
        
        if weight == None:
            weight=self.params['C2']['comp_weight']
        new_link = COMP_LINK(inst_from, inst_to, weight, self.params['C2']['comp_asymmetry'])
        self.comp_links.append(new_link)
        
    def find_comp_links(self, inst_from='any', inst_to='any'):
        """
        Returns a list of comp_links that match the criteria.
        By default, it returns al the comp_links (no criteria specified)
        
        Args:
            - inst_from (SCHEMA_INST or 'any')
            - inst_to (SCHEMA_INST or 'any')
        """
        results = []
        for flink in self.comp_links:
            if inst_from!='any' and (flink.inst_from != inst_from):
                continue
            if inst_to!='any' and (flink.inst_to != inst_to):
                continue
                
            results.append(flink)
        
        results = list(set(results))
        return results
        
    def remove_comp_links(self, inst_from, inst_to):
        """
        Remove the comp_links from working memory that satisfy the criteria.
        """
        f_links = self.find_comp_links(inst_from=inst_from, inst_to=inst_to)
        for f_link in f_links:
            self.comp_links.remove(f_link)
    
    def update_activity(self):
        """
        Computes the overall activity of the working memory.
        The WM activity at time t is defined as the sum of all the instances activities.
        """
        tot_act = 0
        for inst in self.schema_insts:
            tot_act += inst.activity
        self.activity = tot_act
    
    def update_activations(self):
        """
        Update all the activations of instances in working memory based on cooperation and competition f-links.
        Passes activations through coop links with probabiliy P_coop, and through competition liks with probability P_comp
        Then updates all instance activation.
        Saves states.
        """
        # Propagating cooperation
        for flink in self.coop_links:
            r = random.random()
            if(r<self.params['C2']['P_coop']):
                flink.update()  
        
        # Propagating competition
        for flink in self.comp_links:
            r = random.random()
            if(r<self.params['C2']['P_comp']):
                flink.update()
       
        # Update all instances activation and sets alive=False for instances that fall below threshold.
        for inst in self.schema_insts:
            inst.update_activation()
            if inst.activity<self.params['C2']['prune_threshold']:
                inst.alive = False
        
        self.update_activity()
        
        self.limit_capacity() #To impact WM capacity.
        
        self.update_save_state()
    
    def prune(self):
        """
        Removes from WM all the dead instances.
        """
        for inst in self.schema_insts[:]:
            if not inst.alive:
                self.schema_insts.remove(inst)
                for flink in self.coop_links[:]:
                    if (flink.inst_from == inst) or (flink.inst_to == inst):
                        self.coop_links.remove(flink)
                for flink in self.comp_links[:]:
                    if (flink.inst_from == inst) or (flink.inst_to == inst):
                        self.comp_links.remove(flink)
    
    def end_competitions(self):
        """
        Picks a winner for each ongoing competitions. 
        Winner is the instance with the max activatity at the time when the method is called.
            Loser is set to dead (alive=False). All the dead instances are then pruned.
        """
        for link in self.comp_links:
            inst_from = link.inst_from
            inst_to = link.inst_to
            if inst_from.activity <= inst_to.activity:
                inst_from.alive = False
            else:
                inst_to.alive = False
        self.comp_links = []
        self.prune()
        
    ###########################
    ### Degradation methods ###
    ###########################
    def limit_capacity(self, option=0):
        """
        Test various ways to induce WM capacity limitations.
        In progress. For now no way to set up the degradations for each WM...
        """
        if option==0: # Do nothing
            return
        elif option==1: # Set the cooperations weight to 0
            self.params['C2']['coop_weight'] = 0.0
        elif option==2: # Make the cooperation weight quickly decay (non maintenance of cooperation)
            pass # Need to define in WM a parameter that provides the F_link functions. This would also require having a pruning for f_links.
        elif option==3: # Randomly remove coop_links to limit structural capacity
            threshold = 0.1
            for link in self.coop_links[:]:
                val =  random.random()
                if val<threshold:
                    self.coop_link.remove(link)
        elif option==4: # same things but now links are removed in proportion to number of linkss
                max_val = 0.001
                max_capacity = 10.0
                capacity_remaining = (max_capacity - len(self.coop_links))/max_capacity
                threshold = min(max_val, (1 - capacity_remaining)*max_val) #linear
                for link in self.coop_links[:]:
                    val =  random.random()
                    if val<threshold:
                        print "t:%i DAMAGE! coop_removed (%s -> %s)" %(self.t, link.inst_from.name, link.inst_to.name)
                        self.coop_links.remove(link)
        
    ############################
    ### STATE SAVING METHODS ###
    ############################
    def update_save_state(self):
        """
        Add the current state values to save_state.
        """
        # Saving global WM state values.
        self.save_state['WM_activity']['t'].append(self.t)
        self.save_state['WM_activity']['act'].append(self.activity)
        
        
        # Saving new instances activations.
        for inst in self.schema_insts:
            if inst.name not in self.save_state['insts']:
                # Save inst activation values.
                self.save_state['insts'][inst.name] = inst.activation.save_vals.copy()
        
        # Saving C2 values.
        (tot_coop, tot_comp) = self.compute_C2_transfers()
        self.save_state['WM_activity']['comp'].append(tot_comp)
        self.save_state['WM_activity']['coop'].append(tot_coop)
        
        self.save_state['WM_activity']['c2_network']['num_insts'].append(len(self.schema_insts))
        self.save_state['WM_activity']['c2_network']['num_coop_links'].append(len(self.coop_links))
        self.save_state['WM_activity']['c2_network']['num_comp_links'].append(len(self.comp_links))

    def compute_C2_transfers(self):
        """
        Compute the amount of instantaneous cooperation and competition in the network.
        
        Returns (tot_coop, tot_comp) with:
            - tot_coop [FLOAT]: Total amount of current cooperation value transfer.
            - tot_comp [FLOAT]: Total amount of current competition value transfer.
        """
        tot_coop = 0
        tot_comp = 0
        for link in self.coop_links:
            inst_from = link.inst_from
            inst_to = link.inst_to
            transfer = abs((inst_from.activity - inst_to.activity)*link.weight)
            tot_coop += transfer
        
        for link in self.comp_links:
            inst_from = link.inst_from
            inst_to = link.inst_to
            transfer = abs((inst_from.activity - inst_to.activity)*link.weight)
            tot_comp += transfer
            
        return (tot_coop, tot_comp)
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(WM, self).get_info()
        data['params']['dyn'] = self.params['dyn']
        data['params']['C2'] = self.params['C2']
        return data
        
    def get_state(self):
        """
        """
        data = super(WM, self).get_state()
        data['schema_insts'] = [s.name for s in self.schema_insts]
        data['coop_links'] = [l.get_info() for l in self.coop_links]
        data['comp_links'] = [l.get_info() for l in self.coop_links]
        return data
        
    #######################
    ### DISPLAY METHODS ###
    #######################
    def show_dynamics(self, inst_act=True, WM_act=True, c2_levels=True, c2_network=True):
        """
        Note:
            - I am computing the density considering all links as unweighted and bidirectional.This does not take into account the assymetry coef or the weights.
        """
        # Plot instance activations
        if inst_act:
            plt.figure(facecolor='white')
            title = '%s dynamics \n dyn: [tau:%g, int_weight:%g, ext_weigt:%g,  act_rest:%g, k:%g], noise: [mean:%g, std:%g], C2: [coop:%g, comp:%g , coop_asymmetry:%g, comp_asymmetry:%g, prune:%g, conf:%g]' %(
                                self.name,
                                self.params['dyn']['tau'], self.params['dyn']['int_weight'], self.params['dyn']['ext_weight'], self.params['dyn']['act_rest'], self.params['dyn']['k'],
                                self.params['dyn']['noise_mean'], self.params['dyn']['noise_std'], 
                                  self.params['C2']['coop_weight'], self.params['C2']['comp_weight'],  self.params['C2']['coop_asymmetry'], self.params['C2']['comp_asymmetry'], self.params['C2']['prune_threshold'], self.params['C2']['confidence_threshold'])
            plt.title(title)
            plt.xlabel('time', fontsize=14)
            plt.ylabel('activity', fontsize=14)
            for inst in self.save_state['insts'].keys():
                plt.plot(self.save_state['insts'][inst]['t'], self.save_state['insts'][inst]['act'], label=inst, linewidth=2)
            axes = plt.gca()
            axes.set_ylim([0,1])
            axes.set_xlim([0, max(self.save_state['WM_activity']['t'])])
            plt.axhline(y=self.params['C2']['prune_threshold'], color='k',ls='dashed')
            plt.axhline(y=self.params['C2']['confidence_threshold'], color='r',ls='dashed')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
            plt.show()
        
        # Plot global activity values.
        num_plots =  len([val for val in [WM_act, c2_levels] if val==True])
        
        if num_plots != 0:
            plt.figure(facecolor='white')
            i=0
            #plot WM activity
            if WM_act:
                i+=1
                plt.subplot(num_plots,1, i)
                plt.title('WM activity')
                plt.xlabel('time', fontsize=14)
                plt.ylabel('activity', fontsize=14)
                plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['act'], linewidth=2, color='k', label='act')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
                plt.margins(0.1, 0.1)
                
            # Plot c2 levels
            if c2_levels:
                i+=1            
                plt.subplot(num_plots,1, i)
                plt.title('C2 levels')
                plt.xlabel('time', fontsize=14)
                plt.ylabel('activation transfer', fontsize=14)
                plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['comp'], linewidth=2, color='r', label='competition')
                plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['coop'], linewidth=2, color='g', label='cooperation')
                tot_c2 = [v1 + v2 for (v1, v2) in zip(self.save_state['WM_activity']['comp'], self.save_state['WM_activity']['coop'])]
                plt.plot(self.save_state['WM_activity']['t'], tot_c2, '--',  linewidth=2, color='k', label='total')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
                plt.margins(0.1, 0.1)
            
            plt.show()
        
        # Plot c2 network data
        if c2_network:
            plt.figure(facecolor='white')    
            plt.subplot(2,1,1)
            plt.title('C2 instances and links')
            plt.xlabel('time', fontsize=14)
            plt.ylabel('number', fontsize=14)
            plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['c2_network']['num_insts'],  linewidth=2, color='b', label='num insts')
            plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['c2_network']['num_coop_links'],  linewidth=2, color='g', label='num coop links')
            plt.plot(self.save_state['WM_activity']['t'], self.save_state['WM_activity']['c2_network']['num_comp_links'],  linewidth=2, color='r', label='num comp links')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
            plt.margins(0.1, 0.1)
            
            plt.subplot(2,1,2)
            plt.title('C2 network density')
            plt.xlabel('time', fontsize=14)
            plt.ylabel('density', fontsize=14)
            coop_density = [2.0*e_coop/(n*(n-1)) if n>1 else 0 for (n,e_coop) in zip(self.save_state['WM_activity']['c2_network']['num_insts'],self.save_state['WM_activity']['c2_network']['num_coop_links'])]           
            comp_density = [2.0*e_comp/(n*(n-1)) if n>1 else 0 for (n,e_comp) in zip(self.save_state['WM_activity']['c2_network']['num_insts'],self.save_state['WM_activity']['c2_network']['num_comp_links'])]
            plt.plot(self.save_state['WM_activity']['t'], coop_density,  linewidth=2, color='g', label='coop density')
            plt.plot(self.save_state['WM_activity']['t'], comp_density,  linewidth=2, color='r', label='comp density')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
            plt.margins(0.1, 0.1)
            plt.show()
            
        
    def show_state(self):
        """
        Uses NetworX draw methods to display the WM state.
        
        Note:
            - NetworkX display methods are quite bad. Migrate to DOT format or to another way of 
            rendering the graph.
        """
        state = nx.DiGraph()
        for inst in self.schema_insts:
            state.add_node(inst.name, activation=inst.activity)
        for link in self.coop_links:
            state.add_edge(link.inst_from.name, link.inst_to.name, type="coop", weight=link.weight)
            if link.asymmetry_coef < 1:
                state.add_edge(link.inst_to.name, link.inst_from.name, type="coop", weight=link.weight*(1-link.asymmetry_coef))
        for link in self.comp_links:
            state.add_edge(link.inst_from.name, link.inst_to.name, type="comp", weight=link.weight)
            if link.asymmetry_coef < 1:
                state.add_edge(link.inst_to.name, link.inst_from.name, type="comp", weight=link.weight*(1-link.asymmetry_coef))
            
        pos = nx.spring_layout(state)   
        node_labels = dict((n, '%s(%.1f)' %(n, d['activation'])) for n,d in state.nodes(data=True))
        get_edges = lambda edge_type: [e for e in state.edges() if state.edge[e[0]][e[1]]['type'] == edge_type]
        
        plt.figure(facecolor='white')
        plt.axis('off')
        title = '%s state (t=%i)' %(self.name,self.t)
        plt.title(title)
            
        nx.draw_networkx_nodes(state, pos=pos, node_color='b', node_shape='s', with_labels=False)
        nx.draw_networkx_labels(state, pos=pos, labels= node_labels)
        nx.draw_networkx_edges(state, pos=pos, edgelist=get_edges('coop'), edge_color='g')
        nx.draw_networkx_edges(state, pos=pos, edgelist=get_edges('comp'), edge_color='r')
             
class F_LINK(object):
    """
    Functional links between schema instances in working memory
    Activations propagates in both directions. The asymmetry_coef parameter controls how asymmetrical is the link.
        0 <= asymmetry_coef <= 1
            from_inst -> to_inst: weight
            to_inst -> from_inst: weight*(1-asymmetry_coef)
        
    Data:
        - WM (WM): Working memory it is associated with.
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (FLOAT)
        - asymmetry_coef (FLOAT): 0 <= asymmetry_coef <= 1
        - weight_func (Lambda function): Function to update weigths at each f-link update. Lambda function lambda x,y,x : f(x,y,z) that takes three arguments: x = current weight, y = activation of inst_from, z = activation of inst_to, and returns a new weight.
    """
    def __init__(self, inst_from=None, inst_to=None, weight=0.0, asymmetry_coef=0.0, weight_func=lambda x,y,z:x):
        """
        """
        self.inst_from = inst_from
        self.inst_to = inst_to
        self.weight = float(weight)
        self.asymmetry_coef = float(asymmetry_coef)
        self.weight_func=weight_func
    
    def update_weight(self, new_weight):
        self.weight = float(new_weight)
    
    def update(self):
        """
        """
        self.inst_to.act_port_in.value.append(self.inst_from.act_port_out.value*self.weight) # Activation can be propagated in both directions depending on asymmetry coef.
        self.inst_from.act_port_in.value.append(self.inst_to.act_port_out.value*self.weight*(1-self.asymmetry_coef))
        new_weight = self.weight_func(self.weight, self.inst_from.activity, self.inst_to.activity)
        self.update_weight(new_weight)
    
    def copy(self):
        new_flink = F_LINK(inst_from=self.inst_from, inst_to=self.inst_to, weight=self.weight, asymmetry_coef=self.asymmetry_coef)
        return new_flink
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {"inst_from":self.inst_from.name, "inst_to":self.inst_to.name, "weight":self.weight, "asymmetry_coef":self.asymmetry_coef}
        return data
    
class COOP_LINK(F_LINK):
    """
    Cooperation functional links between schema instances in working memory
        
    Data inherited:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (FLOAT)
        - asymmetry_coef (FLOAT): 0 <= asymmetry_coef <= 1
        - weight_func (Lambda function): Function to update weigths at each f-link update. Lambda function lambda x,y,x : f(x,y,z) that takes three arguments: x = current weight, y = activation of inst_from, z = activation of inst_to, and returns a new weight.
    
    Data:        
        - connect (CONNECT)
    """
    def __init__(self, inst_from=None, inst_to=None, weight=1.0, asymmetry_coef=0.0, weight_func=lambda x,y,z:x):
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight, asymmetry_coef, weight_func)
        self.connect = CONNECT()
    
    def set_connect(self, port_from, port_to, weight=0.0, delay=0.0):
        self.connect.port_from = port_from
        self.connect.port_to = port_to
        self.connect.weight = float(weight)
        self.connect.delay = float(delay)
    
    def update_weight(self, new_weight):
        self.weight = float(new_weight)
        self.connect.weight = float(new_weight)
    
    def has_ports(self):
        return self.connect.port_from and self.connect.port_to
    
    def copy(self):
        new_flink = COOP_LINK(inst_from=self.inst_from, inst_to=self.inst_to, weight=self.weight, asymmetry_coef=self.asymmetry_coef)
        new_flink.connect = self.connect.copy()
        return new_flink
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(COOP_LINK, self).get_info()
        data['connect'] = self.connect.get_info()
        return data

class COMP_LINK(F_LINK):
    """
    Competition functional links between schema instances in working memory
        
    Data inherited:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (FLOAT)
        - asymmetry_coef (float): 0 <= asymmetry_coef <= 1
        - weight_func (Lambda function): Function to update weigths at each f-link update. Lambda function lambda x,y,x : f(x,y,z) that takes three arguments: x = current weight, y = activation of inst_from, z = activation of inst_to, and returns a new weight.
    """
    def __init__(self, inst_from=None, inst_to=None, weight=-1.0, asymmetry_coef=0.0, weight_func=lambda x,y,z:x): #Symmetric links
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight, asymmetry_coef, weight_func)

class ASSEMBLAGE(FUNCTION_SCHEMA):
    """
    Defines a schema instance assemblage.
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - inputs (DICT): At each time steps stores the inputs
        - outputs (DICT): At each time steps stores the ouputs
        - params (DICT)
        - activity (FLOAT):
    
    Data:
        - schema_inst ([SCHEMA_INSTS])
        - coop_links ([COOP_LINKS])
        - activation (FLOAT)
        - score (FLOAT): The score is the value that defines the impact of the assemblages on the instances.
    
    Note:
        - For now, the FUNCTION_SCHEMA data is unused by the assemblage.
    """
    def __init__(self, name=""):
        FUNCTION_SCHEMA.__init__(self, name)
        self.schema_insts = []
        self.coop_links = []
        self.activation = 0.0
        self.score = 0.0
    
    def add_instance(self, new_inst):
        """
        Add an instance new_inst (SCHEMA_INST) to the assemblage.
        An instance can only be added if it is not already present in the assemblage.
        Updates activation
        Returns True if the link was sucessfully added, False otherwise.
        """
        for inst in self.schema_insts:
            if inst == new_inst:
                error_msg = "Instance %s is already in the assemblage" %new_inst.name
                raise ValueError(error_msg)

        self.schema_insts.append(new_inst)
        self.update_activation()
        return True
    
    def remove_instance(self, inst):
        """
        Remove an instance from the assemblage.
        Also removes any links that contains this instance.
        Updates activation.
        """
        if not self.has_instance(inst):
            error_msg = "Instance %s is not in the assemblage" %inst.name
            raise ValueError(error_msg)
        
        self.schema_insts.remove(inst)
        links_from = self.find_links(inst_from=inst, inst_to='any')
        links_to = self.find_links(inst_from = 'any', inst_to=inst)
        for link in links_from + links_to:
            self.remove_link(link)
        
        self.update_activation()
        return True
        
    def add_link(self, link):
        """
        Add an cooperation link 'link' (COOP_LINK) to the assemblage.
        A link can only be added that does not add a connection to an already used in port or out port.
        Returns True if the link was sucessfully added, False otherwise.
        """
        for l in self.coop_links:
            if l.has_ports() and ((l.connect.port_from == link.connect.port_from) or (l.connect.port_to == link.connect.port_to)):
                raise ValueError("assemblage already contains a coop_link that link to a similar port.")
                 
        self.coop_links.append(link)
        return True
    
    def remove_link(self, link):
        """
        Remove the link from the assemblage
        """
        if link not in self.coop_links:
            raise ValueError("Cannot remove link from assemblage, link does not exist")
        
        self.coop_links.remove(link)
        return True
            
    
    def find_links(self, inst_from='any', inst_to='any'):
        """
        Returns a list of coop_links that match the criteria.
        By default, it returns al the coop_links (no criteria specified)
        
        Args:
            - inst_from (SCHEMA_INST or 'any')
            - inst_to (SCHEMA_INST or 'any')
        """
        results = []
        for flink in self.coop_links:
            if inst_from!='any' and not(flink.inst_from != inst_from):
                continue
            if inst_to!='any' and not(flink.inst_to != inst_to):
                continue
            results.append(flink)
            
        results = list(set(results))
        return results
        

    def update_activation(self):
        """
        Update the activation of the assemblage.
        
        FOR NOW SIMPLY THE AVERAGE (or SUM) ACTIVATION OF THE INSTANCES CONTAINED IN THE ASSEMBLAGE.
        """
        self.activation = sum([inst.activity for inst in self.schema_insts])/len(self.schema_insts) # Average
#        self.activation = sum([inst.activity for inst in self.schema_insts]) # Sum (favors larger assemblage)
        
        self.activity = self.activation
        self.compute_score()
    
    def compute_score(self):
        """
        Computes the score value.
        """
        self.score = self.activation
        
    def has_instance(self, inst):
        """
        Returns True if the assemblage contains the instance inst
        
        Args:
            - inst (SCHEMA_INST)
        """
        val = inst in self.schema_insts  
        return val
    
    def has_coop_link(self, coop_link):
        """
        Returns True if the assemblage contains the coop_link
        
        Args:
            - coop_link (COOP_LINK)
        """
        val = coop_link in self.coop_links
        return val
        
    def copy(self):
        """
        Returns a copy of itself.
        Note:
            - Only copies the assemblage specific data not the general function schema data.
        """
        new_assemblage = ASSEMBLAGE()
        new_assemblage.activation = self.activation
        new_assemblage.schema_insts = self.schema_insts[:] # neither deep nor shallow copy.
        new_assemblage.coop_links = self.coop_links[:] 
        return new_assemblage
    
    ######################
    ### STATIC METHODS ###
    ######################
    @staticmethod
    def merge(asmb_1, asmb_2):
        """
        Merges two assemblages asmb_1 and asmb_2 by taking the union of their instance sets and of their coop-links sets.
        Returns a new assemblage that correspond to the result of merge.
        
        Args:
            asmb_1, asmb_2 (ASSEMBLAGES)
        """
        asmb = ASSEMBLAGE()
        
        # getting schema_inst union
        insts_1 = set(asmb_1.schema_insts)
        insts_2 = set(asmb_2.schema_insts)
        insts = list(insts_1.union(insts_2))
        asmb.schema_insts = insts
        
        # getting coop_links union
        clinks_1 = set(asmb_1.coop_links)
        clinks_2 = set(asmb_2.coop_links)
        clinks = list(clinks_1.union(clinks_2))
        asmb.coop_links = clinks
        
        asmb.update_activation()
        
        return asmb
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {}
        data['schema_insts'] = [s.name for s in self.schema_insts]
        data['coop_links'] = [l.get_info() for l in self.coop_links]
        data['activation'] = self.activation
        return data            

#################################
##### BRAIN MAPPING CLASSES #####
#################################
class BRAIN_MAPPING(object):
    """
    Defines the mappings between system schemas and brain regions and between schema connections and brain connections.
    
    Data:
        -schema_mapping {schema_name1:[brain_region1, brain_region2,...], schema_name2:[brain_region3, brain_region4,...],...}
        -connect_mapping {connect_name1:[brain_connection1, brain_connection2,...], connect_name2:[brain_connection3, brain_connection4,...],...}
    """
    BRAIN_REGIONS = []
    BRAIN_CONNECTIONS = []
    def __init__(self):
        self.schema_mapping = {}
        self.connect_mapping = {}
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {}
        data['schema_mapping'] = self.schema_mapping
        data['connect_mapping'] = self.connect_mapping
        return data
    

#################################
##### SCHEMA SYSTEM CLASSES #####
#################################
class SCHEMA_SYSTEM(object):
    """
    Defines a model as a system of system schemas.
    Data:
        - name (str):
        - schemas({schema_name:SYSTEM_SCHEMAS}):
        - params (DICT): offers direct access to all the parameters in the model.
        - default_params (DICT): can store default parameter values.
        - connections ([CONNECT]):
        - input_port ([PORT]): the list of ports that read the input
        - output_ports ([PORT]): The list of ports that defines the output value
        - input (): system's input.
        - outputs {'schema:pid':val}: system's outputs.
        - brain_mapping (BRAIN_MAPPING)
        - t (FLOAT): System global time.
        - dt (FLOAT): System time increment.
        - set_up_time (INT): Number of time steps the system is ran so that all its sub-systems are in proper initial states.
        - verbose (BOOL): If True, print execution information.
        - sim_data (DICT): stores the simulation data.
    """
    T0 = 0.0
    TIME_STEP = 1.0
    SET_UP_TIME = 10
    def __init__(self, name=''):
        self.name = name
        self.schemas = {}
        self.params = None
        self.default_params = None
        self.connections = []
        self.input_ports = None
        self.output_ports = None
        self.input = None
        self.outputs = {}
        self.brain_mapping = None
        self.t = SCHEMA_SYSTEM.T0
        self.dt = SCHEMA_SYSTEM.TIME_STEP
        self.set_up_time = SCHEMA_SYSTEM.SET_UP_TIME
        self.verbose = False
        self.sim_data = {'schema_system':{}, 'system_states':{}}
        
    def reset(self):
        """
        Reset the system to its initial state t=0
        """      
        self.input = None
        self.outputs = {}
        self.t = SCHEMA_SYSTEM.T0
        self.sim_data = {'schema_system':{}, 'system_states':{}}
        for schema_name in self.schemas:
            schema = self.schemas[schema_name]
            schema.t = self.t
            schema.reset()
        for connection in self.connections:
            connection.reset()
    
    def add_connection(self, from_schema, from_port, to_schema, to_port, name='', weight=0, delay=0):
        """
        Adds connection (CONNECT) between from_schema:from_port (SYSTEM_SCHEMA:PORT) to to_schema:to_port (SYSTEM_SCHEMA:PORT).
        Returns True if successful, False otherwise.
        """
        port_from = from_schema.find_port(from_port)
        port_to = to_schema.find_port(to_port)
        if port_from and port_to:
            new_connect = CONNECT(name=name, port_from=port_from, port_to=port_to, weight=weight, delay=delay)
            self.connections.append(new_connect)
            new_connect.schema_system = self
            return True
        else:
            return False
    
    def add_schemas(self, schemas):
        """
        Add all the system schemas in "schemas" ([SYSTEM_SCHEMAS]) to the system.
        """
        for schema in schemas:
            schema.dt = self.dt
            schema.t = self.t
            if schema.name in self.schemas:
                error_msg = "There is already a schema named %s" % schema.name
                raise ValueError(error_msg)
            else:
                self.schemas[schema.name] = schema
                schema.schema_system = self
        
        self.params = self.get_params() # update the params value to account for new parameters.
    
    def set_input_ports(self, ports):
        """
        """
        self.input_ports = ports
    
    def set_output_ports(self, ports):
        """
        """
        self.output_ports = ports
    
    def set_input(self, sys_input):
        """
        Sets system input to 'sys_input'
        """
        self.input = sys_input
    
    def update_schema_param(self, schema_name, param_path, param_value):
        """
        Update the parameter valu ein schema_name defined by the param_path to param_value.
        
         Args:
            - schema_name (str): name of the target schema
            - param_path (str): String giving the path to the param using . chain (e.g. "dynamics.activation' would set the path to params['dynamics']['activation'])
            - param_value (): New value of the parameter
        """
        schema = self.schemas[schema_name]
        schema.update_param(param_path, param_value)
    
    def update_params(self, params):
        """
        Update the parameter value for all schema_name defined
        as keys in param_set with the values param_path to param_value.
        
         Args:
            - params (DICT): {"schema_name.param_path":"param_value"}
        """
        for key, param_value in params.iteritems():
            path_list = key.split('.')
            path_list.reverse()
            schema_name = path_list.pop()
            path_list.reverse()
            param_path = '.'.join(path_list)
            self.update_schema_param(schema_name, param_path, param_value)
        
    def get_output(self):
        """
        Returns sysetm output
        """
        if self.t in self.outputs:
            return self.outputs[self.t]
        else:
            return None
            
    def initialize_states(self):
        """
        Run the model for self.set_up_time steps.
        Does not read inputs or posts outputs.
        self.t is not updated, simulation results not saved.
        """
        for t in range(self.set_up_time):
             # Update all the schema states
            for schema_name, schema in self.schemas.iteritems():
                init_t = time.time()
                schema.update()
                end_t = time.time()
                schema.t = self.t
                if self.verbose:
                    print 'Update %s, (%f s)' %(schema_name, end_t - init_t)
            
            # Propagate value through connections
            for connection in self.connections:
                connection.update()
        
    def update(self):
        """
        By defaults:
            - Gets system input
            - Updates all the schemas.
            - Propage port values through connections.
            - Update system outputs.
        """
        # Update time
        self.t += self.dt
        
        # Get system input
        for port in self.input_ports:
            port.value = self.input
            self.input = None
        
        # Update all the schema states
        for schema_name, schema in self.schemas.iteritems():
            init_t = time.time()
            schema.update()
            end_t = time.time()
            schema.t = self.t
            if self.verbose:
                print 'Update %s, (%f s)' %(schema_name, end_t - init_t)
        
        # Propagate value through connections
        for connection in self.connections:
            connection.update()
        
        # Update the system output
        self.outputs[self.t] = {}
        for port in self.output_ports:
            self.outputs[self.t][port.schema.name] = port.value
            port.value = None
        
        # Save simulation data
        if not(self.sim_data['schema_system']):
            self.sim_data['schema_system'] = self.get_info()
        self.sim_data[self.t] = self.get_state()    
    
    def set_default_params(self, params=None):
        """
        Set default model parameters to params if params != None. Else set default params to self.params.
        If params != None, the model does not check for compatibility of the input with the parameter space of the model!
        """
        if params:
            self.default_params = params
        else:
            self.default_params = params.copy()
            
    def reset_default_params(self):
        """
        Resets the params to the default parameters
        """
        self.params = self.default_params.copy()
        
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {'name':self.name, 'T0':SCHEMA_SYSTEM.T0, 'TIME_STEP':SCHEMA_SYSTEM.TIME_STEP, 'dt':self.dt}
        data['connections'] = [c.get_info() for c in self.connections]
        data['input_ports'] = [p.name for p in self.input_ports]
        data['output_ports']= [p.name for p in self.output_ports]
        data['brain_mapping'] = self.brain_mapping.get_info()
        
        data['system_schemas'] = {}
        for schema_name, schema in self.schemas.iteritems():
            data['system_schemas'][schema_name] = schema.get_info()
        
        return data
    
    def get_state(self):
        """
        """
        data = {'schema_states':{}}
        for schema_name, schema in self.schemas.iteritems():
            data['schema_states'][schema_name] = schema.get_state()
        return data
    
    def get_params(self):
        """
        Returns a dictionary containing pointers to the parameters for each system schema in the model.
        """
        sys_params = {}
        for schema_name, schema in self.schemas.iteritems():
            sys_params[schema_name] = schema.params
        
        return sys_params
    
    def save_sim(self, file_path = './tmp/', file_name = 'output.json'):
        """
        """
        my_file = file_path + file_name
        if not(os.path.exists(file_path)):
            os.mkdir(file_path)
        with open(my_file, 'wb') as f:
            json.dump(self.sim_data, f, sort_keys=True, indent=4, separators=(',', ': '))
    
    #######################
    ### DISPLAY METHODS ###
    #######################
    def system2dot(self, image_type='svg', disp=False, show_brain_regions=False, folder='./tmp/'):
        """
        Generates a dot file of the system's graph.
        Also creates an image.
        """
        import subprocess
        import pydot
        
        tmp_folder = folder
        if not(os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)       
        
        prog = 'dot'
        file_type = image_type
        dot_sys = pydot.Dot(graph_type = 'digraph', splines = 'ortho')
        dot_sys.set_rankdir('LR')

        color = 'black'
        node_shape = 'record'
        style = 'filled'
        fill_color = 'white'
        
        dot_sys.add_node(pydot.Node('INPUT', label='INPUT', shape='oval'))
        dot_sys.add_node(pydot.Node('OUTPUT', label='OUTPUT', shape='oval'))
        
        for schema_name, schema in self.schemas.iteritems():
            if show_brain_regions:
                brain_regions = self.brain_mapping.schema_mapping[schema.name]
                label = '<<FONT FACE="consolas">'+schema.name+'</FONT><BR /><FONT POINT-SIZE="10">['+', '.join(brain_regions) +']</FONT>>'
            else:
                label = '<<FONT FACE="consolas">'+schema.name+'</FONT>>'
            dot_sys.add_node(pydot.Node(schema.name, label=label, color=color, shape=node_shape, style=style, fillcolor=fill_color))
        
        for connection in self.connections:
            from_schema = connection.port_from.schema.name
            to_schema = connection.port_to.schema.name
            dot_sys.add_edge(pydot.Edge(from_schema, to_schema, label=connection.name))
        
        for port in self.input_ports:
            from_schema = 'INPUT'
            to_schema = port.schema.name
            dot_sys.add_edge(pydot.Edge(from_schema, to_schema, style='dotted'))
        
        for port in self.output_ports:
            from_schema =  port.schema.name
            to_schema = 'OUTPUT'
            dot_sys.add_edge(pydot.Edge(from_schema, to_schema, style='dotted'))
        
        file_name = tmp_folder + self.name + ".gv"
        dot_sys.write(file_name)
        
         # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
        if disp:
            if image_type != 'png':
                print 'CANNOT DISPLAY %s TYPE, please use "png"' % image_type
            else:
                img_name = '%s.%s' %(file_name,file_type)
                plt.figure(facecolor='white')
                plt.axis('off')
                title = self.name
                plt.title(title)
                img = plt.imread(img_name)
                plt.imshow(img)
    
    def show_params(self):
        """
        Display all the parameters of the schema system.
        """
        print "MODEL PARAMETERS"
        pprint.pprint(self.params, indent=1, width=1)
            
############################
##### MODULE FUNCTIONS #####
############################
def save(schema_system, path='./tmp/'):
    """
    Saves a schema system using pickle.
    """
    file_name = path + schema_system.name
    if not(os.path.exists(path)):
            os.mkdir(path)
            
    with open(file_name, 'w') as f:
        pickle.dump(schema_system, f)

def load(schema_system_name,path='./tmp/'):
    """
    loads a schema system using pickle.
    """
    file_name = path + schema_system_name
    with open(file_name, 'r') as f:
        schema_system  = pickle.load(f)
        return schema_system
    return None
        
###############################################################################
if __name__=="__main__":
    ###############
    ### Test WM ###
    ###############
    schema_names = [1,2,3,4,5]
    act_noise = (0.5, 0.1) # (mean, std)
    coop = [(1,2), (4,5)]
    comp = [(3,2), (3,5)]
    E = 1.0
    insts = {}
    wm = WM()
    wm.update_param('C2.prune_threshold', 0.2)
    for schema_name in schema_names:
        act = np.random.normal(act_noise[0], act_noise[1])
        name = "%i(%.2f)" %(schema_name, act)
        k_schema = KNOWLEDGE_SCHEMA(name=name , LTM=None, content=None, init_act=act)
        inst = SCHEMA_INST(schema=k_schema, trace=k_schema)
        wm.add_instance(inst, inst.trace.init_act)
        insts[schema_name] = inst
    
    
    for (name_from, name_to) in comp:
        wm.add_comp_link(inst_from=insts[name_from], inst_to=insts[name_to], weight=-1)
        print "comp: %s and %s" %(insts[name_from].name, insts[name_to].name)
        
    for (name_from, name_to) in coop:
        wm.add_coop_link(inst_from=insts[name_from], port_from=None, inst_to=insts[name_to], port_to=None, weight=1)
        print "coop: %s and %s" %(insts[name_from].name, insts[name_to].name)
    
    wm.show_state()
    max_step = 20
    for step in range(max_step):
        print "#####################"
        print "t = %i" %step
        wm.t = step
        for inst in wm.schema_insts:
            inst.activation.E = E
        wm.update_activations()
        wm.prune()
      
    # add new schemas
      
    schema_names = [6,7]
    coop = [(6,7), (6,2)]
    comp = [(2,7)]
        
    for schema_name in schema_names:
        act = np.random.normal(act_noise[0], act_noise[1])
        name = "%i(%.2f)" %(schema_name, act)
        k_schema = KNOWLEDGE_SCHEMA(name=name , LTM=None, content=None, init_act=act)
        inst = SCHEMA_INST(schema=k_schema, trace=k_schema)
        wm.add_instance(inst, inst.trace.init_act)
        insts[schema_name] = inst
    
    
    for (name_from, name_to) in comp:
        wm.add_comp_link(inst_from=insts[name_from], inst_to=insts[name_to], weight=-1)
        print "comp: %s and %s" %(insts[name_from].name, insts[name_to].name)
        
    for (name_from, name_to) in coop:
        wm.add_coop_link(inst_from=insts[name_from], port_from=None, inst_to=insts[name_to], port_to=None, weight=1)
        print "coop: %s and %s" %(insts[name_from].name, insts[name_to].name)
    
    wm.show_state()
    max_step = 20
    for step in range(20, 20+max_step):
        print "#####################"
        print "t = %i" %step
        wm.t = step
        for inst in wm.schema_insts:
            inst.activation.E = E
        wm.update_activations()
        wm.prune()
    
    wm.show_dynamics()
    wm.show_state()
            
            
    
    
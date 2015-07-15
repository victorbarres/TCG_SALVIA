# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines the based schema theory classes.

Uses abc to define abstract classes
Uses time only to provide execution timing for procedural schema updating.
Uses random
Uses numpy to implement the schema instances activation values.
Uses matplotlib.plt to visualize WM state dynamics
Uses networkx to visualize WM state
Uses json to save simulation data in json format.
"""
import abc
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import pickle

import networkx as nx
import json

##################################
### SCHEMAS (Functional units) ###
##################################
class SCHEMA(object):
    """
    Schema (base class)
    
    Data:
        - id (int): Unique id
        - name (str): schema name
        - schema_system (SCHEMA_SYSTEM): Schema system to which the instance belongs.
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
    def __init__(self, name='',  port_from=None, port_to=None, weight=0, delay=0):
        """
        """
        SCHEMA.__init__(self, name=name)
        self.port_from = port_from
        self.port_to = port_to
        self.weight = weight
        self.delay = delay
    
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
        
    def update(self):
        """
        For now does not involve weight or delay!
        Sets the value of port_rom to the value of port_to.
        Resets the port_from value to None.
        """
        self.port_to.value = self.port_from.value
        self.port_from.value = None
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {"id":self.id, "name":self.name, "port_from":self.port_from.name, "port_to":self.port_to.name, "weight":self.weight, "delay":self.delay}
        return data

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
        self.LTM = LTM
        self.content = content
        self.init_act = init_act
    
    def set_name(self, name):
        self.name = name

    def set_init(self, init_act):
        self.init_act = init_act
    
    def set_content(self, content):
        self.content = content
    
    def set_LTM(self, LTM):
        self.LTM = LTM

class PROCEDURAL_SCHEMA(SCHEMA):
    """
    Procedural schema base class
    Those schemas cannot be instantiated. They can be linked to brain data.
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
    Data:
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - activity (float): The activity level of the schema.
        - t (FLOAT): Time.
        - dt (FLOAT): Time step.
    """
    def __init__(self, name=''):
        SCHEMA.__init__(self,name)
        self.activity = 0
        self.in_ports = []
        self.out_ports = []
        self.t = 0
        self.dt = 1.0
    
    
    def add_port(self,port_type, port_name='', port_data=None, port_value=None):
        """
        Adds a new port to the procedural schema. Port_type (str) ['IN' or 'OUT'], port_name (str), and a value port_value for the port.
        If sucessessful, returns the port id. Else returns None.
        """
        new_port = PORT(port_type, port_schema=self, port_name=port_name, port_data=port_data, port_value=port_value)
        if port_type == PORT.TYPE_IN:
            self.in_ports.append(new_port)
            return new_port.id
        elif port_type == PORT.TYPE_OUT:
            self.out_ports.append(new_port)
            return new_port.id
        else:
            return None
    
    def get_input(self, port_name):
        """
        Return the current value of the port with name 'port_name' and resets the port value to None. If the port is not an input port, if multiple ports shared the same name or if the port is 
        not found, returns None.
        """
        port = self.find_port(port_name)
        if port and (port.type == PORT.TYPE_IN):
            val = port.value
            port.value = None # Resets port value
            return val
        elif port and (port.type == PORT.TYPE_OUT):
            print("ERROR: port %s refers to an output port" % port_name)
            return None
        else:
            print("ERROR: port %s does not exist or could refer to multiple ports" % port_name)
            return None
    
    def set_output(self, port_name, val):
        """
        Sets the value of the output port with name 'port_name' to 'val'. If the port is not an output port, if multiple ports shared the same name or if the port is 
        not found, returns False, else returns True.
        """
        port = self.find_port(port_name)
        if port and (port.type == PORT.TYPE_OUT):
            port.value = val
            return True
        elif port and (port.type == PORT.TYPE_IN):
            print("ERROR: port %s refers to an output port" % port_name)
            return False
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
            print("ERROR: port %s does not exist or could refer to multiple ports" % port_name)
            return None
        return found[0]
    
    @abc.abstractmethod    
    def update(self):
        """
        This function should be specified for every specific PROCEDURAL_SCHEMA class.
        When called, this function should read the value at the input ports and based on the state of the procedure, update the state of the procedural schema
        and post values at the output ports.
        """
        return
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        Returns a JSON formated string containing the schema's description info.
        """
        data = {"name":self.name, "type":self.__class__.__name__, "parameters":{"dt":self.dt}, 
                     "in_ports":[p.name for p in self.in_ports], "out_ports":[p.name for p in self.out_ports]}
        return data
        
    def get_state(self):
        """
        Returns a JSON formated string containing schema's current state's information.
        """
        data = {"name":self.name, "t":self.t, "activity":self.activity}
        return data
         
#################################
### PROCEDURAL SCHEMA CLASSES ###
#################################        
class SCHEMA_INST(PROCEDURAL_SCHEMA):
    """
    Schema instance
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - activity (float):
    Data:
        - alive (bool): status flag
        - trace (): Pointer to the element that triggered the instantiation.
        - act_params (DICT): {t0:FLOAT,act0: FLOAT, dt:FLOAT, tau:FLOAT act_inf:FLOAT, L:FLOAT, k:FLOAT, x0:FLOAT, noise_mean:FLOAT, noise_std:FLOAT}
        - activation (INST_ACTIVATION): Activation value of schema instance
        - act_port_in (PORT): Stores the vector of all the input activations.
        - act_port_out (PORT): Sends as output the activation of the instance.
    """    
    def __init__(self,schema=None, trace=None):
        PROCEDURAL_SCHEMA.__init__(self,name="")
        self.content = None      
        self.alive = False
        self.trace = None
        self.activity = 0
        self.act_params = {'t0':0.0, 'act0': 1.0, 'dt':0.1, 'tau':1.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0.0, 'noise_std':0.0}
        self.activation = None
        self.act_port_in = PORT("IN", port_schema=self, port_name="act_in", port_value=[]);
        self.act_port_out = PORT("OUT", port_schema=self, port_name="act_in", port_value=0);
        self.instantiate(schema, trace)
     
    def initialize_activation(self):
        """
        Set activation parameters
        """
        self.activation = INST_ACTIVATION(t0=self.act_params['t0'], act0=self.act_params['act0'], dt=self.act_params['dt'], tau=self.act_params['tau'],
                                          act_inf=self.act_params['act_inf'], L=self.act_params['L'], k=self.act_params['k'], x0=self.act_params['x0'],
                                          noise_mean=self.act_params['noise_mean'], noise_std=self.act_params['noise_std'])
        
        self.activation.save_vals["t"].append(self.act_params['t0'])
        self.activation.save_vals["act"].append(self.act_params['act0'])
        self.activity = self.act_params['act0']
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
    
    def instantiate(self, schema, trace):
        """
        Sets up the state of the schema instance at t0 of instantiation with tau characteristic time for activation dynamics.
        """
        self.content = schema.content
        self.name = "%s_%i" %(schema.name, self.id)
        self.alive = True
        self.trace = trace
        self.set_ports()
        self.act_params['act0'] = float(schema.init_act)
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
    def update(self):
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
    def __init__(self, t0=0.0, act0=1.0, dt=0.1, tau=1.0, act_inf=0.0, L=1.0, k=10.0, x0=0.5, noise_mean=0.0, noise_std=0.0):
        self.t0 = float(t0)
        self.act0 = float(act0)
        self.tau = float(tau)
        self.act_inf = float(act_inf)
        self.L = float(L)
        self.k = float(k)
        self.x0 = float(x0)
        self.dt = float(dt) 
        self.t = self.t0
        self.act = self.act0
        self.noise_mean = float(noise_mean)
        self.noise_std = float(noise_std)
        self.save_vals = {"t":[], "act":[]}
        self.E = 0.0
        
    def update(self, I):
        """
        """
        noise =  random.normalvariate(self.noise_mean, self.noise_std)
        d_act = self.dt/(self.tau)*(-self.act + self.logistic(self.E + I + noise)) + self.act_inf
        self.t += self.dt
        self.act += d_act
        self.save_vals["t"].append(self.t)
        self.save_vals["act"].append(self.act)
        self.E = 0.0
    
    def logistic(self, x):
        return self.L/(1.0 + np.exp(-1.0*self.k*(x-self.x0)))
        
## LONG TERM MEMORY ###
class LTM(PROCEDURAL_SCHEMA):
    """
    Long term memory. 
    Stores the set of schemas associated with this memory.
    In addition, weighted connection can be defined betweens schemas to set up the LTM as a schema network. NOT USED IN TCG1.1!
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - activity (float): The activity level of the schema.
    Data:
        - schemas ([SCHEMA]): Schema content of the long term memory
        - connections ([{from:schema1, to:schema2, weight:w}]): List of weighted connections between schemas (for future use if LTM needs to be defined as schema network)
    """
    def __init__(self, name=''):
        PROCEDURAL_SCHEMA.__init__(self,name)
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
                print "%s: Ambiguous schema name" %name
                return None
        
### WORKING MEMORY ###
class WM(PROCEDURAL_SCHEMA):
    """
    Working memory
    Stores the currently active schema instances and the functional links through which they enter in cooperative computation.
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - activity (float): The activity level of the schema.
    Data:
        - schema_insts ([SCHEMA_INST]):
        - coop_links ([COOP_LINK]):
        - comp_links ([COMP_LINK]):
        - dyn_params ({'tau':FLOAT, 'act_inf':FLOAT, 'L':FLOAT, 'k':FLOAT, 'x0':FLOAT, 'noise_mean':FLOAT, 'noise_var':FLOAT})
        - C2_params ({'coop_weight':FLOAT, 'comp_weight':FLOAT, 'prune_threshold':FLOAT, 'confidence_threshold':FLOAT})
            - coop_weight (FLOAT): weight of cooperation f-links
            - comp_weight (FLOAT): weight of competition f-links
            - prune_threshold (FLOAT): Below this threshold the instances are considered inactive (Alive=False)
        - save_state (DICT): Saves the history of the WM states. DOES NOT SAVE THE F_LINKS!!! NEED TO FIX THAT.
        
        - assemblages ????
    """
    def __init__(self, name=''):
        PROCEDURAL_SCHEMA.__init__(self,name)
        self.name = name
        self.schema_insts = []
        self.coop_links = []
        self.comp_links = []
        self.dyn_params = {'tau':10.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0.0, 'noise_std':0.1}
        self.C2_params = {'coop_weight':1.0, 'comp_weight':-4.0, 'prune_threshold':0.3, 'confidence_threshold':0.8, 'coop_asymmetry':1, 'comp_asymmetry':0}
        self.save_state = {'insts':{}}
       
    def add_instance(self,schema_inst, act0=None):
        if schema_inst in self.schema_insts:
            return False
            
        self.schema_insts.append(schema_inst)
        if not(act0):
            act0 = schema_inst.activity # Uses the init_activation defined by the associated schema.
        act_params = {'t0':self.t, 'act0': act0, 'dt':self.dt, 'tau':self.dyn_params['tau'], 'act_inf':self.dyn_params['act_inf'],
                      'L':self.dyn_params['L'], 'k':self.dyn_params['k'], 'x0':self.dyn_params['x0'],
                      'noise_mean':self.dyn_params['noise_mean'], 'noise_std':self.dyn_params['noise_std']}
        schema_inst.act_params = act_params
        schema_inst.initialize_activation()
        self.save_state['insts'][schema_inst.name] = schema_inst.activation.save_vals.copy();
        return True
    
    def remove_instance(self, schema_inst):
        self.schema_insts.remove(schema_inst)
        
    def add_coop_link(self, inst_from, port_from, inst_to, port_to, qual=1.0, weight=None):
        if weight == None:
            weight=self.C2_params['coop_weight']
        new_link = COOP_LINK(inst_from, inst_to, weight*qual, self.C2_params['coop_asymmetry'])
        new_link.set_connect(port_from, port_to)
        self.coop_links.append(new_link)

    def find_coop_links(self,inst_from='any', inst_to='any', port_from='any', port_to='any'):
        """
        Returns a list of coop_links that match the criteria.
        By default, it returns al the coop_links (no criteria specified)
        """
        results = []
        for flink in self.coop_links:
            match = True
            if inst_from!='any' and not(flink.inst_from in inst_from):
                match = False
            if inst_to!='any' and not(flink.inst_to in inst_to):
                match = False
            if port_from!='any' and not(flink.connect.port_from in port_from):
                match = False
            if port_to !='any' and not(flink.connect.port_to in port_to):
                match = False
            
            if match:
                results.append(flink)
        results = list(set(results))
        return results
                   
    def remove_coop_links(self,inst_from, inst_to, port_from='any', port_to='any'):
        """
        Remove the coop_links from working memory that satisfy the criteria.
        """
        f_links = self.find_coop_links(inst_from=inst_from, inst_to=inst_to, port_from=port_from, port_to=port_to)
        for f_link in f_links:
            self.coop_links.remove(f_link)
        
    def add_comp_link(self, inst_from, inst_to, weight=None):
        if weight == None:
            weight=self.C2_params['comp_weight']
        new_link = COMP_LINK(inst_from, inst_to, weight, self.C2_params['comp_asymmetry'])
        self.comp_links.append(new_link)
    
    def find_comp_links(self,inst_from='any', inst_to='any'):
        """
        Returns a list of comp_links that match the criteria.
        By default, it returns al the comp_links (no criteria specified)
        """
        results = []
        for flink in self.comp_links:
            match = True
            if inst_from!='any' and (flink.inst_from != inst_from):
                match = False
            if inst_to!='any' and (flink.inst_to != inst_to):
                match = False
                
            if match:
                results.append(flink)
                
    def remove_comp_links(self,inst_from, inst_to):
        """
        Remove the comp_links from working memory that satisfy the criteria.
        """
        f_links = self.find_comp_links(inst_from=inst_from, inst_to=inst_to)
        for f_link in f_links:
            self.comp_links.remove(f_link)
           
    def update_activations(self, coop_p=1.0, comp_p=1.0):
        """
        Update all the activations of instances in working memory based on cooperation and competition f-links.
        Passes activations through coop links with probabiliy coop_p, and through competition liks with probability comp_p
        Then updates all instance activation.
        Saves states.
        """
        # Propagating cooperation
        for flink in self.coop_links:
            r = random.random()
            if(r<coop_p):
                flink.update()  
        
        # Propagating competition
        for flink in self.comp_links:
            r = random.random()
            if(r<comp_p):
                flink.update()
       
        # Update all instances activation and sets alive=False for instances that fall below threshold.
        for inst in self.schema_insts:
            inst.update_activation()
            if inst.activity<self.C2_params['prune_threshold']:
                inst.alive = False
        
        self.update_activity()
    
    def prune(self):
        """
        Removes from WM all the dead instances
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

    def update_activity(self):
        """
        Computes the overall activity of the working memory.
        The activity reflects the amount of cooperation and competition going on.
        """
        tot_coop = 0
        tot_comp = 0
        for link in self.coop_links:
            inst_from = link.inst_from
            inst_to = link.inst_to
            transfer = abs(inst_from.activity - inst_to.activity)*link.weight
            tot_coop += transfer
        
        for link in self.comp_links:
            inst_from = link.inst_from
            inst_to = link.inst_to
            transfer = abs(inst_from.activity - inst_to.activity)*link.weight*-1
            tot_comp += transfer
        
        self.activity = tot_comp + tot_coop
        if not(self.save_state.has_key('total_activity')):
            self.save_state['total_activity'] = {'t':[], 'act':[], 'comp':[], 'coop':[]}
        self.save_state['total_activity']['t'].append(self.t)
        self.save_state['total_activity']['comp'].append(tot_comp)
        self.save_state['total_activity']['coop'].append(tot_coop)
        self.save_state['total_activity']['act'].append(self.activity)
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(WM, self).get_info()
        data['dyn_params'] = self.dyn_params
        data['C2_params'] = self.C2_params
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
    def show_dynamics(self, c2_levels=True):
        """
        """
        plt.figure(facecolor='white')
        num_plots = 1
        if c2_levels:
            num_plots =2
        plt.subplot(num_plots,1,1)
        title = '%s dynamics \n dyn: [tau:%g, act_inf:%g, L:%g, k:%g, x0:%g], noise: [mean:%g, std:%g], C2: [coop:%g, comp:%g ,prune:%g, conf:%g]' %(
                            self.name,
                            self.dyn_params['tau'], self.dyn_params['act_inf'], self.dyn_params['L'], self.dyn_params['k'], self.dyn_params['x0'],
                            self.dyn_params['noise_mean'], self.dyn_params['noise_std'], 
                              self.C2_params['coop_weight'], self.C2_params['comp_weight'], self.C2_params['prune_threshold'], self.C2_params['confidence_threshold'])
        plt.title(title)
        plt.xlabel('time', fontsize=14)
        plt.ylabel('activity', fontsize=14)
        for inst in self.save_state['insts'].keys():
            plt.plot(self.save_state['insts'][inst]['t'], self.save_state['insts'][inst]['act'], label=inst, linewidth=2)
        axes = plt.gca()
        axes.set_ylim([0,1])
        axes.set_xlim([0, max(self.save_state['total_activity']['t'])])
        plt.axhline(y=self.C2_params['prune_threshold'], color='k',ls='dashed')
        plt.axhline(y=self.C2_params['confidence_threshold'], color='r',ls='dashed')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
        
        if c2_levels:
            plt.subplot(num_plots,1,num_plots)
            plt.title('Total activity')
            plt.xlabel('time', fontsize=14)
            plt.ylabel('activity', fontsize=14)
            plt.plot(self.save_state['total_activity']['t'], self.save_state['total_activity']['comp'],  linewidth=2, color='r', label='competition')
            plt.plot(self.save_state['total_activity']['t'], self.save_state['total_activity']['coop'],  linewidth=2, color='g', label='cooperation')
            plt.plot(self.save_state['total_activity']['t'], self.save_state['total_activity']['act'], '--',  linewidth=2, color='k', label='total')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, prop={'size':8})
            plt.show()
            
        
    def show_state(self):
        """
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
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (float)
        - asymmetry_coef (float): 0 <= asymmetry_coef <= 1
    """
    def __init__(self, inst_from=None, inst_to=None, weight=0.0, asymmetry_coef=0.0):
        """
        """
        self.inst_from = inst_from
        self.inst_to = inst_to
        self.weight = float(weight)
        self.asymmetry_coef = float(asymmetry_coef)
    
    def update_weight(self, new_weight):
        self.weight = float(new_weight)
    
    def update(self):
        """
        """
        self.inst_to.act_port_in.value.append(self.inst_from.act_port_out.value*self.weight) # Activation can be propagated in both directions depending on asymmetry coef.
        self.inst_from.act_port_in.value.append(self.inst_to.act_port_out.value*self.weight*(1-self.asymmetry_coef))
    
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
        
    Data:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - connect (CONNECT)
        
    NOTE: I need to experiment with the possibility to have 
    """
    def __init__(self, inst_from=None, inst_to=None, weight=1.0, asymmetry_coef=0.0):
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight, asymmetry_coef)
        self.connect = CONNECT()
    
    def set_connect(self, port_from, port_to, weight=0.0, delay=0.0):
        self.connect.port_from = port_from
        self.connect.port_to = port_to
        self.connect.weight = float(weight)
        self.connect.delay = float(delay)
    
    def update_weight(self, new_weight):
        self.weight = float(new_weight)
        self.connect.weight = float(new_weight)
    
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
        
    Data:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (float)
    """
    def __init__(self, inst_from=None, inst_to=None, weight=-1.0, asymmetry_coef=0.0): #Symmetric links
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight, asymmetry_coef)

class ASSEMBLAGE(object):
    """
    Defines a schema instance assemblage.
    """
    def __init__(self):
        self.schema_insts = []
        self.coop_links = []
        self.activation = 0.0
        self.score = 0.0
    
    def add_instance(self, new_inst):
        """
        Add an instance new_inst (SCHEMA_INST) to the assemblage.
        An instance can only be added if it is not already presen in the assemblage
        Returns True if the link was sucessfully added, False otherwise.
        """
        for inst in self.schema_insts:
            if inst == new_inst:
                return False
        self.schema_insts.append(new_inst)
        return True
        
    def add_link(self, link):
        """
        Add an cooperation link 'lin'k (COOP_LINK) to the assemblage.
        A link can only be added does not add a connection to an already used in port or out port.
        Returns True if the link was sucessfully added, False otherwise.
        """
        for l in self.coop_links:
            if (l.connect.port_from == link.connect.port_from) or (l.connect.port_to == link.connect.port_to):
                return False  
        self.coop_links.append(link)
        return True

    def update_activation(self):
        """
        Update the activation of the assemblage.
        
        FOR NOW SIMPLY THE AVERAGE (or SUM) ACTIVATION OF THE INSTANCES CONTAINED IN THE ASSEMBLAGE.
        """
        self.activation = sum([inst.activity for inst in self.schema_insts])/len(self.schema_insts) # Average
#        self.activation = sum([inst.activity for inst in self.schema_insts]) # Sum
    
    def copy(self):
        """
        Returns a copy of itself.
        """
        new_assemblage = ASSEMBLAGE()
        new_assemblage.activation = self.activation
        new_assemblage.schema_insts = self.schema_insts[:] # neither deep nor shallow copy.
        new_assemblage.coop_links = self.coop_links[:] 
        return new_assemblage
    
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

#############################
### BRAIN MAPPING CLASSES ###
#############################
class BRAIN_MAPPING(object):
    """
    Defines the mappings between procedural schemas and brain regions and between schema connections and brain connections.
    
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
    

############################
### SCHEMA SYSTEM CLASSES###
############################
class SCHEMA_SYSTEM(object):
    """
    Defines a model as a system of procedural schemas.
    Data:
        - name (str):
        - schemas({schema_name:PROCEDURAL_SCHEMAS}):
        - connections ([CONNECT]):
        - input_port ([PORT]): the list of ports that read the input
        - output_ports ([PORT]): The list of ports that defines the output value
        - input (): system's input.
        - outputs {'schema:pid':val}: system's outputs.
        - brain_mapping (BRAIN_MAPPING)
        - t (FLOAT): System global time.
        - dt (FLOAT): System time increment.
        - verbose (BOOL): If True, print execution information.
        - sim_data (DICT): stores the simulation data.
    """
    T0 = 0.0
    TIME_STEP = 1.0
    def __init__(self, name=''):
        self.name = name
        self.schemas = {}
        self.connections = []
        self.input_ports = None
        self.output_ports = None
        self.input = None
        self.outputs = {}
        self.t = SCHEMA_SYSTEM.T0
        self.dt = SCHEMA_SYSTEM.TIME_STEP
        self.verbose = False
        self.sim_data = {'schema_system':{}, 'system_states':{}}
    
    def add_connection(self, from_schema, from_port, to_schema, to_port, name='', weight=0, delay=0):
        """
        Adds connection (CONNECT) between from_schema:from_port (PROCEDURAL_SCHEMA:PORT) to to_schema:to_port (PROCEDURAL_SCHEMA:PORT).
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
        Add all the procedural schemas in "schemas" ([PROCEDURAL_SCHEMAS]) to the system.
        """
        for schema in schemas:
            schema.dt = self.dt
            schema.t = self.t
            if schema.name in self.schemas:
                print "ERROR: There is already a schema named %s" % schema.name
            else:
                self.schemas[schema.name] = schema
                schema.schema_system = self
    
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
        
    def get_output(self):
        """
        Returns sysetm output
        """
        if self.t in self.outputs:
            return self.outputs[self.t]
        else:
            return None
        
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
        for p in self.output_ports:
            self.outputs[self.t] = p.value
            p.value = None
        
        # Save simulation data
        if not(self.sim_data['schema_system']):
            self.sim_data['schema_system'] = self.get_info()
        self.sim_data[self.t] = self.get_state()    
    
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
        
        data['procedural_schemas'] = {}
        for schema_name, schema in self.schemas.iteritems():
            data['procedural_schemas'][schema_name] = schema.get_info()
        
        return data
    
    def get_state(self):
        """
        """
        data = {'schema_states':{}}
        for schema_name, schema in self.schemas.iteritems():
            data['schema_states'][schema_name] = schema.get_state()
        return data
    
    def save_sim(self, file_name = 'output.json'):
        """
        """
        with open(file_name, 'wb') as f:
            json.dump(self.sim_data, f, sort_keys=True, indent=4, separators=(',', ': '))
    
    #######################
    ### DISPLAY METHODS ###
    #######################
    def system2dot(self, image_type='svg', disp=False):
        """
        Generates a dot file of the system's graph.
        Also creates an image.
        """
        import subprocess
        import pydot
        
        tmp_folder = './tmp/'          
        
        prog = 'dot'
        file_type = image_type
        dot_sys = pydot.Dot(graph_type = 'digraph', splines = 'ortho')
        dot_sys.set_rankdir('LR')
        dot_sys.set_fontname('consolas')

        color = 'black'
        node_shape = 'record'
        style = 'filled'
        fill_color = 'white'
        
        dot_sys.add_node(pydot.Node('INPUT', label='INPUT', shape='oval'))
        dot_sys.add_node(pydot.Node('OUTPUT', label='OUTPUT', shape='oval'))
        
        for schema_name, schema in self.schemas.iteritems():
            brain_regions = self.brain_mapping.schema_mapping[schema.name]
            label = '<'+schema.name+'<BR /><FONT POINT-SIZE="10">['+', '.join(brain_regions) +']</FONT>>'
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
                
########################
### MODULE FUNCTIONS ###
########################
def save(schema_system, path='./tmp/'):
    """
    Saves a schema system using pickle.
    """
    file_name = path + schema_system.name
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
    num_schemas=10
    schemas = [KNOWLEDGE_SCHEMA(name="act:"+str(i*1.0/num_schemas), LTM=None, content=None, init_act=i*1.0/num_schemas) for i in range(1,num_schemas+1)]
    insts = [SCHEMA_INST(schema=s, trace=s) for s in schemas]
    wm = WM()
    for inst in insts:
            wm.add_instance(inst, inst.trace.init_act)
    
    for i in range(len(insts)):
        for j in range(len(insts)):
            if i != j:               
                r = random.random()
                if r <0.1:
                    wm.add_comp_link(inst_from=insts[i], inst_to=insts[j], weight=-1)
                    print "comp: %s and %s" %(insts[i].name, insts[j].name)
                
    for i in range(len(insts)):
        for j in range(len(insts)):
            if i != j:    
                r = random.random()
                if r <0.1:
                    wm.add_coop_link(inst_from=insts[i], port_from=None, inst_to=insts[j], port_to=None, weight=1)
                    print "coop: %s and %s" %(insts[i].name, insts[j].name)
    
    
    max_step = 1000
    for step in range(max_step):
        wm.t = step
        wm.update_activations()
        
    wm.show_dynamics()
    
    
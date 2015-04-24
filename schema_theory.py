# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 14:14:08 2015

@author: Victor Barres

Defines the based schema theory classes.

Uses random
Uses numpy to implement the schema instances activation values.
Uses matplotlib.plt to visualize WM state
"""
import random
import numpy as np
import matplotlib.pyplot as plt
##################################
### SCHEMAS (Functional units) ###
##################################
class SCHEMA:
    """
    Schema (base class)
    
    Data:
        - id (int): Unique id
        - name (str): schema name
    """
    ID_next = 1 # Global schema ID counter
    def __init__(self, name=""):
        self.id = SCHEMA.ID_next
        SCHEMA.ID_next += 1
        self.name = name

class PORT:
    """
    Port class defining inputs and outputs connections.
    Data:
        - id (int): unique port id.
        - name (str): optional port name.
        - schema (SCHEMA): the schema the port is associated with.
        - type ('IN' or 'OUT'): type of port (input or output port)
        - value(): current value at the port.
    """
    TYPE_IN = 'IN'
    TYPE_OUT = 'OUT'
    ID_NEXT = 1 # Global port counter
    
    def __init__(self, port_type, port_schema = None, port_name='', port_value=None):
        self.name = port_name
        self.value = port_value
        self.id = PORT.ID_NEXT
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
    
    def update(self):
        """
        For now does not involve weight or delay!
        Sets the value of port_rom to the value of port_to.
        Resets the port_from value to None.
        """
        self.port_to.value = self.port_from.value
        self.port_from.value = None

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
    """
    def __init__(self, name=''):
        SCHEMA.__init__(self,name)
        self.activity = 0
        self.in_ports = []
        self.out_ports = []
    
    
    def add_port(self,port_type, port_name='', port_value=None):
        """
        Adds a new port to the procedural schema. Port_type (str) ['IN' or 'OUT'], port_name (str), and a value port_value for the port.
        If sucessessful, returns the port id. Else returns None.
        """
        new_port = PORT(port_type, port_schema=self, port_name = port_name, port_value = port_value)
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
        port = self._find_port(port_name)
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
        port = self._find_port(port_name)
        if port and (port.type == PORT.TYPE_OUT):
            port.value = val
            return True
        elif port and (port.type == PORT.TYPE_IN):
            print("ERROR: port %s refers to an output port" % port_name)
            return False
        else:
            return False
    
    def _find_port(self, port_name):
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
        
    def update(self):
        """
        This function should be specified for every specific PROCEDURAL_SCHEMA class.
        When called, this function should read the value at the input ports and based on the state of the procedure, update the state of the procedural schema
        and post values at the output ports.
        """
        return
         
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
        - schema (KNOWLEDGE_SCHEMA):
        - alive (bool): status flag
        - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
        - activation (INST_ACTIVATION): Activation value of schema instance
        - act_port_in (PORT): Stores the vector of all the input activations.
        - act_port_out (PORT): Sends as output the activation of the instance.
    """    
    def __init__(self,schema=None, trace=None, act0=0):
        PROCEDURAL_SCHEMA.__init__(self,name="")
        self.schema = None      
        self.alive = False
        self.trace = None
        self.activity = 0
        self.activation = INST_ACTIVATION()
        self.act_port_in = PORT("IN", port_schema=self, port_name="act_in", port_value=[]);
        self.act_port_out = PORT("OUT", port_schema=self, port_name="act_in", port_value=0);
        self.instantiate(schema, trace, act0)
        
    def set_activation(self, t0=0, act0=1, dt=0.1, tau=1, act_inf=0, L=1.0, k=10.0, x0=0.5):
        """
        Set activation parameters
        """
        self.activation.t0 = t0
        self.activation.act0 = act0
        self.activation.dt = dt
        self.activation.tau = tau
        self.activation.act_inf = act_inf
        self.activation.L = L
        self.activation.k = k
        self.activation.x0 = x0
        self.activity = act0
        self.act_port_out.value = self.activity
    
    def set_ports(self):
        """
        THIS FUNCTION NEEDS TO BE DEFINED FOR EACH SPECIFIC SUBCLASS OF SCHEMA_INST.
        """
        return
    
    def instantiate(self, schema, trace,act0):
        """
        Sets up the state of the schema instance at t0 of instantiation with tau characteristic time for activation dynamics.
        """
        self.schema = schema
        self.name = "%s_%i" %(self.schema.name, self.id)
        self.alive = True
        self.trace = trace
        self.set_ports()
        self.set_activation(act0=act0)
    
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
        
    def update(self):
        """
        This function should be specified for every specific SCHEMA_INST class.
        When called, this function should read the value at the input ports and based on the state of the procedure, update the state of the instance and 
        post values at the output ports.
        """
        return

class INST_ACTIVATION:
    """
    """
    def __init__(self, t0=0, act0=1, tau=1, act_inf=0, L=1.0, k=10.0, x0=0.5):
        self.t0 = t0
        self.act0 = act0
        self.tau = tau
        self.act_inf = act_inf
        self.L = L
        self.k = k
        self.x0 = x0
        self.dt = 1.0 # This should not be changed.
        self.t = self.t0
        self.act = self.act0
        self.save_vals = {"t":[self.t0], "act":[self.act0]}
        
    
    def update(self, I):
        """
        """
        d_act = self.dt/(self.tau)*(-self.act + self.logistic(I) + self.act_inf)
        self.t += self.dt
        self.act += d_act
        self.save_vals["t"].append(self.t)
        self.save_vals["act"].append(self.act)
    
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
        - t (INT): time (+1 at each update)
        - dyn_params ({'tau':FLOAT, 'act_inf':FLOAT, 'L':FLOAT, 'k':FLOAT, 'x0':FLOAT})
        - prune_threshold (float): Below this threshold the instances are considered inactive (Alive=False)
        - save_state (DICT): Saves the history of the WM states. DOES NOT SAVE THE F_LINKS!!! NEED TO FIX THAT.
        
        - assemblages ????
    """
    def __init__(self, name=''):
        PROCEDURAL_SCHEMA.__init__(self,name)
        self.name = name
        self.schema_insts = []
        self.coop_links = []
        self.comp_links = []
        self.t = 0
        self.dyn_params = {'tau':10.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5}
        self.prune_threshold = 0.3
        self.save_state = {}
       
    def add_instance(self,schema_inst):
        self.schema_insts.append(schema_inst) #There is still an issue with TIME! Need to keep track of t0 for each construction instance....
        schema_inst.set_activation(t0= self.t,
                                    tau=self.dyn_params['tau'], 
                                    act_inf=self.dyn_params['act_inf'], 
                                    L=self.dyn_params['L'], 
                                    k=self.dyn_params['k'], 
                                    x0=self.dyn_params['x0'])
        name = "%s_%i" % (schema_inst.schema.name, schema_inst.id)
        self.save_state[name] = schema_inst.activation.save_vals.copy();
    
    def remove_instance(self, schema_inst):
        self.schema_insts.remove(schema_inst)
        
    def add_coop_link(self, inst_from, port_from, inst_to, port_to, weight):
        new_link = COOP_LINK(inst_from, inst_to, weight)
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
            if inst_from!='any' and (flink.inst_from != inst_from):
                match = False
            if inst_to!='any' and (flink.inst_to != inst_to):
                match = False
            if port_from!='any' and (flink.connect.port_from != port_from):
                match = False
            if port_to !='any' and (flink.conncet.port_to != port_to):
                match = False
            
            if match:
                results.append(flink)
                
        return results
                   
    def remove_coop_links(self,inst_from, inst_to, port_from='any', port_to='any'):
        """
        Remove the coop_links from working memory that satisfy the criteria.
        """
        f_links = self.find_coop_links(inst_from=inst_from, inst_to=inst_to, port_from=port_from, port_to=port_to)
        for f_link in f_links:
            self.coop_links.remove(f_link)
        
    
    def add_comp_link(self, inst_from, inst_to, weight):
        new_link = COMP_LINK(inst_from, inst_to, weight)
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
           
    def update_activations(self, coop_p=1, comp_p=1):
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
            if inst.activity<self.prune_threshold:
                inst.alive = False
    
    def prune(self):
        """
        Removes from WM all the dead instances
        """
        for inst in self.schema_insts[:]:
            if not inst.alive:
                self.schema_insts.remove(inst)
    
    def plot_dynamics(self):
        """
        """
        plt.figure(1)
        for inst in self.save_state.keys():
            plt.plot(self.save_state[inst]['t'], self.save_state[inst]['act'], label=inst, linewidth=2)
        
        plt.title('working memory dynamics')
        plt.xlabel('time', fontsize=16)
        plt.ylabel('activity', fontsize=16)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True)
        plt.show()
        
class F_LINK:
    """
    Functional links between schema instances in working memory
        
    Data:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (float)
    """
    def __init__(self, inst_from=None, inst_to=None, weight=0):
        """
        """
        self.inst_from = inst_from
        self.inst_to = inst_to
        self.weight=weight
    
    def update(self):
        """
        """
        self.inst_to.act_port_in.value.append(self.inst_from.act_port_out.value*self.weight)

class COOP_LINK(F_LINK):
    """
    Cooperation functional links between schema instances in working memory
        
    Data:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - connect (CONNECT)
    """
    def __init__(self, inst_from=None, inst_to=None, weight=1):
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight)
        self.connect = CONNECT()
    
    def set_connect(self, port_from, port_to, weight=0, delay=0):
        self.connect.port_from = port_from
        self.connect.port_to = port_to
        self.connect.weight = weight
        self.connect.delay = delay

class COMP_LINK(F_LINK):
    """
    Competition functional links between schema instances in working memory
        
    Data:
        - inst_from (SCHEMA_INST)
        - inst_to (SCHEMA_INST)
        - weight (float)
    """
    def __init__(self, inst_from=None, inst_to=None, weight=-1):
        """
        """
        F_LINK.__init__(self, inst_from, inst_to, weight)

class ASSEMBLAGE:
    """
    Defines a schema instance assemblage.
    """
    def __init__(self):
        self.coop_links = []
        self.activation = 0
    
    def add_link(self, link):
        """
        Add an cooperation link link (COOP_LINK) to the assemblage.
        A link can only be added does not add a connection to an already used in port or out port.
        Returns True if the link was sucessfully added, False otherwise.
        """
        for l in self.coop_links:
            if (l.connect.port_from == link.connect.port_from) or (l.connect.port_to == link.connect_port_to):
                return False
                
        self.coop_links.append(link)
        return True
    
    def update_activation(self):
        """
        Update the activation of the assemblage.
        """
        return

#############################
### BRAIN MAPPING CLASSES ###
#############################
class BRAIN_MAPPING:
    """
    Defines the mappings between procedural schemas and brain regions and between schema connections and brain connections.
    
    Data:
        -schema_mapping {schema_name1:[brain_region1, brain_region2,...], schema_name2:[brain_region3, brain_region4,...],...}
        -connect_mapping {connect_name1:[brain_connecion1, brain_connection2,...], connect_name2:[brain_connection3, brain_connection4,...],...}
    """
    BRAIN_REGIONS = []
    BRAIN_CONNECTIONS = []
    def __init__(self):
        self.schema_mapping = {}
        self.connect_mapping = {}

############################
### SCHEMA SYSTEM CLASSES###
############################
class SCHEMA_SYSTEM:
    """
    Defines a model as a system of procedural schemas.
    Data:
        - name (str):
        - schemas([PROCEDURAL_SCHEMAS]):
        - connections ([CONNECT]):
        - input_port ([PORT]): the list of ports that read the input
        - output_ports ([PORT]): The list of ports that defines the output value
        - input (): system's input.
        - outputs {'schema:pid':val}: system's outputs.
        - brain_mapping (BRAIN_MAPPING)
    """
    T0 = 0
    TIME_STEP = 1.0
    def __init__(self, name=''):
        self.name = name
        self.schemas = []
        self.connections = []
        self.input_ports = None
        self.output_ports = None
        self.input = None
        self.outputs = None
        self.t = SCHEMA_SYSTEM.T0
        self.dt = SCHEMA_SYSTEM.TIME_STEP
    
    def add_connection(self, from_schema, from_port, to_schema, to_port, name='', weight=0, delay=0):
        """
        Adds connection (CONNECT) between from_schema:from_port (PROCEDURAL_SCHEMA:PORT) to to_schema:to_port (PROCEDURAL_SCHEMA:PORT).
        Returns True if successful, False otherwise.
        """
        port_from = from_schema._find_port(from_port)
        port_to = to_schema._find_port(to_port)
        if port_from and port_to:
            new_connect = CONNECT(name=name, port_from=port_from, port_to=port_to, weight=weight, delay=delay)
            self.connections.append(new_connect)
            return True
        else:
            return False
    
    def add_schemas(self, schemas):
        """
        Add all the procedural schemas in "schemas" ([PROCEDURAL_SCHEMAS]) to the system.
        """
        self.schemas += schemas
    
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
        return self.output
        
    def update(self):
        """
        By defaults:
            - Gets system input
            - Updates all the schemas.
            - Propage port values through connections.
            - Update system outputs.
        """
        # Get system input
        for port in self.input_ports:
            port.value = self.input
        
        # Update all the schema states
        for schema in self.schemas:
            schema.update()
        
        # Propagate value through connections
        for connection in self.connections:
            connection.update()
        
        # Update the system output
        self.outputs = {p.schema.name+":"+str(p.id):p.value for p in self.output_ports}
        
        # Update time
        self.t += self.dt
    
    def system2dot(self):
        """
        Generates a dot file of the system's graph.
        Also creates an SVG image.
        """
        import subprocess
        import pydot
        
        tmp_folder = './tmp/'          
        
        prog = 'dot'
        file_type = 'svg'
        dot_sys = pydot.Dot(graph_type = 'digraph', splines = 'ortho')
        dot_sys.set_rankdir('LR')
        dot_sys.set_fontname('consolas')

        color = 'black'
        node_shape = 'record'
        style = 'filled'
        fill_color = 'white'
        
        dot_sys.add_node(pydot.Node('INPUT', label='INPUT', shape='oval'))
        dot_sys.add_node(pydot.Node('OUTPUT', label='OUTPUT', shape='oval'))
        
        for schema in self.schemas:
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
            dot_sys.add_edge(pydot.Edge(from_schema, to_schema))
        
        for port in self.output_ports:
            from_schema =  port.schema.name
            to_schema = 'OUTPUT'
            dot_sys.add_edge(pydot.Edge(from_schema, to_schema))
        
        file_name = tmp_folder + self.name + ".gv"
        dot_sys.write(file_name)
        
         # This is a work around becauses dot.write or doc.create do not work properly -> Cannot access dot.exe (even though it is on the system path)
        cmd = "%s -T%s %s > %s.%s" %(prog, file_type, file_name, file_name, file_type)
        subprocess.call(cmd, shell=True)
        
###############################################################################
if __name__=="__main__":

#    act = INST_ACTIVATION(1.0,1,0,0,0.01);
#    tmax = 20;
#    while act.t<tmax:
#        act.update(random.random())
#    # Plot the trajectory
#    plt.plot(act.save_vals["t"],act.save_vals["act"])
#    plt.xlabel('t')
#    plt.ylabel('act')
#    plt.show()
#    
    ###############
    ### Test WM ###
    ###############
    num_schemas=10
    schemas = [KNOWLEDGE_SCHEMA(name="act:"+str(i*1.0/num_schemas), LTM=None, content=None, init_act=i*1.0/num_schemas) for i in range(1,num_schemas+1)]
    insts = [SCHEMA_INST(schema=s) for s in schemas]
    wm = WM()
    for inst in insts:
            wm.add_instance(inst)
    
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
        wm.update_activations()
        
    wm.plot_dynamics()
    
    
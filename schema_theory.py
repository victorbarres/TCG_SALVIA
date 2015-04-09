# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 14:14:08 2015

@author: Victor Barres

Defines the based schema theory classes.

Uses math to implement the schema instances activation values.
"""
import math
##################################
### Schemas (Functional units) ###
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
        self.id = KNOWLEDGE_SCHEMA.ID_next
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
    
    def set_schema(self, schema):
        self.schema = schema
        
    def set_value(self, val):
        self.value = val
    
    def get_value(self):
        return self.value

class CONNECT(SCHEMA):
    """
    Defines connections between ports (input_port -> output_port)
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
        
class SCHEMA_INST:
    """
    Schema instance (base class)
    
    Data:
        - id (int): Unique id
        - activation (INST_ACTIVATION): Activation value of schema instance
        - schema (KNOWLEDGE_SCHEMA):
        - in_ports ([PORT]):
        - out_ports ([PORT]):
        - alive (bool): status flag
        - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
    """
    ID_next = 1 # Global schema instance ID counter
    
    def __init__(self):
        self.id = SCHEMA_INST.ID_next
        SCHEMA_INST.ID_next +=1
        self.activation = None
        self.schema = None         
        self.alive = False
        self.trace = None
        self.in_ports = []
        self.out_ports = []
        
    def set_activation(self, tau=1, act0=1, act_inf=0, t0=0, dt=0.1):
        """
        Set activation parameters
        """
        self.activation = INST_ACTIVATION(tau, act0, act_inf, t0, dt)
    
    def set_schema(self, schema):
        """
        Set schema to schema (SCHEMA) -> The schema that is instantiated.
        """
        self._schema = schema
        
    def set_alive(self, bool_val):
        """
        Set alive to bool_val (bool)
        """
        self.alive = bool_val
    
    def set_trace(self, a_trace):
        """
        Set trace value to a_trace.
        """
        self.trace = a_trace
    
    def add_port(self,port_type, port_name='', port_value=None):
        """
        Adds a new port to the instance. Port_type (str) ['IN' or 'OUT'], port_name (str), and a value port_value for the port.
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
    
    def set_ports(self):
        """
        THIS FUNCTION NEEDS TO BE DEFINED FOR EACH SPECIFIC SUBCLASS OF SCHEMA_INST.
        """
        return
    
    def instantiate(self, schema, trace):
        """
        Sets up the state of the schema instance at t0 of instantiation.
        """
        self.set_schema(schema)
        self.set_activation(schema.init_act)
        self.set_alive(True)
        self.set_trace(trace)
        self.set_ports()
    
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
    def __init__(self, tau=1, act0=1, act_inf=0, t0=0, dt=0.1):
        self.tau = tau
        self.act0 = act0
        self.act_inf = act_inf
        self.t0 = t0
        self.dt = dt
        self.t = self.t0
        self.act = self.act0
        self.save_vals = {"t":[self.t0], "act":[self.act0]}
        
    
    def update(self, I):
        """
        """
        d_act = 1.0/(self.tau)*(-self.act + self.logistic(I) + self.act_inf)*self.dt
        self.t += self.dt
        self.act += d_act
        self.save_vals["t"].append(self.t)
        self.save_vals["act"].append(self.act)
    
    def logistic(self, x):
        L = 1.0
        k = 10.0
        x0 = 0.5
        return L/(1 + math.exp(-k*(x-x0)))
        
#################################
### PROCEDURAL SCHEMA CLASSES ###
#################################
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
        - activation (float): The activation level of the schema.
    """
    def __init__(self, name=''):
        SCHEMA.__init__(self,name)
        self.activation = 0
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
        - activation (float): The activation level of the schema.
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
    
    def update(self):
        """
        NEEDS TO DEFINE THIS FUNCTION FOR LTM
        """
        return
        
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
        - activation (float): The activation level of the schema.
    Data:
        - schema_insts ([SCHEMA_INST]):
        - f-links ([F_LINK]):
        - time_constant (int):
        - prune_threshold (int):
        
        - assemblages ????
    """
    def __init__(self, name=''):
        PROCEDURAL_SCHEMA.__init__(self,name)
        self.name = name
        self.schema_insts = []
        self.f_links = []
        self.time_constant = 1
        self.prune_threshold = 0
       
    def set_time_constant(self, time_constant):
        self.time_constant = time_constant
    
    def set_prune_threshold(self, prune_threshold):
        self.prune_threshold = prune_threshold
    
    def add_instance(self,schema_inst):
        self.schema_insts.append(schema_inst)
    
    def remove_instance(self, schema_inst):
        self.schema_insts.remove(schema_inst)
        
    def add_f_link(self, from_inst, from_port, to_inst, to_port, weight):
        new_f_link = F_LINK()
        new_f_link.set_WM(self)
        new_f_link.set_port_in(from_inst, from_port)
        new_f_link.set_port_out(to_inst, to_port)
        new_f_link.set_weight(weight)
        self.f_links.append(new_f_link)
    
    def find_f_links(self,from_inst='any', to_inst='any', from_port='any', to_port='any'):
        """
        Returns a list of f_links that match the criteria.
        By default, it returns al the f-links (no criteria specified)
        """
        results = []
        for flink in self.f_links:
            match = True
            if from_inst!='any' and (flink.port_in.schema!=from_inst):
                match = False
            if to_inst!='any' and (flink.port_out.schema!=to_inst):
                match = False
            if from_port!='any' and (flink.port_in!=from_port):
                match = False
            if to_port !='any' and (flink.port_out!=to_port):
                match = False
            
            if match:
                results.append(flink)
                
        return results
                   
    def remove_f_links(self,from_inst, to_inst, from_port='any', to_port='any'):
        """
        Remove the f_links from working memory that satisfy the criteria.
        """
        f_links = self.find_f_links(from_inst=from_inst, to_inst=to_inst, from_port=from_port, to_port=to_port)
        for f_link in f_links:
            self.f_links.remove(f_link)
        
        # -> Might require to redo the assemblages!
           
    def update(self):
        return
        
class F_LINK(CONNECT):
    """
    Functional links between schema instances in working memory
    
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
        - port_from (PORT)
        - port_to (PORT)
        - weight (float)
        - delay (float)
    """
    def __init__(self, name='',  port_from=None, port_to=None, weight=1):
        """
        """
        CONNECT.__init__(self, name=name,  port_from=port_from, port_to=port_to, weight=weight, delay=0)
    
    def update(self):
        """
        Sets the value of port_from to the value of port_to*weight.
        Resets the port_from value to 0.
        """
        self.port_to.value = self.port_from.value*self.weight
        self.port_from.value = 0

class ASSEMBLAGE:
    """
    Defines a schema instance assemblage.
    """
    def __init__(self):
        self.f_links = []
        self.activation = 0
    
    def add_f_link(self, f_link):
        """
        Add an flink f_link (F_LINK) to the assemblage.
        """
        self.f_links.append(f_link)
    
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
    def __init__(self, name=''):
        self.name = name
        self.schemas = []
        self.connections = []
        self.input_ports = None
        self.output_ports = None
        self.input = None
        self.outputs = None
    
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
            port.set_value(self.input)
        
        # Update all the schema states
        for schema in self.schemas:
            schema.update()
        
        # Propagate value through connections
        for connection in self.connections:
            connection.update()
        
        # Update the system output
        self.outputs = {p.schema.name+":"+str(p.id):p.value for p in self.output_ports}
    
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
    import matplotlib.pyplot as plt
    from random import random
    act = INST_ACTIVATION(1.0,1,0,0,0.01);
    tmax = 20;
    while act.t<tmax:
        act.update(random())
    # Plot the trajectory
    plt.plot(act.save_vals["t"],act.save_vals["act"])
    plt.xlabel('t')
    plt.ylabel('act')
    plt.show()
    
    
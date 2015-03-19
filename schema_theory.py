# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 14:14:08 2015

@author: Victor Barres

Defines the based schema theory classes
"""
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
        - activation (float): Current activation value of schema instance
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
        self.activation = 0
        self.schema = None         
        self.alive = False
        self.trace = None
        self.in_ports = []
        self.out_ports = []
        
    def set_activation(self, act):
        """
        Set 'activation' to act (float).
        """
        self.activation = act
    
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
        new_port = PORT(port_type,port_schema=self, port_name = port_name, port_value = port_value)
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
        - brain_regions([str]): Set of brain regions associated with this procedural schema.
    """
    def __init__(self, name=''):
        SCHEMA.__init__(self,name)
        self.activation = 0
        self.in_ports = []
        self.out_ports = []
        self.brain_regions = []
    
    
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
    
    def update(self):
        """
        This function should be specified for every specific PROCEDURAL_SCHEMA class.
        When called, this function should read the value at the input ports and based on the state of the procedure, update the state of the procedural schema
        and post values at the output ports.
        """
        return

class CONNECT(SCHEMA):
    """
    Defines connections between procedural schemas (input_port -> output_port)
    Data (inherited):
        - id (int): Unique id
        - name (str): schema name
    Data:
        - port_in (PORT)
        - port_out (PORT)
        - weight (float)
        - delay (float)
    """
    def __init__(self, name='',  port_in=None, port_out=None, weight=0, delay=0):
        """
        """
        SCHEMA.__init__(self, name=name)
        self.port_in = port_in
        self.port_out = port_out
        self.weight = weight
        self.delay = delay
    
    def set_from(self, port):
        """
        """
        if port.type == PORT.TYPE_OUT:
            self.port_in = port
            return True
        else:
            return False
        
    def set_to(self, port):
        """
        """
        if port.type == PORT.TYPE_IN:
            self.port_out = port
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
        - brain_regions([str]): Set of brain regions associated with this procedural schema.
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
        - brain_regions([str]): Set of brain regions associated with this procedural schema.
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
        
class F_LINK:
    """
    Functional links between schema instances in working memory
    Stores the currently active schema instances and the functional links through which they enter in cooperative computation.
    
    Data:
        - WM (WM): Associated working memory
        - port_in (PORT)
        - port_out (PORT)
        - weight (float)
    """
    
    def __init__(self):
        """
        """
        self.WM = None
        self.port_in = None
        self.port_out = None
        self.weight = 0
    
    def set_WM(self, WM):
        """
        Links the f-link to the associated working memory
        """
        self.WM = WM
    
    def set_from(self, port):
        """
        """
        if port.type == PORT.TYPE_OUT:
            self.port_in = port
            return True
        else:
            return False
        
    def set_to(self, port):
        """
        """
        if port.type == PORT.TYPE_IN:
            self.port_out = port
            return True
        else:
            return False
    
    def set_weight(self, weight):
        """
        Sets up the weight of the f-link.
        """
        self.weight = weight
    
    def update():
        """
        """

class ASSEMBLAGE:
    """
    Defines a schema instance assemablage.
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
        - input (): system's input.
        - output (): system's output.
    """
    def __init__(self, name=''):
        self.name = name
        self.schemas = []
        self.connections = []
        self.input = None
        self.output = None
    
    def system2dot(self):
        """
        Generates a dot file of the system's graph.
        """
        return
    
    def update(self):
        """
        This function should be specified for every specific SCHEMA_SYSTEM class.
        When called, this function should read the  input value and based on the state of the system, update the state schemas and 
        output value.
        """
        return
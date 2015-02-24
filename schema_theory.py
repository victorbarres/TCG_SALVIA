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
        - LTM (LTM): Associated long term memory.
        - content (): Procedural or semantic content of the schema.
        - init_act (float): Initial activation value.
    """
    ID_next = 0 # Global schema ID counter
    
    def __init__(self, name="", LTM=None, content=None, init_act=0):
        self.id = SCHEMA.ID_next
        SCHEMA.ID_next += 1
        self.name = name
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
        - schema (SCHEMA):
        - in_ports ([int]):
        - out_ports ([int]):
        - alive (bool): status flag
    """
    ID_next = 0 # Global schema instance ID counter
    
    def __init__(self):
        self.id = SCHEMA_INST.ID_next
        SCHEMA_INST.ID_next +=1
        self.activation = 0
        self.schema = None         
        self.alive = False
        
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
    
    def set_ports(self):
        return
    
    def instantiate(self, schema):
        """
        """
        self.set_schema(schema)
        self.set_activation(schema.init_act)
        self.set_alive(True)
        self.set_ports()
    
    def get_inputs(self):
        """
        """
    
    def send_outputs(self):
        """
        """
        
class LTM:
    """
    Long term memory. 
    Stores the set of schemas associated with this memory.
    In addition, weighted connection can be defined betweens schemas to set up the LTM as a schema network. NOT USED IN TCG1.1!
    
    Data:
        - name (str): LTM name
        - WM (WM): Associated Working Memory
        - schemas ([SCHEMA]): Schema content of the long term memory
        - connections ([{from:schema1, to:schema2, weight:w}]): List of weighted connections between schemas (for future use if LTM needs to be defined as schema network)
    """
    def __init__(self, name):
        self.name = name
        self.WM = None
        self.schemas = []
        self.connections = []
    
    def set_WM(self, WM):
        if WM.LTM != self:
            WM.set_LTM(self)
        self.WM = WM
        
    def add_schema(self, schema):
        if schema.LTM != self:
            schema.set_LTM(self) # Link the schema to this LTM object
        self.schemas.append(schema)
    
    def add_connection(self, from_schema, to_schema, weight):
        self.connections.append({'from':from_schema, 'to':to_schema, 'weight':weight})
    
        

class WM:
    """
    Working memory
    Stores the currently active schema instances and the functional links through which they enter in cooperative computation.
    
    Data:
        - name (str): WM name
        - LTM (LTM): Associated long term memory
        - schema_insts ([SCHEMA_INST]):
        - f-links ([F_LINK]):
        - time_constant (int):
        - prune_threshold (int):
        
        - assemblages ????
    """
    
    def __init__(self, name):
        self.name = name
        self.LTM = None
        self.schema_insts = []
        self.f_links = []
        self.time_constant = 1
        self.prune_threshold
    
    def set_LTM(self, LTM):
        if LTM.WM != self:
            LTM.set_WM(self)
        self.LTM = LTM
        
    def set_time_constant(self, time_constant):
        self.time_constant = time_constant
    
    def set_prune_threshold(self, prune_threshold):
        self.prune_threshold = prune_threshold
    
    def add_instance(self,schema_inst):
        self.schema_insts.append(schema_inst)
    
    def remove_instance(self, schema_inst):
        self.schema_insts.remove(schema_inst)
        
    def add_f_link(self, from_s_inst, to_s_inst, weight):
        return None
        
    def remove_f_link(self,from_s_inst, to_s_inst):
        return None
        
    def update(self):
        return
        
class F_LINK:
    """
    Functional links between schema instances in working memory
    Stores the currently active schema instances and the functional links through which they enter in cooperative computation.
    
    Data:
        - WM (WM): Associated long term memory
        - port_in ({"schema_inst":SCHEMA_INST, "port":port_id})
        - port_out ({"schema_inst":SCHEMA_INST, "port":port_id})
        - weight (float)
    """
    
    def __init__(self):
        """
        """
        self.WM = None
        self.port_in = {"module":None, "port":None}
        self.port_out = {"module":None, "port":None}
        self.weight = 0
    
    def set_WM(self, WM):
        """
        """
    
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
    
    def read_inputs(self):
        """
        """
    
    def send_outputs(self):
        """
        """

class ASSEMBLAGE:
    """
    Defines a schema instance assemablage.
    """
    def __init__(self):
        self.f_links = []
        self.activation = 0
          
    
    


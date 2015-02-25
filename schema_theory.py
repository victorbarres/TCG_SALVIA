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
        
        - Maybe add trace, what triggered the instantiation.
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
            if from_inst!='any' and (flink.port_in['instance']!=from_inst):
                match = False
            if to_inst!='any' and (flink.port_out['instance']!=to_inst):
                match = False
            if from_port!='any' and (flink.port_in['port']!=from_port):
                match = False
            if to_port !='any' and (flink.port_out['port']!=to_port):
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
        - port_in ({"schema_inst":SCHEMA_INST, "port":port_id, "value":value})
        - port_out ({"schema_inst":SCHEMA_INST, "port":port_id, "value":value})
        - weight (float)
    """
    
    def __init__(self):
        """
        """
        self.WM = None
        self.port_in = {"instance":None, "port":None, "value":None}
        self.port_out = {"instance":None, "port":None, "value":None}
        self.weight = 0
    
    def set_WM(self, WM):
        """
        Links the f-link to the associated working memory
        """
        self.WM = WM
    
    def set_port_in(self, instance, port_id):
        """
        Sets up the origin of the f-link to the (instance, port_id)
        """
        self.port_in["instance"] = instance
        self.port_in["port"] = port_id
        
    def set_port_out(self, instance, port_id):
        """
        Sets up the target of the f-link to the (instance, port_id)
        """
        self.port_out["instance"] = instance
        self.port_out["port"] = port_id
    
    def set_weight(self, weight):
        """
        Sets up the weight of the f-link.
        """
        self.weight = weight
    
    def read_inputs(self):
        """
        Gathers inputs and sets up the input values (self.port_in['value'])
        The input port value is equal to the output port value of the instance it is connected to.
        """
        return
    
    def send_outputs(self):
        """
        Defines the output port value (self.port_out['value'])
        """
        return

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
          
    
    


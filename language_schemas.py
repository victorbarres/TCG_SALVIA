# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:03:19 2015

@author: Victor Barres
Defines language schemas for TCG.
"""
from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, LTM, WM
##################################
### Language knowledge schemas ###
##################################
class CXN_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Construction schema
    
    Data:
        - KNOWEDGE SCHEMA data:
                    - id (int): Unique id
                    - name (str): schema name
                    - LTM (LTM): Associated long term memory.
                    - content (CXN):
                    - init_act (float): Initial activation value.        
    """
    def __init__(self,aCXN):
        KNOWLEDGE_SCHEMA.__init__(self, aCXN.name)
        self.content = aCXN

class CXN_SCHEMA_INST(SCHEMA_INST):
    """
    Construction instance
    
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activation (float): Current activation value of schema instance
            - schema (CXN_SCHEMA):
            - in_ports ([int]):
            - out_ports ([int]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
    """
    def __init__(self, cxn_schema, trace):
        SCHEMA_INST.__init__(self)
        self.instantiate(cxn_schema, trace)
    
    def set_port(self):
        """
        Defines the input and output port for the construction schema instance.
        Each instance has 1 input port.
        Each instance has an output port for each TP_SLOT element in the construction's SynForm.
        """
        SynForm = self.schema.content.SynForm
        for f in SynForm.form:
            if isinstance(f,TP_SLOT): # 1 output port per slot
                self.add_port('out', f.order)
    
        self.add_port('in','input')
        
            
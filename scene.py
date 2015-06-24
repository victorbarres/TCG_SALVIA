# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines visual scene structure related classes for TCG.
"""
import perceptual_schemas as ps  
##########################
### Perceptual process ###
##########################
class PERCEPT:
    """
    Schema perception. ## -> THIS NEEDS TO BE REPLACED!!! It should use the conceptualizer.
    
    Data:
        - schema (SCHEMA): Perceived schema.
        - concept (CONCEPT): Perceived concept (can be different from original concept carried by schema).
        - replace_concept (BOOL): Flag for replacing concept.
    
    Notes:
        - If replace_concept = False -> the concept associated with the percept is the one linked to the schema
        if replace_concept = True -> override schema concept and use the one associated directly with the percept.
        - This class is a first attempt to represent conceptualization process going from perceptual schemas
        to semantic reprsentation. Needs to be improved.
    """
    def __init__(self):
        self.schema = None
        self.concept = None
        self.replace_concept = False 
        
    
    def __str__(self):
        p = ''
        p += 'schema: %s\n' % self.schema.name
        if self.concept:
            p += 'concept: %s\n' % self.concept.name
        else:
            p += 'concept: %s\n' % self.concept
        p += 'replace: %s\n' % self.replace_concept
        return p
        
        
class REGION:
    """
    Scene region.
    
    Data:
        - name (STRING): Name of region
        - x, y (INT): Location
        - w, h (INT): Size
        - saliency (INT): Perceptual saliency of region
        - uncertainty (INT): How uncertain is the perception of this region.
        - percepts ([PERCEPT]): List of percepts associated with this region.
    """
    def __init__(self):
        self.name = ''
        
        self.x = -1 
        self.y = -1
        self.w = 0
        self.h = 0
        
        self.saliency = 0
        self.uncertainty = 0
        
        self.percepts = []
####################
### Visual scene ###
####################    
class SUB_SCENE:
    """
    A subscene represents a structured perceptual units.
    It is defined as a graph of perceptual schemas.
    
    Data:
        - name (str): sub-scene name
        - nodes ([PERCEPT_SCHEMA_INST]): the nodes of the graph. Has to be an instance of a perceptual schema that is not a relation.
        - edges ([PERCEPT_SCHEMA_INST]): the edges of the graph. Has to be an instance of a perceptual schema that is  a relation.
        - area (AREA): The area associated with the sub-scenes -> Defined as the hull of the areas associated with all the subscenes perceptual schema instances.
        - anchor (PERCEPT_SCHEMA_INST): The perceptual anchor of the subscene. Should not be a relation.
        - uncertainty (INT): How uncertain is the perception of this region.
        - saliency (FLOAT):  Perceptual saliency of subscene
    """
    NEXT_ID = 0
    def __init__(self, name=''):
        self.id = SUB_SCENE.NEXT_ID
        SUB_SCENE.NEXT_ID +=1
        self.name = name
        self.nodes = []
        self.edges = []
        self.area = None
        self.anchor = None
        self.uncertainty = 0
        self.saliency = 0
    
    def add_per_schema(self, schema_inst):
        """
        Adds a percetual schema to the sub_scenes.
        If the perceptual schema instantiates a relation schemas, it is added to edges. Else it is added to nodes.
        """
        # Check duplication
        if self.find_schema(schema_inst.schema.name):
            return False
        if isinstance(schema_inst.schema, ps.PERCEPT_SCHEMA_REL):
            self.edges.append(schema_inst)
            self.update_area()
            return True
        else:
            self.nodes.append(schema_inst)
            self.update_area()
            return True
        
        return False
    
    def set_anchor(self, schema_inst):
        """
        Define the anchor schema instance
        """
        self.anchor = schema_inst
    
    def find_schema(self, name):
        """
        Find schema instance with name "name'. If found, return instance, else, return None.
        """
        for schema_inst in self.nodes + self.edges:
            if schema_inst.schema.name == name:
                return schema_inst
        return None
            
    def update_area(self):
        """
        Recalculates the area associated wiht the subscene based on associated schema instances.
        """
        schema_insts = self.nodes + self.edges
        if len(schema_insts) == 0:
            self.area = None
            return False
        self.area = self.schema_insts[0].schema.content['area']
        for schema_inst in schema_insts[1:]:
            self.area = ps.AREA.hull(self.area, schema_inst.schema.content['area'])
        
        self.saliency = self.area.saliency

class SCENE:
    """
    Scene being perceived.
    
    Data:
        - width, height (INT): Scene resolution
        - subscenes ([SUB_SCENE]): List of all subscenes associated with the scene.
        - schemas ([SCHEMA_INST]): List of perceptual schemas instances associated with the scene.
        - focus_regions (DICT{AREA:SUBSCENE}) Look-up table linking areas to subscenes.
    """
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.subscenes = []
        self.schemas = []
        self.focus_regions = {}
    
    
    def clear(self):
        """
        Reset scene.
        """
        self.width = 0
        self.height = 0
        self.subscenes = []
        self.schemas = []
        self.focus_regions = []

    def find_schema(self, name):
        """
        Find schema with name 'name' (STR) in scene.
        """
        for s in self.schemas:
            if s.schema.name == name:
                return s
        return None
        
    def find_subscene(self, name):
        """
        Find subscene with name 'name' (STR) in scene.
        """
        for ss in self.subscenes:
            if ss.name == name:
                return ss
        return None
    
    def add_subscene(self, ss):
        """
        Add subscene ss (SUB_SCENE) to scene if no duplication.
        """
        # Check validity
        if(not(ss) or ss.name == ''):
            return False
        
        # Check duplication
        if self.find_subscene(ss.name):
            return False
        
        # Add new schema
        self.subscenes.append(ss)
        self.focus_regions.append({'area':ss.area, 'subscene':ss})
        for schema_inst in ss.nodes + ss.edges:
            if not(self.find_schema(schema_inst.schema.name)):
                self.schemas.append(schema_inst)
        return True
###############################################################################
if __name__=='__main__':
    print "No test case implemented."
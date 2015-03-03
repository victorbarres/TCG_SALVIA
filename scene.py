# -*- coding: utf-8 -*-
"""
Created on Mon May 05 12:07:09 2014

@author: Victor Barres

Defines visual scene structure related classes for TCG.
"""
from schema_theory import SCHEMA, SCHEMA_INST

##########################
### Perceptual schemas ###
##########################
class AREA:
    """
    Simply defines an area in the visual input
    """
    def __init__(self, x=0, y=0, w=0, h=0, saliency=0):
        """
        Areas are defined as boxes.
        It is assumed that the coordiate are defined with origin at the top left corner of the scene. x axis: vertical down, y axis: horizong toward left.
        x, y coordiate of top-left corner
        w = width
        h = height
        saliency = Bottom-up saliency of the area.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.saliency = saliency
    
    def hull(area1, area2):
        """
        Class method
        Returns the smallest area containing area1 and area2 (~ convex hull)
        Right now the saliency is defined as the max of both saliency values... NOT SURE IT IS A GOOD WAY OF DOING THIS!
        """
        merge_area = AREA()
        merge_area.x = min(area1.x, area2.x)
        merge_area.y = min(area1.y, area2.y)
        merge_area.w = max(area1.y + area1.w, area2.y + area2.w) - merge_area.y
        merge_area.h = max(area1.x + area1.h, area2.x + area2.h) - merge_area.x
        merge_area.saliency = max(area1.saliency + area2.saliency) # THIS MIGHT NOT BE A GOOD IDEA!!
        return merge_area
        

class PERCEPT_SCHEMA(SCHEMA):
    """
    Perceptual schema
    
    Data:
        - SCHEMA data:
                    - id (int): Unique id
                    - name (str): schema name
                    - LTM (LTM): Associated long term memory.
                    - content (): Procedural or semantic content of the schema.
                    - init_act (float): Initial activation value.
        - type (INT): Schema type (UNDEFINED, OBJECT, RELATION, ACTION).
        - content of schema is defines as: 'feature' and 'area'
            'features' (): contains the perceptual features
            'area' (AREA): defines the area of the scene associated with this perceptual schema.
    """
    # Schema types
    UNDEFINED = 0
    OBJECT = 1
    ACTION = 2
    QUALITY = 3
    SPATIAL_REL = 4
    ACTION_REL = 5
    QUALITY_REL = 6
    TEMP_REL = 7
    
    def __init__(self):
        SCHEMA.__init__(self)
        self.type = PERCEPT_SCHEMA.UNDEFINED
        self.set_content({'features':None, 'area':None, 'saliency':None})
    
    def set_features(self, features):
        self.content['features'] = features
    
    def set_area(self, an_area):
        self.content['area'] = an_area
    
    ### -> Set the initial activation
#    def set_saliency(self, saliency=None):
#        """
#        Sets the saliency to saliency (FLOAT). If no saliency is provided, by default, sets saliency of perceptual schema equal to the bottom-up saliency 
#        value of the area it is associated with.
#        """
#        if saliency:
#            self.content['saliency'] = saliency
#            return True
#        elif self.area:
#            self.content['saliency'] = self.content['area'].saliency
#            return True
#        else:
#            return False

class PERCEPT_OBJECT(PERCEPT_SCHEMA):
    """
    Object schema
    """
    def __init__(self):
        PERCEPT_SCHEMA.__init__(self)
        self.type = PERCEPT_SCHEMA.OBJECT

class PERCEPT_ACTION(PERCEPT_SCHEMA):
    """
    Action schema. Define relation (edge) between two object schemas (SC_OBJECT) pFrom and pTo.
    """
    def __init__(self):
        PERCEPT_SCHEMA.__init__(self)
        self.type = PERCEPT_SCHEMA.ACTION

class PERCEPT_QUALITY(PERCEPT_SCHEMA):
    """
    Quality schema.
    """
    def __init__(self):
        PERCEPT_SCHEMA.__init__(self)
        self.type = PERCEPT_SCHEMA.QUALITY

class PERCEPT_SCHEMA_REL(PERCEPT_SCHEMA): ### SHOULD COME WITH PERCEPTUAL SCHEMAS BY DEFAULT AS FROM and To (A VARIABLE! (unbound), eg. something is red). Think about that....
    """
    Defines relation perceptual schemas.
    """
    def __init__(self):
        PERCEPT_SCHEMA.__init__(self)
        self.set_content({'features':None, 'area':None, 'saliency':None, 'from':None, 'to':None})
    
    def set_area(self):
        """
        The area of relation schemas is defines as the hull of the schemas they link.
        """
        if not(self.content['from']) or not(self.content['to']):
            return False
        self.area = AREA.hull(self.content['from'].content['area'], self.content['to'].content['area'])
        return True

class PERCEPT_SPATIAL_REL(PERCEPT_SCHEMA_REL):
    """
    Spatial relation schema. Define relation (edge) between two object schemas (PERCEPT_OBJECT) pFrom and pTo.
    """
    def __init__(self):
        PERCEPT_SCHEMA_REL.__init__(self)
        self.type = PERCEPT_SCHEMA.SPATIAL_REL
        
class PERCEPT_ACTION_REL(PERCEPT_SCHEMA_REL):
    """
    Action relation schema. Define relation (edge) between an action schemas (PERCEPT_ACTION) pFrom and and object schema (PERCEPT_OBJECT) pTo.
    """
    def __init__(self):
        PERCEPT_SCHEMA_REL.__init__(self)
        self.type = PERCEPT_SCHEMA.ACTION_REL
        
class PERCEPT_QUALITY_REL(PERCEPT_SCHEMA_REL):
    """
    Quality relation schema. Define relation (edge) between a quality schemas (PERCEPT_QUALITY) pFrom and another percept schema (PERCEPT_SCHEMA) pTo.
    """
    def __init__(self):
        PERCEPT_SCHEMA_REL.__init__(self)
        self.type = PERCEPT_SCHEMA.QUALITY_REL

class PERCEPT_TEMP_REL(PERCEPT_SCHEMA_REL):
    """
    Temporal relation schema. Define relation (edge) between two action schemas (PERCEPT_ACTION) pFrom and pTo.
    """
    def __init__(self):
        PERCEPT_SCHEMA_REL.__init__(self)
        self.type = PERCEPT_SCHEMA.TEMP_REL
    
class PERCEPT_SCHEMA_INST(SCHEMA_INST):
    """
    Perceptual schema instance.
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activation (float): Current activation value of schema instance
            - schema (PERCEPT_SCHEMA):
            - in_ports ([int]):
            - out_ports ([int]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
        
    Notes:
        For now, those schema instances are not used to form assemablages -> so no use for ports... 
        Trace is left empty, one can think that in a more realistic preceptual model, perceptual schemas would be instantiated on the basis of other perceptual schemas (See VISION model)
    """
    def __init__(self):
        SCHEMA_INST.__init__(self)
    
        
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
        - nodes ([PERCEPT_SCHEMA_INST]): the nodes of the graph. Has to be an instance of a perceptual schema that is not a relation
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
        if isinstance(schema_inst.schema, PERCEPT_SCHEMA_REL):
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
            self.area = AREA.hull(self.area, schema_inst.schema.content['area'])
        
        self.saliency = self.area.saliency

class SCENE:
    """
    Scene being perceived.
    
    Data:
        - width, height (INT): Scene resolution
        - subscenes ([SUB_SCENE]): List of all subscenes associated with the scene.
        - schemas ([SCHEMA_INST]): List of perceptual schemas instances associated with the scene.
        - focus_regions ([{'area':AREA, 'subscene': SUBSCENE}]): Look-up table linking areas to subscenes.
    """
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.subscenes = []
        self.schemas = []
        self.focus_regions = []
    
    
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
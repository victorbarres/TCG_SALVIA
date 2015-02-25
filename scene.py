# -*- coding: utf-8 -*-
"""
Created on Mon May 05 12:07:09 2014

@author: Victor Barres

Defines visual scene structure related classes for TCG.
"""
from schema_theory import SCHEMA

##########################
### Perceptual schemas ###

class AREA:
    """
    Simply defines an area in the visual input
    """
    def __init__(self, x=0, y=0, w=0, h=0):
        """
        Areas are defined as boxes.
        It is assumed that the coordiate are defined with origin at the top left corner of the scene. x axis: vertical down, y axis: horizong toward left.
        x, y coordiate of top-left corner
        w = width
        h = height
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def hull(area1, area2):
        """
        Class method
        Returns the smallest area containing area1 and area2 (~ convex hull)
        """
        merge_area = AREA()
        merge_area.x = min(area1.x, area2.x)
        merge_area.y = min(area1.y, area2.y)
        merge_area.w = max(area1.y + area1.w, area2.y + area2.w) - merge_area.y
        merge_area.h = max(area1.x + area1.h, area2.x + area2.h) - merge_area.x
        
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
            'features' contains the perceptual features
            'area' (AREA) defines the area of the scene associated with this perceptual schema.
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
        self.set_content({'features':None, 'area':None})
    
    def set_features(self, features):
        self.content['features'] = features
    
    def set_area(self, an_area):
        self.content['area'] = an_area

class PERCEPT_SCHEMA_REL(PERCEPT_SCHEMA):
    """
    Defines relation perceptual schemas.
    """
    def __init__(self):
        PERCEPT_SCHEMA.__init__(self)
        self.pFrom = None
        self.pTo = None
    
    def set_area(self):
        """
        The area of relation schemas is defines as the hull of the schemas they link.
        """
        if not(self.pFrom) or not(self.pTo):
            return False
        self.area = AREA.hull(self.pFrom.content['area'], self.pTo.content['area'])

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
        
###############################################################################
### Perceptual process ###

class PERCEPT:
    """
    Schema perception.
    
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
    
    def __str__(self):
        p = ''
        p += 'name: %s\n' % self.name
        p += 'type: visual scene region\n'
        p += 'location: (%i, %i)\n' %(self.x, self.y)
        p += 'size: (%i, %i)\n' %(self.w, self.h)
        p += 'saliency: %i\n' % self.saliency
        p += 'uncertainty: %i\n' % self.uncertainty
        p += 'percepts:\n'
        for per in self.percepts:
            p += ''.join(['\t' + s + '\n' for s in str(per).splitlines()]) + '\n'
        return p
###############################################################################
### Visual scene ###

class SCENE:
    """
    Scene being perceived.
    
    Data:
        - width, height (INT): Scene resolution
        - schemas ([SCHEMA]): List of perceptual schemas associated with the scene.
        - regions ([REGION]): List of regions associated with the scene.
    """
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.schemas = []
        self.regions = []
    
    
    def clear(self):
        """
        Reset scene.
        """
        self.width = 0
        self.height = 0
        self.schemas = []
        self.regions = []

    def find_schema(self, name):
        """
        Find schema with name 'name' (STR) in scene.
        """
        for s in self.schemas:
            if s.name == name:
                return s
        return None
        
    def find_region(self, name):
        """
        Find region with name 'name' (STR) in scene.
        """
        for r in self.regions:
            if r.name == name:
                return r
        return None
    
    def add_schema(self, schema):
        """
        Add schema (SCHEMA) to scene if no duplication.
        """
        # Check validity
        if(not(schema) or schema.name == ''):
            return False
        
        # Check duplication
        if self.find_schema(schema.name):
            return False
        
        # Add new schema
        self.schemas.append(schema)
        return True
        
    def add_region(self, region):
        """
        Add region (REGION) to scene if no duplication.
        """
        # Check validity
        if(not(region) or region.name == ''):
            return False
        
        # Check duplication
        if self.find_region(region.name):
            return False
        
        # Add new region
        self.regions.append(region)
        return True
        
    def __str__(self):
        p = ''
        p += "### VISUAL SCENE ###\n\n"
        p += "width: %i , height: %i\n\n" %(self.width, self.height)
        p += "REGIONS (num=%i):\n\n" % (len(self.regions))
        for r in self.regions:
            p += str(r) + '\n'
        p += "PERCEPTUAL SCHEMAS (num=%i):\n\n" % (len(self.schemas))
        for s in self.schemas:
            p += str(s) + '\n'
        return p
            

###############################################################################

if __name__=='__main__':
    print "No test case implemented."
# -*- coding: utf-8 -*-
"""
Created on Mon May 05 12:07:09 2014

@author: Victor Barres

Define visual scene structure related classes for TCG1.0
"""
###############################################################################
### Perceptual schemas ###

class SCHEMA:
    """
    Perceptual schema
    
    Data:
        - type (INT): Schema type (UNDEFINED, OBJECT or RELATION).
        - name (STRING): Schema name.
        - concept (CONCEPT): Concept associated with the schema.
        - region (REGION): Region of the visual scene associated with the schema.
    """
    # Schema types
    UNDEFINED = 0
    OBJECT = 1
    RELATION = 2
    
    def __init__(self):
        self.type = SCHEMA.UNDEFINED
        self.name = ''
        self.concept = None
        self.region = None

class SC_OBJECT(SCHEMA):
    """
    Object schema
    """
    def __init__(self):
        SCHEMA.__init__(self)
        self.type = SCHEMA.OBJECT
    
    def __str__(self):
        p = ''
        p += 'name: %s\n' % self.name
        p += 'type: perceptual object\n'
        p += 'concept: %s\n' % self.concept.name
        p += 'region: %s\n' % self.region.name
        return p

class SC_REL(SCHEMA):
    """
    Relation schema. Define relation (edge) between two object schemas (SC_OBJECT) pFrom and pTo.
    """
    def __init__(self):
        SCHEMA.__init__(self)
        self.type = SCHEMA.RELATION
        self.pFrom = None
        self.pTo = None
    
    def __str__(self):
        p = ''
        p += 'name: %s\n' % self.name
        p += 'type: perceptual relation\n'
        p += 'concept: %s\n' % self.concept.name
        p += 'from: %s\n' % self.pFrom.name
        p += 'to: %s\n' % self.pTo.name
        p += 'region: %s\n' % self.region.name
        return p
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
# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Defines visual scene structure related classes for TCG.
"""
from __future__ import division
import perceptual_schemas as ps  
###########################
#### Perceptual process ###
###########################
#class PERCEPT:
#    """
#    Schema perception. ## -> THIS NEEDS TO BE REPLACED!!! It should use the conceptualizer.
#    
#    Data:
#        - schema (SCHEMA): Perceived schema.
#        - concept (CONCEPT): Perceived concept (can be different from original concept carried by schema).
#        - replace_concept (BOOL): Flag for replacing concept.
#    
#    Notes:
#        - If replace_concept = False -> the concept associated with the percept is the one linked to the schema
#        if replace_concept = True -> override schema concept and use the one associated directly with the percept.
#        - This class is a first attempt to represent conceptualization process going from perceptual schemas
#        to semantic reprsentation. Needs to be improved.
#    """
#    def __init__(self):
#        self.schema = None
#        self.concept = None
#        self.replace_concept = False 
#        
#    
#    def __str__(self):
#        p = ''
#        p += 'schema: %s\n' % self.schema.name
#        if self.concept:
#            p += 'concept: %s\n' % self.concept.name
#        else:
#            p += 'concept: %s\n' % self.concept
#        p += 'replace: %s\n' % self.replace_concept
#        return p
#        
#        
#class REGION:
#    """
#    Scene region.
#    
#    Data:
#        - name (STRING): Name of region
#        - x, y (INT): Location
#        - w, h (INT): Size
#        - saliency (INT): Perceptual saliency of region
#        - uncertainty (INT): How uncertain is the perception of this region.
#        - percepts ([PERCEPT]): List of percepts associated with this region.
#    """
#    def __init__(self):
#        self.name = ''
#        
#        self.x = -1 
#        self.y = -1
#        self.w = 0
#        self.h = 0
#        
#        self.saliency = 0
#        self.uncertainty = 0
#        
#        self.percepts = []
####################
### Visual scene ###
####################    
class SUB_SCENE(object):
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
    
    def add_per_schema(self, schema_inst, update_uncertainty=True):
        """
        Adds a percetual schema to the sub_scenes.
        If the perceptual schema instantiates a relation schemas, it is added to edges. Else it is added to nodes.
        """
        # Check duplication
        if self.find_schema(schema_inst.name):
            return False
        if isinstance(schema_inst.trace, ps.PERCEPT_SCHEMA_REL):
            self.edges.append(schema_inst)
            self.update_area()
            if update_uncertainty:
                self.update_uncertainty()
            return True
        else:
            self.nodes.append(schema_inst)
            self.update_area()
            if update_uncertainty:
                self.update_uncertainty()
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
            if schema_inst.name == name:
                return schema_inst
        return None
            
    def update_area(self):
        """
        Recalculates the area associated with the subscene based on associated schema instances.
        Note:
            - For now doesn't account for edges since the area is not well defined for edges.
        """
        schema_insts = self.nodes
        if len(schema_insts) == 0:
            self.area = None
            return False
        self.area = schema_insts[0].content['area']
        for schema_inst in schema_insts[1:]:
            self.area = ps.AREA.hull(self.area, schema_inst.content['area'])
        return True
    
    def update_uncertainty(self):
        """
        Recalculates the uncertainty associated with the subscene based on associated schema instances.
        
        Notes: 
            - The uncertainty is simply the sum of the uncertainy of all the schemas contained in the subscene.
        """
        schema_insts = self.nodes + self.edges
        if len(schema_insts) == 0:
            self.uncertainty = None
            return False
        self.uncertainty = 0
        for schema_inst in schema_insts:
            self.uncertainty += schema_inst.content['uncertainty']
        return True
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {'name':self.name, 'id':self.id, 'uncertainty':self.uncertainty, 'saliency':self.saliency}
        data['area'] = self.area.get_info()
        data['nodes'] = [p.name for p in self.nodes]
        data['edges'] = [p.name for p in self.edges]
        return data
        

class SCENE(object):
    """
    Scene being perceived.
    Defines the visual input to the model.
    
    Data:
        - width, height (INT): Scene resolution
        - subscenes ([SUB_SCENE]): List of all subscenes associated with the scene.
        - schemas ([SCHEMA_INST]): List of perceptual schemas instances associated with the scene.
    """
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.subscenes = []
        self.schemas = []
    
    def reset(self):
        """
        Reset scene.
        """
        self.width = 0
        self.height = 0
        self.subscenes = []
        self.schemas = []

    def find_schema(self, name):
        """
        Find schema with name 'name' (STR) in scene.
        """
        for s in self.schemas:
            if s.name == name:
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
        for schema_inst in ss.nodes + ss.edges:
            if not(self.find_schema(schema_inst.name)):
                self.schemas.append(schema_inst)
        return True

class SCENE_LIGHT(object):
    """
    Light version of a scene being perceived.
    Bypasses perceptual schemas to go directly to conceptual schemas.
    
    Data:
        - subscenes ({STR:[CPT_INST]}): maps subscene names onto array of concept instances.
        - scene_structure (DICT): Directed acyclic graph dictionary with nodes as subscenes.
    """
    def __init__(self):
        """
        """
        self.subscenes = {}
        self.scene_structure = {}
    
    def reset(self):
        """
        Reset scene.
        """
        self.subscenes = {}
        self.scene_structure = {}
    
    def add_subscene(self, ss_name, content, saliency, anchor):
        """
        Add subscene to scene
        """
        self.subscenes[ss_name] = {"content":content, "saliency":saliency, "anchor":anchor}

    def find_subscene(self, anchor_name):
        """
        Return the name of the subscene associated to a given anchor.
        Args:
            - anchor_name(STR): Name of an anchor schema inst
        """
        subscenes = [ss_name for ss_name, val in self.subscenes.iteritems() if val["anchor"].name == anchor_name]
        
        subscene = subscenes[0] if subscenes else None
        return subscene
    
    def find_daughters(self, ss_name):
        """
        Finds the daughters of the subscene with name ss_name in the scene_structure
        """
        daughters = self.scene_structure.get(ss_name, [])
        return daughters
    
    def find_parents(self, ss_name):
        """
        Finds the parents of the subscene with name ss_name in the scene_sturcture
        """
        parents = []
        for name, daughters in self.scene_structure.iteritems():
            if ss_name in daughters:
                parents.append(name)
                
        return parents
        
    def get_content(self, ss_name):
        """
        """
        return self.subscenes[ss_name]['content']
    
    def get_saliency(self, ss_name):
        """
        """
        return self.subscenes[ss_name]['saliency']

    def get_anchor(self, ss_name):
        """
        """
        return self.subscenes[ss_name]['anchor']
    
    def update_saliency(self, ss_name, saliency_val):
        """
        Updates the saliency of ss_name to saliency_val
        """
        self.subscenes[ss_name]['saliency'] = saliency_val
        
    
    
    
###############################################################################
if __name__=='__main__':
    print "No test case implemented."
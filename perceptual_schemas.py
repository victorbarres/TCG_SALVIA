# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:53:03 2015

@author: Victor Barres
Defines perceptual schemas for TCG.

Uses numpy for the saliency map.
"""
import numpy as np
import random
from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, SCHEMA_SYSTEM, BRAIN_MAPPING

seed = 0
random.seed(seed)

####################################
### Perceptual knowledge schemas ###
####################################
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
        

class PERCEPT_SCHEMA(KNOWLEDGE_SCHEMA):
    """
    Perceptual schema
    
    Data:
        - KNOWEDGE SCHEMA data:
                    - id (int): Unique id
                    - name (str): schema name
                    - LTM (LTM): Associated long term memory.
                    - content (): 
                    - init_act (float): Initial activation value.
        - type (INT): Schema type (UNDEFINED, OBJECT, RELATION, ACTION).
        - content of schema is defined as: 'feature' and 'area'
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
        KNOWLEDGE_SCHEMA.__init__(self)
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
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
        
    Notes:
        For now, those schema instances are not used to form assemablages -> so no use for ports... 
        Trace is left empty, one can think that in a more realistic preceptual model, perceptual schemas would be instantiated on the basis of other perceptual schemas (See VISION model)
    """
    def __init__(self):
        SCHEMA_INST.__init__(self)

#####################################
### Perceptual procedural schemas ###
#####################################
class VISUAL_WM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Visual_WM'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_fixation')
        self.add_port('IN', 'from_perceptual_LTM')
        self.add_port('OUT', 'to_saliency_map')
        self.add_port('OUT', 'to_conceptualizer')
        self.perceptual_schemas = []
        
    def update(self):
        """
        """
        sub_scene= self.get_input('from_fixation')
        perceptual_knowledge = self.get_input('from_perceptual_LTM')
        self._update_schemas(sub_scene, perceptual_knowledge)
        self.set_output('to_conceptualizer', self.perceptual_schemas)
    
    def _update_schemas(self, sub_scene, perceptual_knowledge):
        """
        """
        return
    
class PERCEPTUAL_LTM(LTM):
    """
    """
    def __init__(self, name='Perceptual_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_visual_WM')
    
    def update(self):
        """
        """
        self.set_output('to_visual_WM', self.schemas)

class SALIENCY_MAP(PROCEDURAL_SCHEMA):
    """
    Data:
        - BU_saliency_data (SALIENCY_DATA): BOTTOM-up saliency data generated by Itti-Koch matlab saliency toolbox.
    """
    def __init__(self, name='Saliency_map'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saccade_system') # For inhibition of return?
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT', 'to_saccade_system') 
        self.BU_saliency_data = None
    
    def update(self):
        """
        """

class SACCADE_SYSTEM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Saccade_system'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saliency_map')
        self.add_port('OUT', 'to_fixation')
        self.add_port('OUT', 'to_saliency_map') # For inhibition of return?
        self.next_saccade = (0,0) # Next saccade coordinates (x,y)
    
    def update(self):
        """
        """
        saliency_map  = self.get_input('from_saliency_map')
        self.next_saccade = self._WTA(saliency_map)
        self.set_output('to_fixation', self.next_saccade)
        self.set_output('to_saliency_map', self.next_saccade)
    
    def _WTA(self, saliency_map):
        """
        """
        max_sal = saliency_map.max()
        max_idx = np.where(saliency_map==max_sal)
        num_res = len(max_idx[0])
        
        # Random tie breaker
        winner_idx = random.randint(0,num_res-1)
        coord = (max_idx[0][winner_idx], max_idx[1][winner_idx])
        return coord

class FIXATION(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self,name='Fixation'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_saccade_system')
        self.add_port('OUT','to_visual_WM')
        self.subscene = None
        self.next_saccade = False
    
    def update(self):
        """
        """
        vis_input = self.get_input('from_input')
        eye_pos = self.get_input('from_saccade_system')
        self._get_subscene(vis_input, eye_pos)
        self.set_output('to_visual_WM', self.subscene)
        self.set_output('to_saccade_system', self.next_saccade)
    
    def _get_subscene(self, vis_input, eye_pos):
        """
        """
        return

###############################################################################
if __name__=='__main__':
    ##############################
    ### percepaul schema system ###
    ##############################
    visualWM = VISUAL_WM()
    perceptualLTM = PERCEPTUAL_LTM()
    saliency_map = SALIENCY_MAP()
    saccade_system = SACCADE_SYSTEM()
    fixation = FIXATION()
    perception_mapping = {'Visual_WM':['ITG'], 
                        'Perceptual_LTM':[], 
                        'Saliency_map':['IPS'], 
                        'Saccade_system':['Basal Ganglia', 'FEF', 'Superior Colliculus'],
                        'Fixation':['Visual cortex']}
                        
    perceptual_schemas = [fixation, saliency_map, saccade_system, visualWM, perceptualLTM]
    
    perceptual_system = SCHEMA_SYSTEM('Perceptual_system')
    perceptual_system.add_schemas(perceptual_schemas)
    
    perceptual_system.add_connection(visualWM, 'to_saliency_map', saliency_map, 'from_visual_WM')
    perceptual_system.add_connection(perceptualLTM, 'to_visual_WM', visualWM, 'from_perceptual_LTM')
    perceptual_system.add_connection(fixation, 'to_visual_WM', visualWM, 'from_fixation')
    perceptual_system.add_connection(saliency_map, 'to_saccade_system', saccade_system , 'from_saliency_map')
    perceptual_system.add_connection(saccade_system, 'to_saliency_map', saliency_map, 'from_saccade_system')
    perceptual_system.add_connection(saccade_system, 'to_fixation', fixation, 'from_saccade_system')
    
   
    
    perceptual_system.set_input_ports([fixation._find_port('from_input'), saliency_map._find_port('from_input')])
    perceptual_system.set_output_ports([visualWM._find_port('to_conceptualizer')])
    
    perception_brain_mapping = BRAIN_MAPPING()
    perception_brain_mapping.schema_mapping = perception_mapping
    perceptual_system.brain_mapping = perception_brain_mapping
    
    perceptual_system.system2dot()


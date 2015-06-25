# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines perceptual schemas for TCG.

Uses numpy for the saliency map.
"""
import numpy as np
import random
from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM

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
    UNDEFINED = 'UNDEFINED'
    OBJECT = 'OBJECT'
    ACTION = 'ACTION'
    QUALITY = 'QUALITY'
    SPATIAL_REL = 'SPATIAL_REL'
    ACTION_REL = 'ACTION_REL'
    QUALITY_REL = 'QUALITY_REL'
    TEMP_REL = 'TEMP_REL'
    
    def __init__(self, name, percept, init_act):
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.type = PERCEPT_SCHEMA.UNDEFINED
        self.set_content({'percept':percept, 'features':None, 'area':None, 'saliency':None})
    
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
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.OBJECT

class PERCEPT_ACTION(PERCEPT_SCHEMA):
    """
    Action schema. Define relation (edge) between two object schemas (SC_OBJECT) pFrom and pTo.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.ACTION

class PERCEPT_QUALITY(PERCEPT_SCHEMA):
    """
    Quality schema.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.QUALITY

class PERCEPT_SCHEMA_REL(PERCEPT_SCHEMA): ### SHOULD COME WITH PERCEPTUAL SCHEMAS BY DEFAULT AS FROM and To (A VARIABLE! (unbound), eg. something is red). Think about that....
    """
    Defines relation perceptual schemas.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.set_content({'percept':percept, 'features':None, 'area':None, 'saliency':None, 'from':None, 'to':None})
    
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
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA_REL.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.SPATIAL_REL
        
class PERCEPT_ACTION_REL(PERCEPT_SCHEMA_REL):
    """
    Action relation schema. Define relation (edge) between an action schemas (PERCEPT_ACTION) pFrom and and object schema (PERCEPT_OBJECT) pTo.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA_REL.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.ACTION_REL
        
class PERCEPT_QUALITY_REL(PERCEPT_SCHEMA_REL):
    """
    Quality relation schema. Define relation (edge) between a quality schemas (PERCEPT_QUALITY) pFrom and another percept schema (PERCEPT_SCHEMA) pTo.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA_REL.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.QUALITY_REL

class PERCEPT_TEMP_REL(PERCEPT_SCHEMA_REL):
    """
    Temporal relation schema. Define relation (edge) between two action schemas (PERCEPT_ACTION) pFrom and pTo.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA_REL.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.TEMP_REL
    
class PERCEPT_SCHEMA_INST(SCHEMA_INST):
    """
    Perceptual schema instance.
    
    Data:
        SCHEMA_INST:
            - id (int): Unique id
            - activation (INST_ACTIVATION): Current activation value of schema instance
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
        self.perceptual_knowledge = None
        self.init_act = 0.5
    
    def initialize(self, per_knowledge):
        """
        Initilize the state of the PERCEPTUAL LTM with percetual_schema based on the content of percetual_knowledge
       
        Args:
            - peceptual_knowledge (PERCEPTUAL_KNOWLEDGE): TCG percetpual knowledge data
        """
        self.perceptual_knowledge = per_knowledge
        
        obj = per_knowledge.find_meaning('OBJECT')
        action = per_knowledge.find_meaning('ACTION')
        qual = per_knowledge.find_meaning('QUALITY')
        action_rel = per_knowledge.find_meaning('ACTION_REL')
        spatial_rel = per_knowledge.find_meaning('SPATIAL_REL')
        qual_rel = per_knowledge.find_meaning('QUALITY_REL')
        temp_rel = per_knowledge.find_meaning('TEMP_REL')
        
        for percept in per_knowledge.percepts(type='TOKEN'):
            new_schema = None
            res = per_knowledge.satisfy_rel(percept, 'is_a', None)
            per_cat = res[2]
            if per_knowledge.match(per_cat, obj, match_type="is_a"):
                new_schema = PERCEPT_OBJECT(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, action, match_type="is_a"):
                 new_schema = PERCEPT_ACTION(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, qual, match_type="is_a"):
                 new_schema = PERCEPT_QUALITY(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, action_rel, match_type="is_a"):
                 new_schema = PERCEPT_ACTION_REL(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, spatial_rel, match_type="is_a"):
                 new_schema = PERCEPT_SPATIAL_REL(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, qual_rel, match_type="is_a"):
                 new_schema = PERCEPT_QUALITY_REL(name=percept.name, percept=percept, init_act=self.init_act)
            elif per_knowledge.match(per_cat, temp_rel, match_type="is_a"):
                 new_schema = PERCEPT_TEMP_REL(name=percept.name, percept=percept, init_act=self.init_act)
            else:
                print "%s: unknown percept type" %percept.meaning
            
            if new_schema:
                self.add_schema(new_schema)
    
    def update(self):
        """
        """
        self.set_output('to_visual_WM', self.schemas)

class SALIENCY_MAP(PROCEDURAL_SCHEMA):
    """
    Data:
        - BU_saliency_map (array): BOTTOM-up saliency data generated by Itti-Koch matlab saliency toolbox.
        - IOR_radius (int): radius of the inhibition of return mask
        - IOR_decay (float): decay value for inhibition of return
        - IOR_max (INT): Max number of IORmaks that can be maintained.
        - IOR_masks ([{'mask':ARRAY, 't':INT, 'fix':(INT, INT)}]): set of inhibition of return masks.
        - IOR_mask (ARRAY): Stores the combined IOR_masks
        - saliency_map (array): BU_saliency_map + inhibition of return  
    """
    def __init__(self, name='Saliency_map'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saccade_system') # For inhibition of return?
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT', 'to_saccade_system') 
        self.BU_saliency_map = None
        self.IOR_radius = 5
        self.IOR_decay = 0.99
        self.IOR_max = 5
        self.IOR_masks = []
        self.IOR_mask = None
        self.saliency_map = None
    
    def update(self):
        """
        """
        cur_fixation = self.get_input('from_saccade_system')
        if cur_fixation != None:
            # Add inhibition of return mask
            self._IOR(cur_fixation)
            
        # Update all masks (decay + remove masks that are go beying memory capacity.)
        if len(self.IOR_masks) > self.IOR_max:
            self.IOR_masks.remove(self.IOR_masks[0])
        for mask in self.IOR_masks[:]:
                mask['t'] += 1
                mask['mask'] *= self.IOR_decay
        
        # Compute total inhibition of return mask
        self.IOR_mask = np.zeros(self.BU_saliency_map.shape)
        for mask in self.IOR_masks:
            self.IOR_mask += mask['mask']
        
        #Compute final saliency_map: BU_saliency - mask
        self.saliency_map = self.BU_saliency_map.copy() - self.IOR_mask        
        self.set_output('to_saccade_system', self.saliency_map)
    
    def _IOR(self, fixation):
        """
        Inhibition of return
        """
        ior_mask = {'mask': np.zeros(self.BU_saliency_map.shape), 't':0, 'fix':fixation}
        
        boundaries=np.zeros((2,2))
        boundaries[0,0] = max(0,fixation[0]-self.IOR_radius)
        boundaries[0,1] = min(ior_mask['mask'].shape[0]-1, fixation[0]+self.IOR_radius)
        boundaries[1,0] = max(0,fixation[1]-self.IOR_radius)
        boundaries[1,1] = min(ior_mask['mask'].shape[1]-1, fixation[1]+self.IOR_radius)
        ior_mask['mask'][boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]] = self.BU_saliency_map[boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]]
        self.IOR_masks.append(ior_mask)

class SACCADE_SYSTEM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Saccade_system'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saliency_map')
        self.add_port('IN', 'from_fixation') # Receives signal to triger next saccade once subscene perception is done.
        self.add_port('OUT', 'to_fixation')
        self.add_port('OUT', 'to_saliency_map') # For inhibition of return
        self.eye_pos = None # Crrent  eye position (x,y)
        self.next_fixation = None # Next saccade coordinates (x,y)
    
    def update(self):
        """
        """
        self.trigger_saccade = self.get_input('from_fixation')
        if self.trigger_saccade:
            saliency_map  = self.get_input('from_saliency_map')
            self.next_fixation = self._WTA(saliency_map)
            if self.next_fixation != self.eye_pos: #Updates next-saccedes if the result of the WTA differs from previously computed value.
                self.eye_pos = self.next_fixation
                self.set_output('to_fixation', self.eye_pos)
                self.set_output('to_saliency_map', self.eye_pos)
    
    def _WTA(self, saliency_map):
        """
        """
        if saliency_map != None:
            max_sal = saliency_map.max()
            max_idx = np.where(saliency_map==max_sal)
            num_res = len(max_idx[0])
            
            # Random tie breaker
            winner_idx = random.randint(0,num_res-1)
            coord = (max_idx[0][winner_idx], max_idx[1][winner_idx])
        else:
            coord = None
        return coord

class FIXATION(PROCEDURAL_SCHEMA):
    """
    Data"
        - subscene
        - uncertainty (INT): Remaining uncertainy in subscene perception.
        - next_saccade (BOOL): True ->  Triggers next saccade when the perception of the subscene is done. Else False.
    """
    def __init__(self,name='Fixation'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_saccade_system')
        self.add_port('OUT','to_visual_WM')
        self.add_port('OUT', 'to_saccade_system')
        self.subscene = None
        self.uncertainty = 0
        self.next_saccade = False 
    
    def update(self):
        """
        """
        vis_input = self.get_input('from_input')
        eye_pos = self.get_input('from_saccade_system')
        if eye_pos != None:
            self._get_subscene(vis_input, eye_pos)
            if self.subscene != None:
                self.uncertainty = self.subscene.uncertainty
        
        if self.uncertainty != None:
            self.uncertainty -= 1
            if self.uncertainty <0:
                self.next_saccade = True
                self.set_output('to_visual_WM', self.subscene)
        
        self.set_output('to_saccade_system', self.next_saccade)
        self.next_saccade = False
    
    def _get_subscene(self, vis_input, eye_pos):
        """
        """
        return

###############################################################################
if __name__=='__main__':
    from test_perceptual_schemas import test
    test()

    


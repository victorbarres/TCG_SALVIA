# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines perceptual schemas for TCG.

Dependencies:
    - Uses numpy for the saliency map.
    - Uses NetworkX for the implementation of the content of the Visual Working Memory (SceneRep graph)
    - Uses random
    - Uses matplotlib.pyplot
    
    - Uses schema_theory
    - Uses viewer
    - Uses scene
"""
import numpy as np
import matplotlib.pyplot as plt
import random

import networkx as nx

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM
import viewer
import scene as scn

seed = None
random.seed(seed)


class AREA(object):
    """
    Simply defines an area in the visual input
    """
    ID_next = 0 # Global area ID counter
    def __init__(self, x=0, y=0, w=0, h=0, saliency=0):
        """
        Areas are defined as boxes.
        It is assumed that the coordiate are defined with origin at the top left corner of the scene. x axis: vertical down, y axis: horizong toward left.
        x, y coordiate of top-left corner
        w = width
        h = height
        saliency = Bottom-up saliency of the area.
        """
        self.id  = AREA.ID_next
        AREA.ID_next += 1
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.saliency = saliency
    
    def contains(self, eye_pos):
       """
       Returns True if eye_pos falls in the area.
       """
       x = eye_pos[0]
       y = eye_pos[1]
       res = (x>=self.x) and (x<=self.x+self.h) and (y>=self.y) and (y<=self.y+self.w)
       return res
      
    def center(self):
        """
        Returns the coordinates of the center of th area.
        """
        x = self.x + self.h/2
        y = self.y + self.w/2
        return (x,y)
    
    def radius(self):
        """
        Defines a radius value for the area (so that it can be considered a circle instead of a box)
        """
        return max(self.h/2, self.w/2) 
    
    def includes(self, area):
        """                    
        Returns True if self includes area.
        The definition is not as stringent as classic area inclusion.
        self includes area if the center of area2 falls within self and area is smaller in surface than self.
        This is quite ad hoc, but will serve as a placeholder for now!
        
        Args:
            - area (AREA)
        """
        cond1  = self.contains(area.center())
        cond2 = (self.w*self.h) > (area.w*area.h)
        
        return (cond1 and cond2)
    
    def set_BU_saliency(self, BU_saliency_map=None):
        """
        Sets the area saliency based on a BU saliency map
        TO BE WRITTEN
        """
        if not(BU_saliency_map):
            self.saliency = random.random()
        else:
            self.saliency = 0 # to be defined.
    
    @staticmethod
    def hull(area1, area2):
        """
        Returns the smallest area containing area1 and area2 (~ convex hull)
        Right now the saliency is defined as the average of both saliency values... NOT SURE IT IS A GOOD WAY OF DOING THIS!
        """
        merge_area = AREA()
        merge_area.x = min([area1.x, area2.x])
        merge_area.y = min([area1.y, area2.y])
        merge_area.w = max([area1.y + area1.w, area2.y + area2.w]) - merge_area.y
        merge_area.h = max([area1.x + area1.h, area2.x + area2.h]) - merge_area.x
        merge_area.saliency = (area1.saliency + area2.saliency)/2 # THIS MIGHT NOT BE A GOOD IDEA!!
        return merge_area
        
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {'id': self.id, 'x':self.x, 'y':self.y, 'w':self.w, 'h':self.h, 'saliency':self.saliency}
        return data

####################################
### Perceptual knowledge schemas ###
####################################
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
        - type (STR): Schema type (UNDEFINED, OBJECT, RELATION, ACTION).
        - content of schema is defined as:
            - 'percept' (PERCEPT): the percept defining the schema (declarative content) linked to perceptual knowledge.
            - 'features' (): contains the perceptual features
#            - 'area' (AREA): defines the area of the scene associated with this perceptual schema.
#            - 'saliency' (FLOAT): Saliency of the schema (can difer from the saliency of the area it is associated to.)
#            - 'uncertainty' (INT): Uncertainty indexing the difficulty of the recognition process for the schema of the schema.
    """
    # Schema types
    UNDEFINED = 'UNDEFINED'
    OBJECT = 'OBJECT'
    PLACE = 'PLACE'
    ACTION = 'ACTION'
    QUALITY = 'QUALITY'
    SCENE_REL = 'SCENE_REL'
    SPATIAL_REL = 'SPATIAL_REL'
    ACTION_REL = 'ACTION_REL'
    QUALITY_REL = 'QUALITY_REL'
    TEMP_REL = 'TEMP_REL'
    
    def __init__(self, name, percept, init_act):
        KNOWLEDGE_SCHEMA.__init__(self, name=name, content=None, init_act=init_act)
        self.type = PERCEPT_SCHEMA.UNDEFINED
        self.set_content({'percept':percept, 'features':None})
    
    def set_features(self, features):
        self.content['features'] = features
    
    ### -> Set the initial activation
    # To be done.

class PERCEPT_OBJECT(PERCEPT_SCHEMA):
    """
    Object schema
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.OBJECT

class PERCEPT_PLACE(PERCEPT_SCHEMA):
    """
    Place schema
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.PLACE

class PERCEPT_ACTION(PERCEPT_SCHEMA):
    """
    Action schema.
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
        self.content['pFrom'] = None
        self.content['pTo'] = None
    
    def set_area(self):
        """
        The area of relation schemas is defines as the hull of the schemas they link.
        """
        if not(self.content['pFrom']) or not(self.content['pTo']):
            return False
        self.area = AREA.hull(self.content['pFrom'].content['area'], self.content['pTo'].content['area'])
        return True

class PERCEPT_SCENE_REL(PERCEPT_SCHEMA_REL):
    """
    Scene relation schema. Define relation (edge) between two schemas (PERCEPT_OBJECT) pFrom and pTo.
    """
    def __init__(self, name, percept, init_act):
        PERCEPT_SCHEMA_REL.__init__(self, name, percept, init_act)
        self.type = PERCEPT_SCHEMA.SCENE_REL

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
        Inherited from SCHEMA_INST:
            Note: 
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
            - covers ({'cpt_inst'=CPT_SCHEMA_INST}): Pointer to the concept instances associated through conceptualization.
        
    Notes:
        For now, those schema instances are not used to form assemablages -> so no use for ports... 
        Trace is left empty, one can think that in a more realistic preceptual model, perceptual schemas would be instantiated on the basis of other perceptual schemas (See VISION model)
    """
    def __init__(self, per_schema, trace):
        SCHEMA_INST.__init__(self, schema=per_schema, trace=trace)
        content_copy = per_schema.content.copy()
        self.content = content_copy
        self.covers = {'cpt_inst':None}
    
    def set_area(self, area):
        """
        Args:
            - area (AREA)
        """
        self.content['area'] = area
    
    def set_saliency(self, saliency=0.0):
        """
        Might differ from area saliency
        Args:
            - saliency (float)
        """
        self.content['saliency'] = saliency

#####################################
### Perceptual procedural schemas ###
#####################################
#class SALIENCY_MAP(PROCEDURAL_SCHEMA):
#    """
#    Data:
#        - BU_saliency_map (array): BOTTOM-up saliency data generated by Itti-Koch matlab saliency toolbox.
#        - params ({'IOR':{'radius':INT, ' decay': FLOAT, 'max': INT})
#            - radius (INT): radius of the inhibition of return mask
#            - decay (FLOAT): decay value for inhibition of return
#            - max (INT): Max number of IORmaks that can be maintained.
#        - IOR_masks ([{'mask':ARRAY, 't':INT, 'fix':(INT, INT)}]): set of inhibition of return masks.
#        - IOR_mask (ARRAY): Stores the combined IOR_masks
#        - saliency_map (array): BU_saliency_map + inhibition of return
#    """
#    def __init__(self, name='Saliency_map'):
#        PROCEDURAL_SCHEMA.__init__(self, name)
#        self.add_port('IN', 'from_saccade_system') # For inhibition of return?
#        self.add_port('IN', 'from_input')
#        self.add_port('IN', 'from_visual_WM')
#        self.add_port('OUT', 'to_saccade_system') 
#        self.BU_saliency_map = None
#        self.params['IOR'] = {'radius': 5, 'decay': 0.99, 'max': 5}
#        self.IOR_masks = []
#        self.IOR_mask = None
#        self.saliency_map = None
#    
#    def process(self):
#        """
#        """
#        cur_fixation = self.inputs['from_saccade_system']
#        if cur_fixation != None:
#            # Add inhibition of return mask
#            self._IOR(cur_fixation)
#            
#        # Update all masks (decay + remove masks that are go beying memory capacity.)
#        if len(self.IOR_masks) > self.params['IOR']['max']:
#            self.IOR_masks.remove(self.IOR_masks[0])
#        for mask in self.IOR_masks[:]:
#                mask['t'] += 1
#                mask['mask'] *= self.params['IOR']['decay']
#        
#        # Compute total inhibition of return mask
#        self.IOR_mask = np.zeros(self.BU_saliency_map.shape)
#        for mask in self.IOR_masks:
#            self.IOR_mask += mask['mask']
#        
#        #Compute final saliency_map: BU_saliency - mask
#        self.saliency_map = self.BU_saliency_map.copy() - self.IOR_mask        
#        self.outputs['to_saccade_system'] =  self.saliency_map
#    
#    def _IOR(self, fixation):
#        """
#        Inhibition of return
#        """
#        ior_mask = {'mask': np.zeros(self.BU_saliency_map.shape), 't':0, 'fix':fixation}
#        IOR_radius = self.params['IOR']['radius']
#        boundaries=np.zeros((2,2))
#        boundaries[0,0] = max(0,fixation[0]-IOR_radius)
#        boundaries[0,1] = min(ior_mask['mask'].shape[0]-1, fixation[0]+IOR_radius)
#        boundaries[1,0] = max(0,fixation[1]-IOR_radius)
#        boundaries[1,1] = min(ior_mask['mask'].shape[1]-1, fixation[1]+IOR_radius)
#        ior_mask['mask'][boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]] = self.BU_saliency_map[boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]]
#        self.IOR_masks.append(ior_mask)
#
#class SACCADE_SYSTEM(PROCEDURAL_SCHEMA):
#    """
#    """
#    def __init__(self, name='Saccade_system'):
#        PROCEDURAL_SCHEMA.__init__(self, name)
#        self.add_port('IN', 'from_saliency_map')
#        self.add_port('OUT', 'to_fixation')
#        self.add_port('OUT', 'to_saliency_map') # For inhibition of return
#        self.eye_pos = None # Current  eye position (x,y)
#        self.next_fixation = None # Next saccade coordinates (x,y)
#    
#    def process(self):
#        """
#        """
#        saliency_map  = self.inputs['from_saliency_map']
#        self.next_fixation = self._WTA(saliency_map)
#        if self.next_fixation != self.eye_pos: #Updates next-saccedes if the result of the WTA differs from previously computed value.
#            self.eye_pos = self.next_fixation
#            self.outputs['to_fixation'] =  self.eye_pos
#            self.outputs['to_saliency_map'] =  self.eye_pos
#    
#    def _WTA(self, saliency_map):
#        """
#        """
#        if saliency_map != None:
#            max_sal = saliency_map.max()
#            max_idx = np.where(saliency_map==max_sal)
#            num_res = len(max_idx[0])
#            
#            # Random tie breaker
#            winner_idx = random.randint(0,num_res-1)
#            coord = (float(max_idx[0][winner_idx]), float(max_idx[1][winner_idx]))
#        else:
#            coord = None
#        return coord
#    
#    ####################
#    ### JSON METHODS ###
#    ####################
#    def get_state(self):
#        """
#        """
#        data = super(SACCADE_SYSTEM, self).get_state()
#        data['eye_pos'] = self.eye_pos
#        data['next_fixation'] = self.next_fixation
#        return data
#
#class FIXATION(PROCEDURAL_SCHEMA):
#    """
#    CHANGE NAME TO FOCUS?
#    """
#    def __init__(self, name='Fixation'):
#        PROCEDURAL_SCHEMA.__init__(self, name)
#        self.add_port('IN', 'from_saccade_system')
#        self.add_port('OUT', 'to_output')
#        self.eye_pos = (0,0)
#    
#    def process(self):
#        """
#        """
#        eye_pos = self.inputs['from_saccade_system']
#        if eye_pos:
#            self.eye_pos = eye_pos
#    
#    ####################
#    ### JSON METHODS ###
#    ####################
#    def get_state(self):
#        """
#        """
#        data = super(FIXATION, self).get_state() 
#        data['eye_pos'] = self.eye_pos
        
class VISUAL_WM(WM):
    """
    """
    def __init__(self, name='Visual_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_subscene_rec')
        self.add_port('IN', 'from_saliency_map')
        self.add_port('IN', 'from_semantic_WM')
        self.add_port('OUT', 'to_saliency_map')
        self.add_port('OUT', 'to_subscene_rec')
        self.add_port('OUT', 'to_conceptualizer')
        self.params['dyn'] = {'tau':1000.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0.0, 'noise_std':0.0}
        self.params['C2'] = {'coop_weight':0.0, 'comp_weight':0.0, 'prune_threshold':0.01, 'confidence_threshold':0.0, 'coop_asymmetry':1, 'comp_asymmetry':0, 'P_comp':1.0, 'P_coop':1.0} # C2 is not implemented in this WM.
        self.SceneRep = nx.DiGraph()
        
    def process(self):
        """
        """
        ss_input= self.inputs['from_subscene_rec']
        if ss_input:
            sub_scene = ss_input['subscene']
            init_act = ss_input['init_act']
            new_insts = []
            for inst in sub_scene.nodes + sub_scene.edges:
                if not(inst in self.schema_insts):
                    inst.set_activation(init_act)
                    self.add_instance(inst)
                    new_insts.append(inst)
            self.update_SceneRep(new_insts)
        self.update_activations()
        self.prune()
        self.outputs['to_conceptualizer'] =  self.SceneRep
        
        missing_info = self.inputs['from_semantic_WM']
        self.outputs['to_subscene_rec'] = missing_info # For now just passing the message.
    
    def update_SceneRep(self, per_insts):
        """
        Updates the SceneRep: Adds the nodes and edges needed based on the receivd percept instances.
        
        NOTE:
            - Does not handle the case of percept instance updating.
            - SceneRep carreies the instance and the percept.
        """
        if per_insts:
            # First process all the instances that are not relations.
            for inst in [i for i in per_insts if not(isinstance(i.trace, PERCEPT_SCHEMA_REL))]:
                area_center = inst.content['area'].center()
                node_pos = (area_center[1], -1*area_center[0])
                self.SceneRep.add_node(inst.name, pos=node_pos, per_inst=inst, percept=inst.content['percept'], new=True)
            
            # Then add the relations
            for rel_inst in [i for i in per_insts if isinstance(i.trace, PERCEPT_SCHEMA_REL)]:
                node_from = rel_inst.content['pFrom'].name
                node_to = rel_inst.content['pTo'].name
                self.SceneRep.add_edge(node_from, node_to, per_inst=rel_inst, percept=rel_inst.content['percept'],  new=True)
        
#            self.show_SceneRep()
    
    def show_SceneRep(self):
        node_labels = dict((n, '%s(%.1f)' %(n, d['per_inst'].activity)) for n,d in self.SceneRep.nodes(data=True))
        edge_labels = dict(((u,v), '%s(%.1f)' %(d['percept'].name, d['per_inst'].activity)) for u,v,d in self.SceneRep.edges(data=True))
#        pos = nx.spring_layout(self.SceneRep) # uses a spring layout.
        pos=nx.get_node_attributes(self.SceneRep,'pos') #Uses the position attribute in SceneRep to position nodes.
        plt.figure(facecolor='white')
        plt.axis('off')
        title = '%s state (t=%i)' %(self.name,self.t)
        plt.title(title)
        nx.draw_networkx(self.SceneRep, pos=pos, with_labels= False)
        nx.draw_networkx_labels(self.SceneRep, pos=pos, labels= node_labels)
        nx.draw_networkx_edge_labels(self.SceneRep, pos=pos, edge_labels=edge_labels)
    
class PERCEPT_LTM(LTM):
    """
    """
    def __init__(self, name='Percept_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_subscene_rec')
        self.perceptual_knowledge = None
        self.params['init_act'] = 0.5
    
    def initialize(self, per_knowledge):
        """
        Initilize the state of the PERCEPTUAL LTM with percetual_schema based on the content of percetual_knowledge
       
        Args:
            - peceptual_knowledge (PERCEPTUAL_KNOWLEDGE): TCG percetpual knowledge data
        """
        self.perceptual_knowledge = per_knowledge
        
        obj = per_knowledge.find_meaning('OBJECT')
        place = per_knowledge.find_meaning('PLACE')
        action = per_knowledge.find_meaning('ACTION')
        qual = per_knowledge.find_meaning('QUALITY')
        scene_rel = per_knowledge.find_meaning('SCENE_REL')
        action_rel = per_knowledge.find_meaning('ACTION_REL')
        spatial_rel = per_knowledge.find_meaning('SPATIAL_REL')
        qual_rel = per_knowledge.find_meaning('QUALITY_REL')
        temp_rel = per_knowledge.find_meaning('TEMP_REL')
        
        for percept in per_knowledge.percepts(type='TOKEN'):
            new_schema = None
            res = per_knowledge.satisfy_rel(percept, 'is_token', None)
            per_cat = res[0][2]
            if per_knowledge.match(per_cat, obj, match_type="is_a"):
                new_schema = PERCEPT_OBJECT(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, place, match_type="is_a"):
                 new_schema = PERCEPT_PLACE(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, action, match_type="is_a"):
                 new_schema = PERCEPT_ACTION(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, qual, match_type="is_a"):
                 new_schema = PERCEPT_QUALITY(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, action_rel, match_type="is_a"):
                 new_schema = PERCEPT_ACTION_REL(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, spatial_rel, match_type="is_a"):
                 new_schema = PERCEPT_SPATIAL_REL(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, qual_rel, match_type="is_a"):
                 new_schema = PERCEPT_QUALITY_REL(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, temp_rel, match_type="is_a"):
                 new_schema = PERCEPT_TEMP_REL(name=percept.name, percept=percept, init_act=self.params['init_act'])
            elif per_knowledge.match(per_cat, scene_rel, match_type="is_a"):
                 new_schema = PERCEPT_SCENE_REL(name=percept.name, percept=percept, init_act=self.params['init_act'])
            else:
                print "%s: unknown percept type" %percept.meaning
            
            if new_schema:
                self.add_schema(new_schema)
    
    def process(self):
        """
        """
        self.outputs['to_subscene_rec'] =  self.schemas
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(PERCEPT_LTM, self).get_info()
        data['params'] = self.params
        return data

class SUBSCENE_RECOGNITION(PROCEDURAL_SCHEMA):
    """
    Packages the selective attention processes assuming that for now the pre-attentive parallel perceptual processing phase as already taken place.
    Data
        - params: {'recognition_time':FLOAT}: Defines the time it takes to perceive a schema of uncertainty 1.
        - data (DICT): Stores the schema's data.
            - 'scene_input' (DICT): scene input generated by TCG_LOADER.load_scene().
            - 'scene' (SCENE): stores data based on scene data received as input (as defined by LOADER)
        - scene_data (SCENE): stores data based on scene data received as input (as defined by LOADER)
        - subscene (SUB_SCENE): Currently perceived sub_scene.
        - uncertainty (INT): Remaining uncertainy in subscene perception.
        - next_saccade (BOOL): True ->  Triggers next saccade when the perception of the subscene is done. Else False.
        - eye_pos ((FLOAT, FLOAT)): Current eye position
        - focus_area (AREA): Current focus area. None -> no specific focus area.
        
    """
    def __init__(self, name='Subscene_recognition'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_percept_LTM')
        self.add_port('IN', 'from_saliency_map')
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT','to_visual_WM')
        self.add_port('OUT','to_output')
        self.params = {'recognition_time':10}
        self.data = {'scene': None, 'scene_input' : None}
        self.scene_data = None
        self.subscene = None
        self.uncertainty = 0
        self.next_saccade = False 
        self.eye_pos = (0,0)
        self.focus_area = None
        
    def initialize(self, scene_input, per_schemas, BU_saliency_map=None):
        """
        Creates the scene_data (SCENE) based on the scene_input.
        Scene_input should be a DICT generated by TCG_LOADER.load_scene.
        """
            
        my_scene = scn.SCENE()
        my_scene.width = scene_input['resolution'][0]
        my_scene.height = scene_input['resolution'][1]
            
        name_table = {}
        for i in  [s for s in scene_input['schemas'].keys() if scene_input['schemas'][s]['type'] != 'RELATION']: # First instantiate all the schemas that are not relations.
            dat = scene_input['schemas'][i]
            schema = [schema for schema in per_schemas if schema.content['percept'].name == dat['schema']][0]
            inst = PERCEPT_SCHEMA_INST(schema, trace=schema)
            area = AREA(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1])
            area.set_BU_saliency(BU_saliency_map=None) # THIS NEEDS TO BE CHANGED (for now random)    
            inst.set_area(area)
            if dat['saliency'] == 'auto':
                inst.set_saliency(area.saliency)  # Does this make any sense at all??
            else:
                inst.set_saliency(dat['saliency'])
            inst.content['uncertainty'] = int(dat['uncertainty'])
            name_table[dat['name']] = inst
        
        for i in  [s for s in scene_input['schemas'].keys() if scene_input['schemas'][s]['type'] == 'RELATION']: # Now dealing with relations
            dat = scene_input['schemas'][i]
            schema = [schema for schema in per_schemas if schema.content['percept'].name == dat['schema']][0]
            inst = PERCEPT_SCHEMA_INST(schema, trace=schema)
            inst.content['pFrom'] = name_table[dat['from']]
            inst.content['pTo'] = name_table[dat['to']]
            area = AREA(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1]) # This means that the area is gonna be of size 0
            area.set_BU_saliency(BU_saliency_map=None) # THIS NEEDS TO BE CHANGED (for now random)            
            inst.set_area(area)
            if dat['saliency'] == 'auto':
                inst.set_saliency(area.saliency) # Does this make any sense at all?? 
            else:
                inst.set_saliency(dat['saliency'])
            inst.content['uncertainty'] = int(dat['uncertainty'])
            name_table[dat['name']] = inst
        
        # Build subscenes
        for ss in scene_input['subscenes'].keys():
            dat = scene_input['subscenes'][ss]
            subscene = scn.SUB_SCENE(name = dat['name'])
            for schema in dat['schemas']:
                subscene.add_per_schema(name_table[schema])
            
            if dat['saliency'] != 'auto':
                subscene.saliency = float(dat['saliency'])
            
            if dat['uncertainty'] != 'auto':
                subscene.uncertainty = int(dat['uncertainty'])
            
            my_scene.add_subscene(subscene)
        
        self.scene_data = my_scene
        
        # Initialize eye_pos to center of scene.
        self.eye_pos = (my_scene.width/2, my_scene.height/2)
            
    def process(self):
        """
        """
        if self.inputs['from_input']:
            self.data['scene_input'] = self.inputs['from_input']
        per_schemas = self.inputs['from_percept_LTM']
        
        # Wait to have received all info to initalize
        if self.data['scene_input'] and per_schemas and not(self.scene_data):
            self.initialize(self.data['scene_input'], per_schemas)
            self.next_saccade = True
        
        # Start saccade and subscene recognition process        
        output = {'eye_pos':None, 'focus_area':None, 'subscene':None, 'saliency':None, 'next_saccade':None, 'uncertainty':None}
        if self.next_saccade:
            self.get_subscene()
            self.next_saccade = False
            if self.subscene:
                output['eye_pos'] = self.eye_pos
                output['subscene'] = {'name':self.subscene.name, 'radius': self.subscene.area.radius()}
                output['saliency'] = self.subscene.saliency
                output['focus_area'] = (self.focus_area.center(), self.focus_area.radius()) if self.focus_area else None
                print "Perceiving subscene: %s (saliency: %.2f)" %(self.subscene.name, self.subscene.saliency)
                print "Eye pos: (%.1f,%.1f)" %(self.eye_pos[0], self.eye_pos[1])
                self.uncertainty = self.subscene.uncertainty*self.params['recognition_time']
                output['uncertainty'] = self.uncertainty
        
        if self.subscene:
            self.uncertainty -= 1
            output['uncertainty'] = self.uncertainty
            if self.uncertainty <0:
                self.next_saccade = True
                output['next_saccade'] = self.t
                print 't: %i, trigger next saccade' % self.t
                self.outputs['to_visual_WM'] =  {'subscene':self.subscene, 'init_act':self.subscene.saliency}
                self.subscene.saliency = -1 # THIS NEEDS TO BE CHANGED!! 
                self.subscene = None
        
        percept_schema_inst = self.inputs['from_visual_WM']
        if percept_schema_inst:
            self.focus_area = percept_schema_inst.content['area']
            self.next_saccade = True # Even if the retrieval of the current subscene is not over, it retriggers saccade.
            area_center = self.focus_area.center()
            area_radius = self.focus_area.radius()
            print "t:%i, TD focus orientation to %s, area (x=%i, y=%i, r=%i)" %(self.t, percept_schema_inst.name, area_center[0], area_center[1], area_radius)
        
        self.outputs['to_output'] =  output

    def get_subscene(self):
        """
        Get the subscene in focus with highest saliency that hasn't yet been processed.
        Sets the eye position to the center of the subscene area.
        """
        max_saliency = 0
        in_focus_ss = self.in_focus()
        for ss in in_focus_ss:
            if ss.saliency > max_saliency:
                max_saliency = ss.saliency
                self.subscene = ss
                self.eye_pos = self.subscene.area.center()
#                ############ Test of strategy of zoom-in first. #############
#                if not(self.focus_area):
#                    self.focus_area = self.subscene.area 
    
    def in_focus(self):
        """
        Returns the set of subscenes that are currently in focus.
        A subscene is in focus if the current focus area includes the subscene's area.
        If the focus area is not defined, all the subscenes are in focus.
        If there are no sub_scene to return within the focus area, all the subscenes are in focus and reset focus_area to None.
        
        Notes:
            - The definition of what is "in focus" is incorrect
        """
        in_focus_ss = []
        candidates = [ss for ss in self.scene_data.subscenes if ss.saliency >0] # Don't consider the subscenes whose saliency has already been set to -1
        
        if self.focus_area:
            for ss in candidates:
                if ss.area != self.focus_area and self.focus_area.includes(ss.area):
                    in_focus_ss.append(ss)
                    
            if not(in_focus_ss): # No subscene in focus
                self.focus_area = None
        
        if not(self.focus_area):
            in_focus_ss = candidates
        
        return in_focus_ss
    #######################
    ### DISPLAY METHODS ###
    #######################
    def show_scene(self, img_file):
        """
        """
        if self.scene_data:
            viewer.TCG_VIEWER.display_scene(self.scene_data, img_file)
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(SUBSCENE_RECOGNITION, self).get_state()
        if self.subscene:
            data['subscene'] = self.subscene.get_info()
        else:
            data['subscene'] = None
        data['uncertainty'] = self.uncertainty
        data['next_saccade'] = self.next_saccade
        return data


class SIMPLE_SALIENCY_MAP(PROCEDURAL_SCHEMA):
    """
    Data:
        - BU_saliency_map (array): BOTTOM-up saliency data generated by Itti-Koch matlab saliency toolbox.
        - areas [AREA]:
    """
    def __init__(self, name='Saliency_map'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_visual_WM')
        self.add_port('OUT', 'to_visual_WM') 
        self.add_port('OUT', 'to_subscene_rec')
        self.BU_saliency_map = None
        self.areas = []
    
    def process(self):
        """
        """
        areas = self.inputs['from_visual_WM']
        if areas:
            #add new areas
            new_areas = [a for a in areas if not(a in self.areas)]
            self.areas.extend[new_areas]
            
            #remove unused areas
            dead_areas = [a for a in self.areas if not(a in areas)]
            for area in dead_areas:
                self.areas.remove(area)
        
        # NOTHING IS DONE HERE...                
        
        # Send saliency value to visualWM and subscene_rec
        self.outputs['to_visual_WM'] = self.BU_saliency_map
        self.outputs['to_subscene_rec'] =  self.BU_saliency_map

###############################################################################
if __name__=='__main__':
    from test_TCG_scene_description import test
    test(seed=None)

    


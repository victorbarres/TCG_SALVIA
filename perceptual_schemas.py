# -*- coding: utf-8 -*-
"""
@author: Victor Barres
Defines perceptual schemas for TCG.

Uses numpy for the saliency map.
Uses NetworkX for the implementation of the content of the Visual Working Memory (SceneRep graph)
"""
import numpy as np
import matplotlib.pyplot as plt
import random

import networkx as nx

from schema_theory import KNOWLEDGE_SCHEMA, SCHEMA_INST, PROCEDURAL_SCHEMA, LTM, WM
import scene as scn

seed = None
random.seed(seed)

####################################
### Perceptual knowledge schemas ###
####################################
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
           
    
    def hull(area1, area2):
        """
        Class method
        Returns the smallest area containing area1 and area2 (~ convex hull)
        Right now the saliency is defined as the max of both saliency values... NOT SURE IT IS A GOOD WAY OF DOING THIS!
        """
        merge_area = AREA()
        merge_area.x = min([area1.x, area2.x])
        merge_area.y = min([area1.y, area2.y])
        merge_area.w = max([area1.y + area1.w, area2.y + area2.w]) - merge_area.y
        merge_area.h = max([area1.x + area1.h, area2.x + area2.h]) - merge_area.x
        merge_area.saliency = max([area1.saliency + area2.saliency]) # THIS MIGHT NOT BE A GOOD IDEA!!
        return merge_area
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = {'id': self.id, 'x':self.x, 'y':self.y, 'w':self.w, 'h':self.h, 'saliency':self.saliency}
        return data
        

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
            - 'area' (AREA): defines the area of the scene associated with this perceptual schema.
            - 'saliency' (FLOAT): Saliency of the schema (can difer from the saliency of the area it is associated to.)
            - 'uncertainty' (INT): Uncertainty indexing the difficulty of the recognition process for the schema of the schema.
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
        self.set_content({'percept':percept, 'features':None, 'area':None, 'saliency':None, 'uncertainty':None})
    
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
            - id (INT): Unique id
            - activation (INST_ACTIVATION): Current activation value of schema instance
            - schema (PERCEPT_SCHEMA):
            - in_ports ([PORT]):
            - out_ports ([PORT]):
            - alive (bool): status flag
            - trace (): Pointer to the element that triggered the instantiation. # Think about this replaces "cover" in construction instances for TCG1.0
            - covers ({'cpt_insts'=[]}): Pointer to the concept instances associated through conceptualization.
        
    Notes:
        For now, those schema instances are not used to form assemablages -> so no use for ports... 
        Trace is left empty, one can think that in a more realistic preceptual model, perceptual schemas would be instantiated on the basis of other perceptual schemas (See VISION model)
    """
    def __init__(self, per_schema, trace):
        SCHEMA_INST.__init__(self, schema=per_schema, trace=trace)
        content_copy = per_schema.content.copy()
        self.content = content_copy
        self.covers = {'cpt_insts':[]}
    
    def set_area(self, x=0, y=0, w=0, h=0, saliency=0):
        """
        """
        area = AREA(x,y,w,h,saliency)
        self.content['area'] = area
        self.content['saliency'] = saliency

#####################################
### Perceptual procedural schemas ###
#####################################
class SALIENCY_MAP(PROCEDURAL_SCHEMA):
    """
    Data:
        - BU_saliency_map (array): BOTTOM-up saliency data generated by Itti-Koch matlab saliency toolbox.
        - IOR_params ({'IOR_radius':INT, ' IOR_decay': FLOAT, 'IOR_max': INT})
            - IOR_radius (INT): radius of the inhibition of return mask
            - IOR_decay (FLOAT): decay value for inhibition of return
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
        self.IOR_params  = {'IOR_radius': 5, 'IOR_decay': 0.99, 'IOR_max': 5}
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
        if len(self.IOR_masks) > self.IOR_params['IOR_max']:
            self.IOR_masks.remove(self.IOR_masks[0])
        for mask in self.IOR_masks[:]:
                mask['t'] += 1
                mask['mask'] *= self.IOR_params['IOR_decay']
        
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
        IOR_radius = self.IOR_params['IOR_radius']
        boundaries=np.zeros((2,2))
        boundaries[0,0] = max(0,fixation[0]-IOR_radius)
        boundaries[0,1] = min(ior_mask['mask'].shape[0]-1, fixation[0]+IOR_radius)
        boundaries[1,0] = max(0,fixation[1]-IOR_radius)
        boundaries[1,1] = min(ior_mask['mask'].shape[1]-1, fixation[1]+IOR_radius)
        ior_mask['mask'][boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]] = self.BU_saliency_map[boundaries[0,0]:boundaries[0,1], boundaries[1,0]:boundaries[1,1]]
        self.IOR_masks.append(ior_mask)

class SACCADE_SYSTEM(PROCEDURAL_SCHEMA):
    """
    """
    def __init__(self, name='Saccade_system'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saliency_map')
        self.add_port('OUT', 'to_fixation')
        self.add_port('OUT', 'to_saliency_map') # For inhibition of return
        self.eye_pos = None # Current  eye position (x,y)
        self.next_fixation = None # Next saccade coordinates (x,y)
    
    def update(self):
        """
        """
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
            coord = (float(max_idx[0][winner_idx]), float(max_idx[1][winner_idx]))
        else:
            coord = None
        return coord
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(SACCADE_SYSTEM, self).get_state()
        data['eye_pos'] = self.eye_pos
        data['next_fixation'] = self.next_fixation
        return data

class FIXATION(PROCEDURAL_SCHEMA):
    """
    CHANGE NAME TO FOCUS?
    """
    def __init__(self, name='Fixation'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_saccade_system')
        self.add_port('OUT', 'to_output')
        self.eye_pos = (0,0)
    
    def update(self):
        """
        """
        eye_pos = self.get_input('from_saccade_system')
        if eye_pos:
            self.eye_pos = eye_pos
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_state(self):
        """
        """
        data = super(FIXATION, self).get_state() 
        data['eye_pos'] = self.eye_pos
        
class VISUAL_WM(WM):
    """
    """
    def __init__(self, name='Visual_WM'):
        WM.__init__(self, name)
        self.add_port('IN', 'from_subscene_rec')
        self.add_port('OUT', 'to_saliency_map')
        self.add_port('OUT', 'to_conceptualizer')
        self.dyn_params = {'tau':1000.0, 'act_inf':0.0, 'L':1.0, 'k':10.0, 'x0':0.5, 'noise_mean':0.0, 'noise_std':0.0}
        self.C2_params = {'coop_weight':0, 'comp_weight':0, 'prune_threshold':0.01, 'confidence_threshold':0} # C2 is not implemented in this WM.
        self.SceneRep = nx.DiGraph()
        
    def update(self):
        """
        """
        sub_scene= self.get_input('from_subscene_rec')

        if sub_scene:
            new_insts = []
            for inst in sub_scene.nodes + sub_scene.edges:
                if not(inst in self.schema_insts):
                    self.add_instance(inst)
                    new_insts.append(inst)
            self.update_SceneRep(new_insts)
#            self.show_SceneRep()
        self.update_activations()
        self.prune()
        self.set_output('to_conceptualizer', self.SceneRep)
    
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
#        edge_labels = dict(((u,v), '%s(%.1f)' %(d['percept'].name, d['per_inst'].activity)) for u,v,d in self.SceneRep.edges(data=True))s
#        pos = nx.spring_layout(self.SceneRep)
        pos=nx.get_node_attributes(self.SceneRep,'pos')
        plt.figure(facecolor='white')
        plt.axis('off')
        title = '%s state (t=%i)' %(self.name,self.t)
        plt.title(title)
        nx.draw_networkx(self.SceneRep, pos=pos, with_labels= False)
        nx.draw_networkx_labels(self.SceneRep, pos=pos, labels= node_labels)
#        nx.draw_networkx_edge_labels(self.SceneRep, pos=pos, edge_labels=edge_labels)
    
class PERCEPT_LTM(LTM):
    """
    """
    def __init__(self, name='Percept_LTM'):
        LTM.__init__(self, name)
        self.add_port('OUT', 'to_subscene_rec')
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
            res = per_knowledge.satisfy_rel(percept, 'is_token', None)
            per_cat = res[0][2]
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
        self.set_output('to_subscene_rec', self.schemas)
    
    ####################
    ### JSON METHODS ###
    ####################
    def get_info(self):
        """
        """
        data = super(PERCEPT_LTM, self).get_info()
        data['init_act'] = self.init_act
        return data

class SUBSCENE_RECOGNITION(PROCEDURAL_SCHEMA):
    """
    Data
        - inputs
        - scene_data (SCENE): stores data based on scene data received as input (as defined by LOADER)
        - subscene
        - uncertainty (INT): Remaining uncertainy in subscene perception.
        - next_saccade (BOOL): True ->  Triggers next saccade when the perception of the subscene is done. Else False.
    """
    def __init__(self, name='Subscene_recognition'):
        PROCEDURAL_SCHEMA.__init__(self, name)
        self.add_port('IN', 'from_input')
        self.add_port('IN', 'from_percept_LTM')
        self.add_port('OUT','to_visual_WM')
        self.inputs = {'scene_input':None, 'per_schemas':None}
        self.scene_data = None
        self.subscene = None
        self.uncertainty = 0
        self.next_saccade = False 
        self.eye_pos = (0,0)
        
    def initialize(self, scene_input, per_schemas):
        """
        Creates the scene_data (SCENE) based on the scene_input.
        Scene_input should be a DICT generated by LOADER.load_scene.
        """
        my_scene = scn.SCENE()
        my_scene.width = scene_input['resolution'][0]
        my_scene.height = scene_input['resolution'][1]
            
        name_table = {}
        for i in  [s for s in scene_input['schemas'].keys() if scene_input['schemas'][s]['type'] != 'RELATION']: # First instantiate all the schemas that are not relations.
            dat = scene_input['schemas'][i]
            schema = [schema for schema in per_schemas if schema.content['percept'].name == dat['schema']][0]
            inst = PERCEPT_SCHEMA_INST(schema, trace=schema)
            if dat['saliency'] == 'auto':
                saliency  = random.random() # THIS NEEDS TO BE CHANGED!!!
            else:
                saliency = dat['saliency']
            inst.set_area(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1], saliency=saliency)
            inst.content['uncertainty'] = int(dat['uncertainty'])
            name_table[dat['name']] = inst
        
        for i in  [s for s in scene_input['schemas'].keys() if scene_input['schemas'][s]['type'] == 'RELATION']: # Now dealing with relations
            dat = scene_input['schemas'][i]
            schema = [schema for schema in per_schemas if schema.content['percept'].name == dat['schema']][0]
            inst = PERCEPT_SCHEMA_INST(schema, trace=schema)
            if dat['saliency'] == 'auto':
                saliency  = random.random() # THIS NEEDS TO BE CHANGED!!!
            else:
                saliency = dat['saliency']
            inst.set_area(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1], saliency=saliency)
            inst.content['pFrom'] = name_table[dat['from']]
            inst.content['pTo'] = name_table[dat['to']]
            inst.content['uncertainty'] = int(dat['uncertainty'])
            name_table[dat['name']] = inst
        
        # Build subscenes
        for ss in scene_input['subscenes'].keys():
            dat = scene_input['subscenes'][ss]
            subscene = scn.SUB_SCENE(name = dat['name'])
            for schema in dat['schemas']:
                subscene.add_per_schema(name_table[schema])
            
            my_scene.add_subscene(subscene)
        
        self.scene_data = my_scene
        
        # Initialize eye_pos to center of scene.
        self.eye_pos = (my_scene.width/2, my_scene.height/2)
            
    def update(self):
        """
        """
        scene_input = self.get_input('from_input')
        if scene_input:
            self.inputs['scene_input'] = scene_input
        per_schemas = self.get_input('from_percept_LTM')
        if per_schemas:
            self.inputs['per_schemas'] = per_schemas
        
        if self.inputs['scene_input'] and self.inputs['per_schemas']:
            self.initialize(self.inputs['scene_input'], self.inputs['per_schemas'])
            self.inputs['scene_input'] =  None
            self.inputs['per_schemas'] = None
            self.next_saccade = True
            
        if self.next_saccade:
            self._get_subscene()
            self.next_saccade = False
            if self.subscene:
                print "Perceiving subscene: %s" %self.subscene.name
                print "Eye pos: (%.1f,%.1f)" %(self.eye_pos[0], self.eye_pos[1])
                self.uncertainty = self.subscene.uncertainty*10
        
        if self.subscene:
            self.uncertainty -= 1
            if self.uncertainty <0:
                self.next_saccade = True
                print 't: %i, trigger next saccade' % self.t
                self.set_output('to_visual_WM', self.subscene)
                self.subscene.saliency = -1 # THIS NEEDS TO BE CHANGED!! 
                self.subscene = None

    def _get_subscene(self):
        """
        Get the subscene with highest saliency that hasn't yet been processed.
        Sets the eye position to the center of the subscene area.
        """
        max_saliency = 0
        for ss in self.scene_data.subscenes:
            if ss.saliency > max_saliency:
                max_saliency = ss.saliency
                self.subscene = ss
                self.eye_pos = self.subscene.area.center()
    
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

###############################################################################
if __name__=='__main__':
    from test_perceptual_schemas import test
    test()

    


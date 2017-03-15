# -*- coding: utf-8 -*-
"""
@author: Victor Barres

TCG data loader module
    
    This version requires JSON formatted inputs!

    Loader for world knowledge, grammar, and scenes.
    
    To load conceptual knowledge use load_conceptual_knowledge method (returns a conceptual_knowledge)
    To load perceptual knowledge use load_perceptual_knowledge method (returns a perceptual_knowledge)
    To load conceptualization use load_conceptualization method (returns a conceptualization)
    To load grammar use load_grammar method (returns a grammar)
    To load visual scene use load_scene method (returns a scene)
    
    All other methods should be considered private and are subject to change.
"""
from __future__ import division
import json
import re


import scene as SCN
import concept as CPT
import frame as FRM
import percept as PER
import construction as CXN
import perceptual_schemas as ps
import language_schemas  as ls
import saliency_matlab as SMAT  

class TCG_LOADER(object):

    ############################
    ### Data reading methods ###
    ############################
    @staticmethod
    def json_read(file_name, path='./'):
        file_name = path+file_name
        try:
            f = open(file_name, 'r')
        except IOError as e:
            print "Cannot open %s. %s" %(file_name, e.strerror)
            return False
        
        try:
           json_data = json.load(f)
        except ValueError as e:
            print "Invalid json file %s. %s" %(file_name, e)
            return False
        
        f.close()
        
        return json_data
    
    ######################################
    ### Private object reading methods ###
    ######################################
    
    ###############
    ### CONCEPT ###
    @staticmethod
    def read_concept(atype, sup_cpt, cpt_knowledge, cpt_data):
        """
        """
        for concept in cpt_data:
            # Create new concept entity
            sub_cpt = cpt_knowledge.find_meaning(concept)
            if not(sub_cpt):
                sub_cpt = CPT.CONCEPT(name=concept, meaning=concept)
                cpt_knowledge.add_ent(sub_cpt)
    
            # Create new concept relation
            new_semrel = CPT.SEM_REL(aType=atype, from_cpt=sub_cpt, to_cpt=sup_cpt)
            
            # update sem_net
            flag = cpt_knowledge.add_relation(new_semrel)
            if not(flag):
                return False
            
            flag = TCG_LOADER.read_concept(atype, sub_cpt, cpt_knowledge, cpt_data[concept])
            if not(flag):
                return False
        
        return True
        
    #############
    ### FRAME ###
    @staticmethod
    def read_frame_node(new_frame, aNode, name_table, cpt_knowledge):
        """
        """
        # Create new node
        new_node = FRM.WK_FRAME_NODE()
        name = aNode['name']
        new_node.name = '%s_%i' %(name, new_node.id)
        
        concept = cpt_knowledge.find_meaning(aNode['concept'])
        if not concept:
            error_msg = "Cannot find concept %s in conceptual knowledge" %aNode['concept']
            raise ValueError(error_msg)
        new_node.concept = concept
        
        if 'frame' in aNode:
            new_node.frame = aNode['frame']
        
        # Update construction and name_table    
        new_frame.add_frame_elem(new_node)
        name_table['names'][name] = new_node
        
    @staticmethod
    def read_frame_rel(new_frame, aRel, name_table, cpt_knowledge):
        """
        """    
        # Create new relation
        new_rel = FRM.WK_FRAME_REL()
        name = aRel['name']
        new_rel.name = '%s_%i' %(name, new_rel.id)
        
        
        concept = cpt_knowledge.find_meaning(aRel['concept'])
        new_rel.concept = concept
    
        pFrom = aRel['from']
        pTo = aRel['to']
        
        # Check that both to and from are defined for the edge
        if not(pFrom and pTo):
            return False
        
        # Update construction and name table
        new_frame.add_frame_elem(new_rel)
        name_table['names'][name] = new_rel
        name_table['rels'][name] = (pFrom, pTo)

    @staticmethod           
    def read_wk_frame(aFrame, cpt_knowledge):
        """
        """
        # Create new frame  
        new_frame = FRM.WK_FRAME()
        new_frame.name = aFrame['name']
        trigger = aFrame['trigger']
        if 'preference' in aFrame:
            new_frame.preference = aFrame['preference']
        
        wk_frame =  aFrame['WK_Frame']

        # Name table
        name_table = {'names':{}, 'rels':{}}
        for node in wk_frame['nodes']:
            TCG_LOADER.read_frame_node(new_frame, node, name_table, cpt_knowledge)
        for rel in wk_frame['edges']:
            TCG_LOADER.read_frame_rel(new_frame, rel, name_table, cpt_knowledge)
        
        for rel_name, node_pair in name_table['rels'].iteritems(): # Creating Frame relations
            from_name = node_pair[0]
            to_name = node_pair[1]
            if(not(name_table['names'].has_key(rel_name) and 
                name_table['names'].has_key(from_name) and 
                name_table['names'].has_key(to_name))):
                error_msg = "Unknown FrameRel bounding."
                raise ValueError(error_msg)
           
            frame_elem = name_table['names'][rel_name]
            frame_elem.pFrom = name_table['names'][from_name]
            frame_elem.pTo = name_table['names'][to_name]
        
        trigger_node = name_table['names'][trigger]
        trigger_node.trigger = True
        new_frame.trigger = name_table['names'][trigger]
        
        
        new_frame._create_graph() # Creating NetworkX implementation of Frame
        return new_frame
   
    ###############
    ### PERCEPT ###
    @staticmethod
    def read_percept(atype, sup_per, per_knowledge, per_data):
        """
        """
        for percept in per_data:
            # Create new percept entity
            sub_per = PER.PERCEPT_CAT(name=percept, meaning=percept)
            per_knowledge.add_ent(sub_per)
    
            # Create new percept relation
            new_semrel = PER.SEM_REL(aType=atype, from_per=sub_per, to_per=sup_per)
            
            # update sem_net
            flag = per_knowledge.add_relation(new_semrel)
            if not(flag):
                return False
            
            if(isinstance(per_data[percept], list)):
                for token in per_data[percept]:
                    tok_per = PER.PERCEPT_TOKEN(name=token, meaning=token)
                    per_knowledge.add_ent(tok_per)
                     # Create new percept relation
                    new_semrel = PER.SEM_REL(aType='is_token', from_per=tok_per, to_per=sub_per)
                    # update sem_net
                    flag = per_knowledge.add_relation(new_semrel)
                    if not(flag):
                        return False
    
            else:
                flag = TCG_LOADER.read_percept('is_a', sub_per, per_knowledge, per_data[percept])
                if not(flag):
                    return False
        
        return True
    
    ###########
    ### CXN ###
    # CXN CAN ONLY BE LOADED ONCE THE CONCEPTUAL KNOWLEDGE HAS BEEN LOADED IN A CONCEPTUAL_KNOWLEDGE.
    # NEED TO ADD PROPER TRUE/FALSE RETURN VALUES FOR ALL THOSE FUNCTIONS
    @staticmethod
    def read_node(new_cxn, aNode, name_table, cpt_knowledge):
        """
        """
        # Create new node
        new_node = CXN.TP_NODE()
        name = aNode['name']
        new_node.name = '%s_%i' %(name, new_node.id)
        
        concept = cpt_knowledge.find_meaning(aNode['concept'])
        if not concept:
            error_msg = "Cannot find concept %s in conceptual knowledge" %aNode['concept']
            raise ValueError(error_msg)
        new_node.concept = concept
        
        new_node.head = aNode['head']
        if 'focus' in aNode:
            new_node.focus = aNode['focus']
        if 'frame' in aNode:
            new_node.frame = aNode['frame']
        
        # Update construction and name_table    
        new_cxn.add_sem_elem(new_node)
        name_table['SemNodes'][name] = new_node
        name_table['names'][name] = new_node.name
        
    @staticmethod
    def read_rel(new_cxn, aRel, name_table, cpt_knowledge):
        """
        """    
        # Create new relation
        new_rel = CXN.TP_REL()
        name = aRel['name']
        new_rel.name = '%s_%i' %(name, new_rel.id)
        
        
        concept = cpt_knowledge.find_meaning(aRel['concept'])
        new_rel.concept = concept
    
        pFrom = aRel['from']
        pTo = aRel['to']
        
        # Check that both to and from are defined for the edge
        if not(pFrom and pTo):
            return False
        
        # Update construction and name table
        new_cxn.add_sem_elem(new_rel)
        name_table['SemNodes'][name] = new_rel
        name_table['SemEdges'][name] = (pFrom, pTo)
        name_table['names'][name] = new_rel.name
    
    @staticmethod
    def read_slot(new_cxn, aSlot, name_table):
        """
        """
        new_slot = CXN.TP_SLOT()
        name = aSlot['name']
        new_slot.name = '%s_%i' %(name, new_slot.id)
            
        new_slot.cxn_classes = aSlot['classes']
        
        # Update construction and name table
        new_cxn.add_syn_elem(new_slot)
        name_table['SynForms'][name] = new_slot
        name_table['names'][name] = new_slot.name
    
    @staticmethod       
    def read_phon(new_cxn, aPhon, name_table): # REWORK THIS? SHOULD I RECONSIDER THE PHON TYPE?
        """
        """
        new_phon = CXN.TP_PHON()
        name = aPhon['name']
        new_phon.name = '%s_%i' %(name, new_phon.id)
        new_phon.cxn_phonetics = aPhon['phon']
        
        # Temporarily estimates the syllable length (count the number of alphabet characters)
        for char in new_phon.cxn_phonetics:
            if char.isalpha():
                new_phon.num_syllables += 1
                
        # Update construction and name table
        new_cxn.add_syn_elem(new_phon)
        name_table['SynForms'][name] = new_phon
        name_table['names'][name] = new_phon.name
    
    @staticmethod           
    def read_semframe(new_cxn, SemFrame, name_table, cpt_knowledge):
        """
        """
        for node in SemFrame['nodes']:
            TCG_LOADER.read_node(new_cxn, node, name_table, cpt_knowledge)
        for rel in SemFrame['edges']:
            TCG_LOADER.read_rel(new_cxn, rel, name_table, cpt_knowledge)
        
        for rel_name, node_pair in name_table['SemEdges'].iteritems(): # Creating SemFrame relations
            from_name = node_pair[0]
            to_name = node_pair[1]
            if(not(name_table['SemNodes'].has_key(rel_name) and 
                name_table['SemNodes'].has_key(from_name) and 
                name_table['SemNodes'].has_key(to_name))):
                return False
           
            sem_elem = name_table['SemNodes'][rel_name]
            sem_elem.pFrom = name_table['SemNodes'][from_name]
            sem_elem.pTo = name_table['SemNodes'][to_name]
        
        new_cxn.SemFrame._create_graph() # Creating SemFrame graph
        
    @staticmethod   
    def read_synform(new_cxn, SynForm, name_table):
        """
        """
        for form_elem in SynForm:
            if form_elem['type'] == 'SLOT':
                TCG_LOADER.read_slot(new_cxn, form_elem, name_table)
            elif form_elem['type'] == 'PHON':
                TCG_LOADER.read_phon(new_cxn, form_elem, name_table)
                
    @staticmethod      
    def read_symlinks(new_cxn, sym_links, name_table):
        """
        """
        for key, val in sym_links.iteritems():
            sem_name = name_table['names'][key]
            form_name = name_table['names'][val]
            new_cxn.add_sym_link(sem_name, form_name)
            
    @staticmethod             
    def read_cxn(grammar, aCxn, cpt_knowledge):
        """
        """
        # Create new cxn  
        new_cxn = CXN.CXN()
        new_cxn.name = aCxn['name']
        new_cxn.clss = aCxn['class']
        if 'preference' in aCxn:
            new_cxn.preference = aCxn['preference']
        if 'group' in aCxn:
            new_cxn.group = aCxn['group']
        
        # Name table
        name_table = {'SemNodes':{}, 'SemEdges':{}, 'SynForms':{}, 'names':{}}
        
        # READ SEMFRAME
        TCG_LOADER.read_semframe(new_cxn, aCxn['SemFrame'], name_table, cpt_knowledge)
            
        # READ SYNFORM
        TCG_LOADER.read_synform(new_cxn, aCxn['SynForm'], name_table)
                
        # READ SYMLINKS
        TCG_LOADER.read_symlinks(new_cxn, aCxn['SymLinks'], name_table)
        
        flag = grammar.add_construction(new_cxn)
        if not(flag):
            return False
            
        return True
    
    #############
    ### SCENE ###
    
    #def read_sc_obj(new_rgn, aObj, name_table):
    #    # Create new object
    #    new_obj = SCN.SC_OBJECT()
    #    new_obj.name = aObj['name']
    #    new_obj.region = new_rgn
    #    
    #    new_concept = CPT.CONCEPT()
    #    new_concept.create(meaning = aObj['concept'])
    #    new_obj.concept = new_concept
    #    
    #     # Update region and name_table
    #    if name_table['schemas'].has_key(new_obj.name):
    #        return False
    #    
    #    name_table['schemas'][new_obj.name] = new_obj
    #    return True 
    #    
    #def read_sc_rel(new_rgn, aRel, name_table):
    #    # Create new object
    #    new_rel = SCN.SC_REL()
    #    new_rel.name = aRel['name']
    #    new_rel.region = new_rgn
    #    
    #    new_concept = CPT.CONCEPT()
    #    new_concept.create(meaning = aRel['concept'])
    #    new_rel.concept = new_concept
    #        
    #    # Update region and name_table
    #    if name_table['schemas'].has_key(new_rel.name):
    #        return False
    #    
    #    name_table['schemas'][new_rel.name] = new_rel
    #    name_table['edges'][new_rel.name] = (aRel['from'], aRel['to'])
    #    return True
    #
    #def read_percept(new_rgn, perceive, name_table):
    #    for schema_name in perceive:
    #         # Create new percept
    #        new_per = SCN.PERCEPT()
    #        # Update region and name table
    #        new_rgn.percepts.append(new_per)
    #        name_table['percepts'][new_per] = schema_name
    #        
    #    if not(name_table['percepts'].keys()):
    #            return False
    #        
    #    return True
    #
    #def read_update(new_rgn, updates, name_table):
    #    for sc_name, new_meaning in updates.iteritems():
    #        # Create new percept
    #        new_per = SCN.PERCEPT()
    #        new_concept = CPT.CONCEPT(meaning = new_meaning)
    #        new_PER.concept = new_concept
    #        new_PER.replace_concept = True
    #        # Update region name table
    #        new_rgn.percepts.append(new_per)
    #        name_table['percepts'][new_per] = sc_name
    #            
    #def read_region(scene, aRgn, name_table):
    #    # Create new region
    #    new_rgn = SCN.REGION()
    #    new_rgn.name = aRgn['name']
    #    
    #    new_rgn.x = aRgn['location'][0]
    #    new_rgn.y = aRgn['location'][1]
    #    
    #    new_rgn.w = aRgn['size'][0]
    #    new_rgn.h = aRgn['size'][1]
    #    
    #    new_rgn.saliency = aRgn['saliency']
    #    new_rgn.uncertainty = aRgn['uncertainty']
    #    
    #    for schema in aRgn['schemas']:
    #        if schema['type']=='OBJ':
    #            flag = read_sc_obj(new_rgn, schema, name_table)
    #            if not(flag):
    #                return False
    #        elif schema['type']=='REL':
    #            flag = read_sc_rel(new_rgn, schema, name_table)
    #            if not(flag):
    #                return False
    #        else:
    #            return False
    #    
    #    flag = read_percept(new_rgn, aRgn['perceive'], name_table)
    #    if not(flag):
    #        return False
    #    
    #    if aRgn.has_key('update'):
    #        read_update(new_rgn, aRgn['update'], name_table)
    #
    #    flag = scene.add_region(new_rgn)
    #    if not(flag):
    #        return False
    #    return True
                
    ###############################          
    ### Public loading methods ###
    ###############################
    @staticmethod   
    def load_conceptual_knowledge(file_name='', file_path='./'):
        """
        Loads and returns the conceptual knowledge defined in file_path\file_name. Return None if error.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path=file_path)
        cpt_data = json_data['CONCEPTUAL_KNOWLEDGE']
        
        # Create conceptual knowledge object
        my_conceptual_knowledge = CPT.CONCEPTUAL_KNOWLEDGE()
        
        top = 'CONCEPT'
        top_cpt = CPT.CONCEPT(name=top, meaning=top)
        my_conceptual_knowledge.add_ent(top_cpt)
        
        flag = TCG_LOADER.read_concept("is_a", top_cpt, my_conceptual_knowledge, cpt_data)

           
        if not(flag):
            return None
    
        return my_conceptual_knowledge
        
    @staticmethod
    def load_frame_knowledge(file_name='', file_path='./', cpt_knowledge = None):
        """
        Loads and returns the frame knowledge defined in file_path\file_name. Return None if error.
        Requires a cpt_knowledge (CONCEPTUAL_KNOWLEDGE)
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path=file_path)
        frame_data = json_data['WK_FRAMES']
        
        # Create frame knowledge object
        my_frame_knowledge = FRM.FRAME_KNOWLEDGE()
        
        for frame in frame_data:
            wk_frame = TCG_LOADER.read_wk_frame(frame, cpt_knowledge)
            my_frame_knowledge.add_frame(wk_frame)
    
        return my_frame_knowledge
        
    @staticmethod       
    def load_perceptual_knowledge(file_name='', file_path='./'):
        """
        Load and returns the perceptual knowledge defined in file_path\file_name
        """
        #OPen and read file
        json_data = TCG_LOADER.json_read(file_name, path=file_path)
        per_data = json_data['PERCEPTUAL_KNOWLEDGE']
        
        # Create peceptual_knowledge object
        my_perceptual_knowledge = PER.PERCEPTUAL_KNOWLEDGE()
        
        top = 'PERCEPT'
        top_per = PER.PERCEPT_CAT(name=top, meaning=top)
        my_perceptual_knowledge.add_ent(top_per)
        
        flag = TCG_LOADER.read_percept('is_a', top_per, my_perceptual_knowledge, per_data)
        if not(flag):
            return None
    
        return my_perceptual_knowledge
    
    @staticmethod   
    def load_conceptualization(file_name='', file_path='./', cpt_knowledge=None, per_knowledge=None):
        """
        Load and returns the TCG conceptualization defined in file_path\file_name
        Requires a cpt_knowledge (CONCEPTUAL_KNOWLEDGE) and a perceptual knowledge (PERCEPTUAL_KNOWLEDGE)
        """
        #Open and read file
        json_data = TCG_LOADER.json_read(file_name, path=file_path)
        czer_data = json_data['CONCEPTUALIZATION']
        my_conceptualization = PER.CONCEPTUALIZATION()
        for cpt in czer_data:
            if not(cpt_knowledge.has_concept(cpt)):
                print "%s: concept not found in sem_net" %cpt
            else:
                for pcpt in czer_data[cpt]:
                    if not(per_knowledge.has_percept(pcpt)):
                        print "%s: percept not found in perceptual knowledge" %pcpt
                    else:
                        my_conceptualization.add_mapping(pcpt, cpt)
        
        return my_conceptualization
    
    @staticmethod       
    def load_grammar(file_name='', file_path='./', cpt_knowledge = None):
        """
        Loads and returns the TCG grammar defined in file_path\file_name.
        Requires a cpt_knowledge (CONCEPTUAL_KNOWLEDGE).
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        gram_data = json_data['grammar']
        
        # Create grammar object
        my_grammar = CXN.GRAMMAR()
        
        for aCxn in gram_data:
            TCG_LOADER.read_cxn(my_grammar, aCxn, cpt_knowledge)
    
        return my_grammar
    
    @staticmethod               
    def load_scene(file_name = '', file_path = './', percept_LTM = None):
        """
        Loads and returns a SCENE containing the visual scene data defined in file_path\file_name.
        Args:
            - file_name (STR)
            - file_path (STR)
            - percept_LTM (PERCEPT_LTM):
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        scene_input = json_data['scene']
        
        # Get perceptual schemas
        per_schemas = percept_LTM.schemas
        
        # Build scene
        my_scene = SCN.SCENE()
        my_scene.width = scene_input['resolution'][0]
        my_scene.height = scene_input['resolution'][1]
            
        name_table = {}
        for i in  [s for s in scene_input['schemas'].keys() if scene_input['schemas'][s]['type'] != 'RELATION']: # First instantiate all the schemas that are not relations.
            dat = scene_input['schemas'][i]
            schema = [schema for schema in per_schemas if schema.content['percept'].name == dat['schema']][0]
            inst = ps.PERCEPT_SCHEMA_INST(schema, trace=schema)
            area = ps.AREA(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1])
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
            inst = ps.PERCEPT_SCHEMA_INST(schema, trace=schema)
            inst.content['pFrom'] = name_table[dat['from']]
            inst.content['pTo'] = name_table[dat['to']]
            area = ps.AREA(x=dat['location'][0], y=dat['location'][1], w=dat['size'][0], h=dat['size'][1]) # This means that the area is gonna be of size 0
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
            subscene = SCN.SUB_SCENE(name = dat['name'])
            for schema in dat['schemas']:
                subscene.add_per_schema(name_table[schema])
            
            if dat['saliency'] != 'auto':
                subscene.saliency = float(dat['saliency'])
            
            if dat['uncertainty'] != 'auto':
                subscene.uncertainty = int(dat['uncertainty'])
            
            my_scene.add_subscene(subscene)
        
        return my_scene
    
    @staticmethod               
    def load_scene_light(file_name = '', file_path = './', scene_name = '', concept_LTM = None):
        """
        Loads and returns a SCENE_LIGHT containing the scene_input data defined in file_path\file_name.
        Args:
            - file_name (STR)
            - file_path (STR)
            - scene_name (STR)
            - concept_LTM (CONCEPT_LTM):
        """
        
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        scene_dat = json_data['inputs'][scene_name]
        
        # Build scene
        my_scene = SCN.SCENE_LIGHT()
        subscenes = scene_dat['subscenes']
        scene_structure = scene_dat['scene_structure']
        BU_saliency = scene_dat['BU_saliency']
        BU_saliency.reverse() # For simplicity later!

        # Interpreting subscenes
        interpreter = ls.ISRF_INTERPRETER(concept_LTM)
        for ss_name, val in subscenes.iteritems():
            proposition = val['sem_input']
            cpt_instances = interpreter.prop_interpreter(proposition)
            saliency = (BU_saliency.index(ss_name) + 1)/len(BU_saliency) # Saliency is simply defined based on the index in the BU_saliency list (reversed)
            anchor = interpreter.get_instance(val['anchor'])
            my_scene.add_subscene(ss_name, cpt_instances, saliency, anchor)
        
        my_scene.scene_structure = scene_structure
        
        return my_scene
        
    
    @staticmethod    
    def load_BU_saliency(file_name = '', file_path = './'):
        """
        Loads and returns the saliency data defined in in file_path\file_name.mat Return None if error.
        """
        saliency_data = SMAT.SALIENCY_DATA()
        saliency_data.load(file_path + file_name) # This needs to eb better integrated with the scene data.
        return saliency_data
    
    @staticmethod
    def load_sem_input(file_name = '', file_path = './'):
        """
        Loads and returns the semantic input data defined in in file_path\file_name.
        Return None if error.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        return json_data['inputs']
    
    @staticmethod
    def load_sem_macro(macro_name, file_name = '', file_path = './'):
        """
        Proceses the semantic input macro macro_name (STR) defined in in file_path\file_name.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        sem_macro = json_data['input_macros'][macro_name]
        substitutions = sem_macro['substitutions']
        sem_input_frame = json.dumps(sem_macro['sem_input_frame'])
        
        
        def substitute(my_input, a_substitution):
            pattern = lambda word: r'\b%s\b' %word
            new_input = my_input
            for u,v in a_substitution.iteritems():
                my_pattern = pattern(u)
                new_input = re.sub(my_pattern, v, new_input)
            
            return json.loads(new_input)
        
        def build_substitution_set(substitutions):
            a_substitution = {}
            substitution_set =[a_substitution]
            
            for k,v in substitutions.iteritems():
                new_substitution_set = []
                while substitution_set:
                    substitution = substitution_set.pop()
                    for value in v:
                        new_substitution = substitution.copy()
                        new_substitution[k] = value
                        new_substitution_set.append(new_substitution)
                substitution_set = new_substitution_set[:]
                
            return substitution_set
            
        substitution_set = build_substitution_set(substitutions)
                             
        sem_inputs = {str(substitution): substitute(sem_input_frame, substitution) for substitution in substitution_set}
        
        return sem_inputs
        
    @staticmethod
    def load_ling_input(file_name = '', file_path = './'):
        """
        Loads and returns the linguistic input data defined in in file_path\file_name.
        Return None if error.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        return json_data['inputs']
    
    @staticmethod
    def load_ground_truths(file_name = '', file_path = './'):
        """
        Loads and returns the ground_truths data defined in in file_path\file_name.
        Return None if error.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        ground_truths = json_data.get('ground_truths', {})
        return ground_truths
  
def test():
    """ Loader test function
    """
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics_dev.json", "./data/semantics/")
    my_frame_knowledge = TCG_LOADER.load_frame_knowledge("TCG_semantics_dev.json", "./data/semantics/", my_conceptual_knowledge)   
    for f in my_frame_knowledge.frames:
        f.show()
#    my_perceptual_knowledge = TCG_LOADER.load_perceptual_knowledge("TCG_semantics_main.json", "./data/semantics/")
#    my_conceptualization = TCG_LOADER.load_conceptualization("TCG_semantics_main.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
#    my_grammar = TCG_LOADER.load_grammar("TCG_grammar_VB_main.json", "./data/grammars/", my_conceptual_knowledge)
#    my_scene = TCG_LOADER.load_scene("TCG_scene.json", "./data/scenes/TCG_cholitas/")
#    
#    my_cxn = my_grammar.find_construction('WOMAN')
#    my_cxn.show()
###############################################################################
if __name__=='__main__':
    test()
    

    
    
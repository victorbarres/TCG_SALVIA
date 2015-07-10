# -*- coding: utf-8 -*-
"""
@author: Victor Barres

TCG data loader module
    
    This version requires JSON formatted inputs!

    Loader for world knowledge, grammar, and scenes.
    
    To load conceptual knowledge use load_conceptual_knowledge method (returns a conceptual_knowledge)
    To load perceptual knowledge use load_perceptual_knowledge fmethod (returns a perceptual_knowledge)
    To load conceptualization use load_conceptualization method (returns a conceptualization)
    To load grammar use load_grammar method (returns a grammar)
    To load visual scene use load_scene method (returns a scene)
    
    All other methods should be considered private and are subject to change.
"""
import json

import concept as cpt
import percept as per
import construction as cxn
import saliency_matlab as smat

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
        
        json_data = json.load(f)
        f.close()
        
        return json_data
    
    ######################################
    ### Private object reading methods ###
    ######################################
    
    ###############
    ### CONCEPT ###
    @staticmethod
    def read_concept(atype, sup_cpt, cpt_knowledge, cpt_data):
        
        for concept in cpt_data:
            # Create new concept entity
            sub_cpt = cpt_knowledge.find_meaning(concept)
            if not(sub_cpt):
                sub_cpt = cpt.CONCEPT(name=concept, meaning=concept)
                cpt_knowledge.add_ent(sub_cpt)
    
            # Create new concept relation
            new_semrel = cpt.SEM_REL(aType=atype, from_cpt=sub_cpt, to_cpt=sup_cpt)
            
            # update sem_net
            flag = cpt_knowledge.add_relation(new_semrel)
            if not(flag):
                return False
            
            flag = TCG_LOADER.read_concept(atype, sub_cpt, cpt_knowledge, cpt_data[concept])
            if not(flag):
                return False
        
        return True
    
    ###############
    ### PERCEPT ###
    @staticmethod
    def read_percept(atype, sup_per, per_knowledge, per_data):
        
        for percept in per_data:
            # Create new percept entity
            sub_per = per.PERCEPT_CAT(name=percept, meaning=percept)
            per_knowledge.add_ent(sub_per)
    
            # Create new percept relation
            new_semrel = per.SEM_REL(aType=atype, from_per=sub_per, to_per=sup_per)
            
            # update sem_net
            flag = per_knowledge.add_relation(new_semrel)
            if not(flag):
                return False
            
            if(isinstance(per_data[percept], list)):
                for token in per_data[percept]:
                    tok_per = per.PERCEPT_TOKEN(name=token, meaning=token)
                    per_knowledge.add_ent(tok_per)
                     # Create new percept relation
                    new_semrel = per.SEM_REL(aType='is_token', from_per=tok_per, to_per=sub_per)
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
        new_node = cxn.TP_NODE()
        name = aNode['name']
        new_node.name = '%s_%i' %(name, new_node.id)
        
        concept = cpt_knowledge.find_meaning(aNode['concept'])
        new_node.concept = concept
        
        new_node.head = aNode['head']
        if 'focus' in aNode:
            new_node.focus = aNode['focus']
        
        # Update construction and name_table    
        new_cxn.add_sem_elem(new_node)
        name_table['SemNodes'][name] = new_node
        name_table['names'][name] = new_node.name
        
    @staticmethod
    def read_rel(new_cxn, aRel, name_table, cpt_knowledge):
        """
        """    
        # Create new relation
        new_rel = cxn.TP_REL()
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
        new_slot = cxn.TP_SLOT()
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
        new_phon = cxn.TP_PHON()
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
        
        new_cxn.SemFrame._create_NX_graph() # Creating NetworkX implementation of SemFrame
        
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
        new_cxn = cxn.CXN()
        new_cxn.name = aCxn['name']
        new_cxn.clss = aCxn['class']
        if 'preference' in aCxn:
            new_cxn.preference = aCxn['preference']
        
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
    #    new_obj = scn.SC_OBJECT()
    #    new_obj.name = aObj['name']
    #    new_obj.region = new_rgn
    #    
    #    new_concept = cpt.CONCEPT()
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
    #    new_rel = scn.SC_REL()
    #    new_rel.name = aRel['name']
    #    new_rel.region = new_rgn
    #    
    #    new_concept = cpt.CONCEPT()
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
    #        new_per = scn.PERCEPT()
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
    #        new_per = scn.PERCEPT()
    #        new_concept = cpt.CONCEPT(meaning = new_meaning)
    #        new_per.concept = new_concept
    #        new_per.replace_concept = True
    #        # Update region name table
    #        new_rgn.percepts.append(new_per)
    #        name_table['percepts'][new_per] = sc_name
    #            
    #def read_region(scene, aRgn, name_table):
    #    # Create new region
    #    new_rgn = scn.REGION()
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
        my_conceptual_knowledge = cpt.CONCEPTUAL_KNOWLEDGE()
        
        top = 'CONCEPTUAL_KNOWELDGE'
        top_cpt = cpt.CONCEPT(name=top, meaning=top)
        my_conceptual_knowledge.add_ent(top_cpt)
        
        flag = TCG_LOADER.read_concept("is_a", top_cpt, my_conceptual_knowledge, cpt_data)
        if not(flag):
            return None
        
        cpt.CONCEPT.CONCEPTUAL_KNOWLEDGE = my_conceptual_knowledge # BAD SIDE EFFECT!!! PREVENTS FROM GENERATING INDEPENDENT MODELS FOR DIFFERENT AGENTS!
    
        return my_conceptual_knowledge
        
    @staticmethod       
    def load_perceptual_knowledge(file_name='', file_path='./'):
        """
        Load and returns the perceptual knowledge defined in file_path\file_name
        """
        #OPen and read file
        json_data = TCG_LOADER.json_read(file_name, path=file_path)
        per_data = json_data['PERCEPTUAL_KNOWLEDGE']
        
        # Create peceptual_knowledge object
        my_perceptual_knowledge = per.PERCEPTUAL_KNOWLEDGE()
        
        top = 'PERCEPTUAL_KNOWELDGE'
        top_per = per.PERCEPT_CAT(name=top, meaning=top)
        my_perceptual_knowledge.add_ent(top_per)
        
        flag = TCG_LOADER.read_percept('is_a', top_per, my_perceptual_knowledge, per_data)
        if not(flag):
            return None
        
        per.PERCEPT.PERCEPTUAL_KNOWLEDGE =  my_perceptual_knowledge
    
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
        my_conceptualization = per.CONCEPTUALIZATION()
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
        my_grammar = cxn.GRAMMAR()
        
        for aCxn in gram_data:
            TCG_LOADER.read_cxn(my_grammar, aCxn, cpt_knowledge)
    
        return my_grammar
    
    @staticmethod               
    def load_scene(file_name = '', file_path = './'):
        """
        Loads and returns a DICT containing the visual scene data defined in file_path\file_name. Return None if error.
        
        Note: Might want to check that the perceptual schemas are indeed defined in perceptual knowledge.
        """
        # Open and read file
        json_data = TCG_LOADER.json_read(file_name, path = file_path)
        my_scene = json_data['scene']
        return my_scene
    
    @staticmethod    
    def load_BU_saliency(file_name = '', file_path = './'):
        """
        Loads and returns a the saliency data define in in file_path\file_name.mat Return None if error.
        """
        saliency_data = smat.SALIENCY_DATA()
        saliency_data.load(file_path + file_name) # This needs to eb better integrated with the scene data.
        return saliency_data
    
            
        
###############################################################################
if __name__=='__main__':
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_perceptual_knowledge = TCG_LOADER.load_perceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    my_conceptualization = TCG_LOADER.load_conceptualization("TCG_semantics.json", "./data/semantics/", my_conceptual_knowledge, my_perceptual_knowledge)
    my_grammar = TCG_LOADER.load_grammar("TCG_grammar.json", "./data/grammars/", my_conceptual_knowledge)
    my_scene = TCG_LOADER.load_scene("TCG_scene.json", "./data/scenes/TCG_cholitas/")

    
    
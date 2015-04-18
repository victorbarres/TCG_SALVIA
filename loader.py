# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 2014

@author: Victor Barres

TCG 1.1 data loader module
    
    This version requires JSON formatted inputs!

    Loader for grammar, scenes and conceptual knowledge.
    
    To load grammar use load_grammar function (returns a grammar)
    To load visual scene use load_scene function (returns a scene)
    To load conceptual knowledge use function (returns a SemNet)
    
    All other functions should be considered private and are subject to change.
"""
import json

import concept as cpt
import construction as cxn
import scene as scn


#############################
### Data reading function ###
#############################
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

########################################
### Private object reading functions ###
########################################

###########
### SEM ###

def read_semrel(atype, supMeaning, sem_net, aSemantics):
    
    for meaning in aSemantics:
        # Create new semantic relation
        new_semrel = cpt.SEM_REL()
        new_semrel.type = atype
        new_semrel.supMeaning = supMeaning
        new_semrel.subMeaning = meaning
        
         # update sem_net
        flag = sem_net.add_relation(new_semrel)
        if not(flag):
            return False
            
        flag = read_semrel(atype, meaning, sem_net, aSemantics[meaning])
        if not(flag):
            return False
    
    return True

###########
### CXN ###

# NEED TO ADD PROPER TRUE/FALSE RETURN VALUES FOR ALL THOSE FUNCTIONS

def read_node(new_cxn, aNode, name_table): # NEED TO CHECK THE CURRENT STATUS OF CONCEPT OBJECTS.
    """
    """
    # Create new node
    new_node = cxn.TP_NODE()
    new_node.name = aNode['name']
    
    new_concept = cpt.CONCEPT()
    new_concept.create(meaning = aNode['concept'])
    new_node.concept = new_concept
    
    new_node.head = aNode['head']
    if 'focus' in aNode:
        new_node.focus = aNode['focus']
    
    # Update construction and name_table
    if new_cxn.find_sem_elem(new_node.name):
        return False
    
    new_cxn.add_sem_elem(new_node)
    name_table['SemNames'][new_node.name] = new_node

def read_rel(new_cxn, aRel, name_table):
    """
    """    
    # Create new relation
    new_rel = cxn.TP_REL()
    new_rel.name = aRel['name']
    
    
    new_concept = cpt.CONCEPT()
    new_concept.create(meaning = aRel['concept'])
    new_rel.concept = new_concept

    
    pFrom = aRel['from']
    pTo = aRel['to']
    
    # Check that both to and from are defined for the edge
    if not(pFrom and pTo):
        return False
    
    # Update construction and name table
    new_cxn.add_sem_elem(new_rel)
    name_table['SemNames'][new_rel.name] = new_rel
    name_table['SemEdges'][new_rel.name] = (pFrom, pTo)

def read_slot(new_cxn, aSlot, name_table):
    """
    """
    slot_name = aSlot['name']
    
    new_slot = cxn.TP_SLOT()
        
    new_slot.cxn_classes = aSlot['classes']
    
    # Update construction and name table
    new_cxn.add_syn_elem(new_slot)
    name_table['SlotNames'][slot_name] = new_slot
        
def read_phon(new_cxn, aPhon, name_table): # REWORK THIS? SHOULD I RECONSIDER THE PHON TYPE?
    """
    """
    new_phon = cxn.TP_PHON()
    new_phon.phonetics = aPhon['phon']
    
    # Temporarily estimates the syllable length (count the number of alphabet characters)
    for char in new_phon.phonetics:
        if char.isalpha():
            new_phon.num_syllables += 1
            
            
def read_semframe(new_cxn, SemFrame, name_table):
    """
    """
    for node in SemFrame['nodes']:
        read_node(new_cxn, node, name_table)
    for rel in SemFrame['edges']:
        read_rel(new_cxn, rel, name_table)
    
    for rel_name, node_pair in name_table['SemEdges'].iteritems(): # Creating SemFrame relations
        from_name = node_pair[0]
        to_name = node_pair[1]
        if(not(name_table['SemNames'].has_key(rel_name) and 
            name_table['SemNames'].has_key(from_name) and 
            name_table['SemNames'].has_key(to_name))):
            return False
       
        sem_elem = name_table['SemNames'][rel_name]
        sem_elem.pFrom = name_table['SemNames'][from_name]
        sem_elem.pTo = name_table['SemNames'][to_name]
    
    new_cxn.SemFrame._create_NX_graph() # Creating NetworkX implementation of SemFrame

def read_synform(new_cxn, SynForm, name_table):
    """
    """
    for form_elem in SynForm:
        if form_elem['type'] == 'SLOT':
            read_slot(new_cxn, form_elem, name_table)
        elif form_elem['type'] == 'PHON':
            read_phon(new_cxn, form_elem, name_table)
    
def read_symlinks(new_cxn, sym_links, name_table):
    """
    """
    for key, val in sym_links.iteritems():
        sem_elem = name_table['SemNames'][key]
        slot = name_table['SlotNames'][val]
        new_cxn.add_sym_link(sem_elem, slot)
          
def read_cxn(grammar, aCxn):
    """
    """
    # Create new cxn  
    new_cxn = cxn.CXN()
    new_cxn.name = aCxn['name']
    new_cxn.clss = aCxn['class']
    if 'preference' in aCxn:
        new_cxn.preference = aCxn['preference']
    
    
    # Name table
    name_table = {'SemNames':{}, 'SemEdges':{}, 'SlotNames':{}}
    
    # READ SEMFRAME
    read_semframe(new_cxn, aCxn['SemFrame'], name_table)
        
    # READ SYNFORM
    read_synform(new_cxn, aCxn['SynForm'], name_table)
            
    # READ SYMLINKS
    read_symlinks(new_cxn, aCxn['SymLinks'], name_table)
    
    flag = grammar.add_construction(new_cxn)
    if not(flag):
        return False
        
    return True

#############
### SCENE ###

def read_sc_obj(new_rgn, aObj, name_table):
    # Create new object
    new_obj = scn.SC_OBJECT()
    new_obj.name = aObj['name']
    new_obj.region = new_rgn
    
    new_concept = cpt.CONCEPT()
    new_concept.create(meaning = aObj['concept'])
    new_obj.concept = new_concept
    
     # Update region and name_table
    if name_table['schemas'].has_key(new_obj.name):
        return False
    
    name_table['schemas'][new_obj.name] = new_obj
    return True 
    
def read_sc_rel(new_rgn, aRel, name_table):
    # Create new object
    new_rel = scn.SC_REL()
    new_rel.name = aRel['name']
    new_rel.region = new_rgn
    
    new_concept = cpt.CONCEPT()
    new_concept.create(meaning = aRel['concept'])
    new_rel.concept = new_concept
        
    # Update region and name_table
    if name_table['schemas'].has_key(new_rel.name):
        return False
    
    name_table['schemas'][new_rel.name] = new_rel
    name_table['edges'][new_rel.name] = (aRel['from'], aRel['to'])
    return True

def read_percept(new_rgn, perceive, name_table):
    for schema_name in perceive:
         # Create new percept
        new_per = scn.PERCEPT()
        # Update region and name table
        new_rgn.percepts.append(new_per)
        name_table['percepts'][new_per] = schema_name
        
    if not(name_table['percepts'].keys()):
            return False
        
    return True

def read_update(new_rgn, updates, name_table):
    for sc_name, new_meaning in updates.iteritems():
        # Create new percept
        new_per = scn.PERCEPT()
        new_concept = cpt.CONCEPT(meaning = new_meaning)
        new_per.concept = new_concept
        new_per.replace_concept = True
        # Update region name table
        new_rgn.percepts.append(new_per)
        name_table['percepts'][new_per] = sc_name
            
def read_region(scene, aRgn, name_table):
    # Create new region
    new_rgn = scn.REGION()
    new_rgn.name = aRgn['name']
    
    new_rgn.x = aRgn['location'][0]
    new_rgn.y = aRgn['location'][1]
    
    new_rgn.w = aRgn['size'][0]
    new_rgn.h = aRgn['size'][1]
    
    new_rgn.saliency = aRgn['saliency']
    new_rgn.uncertainty = aRgn['uncertainty']
    
    for schema in aRgn['schemas']:
        if schema['type']=='OBJ':
            flag = read_sc_obj(new_rgn, schema, name_table)
            if not(flag):
                return False
        elif schema['type']=='REL':
            flag = read_sc_rel(new_rgn, schema, name_table)
            if not(flag):
                return False
        else:
            return False
    
    flag = read_percept(new_rgn, aRgn['perceive'], name_table)
    if not(flag):
        return False
    
    if aRgn.has_key('update'):
        read_update(new_rgn, aRgn['update'], name_table)

    flag = scene.add_region(new_rgn)
    if not(flag):
        return False
    return True
            
################################           
### Public loading functions ###
################################
            
def load_grammar(file_name, file_path = './'):
    """
    Load and return the TCG grammar defined in file_path\file_name.
    """        
    # Open and read file
    json_data = json_read(file_name, path = file_path)
    gram_data = json_data['grammar']
    
    # Create grammar object
    my_grammar = cxn.GRAMMAR()
    
    for aCxn in gram_data:
        read_cxn(my_grammar, aCxn)

    return my_grammar

def load_scene(file_name, file_path = './'):
    """
    Load and return the visual scene defined in file_path\file_name. Return None if error.
    """
    # Open and read file
    json_data = json_read(file_name, path = file_path)
    scene_data = json_data['scene']
    
    # Create scene object
    my_scene = scn.SCENE()
    
    my_scene.width = scene_data['resolution'][0]
    my_scene.height = scene_data['resolution'][1]
    
    # Name table
    name_table = {'schemas':{}, 'edges':{}, 'percepts':{}}
    
    for rgn in scene_data['regions']:
        flag = read_region(my_scene, rgn, name_table)
        if not(flag):
            return None

    # Building relations
    for edge, pair in name_table['edges'].iteritems():
        pFrom = pair[0]
        pTo = pair[1]
        
        if(not(name_table['schemas'].has_key(edge) and
                name_table['schemas'].has_key(pFrom) and
                name_table['schemas'].has_key(pTo))):
            return None
        
        name_table['schemas'][edge].pFrom = name_table['schemas'][pFrom]
        name_table['schemas'][edge].pTo = name_table['schemas'][pTo]
    
    # Builind percepts
    for percept, sc_name in name_table['percepts'].iteritems():
        if not(name_table['schemas'].has_key(sc_name)):
            return None
        
        percept.schema = name_table['schemas'][sc_name]
    
    # Storing schemas in the scene
    for sc in name_table['schemas'].values():
        my_scene.add_schema(sc)
    
    return my_scene

def load_SemNet(file_name, file_path = './'):
    """
    Load and return the semantic network defined in file_path/file_name. Return None if error.
    """
    # Open and read file
    sem_data = json_read(file_name, path = file_path)
    
    # Create scene object
    my_semnet = cpt.SEM_NET()
    
    flag = read_semrel(cpt.SEM_REL.IS_A, None, my_semnet, sem_data)
    if not(flag):
        return None

    return my_semnet
            
        
###############################################################################
if __name__=='__main__':
    print "nothing here!"
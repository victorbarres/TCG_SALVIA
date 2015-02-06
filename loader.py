# -*- coding: utf-8 -*-
"""
Created on Mon May 05 13:24:02 2014

@author: Victor Barres

TCG 1.0 data loader module
"""

#import TCG
import concept as cpt
import construction as cxn
import scene as scn

class LOADER:
    """
    Loader for grammar, scenes and conceptual knowledge.
    
    To load grammar use load_grammar method (returns a grammar)
    To load visual scene use load_scene method (returns a scene)
    To load conceptual knowledge use load_SemNet (returns a SemNet)
    
    All other methods should be considered private and are subject to change.
    
    Format:
        - Construction example:
            construction SPA
            {
            	class: S
            	preference: 1	# sentential structure preference
            	
            	node OBJ { concept: ENTITY+ shared head }
            	node ATTR { concept: PROPERTY+ shared }
            	relation ATTR_OBJ { concept: MODIFY from: ATTR to: OBJ }
            
            	[OBJ: NC NP N] 'is' [ATTR: A]
             }
        
        - Region example:
            region KICK_AREA
            {
            	location: 0, 0 size: 0, 0
            	saliency: 80
            	uncertainty: 1
            
            	object KICK { concept: KICK }
            	relation KICK_AGENT { concept: AGENT from: KICK to: WOMAN_L }
            	relation KICK_PATIENT { concept: PATIENT from: KICK to: WOMAN_R }
            
            	perceive KICK, KICK_PATIENT, KICK_AGENT
            	update {WOMAN_R = HUMAN} # To indicate concept replacement
            }
        
        - Grammar file example:
            construction CXN1
            {...}
            
            construction CXN2
            {...}
        
        - Scene file example:
            image: "image_name.jpg"
            resolution: 1024 * 768
            
            region RGN1
            {...}
            
            region RGN2
            {...}
    
    Notes:
        - Format only provides examples, for detailed input file formatting guidelines see Jinyong Lee's thesis.
        - Grammar is the equivalent of Vocabulary in c++ code.
    """
    
    COMMENT_SYMBOL = ('#','#/', '/#')
    
    def __init__(self):
        self.pos = []
        self.data = []
        self.tk = None
        self.prev_tk = None
        self.prev_pos = []
        self.done = True
        self.file_name = ''
    
    ###########################################################################
    ### Data reading methods ###
    def read_file(self,file_name, path='./'):
        file_name = path+file_name
        try:
            f = open(file_name, 'r')
        except IOError as e:
            print "Cannot open %s. %s" %(file_name, e.strerror)
            return False
        
        f_content = f.read()
        f.close()
        
        f_data = f_content.splitlines
        
        f_data = [line.split() for line in f_content.splitlines()]      
        
        self.file_name = file_name        
        
        for d in f_data:
            if d !=[]:
                self.data.append(d)
                
        self.pos = [0,0]
        self.tk = None
        self.done = False
        
        return True
    
    def next_tk(self):
        if len(self.data[self.pos[0]])-1>self.pos[1]: # Some token remain on the line
            self.prev_pos = list(self.pos)
            self.pos[1] += 1
            self.prev_tk = self.tk
            self.tk = self.data[self.pos[0]][self.pos[1]]
        elif len(self.data)-1>self.pos[0]: # There are remaining lines
            self.prev_pos = list(self.pos)
            self.pos[0] += 1
            self.pos[1] = 0
            self.prev_tk = self.tk
            self.tk = self.data[self.pos[0]][self.pos[1]]
        else:
            self.done = True
    
    def next_line(self):
        if len(self.data)-1>self.pos[0]: # There are remaining lines
            self.prev_pos = list(self.pos)
            self.pos[0] += 1
            self.pos[1] = 0
            self.prev_tk = self.tk
            self.tk = self.data[self.pos[0]][self.pos[1]]
        else:
            self.done = True
            
    def read_tk(self):
        if self.tk == None:
            self.tk = self.data[self.pos[0]][self.pos[1]]
        else:
            self.next_tk()
        
        if self.tk == LOADER.COMMENT_SYMBOL[1]:
            while(self.tk != LOADER.COMMENT_SYMBOL[2]):
                self.next_line()
            self.next_line()
        
        while(self.tk[0] == LOADER.COMMENT_SYMBOL[0]):
            self.next_line()
        
        if self.done:
            return ''
        else:
            return self.tk
    
    def backtrack(self):
        if self.prev_tk == None:
            self.reset()
        else:
            self.pos = list(self.prev_pos)
            self.tk = self.prev_tk
        
        if self.done:
            self.done = False        
    
    def reset(self):
        self.pos = [0,0]
        self.tk = None
        self.done = False
        
    def clear(self):
        self.pos = []
        self.data = []
        self.tk = None
    
    def error(self, message= ''):
        errMsg = ""
        errMsg += "Error in %s\n" % self.file_name
        errMsg += "Ln %d Col %d: " % (self.pos[0], self.pos[1])
        errMsg += "%s\n" % message
        if self.pos[0]-1>=0:
            errMsg += "%s " % ' '.join(self.data[self.pos[0]-1])
        errMsg += "<!!> %s\n" % ' '.join(self.data[self.pos[0]])
        print errMsg
        
    ###########################################################################
    ### Private object reading methods ###
    def read_concept(self, new_concept):
        tk = self.read_tk()
        
        if not(tk.isupper()):
            return False
            
        new_concept.create(meaning = tk)
        return True
    
    def read_semrel(self, atype, supMeaning, sem_net):
        meaning = None
        defSupMean = bool(supMeaning)
        defSubMean = False
        
        if not(supMeaning): # Processing root meaning
            tk = self.read_tk()
            if not(tk.isupper()):
                self.error("Cannot read root meaning")
                return False
            
            supMeaning = tk
            defSupMean = True
            
            if self.read_tk() != '{':
                self.error("Missing { ")
                return False
            
        # Process tokens
        while True:
            tk = self.read_tk()
            
            if not(tk):
                self.error("Unexpected end of file")
                return False
            
            if tk == '{':
                if not(defSupMean):
                    self.error("Missing supMeaning")
                    return False
                if not(meaning):
                    break
                
                flag = self.read_semrel(atype, meaning, sem_net)   
                
                if not(flag):
                    self.error("Could not read semantic relation")
                    return False
                
                defSubMean = True
            
            elif tk == '}':
                break # No more fields to process
                
            elif tk.isupper():
                meaning = tk
                
                defSubMean = True
                # Create new semantic relation
                new_semrel = cpt.SEM_REL()
                new_semrel.type = atype
                new_semrel.supMeaning = supMeaning
                new_semrel.subMeaning = meaning
                
                # update sem_net
                flag = sem_net.add_relation(new_semrel)
                if not(flag):
                    self.error("Duplicate semantic relation")
                    return False
            else:
                self.error("Cannot read SemRel. Check that concepts are all caps")
                return False
            
        # Post-processing
        if not(defSupMean and defSubMean):
            self.error("Missing subordinate or superordinate meaning")
            return False
        
        return True
        
    def read_node(self, new_cxn, name_table):
        # Check for name
        node_name = self.read_tk()
        if not(node_name.isupper()):
            return False
        
        if self.read_tk() != '{':
            return False
        
        # Create new node
        new_node = cxn.TP_NODE()
        new_node.name = node_name
        
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
            
            if tk == '}':
                break # No more fields left
                
            elif tk == 'concept:':
                new_concept = cpt.CONCEPT()
                flag = self.read_concept(new_concept)
                if not(flag):
                    return False
                new_node.concept = new_concept
            elif tk == 'head':
                new_node.head = True
            elif tk == 'shared':
                new_node.shared = True
            else:
                return False
        
        # Update construction and name_table
        if new_cxn.find_sem_elem(new_node.name):
            self.error('Duplicate SemFrame node')
            return False
            
        new_cxn.add_sem_elem(new_node)
        name_table['SemNames'][new_node.name] = new_node
        
        return True
        
    def read_rel(self, new_cxn, name_table):
        # Check name
        rel_name = self.read_tk()
        if not(rel_name.isupper()):
            return False
        
        if self.read_tk() != '{':
            return False
        
        # Create new relation
        new_rel = cxn.TP_REL()
        new_rel.name = rel_name
        
        pFrom = ''
        pTo = ''
        
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
            
            if tk == '}':
                break # No more fields left
                
            elif tk == 'concept:':
                new_concept = cpt.CONCEPT()
                flag = self.read_concept(new_concept)
                if not(flag):
                    return False
                new_rel.concept = new_concept
                
            elif tk == 'from:':
                tk = self.read_tk()
                if not(tk.isupper()):
                    return False
                pFrom = tk
                
            elif tk == 'to:':
                tk = self.read_tk()
                if not(tk.isupper()):
                    return False
                pTo = tk
                
            else:
                return False
        
        # Check that both to and from are defined for the edge
        if not(pFrom and pTo):
            return False
        
        # Update constructoin and name table
        new_cxn.add_sem_elem(new_rel)
        name_table['SemNames'][new_rel.name] = new_rel
        name_table['SemEdges'][new_rel.name] = (pFrom, pTo)
        
        return True
    
    def read_slot(self, new_cxn, name_table):
        tk = self.tk
        if tk[-1]!=':':
            return False
        
        node_name = tk[1:-1]
        
        new_slot = cxn.TP_SLOT()
        flag = True
        while flag:
            tk = self.read_tk()
            if tk[-1] == ']':
                clss = tk[:-1]
                flag = False # End of slot
            else:
                clss = tk
            
            if clss in new_slot.cxn_classes:
                self.error('Duplicate SynForm slot class')
                return False
            
            new_slot.cxn_classes.append(clss)        
        
        # Update construction and name table
        new_cxn.add_syn_elem(new_slot)
        name_table['Slot2Sem'][new_slot] = node_name
        
        return True
            
    def read_phon(self, new_cxn, name_table):
        tk = self.tk[1:]
        phon_list = []
        
        if tk[-1] == "'":
            flag = False
            phon_list.append(tk[:-1])
        else:
            phon_list.append(tk)
            flag = True
            
        while flag:
            tk = self.read_tk()
            if tk[-1]=="'":
                flag = False
                phon_list.append(tk[:-1])
            else:
                phon_list.append(tk)
            
        new_phon = cxn.TP_PHON()
        new_phon.phonetics = ' '.join(phon_list)
        
        # Temporarily estimates the syllable length (count the number of alphabet characters)
        for char in new_phon.phonetics:
            if char.isalpha():
                new_phon.num_syllables += 1
        
        new_cxn.add_syn_elem(new_phon)
        return True
        
    def read_cxn(self, grammar):
        # Check for name
        cxn_name = self.read_tk()
        if not(cxn_name.isupper()) :
            self.error('Incorrect cxn name ' + str(cxn_name))
            return False
            
        if self.read_tk() != '{':
            self.error("Missing {")
            return False
        
        # Create new cxn  
        new_cxn = cxn.CXN()
        new_cxn.name = cxn_name
        
        # Name table
        name_table = {'SemNames':{}, 'SemEdges':{}, 'Slot2Sem':{}}
        
        # Field definition flags
        defClass = False
        defSemFrame = False
        defSynForm = False
        
        # Process fields
        while True:
            tk = self.read_tk()
            if not(tk):
                self.error("Unexpected end of file")
                return False
                
            if tk == '}':
                break # No more fields left to process
                
            elif tk == 'class:':
                clss = self.read_tk()
                if not(clss):
                    self.error("Unexpected end of file")
                    return False
                new_cxn.clss = clss
                defClass = True
                
            elif tk == 'preference:':
                pref = self.read_tk()
                if not(pref):
                    self.error("Unexpected end of file")
                    return False
                new_cxn.preference = int(pref)
                
            elif tk == 'node':
                flag = self.read_node(new_cxn, name_table)
                if not(flag):
                    self.error("Could not read node")
                    return False
                defSemFrame = True
                
            elif tk == 'relation':
                flag = self.read_rel(new_cxn, name_table)
                if not(flag):
                    self.error("Could not read relation")
                    return False
                defSemFrame = True
                
            elif tk[0] == '[':
                flag = self.read_slot(new_cxn, name_table)
                if not(flag):
                    self.error("Could not read slot")
                    return False
                defSynForm = True
                
            elif tk[0] == "'":
                flag = self.read_phon(new_cxn, name_table)
                if not(flag):
                    self.error("Could not read phonetic content")
                    return False
                defSynForm = True
            else:
                self.error("Unknown cxn keyword")
                return False
        
        # Post-processing
        if not(defClass and defSemFrame and defSynForm):
            self.error("Missing field in cxn")
            return False
        
        # Link names
        # Creating symbolic links between slots and SemFrame nodes.
        for slot, sem_name in name_table['Slot2Sem'].iteritems():
            if not(name_table['SemNames'].has_key(sem_name)):
                self.error('Slot linked to unknown SemFrame node')
                return False
            sem_elem = name_table['SemNames'][sem_name]
            sem_elem.linked_slot = slot
            slot.linked_SemElem = sem_elem
            
        # Creating SemFrame relations
        for rel_name, node_pair in name_table['SemEdges'].iteritems():
            from_name = node_pair[0]
            to_name = node_pair[1]
            if(not(name_table['SemNames'].has_key(rel_name) and 
                name_table['SemNames'].has_key(from_name) and 
                name_table['SemNames'].has_key(to_name))):
                self.error('Incorrect SemFrame relation')
                return False
           
            sem_elem = name_table['SemNames'][rel_name]
            sem_elem.pFrom = name_table['SemNames'][from_name]
            sem_elem.pTo = name_table['SemNames'][to_name]
        
        flag = grammar.add_construction(new_cxn)
        if not(flag):
            self.error("Duplicate construction")
            return False
            
        return True
    
    def read_sc_obj(self, new_rgn, name_table):
        # Check for name
        obj_name = self.read_tk()
        if not(obj_name.isupper()):
            return False
        
        if self.read_tk() != '{':
            return False
        
        # Create new object
        new_obj = scn.SC_OBJECT()
        new_obj.name = obj_name
        new_obj.region = new_rgn
        
        # Field definition tag
        defConcept = False
        
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
            
            if tk == '}':
                break # No more fields left
                
            elif tk == 'concept:':
                new_concept = cpt.CONCEPT()
                flag = self.read_concept(new_concept)
                if not(flag):
                    return False
                new_obj.concept = new_concept
                defConcept = True
            else:
                return False
        
        # Post-processing
        if not(defConcept):
            self.error("Missing field for object schema")
            return False
            
        # Update region and name_table
        if name_table['schemas'].has_key(new_obj.name):
            self.error('Duplicate object schema')
            return False
        
        name_table['schemas'][new_obj.name] = new_obj
        
        return True 
    
    def read_sc_rel(self, new_rgn, name_table):
        # Check for name
        rel_name = self.read_tk()
        if not(rel_name.isupper()):
            return False
        
        if self.read_tk() != '{':
            return False
        
        # Create new object
        new_rel = scn.SC_REL()
        new_rel.name = rel_name
        new_rel.region = new_rgn
        
        # Field definition tag
        defConcept = False
        defFrom = False
        defTo = False
        
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
            
            if tk == '}':
                break # No more fields left
                
            elif tk == 'concept:':
                new_concept = cpt.CONCEPT()
                flag = self.read_concept(new_concept)
                if not(flag):
                    return False
                new_rel.concept = new_concept
                defConcept = True
                
            elif tk == 'from:':
                tk = self.read_tk()
                if not(tk.isupper()):
                    return False
                pFrom = tk
                defFrom = True
                
            elif tk == 'to:':
                tk = self.read_tk()
                if not(tk.isupper()):
                    return False
                pTo = tk
                defTo = True
            else:
                return False
        
        # Post-processing
        if not(defConcept and defFrom and defTo):
            self.error("Missing field for relation schema")
            return False
            
        # Update region and name_table
        if name_table['schemas'].has_key(new_rel.name):
            self.error('Duplicate relation schema')
            return False
            
        name_table['schemas'][new_rel.name] = new_rel
        name_table['edges'][new_rel.name] = (pFrom, pTo)
        return True
    
    def read_percept(self, new_rgn, name_table):
        if self.read_tk() != '{':
            return False
            
        # Process fields
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
                
            elif tk == '}':
                break # No more elements to perceive

            elif tk.isupper():
                # Create new percept
                new_per = scn.PERCEPT()
                # Update region and name table
                new_rgn.percepts.append(new_per)
                if tk[-1]==',':
                    sc_name = tk[:-1]
                else:
                    sc_name = tk
                name_table['percepts'][new_per] = sc_name
#            if tk.isupper and tk[-1]!=',':
#                # Create new percept
#                new_per = scn.PERCEPT()
#                sc_name = tk
#                tk = self.read_tk()
#                if tk !='=':
#                    # Update region and table
#                    new_rgn.percepts.append(new_per)
#                    name_table['percepts'][new_per] = sc_name
#                    self.backtrack()
#                    break
#                elif tk == '=':
#                    tk = self.read_tk()
#                    new_concept = cpt.CONCEPT(meaning = tk)
#                    new_per.concept = new_concept
#                    new_per.replace_concept = True
#                    # Update region name table
#                    new_rgn.percepts.append(new_per)
#                    name_table['percepts'][new_per] = sc_name
#                    break
            else:
                return False
            
        if not(name_table['percepts'].keys()):
                return False
            
        return True
    
    def read_update(self, new_rgn, name_table):
        if self.read_tk() != '{':
            return False
        
        while True:
            tk = self.read_tk()
            if not(tk):
                return False
            elif tk == '}':
                break # No more element to update
            elif tk.isupper():
                # Create new percept
                new_per = scn.PERCEPT()
                sc_name = tk
                tk = self.read_tk()
                if tk != '=':
                    return False
                tk = self.read_tk()
                if not(tk) or not(tk.isupper()):
                    return False
                if tk[-1] == ',':
                    new_mean = tk[:-1]
                else:
                    new_mean = tk
                new_concept = cpt.CONCEPT(meaning = new_mean)
                new_per.concept = new_concept
                new_per.replace_concept = True
                # Update region name table
                new_rgn.percepts.append(new_per)
                name_table['percepts'][new_per] = sc_name
            else:
                return False
                
        return True
                
    def read_region(self, scene, name_table):
        # Check name
        rgn_name = self.read_tk()
        
        if not(rgn_name.isupper()):
            self.error("Incorrect region name")
            return False
        
        if self.read_tk() != '{':
            self.error("Missing {")
            return False
        
        # Create new region
        new_rgn = scn.REGION()
        new_rgn.name = rgn_name
        
        # field definition flags
        defLocation = False
        defSize = False
        defSaliency = False
        defUncertainty = False
        
        # Process fields
        while True:
            tk = self.read_tk()
            if not(tk):
                self.error("Unexpected end of file")
            
            if tk == '}':
                break # No more fields to process
                
            elif tk == 'location:':
                tk = self.read_tk()
                if tk[-1]!=',':
                    self.error("Incorrect location format (location: x, y)")
                    return False
                new_rgn.x = int(tk[:-1])
                new_rgn.y = int(self.read_tk())
                defLocation = True
                
            elif tk == 'size:':
                tk = self.read_tk()
                if tk[-1] != ',':
                    self.error("Incorrect size format (size: w, h))")
                    return False
                new_rgn.w = int(tk[:-1])
                new_rgn.h = int(self.read_tk())
                defSize = True
                
            elif tk == 'saliency:':
                tk = self.read_tk()
                new_rgn.saliency = int(tk)
                defSaliency = True
                
            elif tk == 'uncertainty:':
                tk = self.read_tk()
                new_rgn.uncertainty = int(tk)
                defUncertainty = True
                
            elif tk == 'object':
                flag = self.read_sc_obj(new_rgn, name_table)
                if not(flag):
                    self.error("Could not read perceptual schema object")
                    return False
                    
            elif tk == 'relation':
                flag = self.read_sc_rel(new_rgn, name_table)
                if not(flag):
                    self.error("Could not read percetual schema relation")
                    return False
                    
            elif tk == 'perceive':
                flag = self.read_percept(new_rgn, name_table)
                if not(flag):
                    self.error("Could not read percepts")
                    return False
            
            elif tk == 'update':
                flag = self.read_update(new_rgn, name_table)
                if not(flag):
                    self.error("Could not read updates")
                    return False

            else:
                self.error("Unkonwn region keyword")
                return False
        
        # Post-processing
        if not(defLocation and defSize and defSaliency and defUncertainty):
            self.error("Missing field in region")
            return False

        flag = scene.add_region(new_rgn)
        if not(flag):
            self.error("Duplicate region")
            return False
        return True
                
    ###########################################################################            
    ### Public loading methods ###
                
    def load_grammar(self, file_name, file_path = './'):
        """
        Load and return the TCG grammar defined in file_path\file_name. Return None if error.
        """
        self.clear()
        
        # Open and read file
        flag = self.read_file(file_name, path = file_path)
        if not(flag):
            self.error("Failed to open construction grammar file")
            return None
        
        # Create grammar object
        my_grammar = cxn.GRAMMAR()
        
        # Process tokens
        while not(self.done):
            tk = self.read_tk()
            if tk == 'construction':
                flag = self.read_cxn(my_grammar)
                if not(flag):
                    return None
            elif (tk != 'construction' and not(self.done)):
                self.error("Unknown grammar keyword")
                return None
        
        return my_grammar
    
    def load_scene(self, file_name, file_path = './'):
        """
        Load and return the visual scene defined in file_path\file_name. Return None if error.
        """
        self.clear()
        
        # Open and read file
        flag = self.read_file(file_name, path = file_path)
        if not(flag):
            self.error("Failed to open visual scene file")
            return None
        
        # Create scene object
        my_scene = scn.SCENE()
        
        # Field definition flags
        defImage = False
        defResol = False
        
        # Name table
        name_table = {'schemas':{}, 'edges':{}, 'percepts':{}}
        
        # Process tokens
        while not(self.done):
            tk = self.read_tk()
            if tk == 'image:':
                tk = self.read_tk()
                defImage = True
            
            elif tk == 'resolution:':
                tk = self.read_tk()
                if not(tk.isdigit()):
                    self.error("Incorrect resolution format")
                    return None
                w = int(tk)
                if self.read_tk() != '*':
                    self.error("Incorrect resolution format")
                    return None
                tk = self.read_tk()
                if not(tk.isdigit()):
                    self.error("Incorrect resolution format")
                h = int(tk)
                
                my_scene.width = w
                my_scene.height = h
                defResol = True
            
            elif tk == 'region':
                flag = self.read_region(my_scene, name_table)
                if not(flag):
                    self.error("Cannot read region")
                    return None
            else:
                if not(self.done):
                    self.error("Unknown scene keyword")
                    return None
        
        # Post-processing
        if not(defImage and defResol):
            self.error("Missing fields")
            return None
        
        # Building relations
        for edge, pair in name_table['edges'].iteritems():
            pFrom = pair[0]
            pTo = pair[1]
            
            if(not(name_table['schemas'].has_key(edge) and
                    name_table['schemas'].has_key(pFrom) and
                    name_table['schemas'].has_key(pTo))):
                self.error("Cannot build relation schema " + str(edge))
                return None
            
            name_table['schemas'][edge].pFrom = name_table['schemas'][pFrom]
            name_table['schemas'][edge].pTo = name_table['schemas'][pTo]
        
        # Builind percepts
        for percept, sc_name in name_table['percepts'].iteritems():
            if not(name_table['schemas'].has_key(sc_name)):
                self.error("Cannot build percept")
                return None
            
            percept.schema = name_table['schemas'][sc_name]
        
        # Storing schemas in the scene
        for sc in name_table['schemas'].values():
            my_scene.add_schema(sc)
        
        return my_scene
    
    def load_SemNet(self, file_name, file_path = './'):
        """
        Load and return the semantic network defined in file_path/file_name. Return None if error.
        """
        self.clear()
        
        # Open and read file
        flag = self.read_file(file_name, path = file_path)
        if not(flag):
            self.error("Failed to open semantic network file")
            return None
        
        # Create scene object
        my_semnet = cpt.SEM_NET()
        
        # Process tokens
        while not(self.done):
            tk = self.read_tk()           
            if tk == 'is_a':
                flag = self.read_semrel(cpt.SEM_REL.IS_A, None, my_semnet)
                if not(flag):
                    self.error("Could not read IS_A network")
                    return None
                    
            else:
                if not(self.done):
                    self.error("Unknown scene keyword")
                    return None
        
        return my_semnet
            
        
###############################################################################
if __name__=='__main__':
    log = ''
    
    ld = LOADER()
#    
#    file_name = 'data\TCG_grammar.txt'
#    g = ld.load_grammar(file_name)
#    log += "GRAMMAR LOADED FROM %s\n\n" % file_name
#    log += str(g)
#    
    file_name = 'data/scene_womanhitman.txt'
    s = ld.load_scene(file_name)
    log += "SCENE LOADED FROM %s\n\n" % file_name
    log += str(s)
#
    f = open('my_log', 'w')
    f.write(log)
    f.close()
    
#    file_name = 'test_semantics.txt'
#    snet = ld.load_SemNet(file_name)
#    
#    print snet
        
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 18:14:40 2014

@author: Victor Barres

Define schema instance related classes for TCG1.0
"""

import concept as CPT
from construction import TP_ELEM

###############################################################################
### Schema instance ###
class SCHEMA_INST:
    """
    Schema instance (base class)
    
    Data:
        - id (int): Unique id
        - type (int): Type of schema
        - activation (int): Current activation value of schema instance
        - alive, old, fresh (bool): status flags
    """
    ID_next = 0 # Global schema instance ID counter
    inst_activity = False # Gloabal instance activity flag. Monitors instantaneous activity
    
    # Instance types
    UNDEFINED = 0
    NODE = 1
    RELATION = 2
    CONSTRUCTION = 3

    def __init__(self):
        self.id = SCHEMA_INST.ID_next
        SCHEMA_INST.ID_next +=1
        
        self.type = SCHEMA_INST.UNDEFINED
        self.alive = False
        self.old = False
        self.fresh = False
        
        self.activation = 0
    
    def Alive(self, bool_val):
        """
        If not already the case, set alive to bool_val (bool) and signal instantaneous activity.
        """
        if self.alive != bool_val:
            SCHEMA_INST.inst_activity = True
            self.alive = bool_val

    def Old(self, bool_val):
        """
        If not already the case, set old to bool_val (bool) and signal instantaneous activity
        """
        if self.old != bool_val:
            SCHEMA_INST.inst_activity = True
            self.old = bool_val
    
    def Fresh(self, bool_val):
        """
        If not already the case, set 'fresh' to bool_val (bool) and signal instantaneous activity
        """
        if self.fresh != bool_val:
            SCHEMA_INST.inst_activity = True
            self.fresh = bool_val
        
    def Activation(self, act):
        """
        If not already the case, set 'activation' to act (int) and signal instananeous activity
        """
        if self.activation != act:
            SCHEMA_INST.inst_activity = True
            self.activation = act
    
    def validate(self):
        return

### SemRep schema instance ###     
class SEMREP_INST(SCHEMA_INST):
    """
    SemRep instance
    
    Data (inherited):
        - id (int): Unique id
        - type (int): Type of schema
        - activation (int): Current activation value of schema instance
        - alive, old, fresh (bool): status flags
    
    Data:
        - concept (CONCEPT): Representing concept
        - schema (SCHEMA): Associated perceptual schema
    """
    
    def __init__(self):
        SCHEMA_INST.__init__(self)
        self.concept = CPT.CONCEPT()
        self.schema = None
    
    def Instantiate(self, pSchema, act):
        """
        Instantiate schema.
        
        Args:
            - pSchema(SCHEMA): perceptual schema
            - act (int): initial activation
        """
        if not(pSchema):
            return
        
        self.Fresh(True)
        self.Alive(True)
        self.Old(False)
        
        self.Activation(act)
        self.schema = pSchema
        
        self.concept.create(concept=pSchema.concept)
        
    
    def Update(self, new_concept):
        """
        Update concept to new_concept (CONCEPT)
        """
        self.Fresh(True)
        
        self.concept.create(concept=new_concept)        

class NODE_INST(SEMREP_INST):
    """
    Node instance
    """
    def __init__(self):
        SEMREP_INST.__init__(self)
        self.type = SCHEMA_INST.NODE

class REL_INST(SEMREP_INST):
    """
    Relation instance.
    """
    def __init__(self):
        SEMREP_INST.__init__(self)
        self.type = SCHEMA_INST.RELATION
        self.pFrom = None
        self.pTo = None
    
    def validate(self):
        """
        Check if connecting SemRep instances exist and are alive.
        """
        if not(self.pFrom and self.pTo and self.pFrom.alive and self.pTo.alive):
            self.Alive(False)

### Construction schema instance ###
class CXN_INST(SCHEMA_INST):
    """
    Construction instance.
    
    Data (inherited):
        - id (int): Unique id
        - type (int): Type of schema
        - activation (int): Current activation value of schema instance
        - alive, old, fresh (bool): status flags
    
    Data:
        - base_cxn (CXN): Base grammatical construction.
        - cxn_struct (CXN_STRUCT): Structure to which the construction instance belong to.
        
        - covers ([SEMREP_INST]): Covering SemRep instances.
        - elems ([TP_SEM_ELEM]): SemFrame elements paired with covering SemRep instances.
        - slots ([TP_SLOT]): Slots elements paired with covering SemRep instances.
        
        - _matches ({INT: MATCH_INFO}): Matching dictionary. Key = Cxn  instance in. Value = match info
    """
    def __init__(self):
        SCHEMA_INST.__init__(self)
        self.type = SCHEMA_INST.CONSTRUCTION
        self.base_cxn = None
        self.cxn_struct = None
        self.covers = []
        self.elems = []
        self.slots = []
        self._matches = {}
    
    def instantiate(self, cxn, semrep, act):
        """
        Instantiate a construction schema instance for the grammatical construction cxn (CXN) based
        on the matching with the SemRep instances semrep ([SEMREP_INST]),
        with activation act (int).
        """ 
        if not(cxn):
            return
            
        self.Fresh(True)
        self.Alive(True)
        self.Old(False)
        self.Activation(act)
        
        self.base_cxn = cxn
        
        # Reset covering instances
        self.covers = semrep
        self.elems = self.base_cxn.SemFrame
        self.slots = [e.linked_slot for e in self.elems]
        
        
        # THIS IS THE EQUIVALENT OF C++ CODE...
#        self.covers = []
#        self.elems = []
#        self.slots = []
#        for i in range(len(semrep)):
#            self.covers.append(semrep[i])
#            self.elems.append(self.cxn.SemFrame[i])
#            self.slots.append(self.cxn.SemFrame[i].linked_slot)
        
        
    def validate(self):
        """
        Check whether covering SemRep instances are still alive. Update status flags and match table.
        """
        # For a cxn instance to be alive, all the covering SemRep instances need to be alive.
        for c in self.covers:
            if not(c.alive):
                self.Alive(False)
                
        # Match table maintenance
        for i in self._matches.keys():
            if not(self._matches[i].other.alive):
                del self._matches[i]   
    
    def compare(self, aCxnInst):
        """
        Compare current cxn instance to another cxn instance aCxnInst (CXN_INST).
        
        Return true if  (1) the two cxn inst share the same base construction 
                        (2) they cover the same SemRep instances.
        """
        # Check base construction
        if self.base_cxn != aCxnInst.base_cxn:
            return False
        
        # Check covering SemRep instances
        if self.covers != aCxnInst.covers:
            return False
        
        return True
        
    
    ## Class methods ##
    def match(cxn1, cxn2, match_info):
        """
        Match two construction instances. Return True when no conflict occurs.
        
        Args:
            - cxn1 (CNX_INST): first construction instance
            - cxn2 (CXN_INST): second construction instance
            - match_info (MATCH_INFO): Stores match operation results.
            
       Algorithm:
            - 1:If a relation already exists between instances (stored in cxn._matches), it is copied and returned.
            - 2: Loop through all the SemRep instances covered by both cxn1 and cxn2
                - if the two instances overlap on a SemRep instance that is not linked to a shared SemFrame elements in both instances -> CONFLICT
                - Otherwise, check if cxn2 can link to a slot of cxn1 (cxn1 = parent, cxn2 = child) or vice versa.
                A link is possible if:
                    i. SemFrame element covering the SemRep instance in the parent instance has an associated slot
                    ii. The child instance's class matches the class restriction of this slot.
                    iii. The SemFrame element of the child instance linked to the SemRep instance is the head.
                    
        Notes:
            - The match methods returns at most 1 match option. If both cxn1 and cxn2 can be parents, it will only return the option with cxn1 as parent.
        """
        match_info.clear()
        
        if not(cxn1) or not(cxn2):
            match_info.match = 0
            return True
        
        if cxn1 == cxn2:
            match_info.match = -1 # Identical cxn instances are conflicting
            return False
        
        # Scan matching table to see if a relation already exist between the constructions
        if cxn1._matches.has_key(cxn2.id):
            match_info.copy(cxn1._matches[cxn2.id])
            return (match_info.match > -1)
            
        match_info.match = 0 # Initially no relation between cxn instances
        
        # Iterating over all SemRep instances where both constructions instances overlap
        for idx1 in range(len(cxn1.covers)):            
            try:
                idx2 = cxn2.covers.index(cxn1.covers[idx1])
            except ValueError:
                continue
            
            # Set overlap flag
            match_info.overlap = True
            
            # Check conflict
            if(not(cxn1.elems[idx1].shared) and not(cxn2.elems[idx2].shared)):
                match_info.match = -1 # If both constructions overlap on an element that cannot be share -> Conflict
                break
            
            # Check if construction class match slots class restrictions.
            # cxn1 parent cxn2 child
            if(cxn2.elems[idx2].head and 
                    cxn1.slots[idx1] and 
                    (cxn2.base_cxn.clss in cxn1.slots[idx1].cxn_classes)):
                match_info.match = 1
                match_info.parent = cxn1
                match_info.child = cxn2
                match_info.SynFormIdx = cxn1.base_cxn.SynForm.index(cxn1.slots[idx1])
            # cxn2 parent cxn1 child
            if(cxn1.elems[idx1].head and
                    cxn2.slots[idx2] and
                    (cxn1.base_cxn.clss in cxn2.slots[idx2].cxn_classes)):
                match_info.match = 1
                match_info.parent = cxn2
                match_info.child = cxn1
                match_info.SynFormIdx = cxn2.base_cxn.SynForm.index(cxn2.slots[idx2])
        
        # Update match table in both construction instances
        minfo_cxn1 = MATCH_INFO()
        minfo_cxn1.copy(match_info)
        minfo_cxn1.other = cxn2
        cxn1._matches[cxn2.id] = minfo_cxn1
        
        minfo_cxn2 = MATCH_INFO()
        minfo_cxn2.copy(match_info)
        minfo_cxn2.other = cxn1
        cxn2._matches[cxn1.id] = minfo_cxn2
        
        return (match_info.match > -1)
        
###############################################################################
### Construction instance assemblage ###
    
class MATCH_INFO:
    """
    Construction instance matching information.
    
    Data:
        - match (int): -1 = conflict, 0 = no relation, 1 = union
        - overlap (bool): overlap flag
        - parent (CXN_INST): parent construction instance
        - child (CXN_INST): child contruction instance
        - SynFormIdx (int): SynForm index of the parent's slot to which the child is linked.
        
        - other (CXN_INST): ...for maintenance purposes...
    """
    def __init__(self):
        self.match = 0
        self.overlap = False
        self.parent = None
        self.child = None
        self.SynFormIdx = -1
        self.other = None
    
    def clear(self):
        """
        Reset match info values
        """
        self.match = 0
        self.overlap = False
        self.parent = None
        self.child = None
        self.SynFormIdx = -1
        
    def copy(self, mInfo):
        """
        Copies match info values from mInfo (MATCH_INFO).
        """
        if not(mInfo):
            return
        
        self.match = mInfo.match
        self.overlap = mInfo.overlap
        self.parent = mInfo.parent
        self.child = mInfo.child
        self.SynFormIdx = mInfo.SynFormIdx
        
class CXN_LINK:
    """
    Hierachical link between construction instances.
    
    Data:
        - parent (CXN_INST): parent cxn instance
        - child (CXN_INST): child cxn instance
        - SynFormIdx (int): index of the parent's linking slot in its SynFrom list
    """
    def __init__(self):
        self.parent = None
        self.child = None
        self.SynFormIdx = -1
    
    def compare(self, other):
        is_equal = ((self.parent == other.parent) and 
                    (self.child == other.child) and
                    (self.SynFormIdx == other.SynFormIdx))
        return is_equal

class CXN_STRUCT:
    """
    Construction hiearchy structure.
    
    Data:
        - top (CXN_INST): Top construction instance
        - insts ([CNX_INST]): Construction instances forming the structure
        - links ([CXN_LINK]): Hierachical construction links forming the structure
        - suitability (int): Suitability of the structure
        - fresh, valid (bool): Status flags
        
    Notes:
        - Suitability is computed as:
            - each covered SemRep instance (that is not shared) adds SEM_WEIGHT
            - utterance lengths is measured as number of syllables. Suitability is inveresely 
            proportional to utterance length (favor compact utterances) weighted by LEN_WEIGHT.
            - each contruction adds preference*PRF_WEIGHT.
            
            ex. For a single construction that covers 2 unshared SemRep nodes, has 7 syllables and a preference of 4
            
            Suitability = 2*SEM_WEIGHT - 7*LEN_WEIGHT + 4*PRF_WEIGHT.
            
            Other parameters (e.g. frequency, task requirement, etc.) can be considered to.
    """
    SEM_WEIGHT = 100 # Semantic coverage weight
    LEN_WEIGHT = 1 # Utterance weight length (lengt measured as number of syllables)
    RDD_WEIGHT = 100 # Utterance redundancy weight
    PRF_WEIGHT = 50 # Utterance preference weight
    
    def __init__(self):
        self.top = None
        self.insts = []
        self.links = []
        self.suitability = 0
        self.fresh = False
        self.valid = True
    
    def get_child(self, parent, idx):
        """
        If it exists, return the child (CXN_INST) for a given parent (CXN_INST) 
        and a given SynForm index idx (int).
        """
        for link in self.links:
            if(link.parent == parent and link.SynFormIdx == idx):
                return link.child
            
        return None
    
    def get_parent(self, child):
        """
        If it exist return the parent (CXN_INST) for a given child (CXN_INST).
        """
        for link in self.links:
            if(link.child == child):
                return link.parent
        
        return None
    
    def check_lineage(self, cxn_str):
        """
        Returns True if cxn_str is identical, contains or is contained in the construction structure.
        """
        if not(cxn_str):
            return False
        
        if(self.top == cxn_str.top):
            return True # Same grammatical structure.
        
        return (self.compare(cxn_str) > 1) # Overlapping structure
    
    def check_membership(self, cxn = None, link = None):
        """
        Check if a given cxn (CXN_INST) or link (CXN_LINK) are part of the structure.
        """
        if cxn and link:
            raise NameError('Cannot check membership of cxn and link simultaneously')
        
        if cxn:
            return (cxn in self.insts)
        
        if link:
            for l in self.links:
                if link.compare(l):
                    return True            
        return False
    
    def check_obsolete(self):
        """
        Check if the cxn structure is obsolete. Structure is considered obsolete
        if all the SemRep instances covered by the cxn instances are old.
        """
        for inst in self.insts:
            for sem_inst in inst.covers:
                if not(sem_inst.old):
                    return False # Not obsolete if only one of the covered SemRep instances is not old.
        
        return True
    
    def check_complete(self):
        """
        Check if a cxn structure is complete. Structure is complete if all the slots 
        of all the cxn instances currently in the structure are linked to a cxn inst.
        """
        for inst in self.insts:
            for i in range(len(inst.base_cxn.SynForm)):
                form = inst.base_cxn.SynForm[i]
                if form.type != TP_ELEM.SLOT:
                    continue
                if not(self.get_child(inst, i)):
                    return False
                    
        return True
        
    def clear(self):
        """
        Clear cxn structure.
        """
        self.top = None
        self.insts = []
        self.links = []
        self.suitability = 0
        self.fresh = False
        self.valid = True
        
    def create(self, cxn):
        """
        Initialize the empty construction struture with cxn (CXN_INST) as the top construction.
        Calculate initial suitability of the structure (see class docstring for more info).
        
        Args:
            - cxn (CXN_INST): The initial top cxn instance
        """
        if (not(cxn) or self.top):
            return # Cannot create if top is already occupied.
            
        self.top = cxn
        self.insts.append(cxn)
        self.fresh = True
        
        ### Calculate base suitability ###
        # Semantic coverage
        for i in range(len(cxn.covers)):
            if cxn.elems[i].shared:
                continue # Structure doesn't get point for shared elements
            
#            if not(CONCEPT.match(cxn.covers[i].concept, cxn.elems[i].concept, False)):
#                continue
            #-> Semantic closeness is not necessary since the similarity between two matching concepts is always 0
            
            self.suitability += CXN_STRUCT.SEM_WEIGHT
        
        # Utterance length
        totLen = 0
        for form in cxn.base_cxn.SynForm:
            if form.type != TP_ELEM.PHONETICS:
                continue
            
            totLen += form.num_syllables
        self.suitability -= totLen * CXN_STRUCT.LEN_WEIGHT # Inversely proportional to utterance length.
        
        # Construction preference
        self.suitability += cxn.base_cxn.preference * CXN_STRUCT.PRF_WEIGHT
        
#        Other parameters (e.g. frequency, task requirement, etc.) can be considered to.
    
    def compare(self, cxn_str):
        """
        Compare this construction structure with cxn_str (CXN_STR).
        
        Return:
            - 0: None matched
            - 1: Partial match
            - 2: Contained (subset of cxn_str)
            - 3: Identical
            - 4: Contains (superset of cxn_str)
        """
        matched = 0
 
        # Count the  number of matching links between structures.
        for link in self.links:
            if cxn_str.check_membership(link = link):
                matched +=1
        
        if matched == 0:
            if(self.links == [] and cxn_str.links == []):
                if self.top == cxn_str.top:
                    return 3 # identical
            
            if self.links == []:
                if cxn_str.check_membership(cxn  = self.top):
                    return 2 # contained (subset)
                    
            if cxn_str.links == []:
                if self.check_membership(cxn = cxn_str.top):
                    return 4 # contains (superset)
            
            return 0 # none matched
        
        if matched == len(self.links):
            if len(self.links) == len(cxn_str.links):
                return 3 # identical
            
            return 2 # contained (subset)
        
        if matched == len(cxn_str.links):
            return 4 # contains (superset)
        
        return 1 # Partial match
    
    def merge(self, cxn_str):
        """
        Merge construction structure with cxn_str (CXN_STR). 
        Elements (links and cxn insts) of cxn_str are added to the construction structure.
        Suitability of both cnx structures are added.
        
        THE TWO CONSTRUCTION STRUCTURES SHOULD NOT SHARE ANY ELEMENT (NO DUPLICATION ASSUMED).
        
        Notes: This method is only there to be used within the combine class method, since the output of merge is not a proper
        construction structure (more a set containing 2 cnx sructs since the top instances have not been linked).
        """
        # add base suitability
        self.suitability += cxn_str.suitability
        
        # Merge instances (no duplication assumed)
        for inst in cxn_str.insts:
            self.insts.append(inst)
        
        # Merge links (no duplication assumed)
        for link in cxn_str.links:
            cLink = CXN_LINK()
            cLink.parent = link.parent
            cLink.child = link.child
            cLink.SynFormIdx = link.SynFormIdx
            
            self.links.append(cLink)
    
    def readout(self, cxn, act, phon_list, vocal = True):
        """
        Recursively read out the phonological content generated by the cxn str starting 
        from a given cxn inst.
        
        Args:
            - cxn (CXN_INST): The cxn instance form where to start the read out process 
            (use top cxn inst to span the whole structure). 
            Method then called recursively on child cxn instances.
            - act (INT): Value used to reactivate cxn inst and SemRep inst.
            - phon_list ([TP_PHON]): List phonetic content of recursively read out from cxn inst SynForms.
            - vocal (BOOL): If True, read out impacts activations and status flags values of cxn inst and semrep insts.
            
        Returns:
            - Phon_list is modified through the recursive application of method (side effect).
            - Returns None if no emtpy slot is encountered.
            - If an empty slot is encountered, process is interuppted, and a SemRep inst
            that should be but are not covered is returned.
            
        Notes:
            - the SemRep instance returned is the one associate with the first empty slot found.
            
        """
        if(vocal):
            # Reactivate construction instance and its covering SemRep instances
            cxn.Activation(act)
            for i in range(len(cxn.covers)):
                if not(cxn.elems[i].shared):
                    cxn.covers[i].Activation(act)
            
            # Set to old = True for cxn instance and its covering SemRep instances
            cxn.Old(True)
            for i in range(len(cxn.covers)):
                if not(cxn.elems[i].shared):
                    cxn.covers[i].Old(True)
        
        # Read out phonetic notations
        for i in range(len(cxn.base_cxn.SynForm)):
            syn_elem = cxn.base_cxn.SynForm[i]
            if(syn_elem.type == TP_ELEM.PHONETICS):
                # Read out phonetic notation
                phon_list.append(syn_elem)
            else:
                # Retrieve slotted child
                child = self.get_child(cxn, i)
                if child:
                    # Recursively produce utterance
                    unspoken = self.readout(child, act, phon_list, vocal)
                    if unspoken:
                            return unspoken # Production of utterance interrupt
                    
                else:
                    # Retrieve SemRep instance to be spoken next
                    sem_elem = syn_elem.linked_SemElem
                    unspoken = cxn.covers[cxn.base_cxn.SemFrame.index(sem_elem)]
                    return unspoken
        
        return None
                
    ## Class methods ##        
    def conflict(cxn_str1, cxn_str2):
        """
        Check if there is a conflict between two construction structures. Return True if a conflict is found.
        
        Note: Method goes through all the match info data between pairs of instances (i1, i2) in cxn_str1 x cxn_str2.
        """
        if(not(cxn_str1) or not(cxn_str2)):
            return False
        
        # Check conflict between member instances
        for inst1 in cxn_str1.insts:
            for inst2 in cxn_str2.insts:
                temp_info = MATCH_INFO()
                if not(CXN_INST.match(inst1, inst2, temp_info)):
                    return True # conflict exist
        
        return False
    
    def overlap(cxn_str1, cxn_str2):
        """
        Check if two construction structures overlap on the SemRep.. Return True if an overlap is found.
        
        Notes: Method goes through all the match info data between pairs of instances (i1, i2) in cxn_str1 x cxn_str2.
        """
        if(not(cxn_str1) or not(cxn_str2)):
            return False
        
        # Check for overlap between member instances
        for inst1 in cxn_str1.insts:
            for inst2 in cxn_str2.insts:
                temp_info = MATCH_INFO()
                CXN_INST.match(inst1, inst2, temp_info)
                if temp_info.overlap:
                    return True # overlap!
        
        return False
    
    def combine(cxn_str1, cxn_str2):
        """
        Combine two construction structures and spawn a new structure.
        
        Returns:
            - A new construction structure that combines both cxn_str1 and cxn_str2.
            - None if combination fails.
        
        Notes: 
            - Cnx str are combined at the top.
            - The top unit of one cxn str is linked to a compatible empty slot in the top unit of the other.
            - CONDITIONS: Top units match; there is an compatible empty slot; 
            there is no conflict between the two construction structures.
        """
        if(not(cxn_str1) or not(cxn_str2)):
            return None
            
        # Match top instances
        mat_info = MATCH_INFO()
        CXN_INST.match(cxn_str1.top, cxn_str2.top, mat_info)
        if mat_info.match < 1:
            return None # Combination is not possible
        
        # Check slot availability between the two top constructions
        if mat_info.parent == cxn_str1.top:
            links = cxn_str1.links
        else:
            links = cxn_str2.links
        
        for l in links:
            if(l.parent == mat_info.parent and l.SynFormIdx == mat_info.SynFormIdx):
                return None # Link already exists (i.e. slot is not empty)
        
        # Check conflict between member instances
        if CXN_STRUCT.conflict(cxn_str1, cxn_str2):
            return None # Conflict
            
        # Create a new structure
        cxn_str = CXN_STRUCT()
        cxn_str.top = mat_info.parent
        cxn_str.fresh = True
        cxn_str.merge(cxn_str1)
        cxn_str.merge(cxn_str2)
        
        # create link between top instances
        cxn_link = CXN_LINK()
        cxn_link.parent = mat_info.parent
        cxn_link.child = mat_info.child
        cxn_link.SynFormIdx = mat_info.SynFormIdx
        
        cxn_str.links.append(cxn_link)
        
        return cxn_str
###############################################################################
if __name__=='__main__':
    import scene as SCN
    
    s_i = SCHEMA_INST()
    print s_i
    print "id: %i" % s_i.id
    print "type: %i" % s_i.type
    print "activation: %i" % s_i.activation
    print "Fresh Alive Old"
    print s_i.fresh
    print s_i.alive
    print s_i.old
    print "Set all three to True"
    s_i.Alive(True)
    s_i.Fresh(True)
    s_i.Old(True)
    print s_i.fresh
    print s_i.alive
    print s_i.old
    print "Set activation to 10"
    s_i.Activation(10)
    print "activation: %i" %s_i.activation
    print "\n"
    
    o_cpt = CPT.CONCEPT(name = 'Object_CPT_1', meaning = 'ObjectConcept')
    o_rgn = SCN.REGION()
    o_rgn.name = "object region"
    o_schema = SCN.SC_OBJECT()
    o_schema.region = o_rgn
    o_schema.name = "OBJECT_SCHEMA_1"
    o_schema.concept = o_cpt
    
    s_i = SEMREP_INST()
    print s_i
    print "id: %i" % s_i.id
    print "type: %i" % s_i.type
    print "activation: %i" % s_i.activation
    print "Fresh Alive Old"
    print s_i.fresh
    print s_i.alive
    print s_i.old
    print "Set all three to True"
    s_i.Alive(True)
    s_i.Fresh(True)
    s_i.Old(True)
    print s_i.fresh
    print s_i.alive
    print s_i.old
    print "Set activation to 10"
    s_i.Activation(10)
    print "activation: %i" %s_i.activation
    print "schema"
    print s_i.schema
    print "concept"
    print s_i.concept
    print "\n"
    print "Instantiate with object schema"
    s_i.Instantiate(o_schema, 100)
    print "activation: %i" %s_i.activation
    print "schema"
    print s_i.schema
    print "concept"
    print s_i.concept
    
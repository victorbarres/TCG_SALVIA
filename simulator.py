# -*- coding: utf-8 -*-
"""
Created on Fri May 09 13:49:40 2014

@author: Victor Barres

Define the simulator that runs the SemRep/TCG processes for TCG1.0
"""

import concept as CPT
import construction as CXN
import scene as SCN
import instance as INST
import random

class COMP_TRACE:
    """
    Competition trace
    Used by the simulator to keep track of construction instances competition outcomes.
    A comp_trace object is generated after each competition and stored by the simulator.
    
    Data:
        - winner (CXN_INST): winner instance
        - loser (CXN_INST): loser instance
        - winSuit (INT): winer suitability (i.e. suitability of the structure it belongs to)
        - losSuit (INT): loser suitability (i.e. suitability of the structure it belongs to)
    """
    def __init__(self):
        self.winner = None
        self.loser = None
        self.winSuit = 0
        self.losSuit = 0

class SIMULATOR:
    """
    Simulator runs SemRep/TCG processes.
    The simulator needs to be initialized with a grammar, a SemNet (semantic knowledge) and a visual scene.
    Max time, thresholds of utterance values and TCG principles flags also need to be defined.
    
    Simulation is run by successive calls to proceed() method, until a termination condition is met. Each call to proceed() corresponds to
    1 time step.
    
    Data:
        <LONG TERM MEMORY>
        - SemNet (SEM_NET): Semantic network (world knowledge)
        - grammar (GRAMMAR): Grammatical knowledge
        
        <VISUAL INPUT>
        - scene (SCENE): Currently viewed scene
        
        <VISION SYSTEM>
        - atten (REGION): Region currently under attentional focus
        - next_atten (REGION): Next attention focus. Can be either defined based on saliency or based on verbal guidance (see produce_utterance())
        - vis_update (BOOL): Visual update flag
        - per_regions ([REGION]): Already perceived regions
        
        <LANGUAGE SYSTEM>
        - utter (STR): Produced utterance
        - incomp_utter (BOOL): Incomplete utterance flag. True if the last utterance did not cover the whole active SemRep. Trigers the VERBAL GUIDANCE!
        - rd_str (CXN_STRUCT): Last read-out construction structure (useful to implement utterance continuity)
        - rd_phons ([TP_PHON]): Last read-out phonetic notations (useful to implement utterance continuity)
        
        <WORKING MEMORY>
        - instances ([SCHEMA_INST]): All schema instances
        - sem_insts ([SEMREP_INST]): All SemRep instances
        - cxn_insts ([CXN_INST]): All construction instances
        - cxn_strs ([CXN_STRUCT]): All construction structures        
        - comp_traces ([COMP_TRACE]): Competition traces. Keep trace of cxn instances competition results
        
        <SIMULATION PARAMETERS>
        - time (INT):  Current simulation time (in relative unit)
        - max_time (INT): Max simulation duration
        - utter_time (INT): Last utterance production time
        
        <THRESHOLD OF UTTERANCE>
        - thresh_time (INT): Time threshold (-1 for infinity)
        - thresh_cxn (INT): Construction number limit (-1 for infinity)
        - thresh_syll (INT): Syllable length limit (-1 for infinity)
        
        <TCG PRINCIPLE FLAGS>
        - prema_prod (BOOL): Premature production principle
        - utter_cont (BOOL): Utterance continuity principle
        - verb_guide (BOOL): Verbal guidance principle
    """
    def __init__(self):
        self.SemNet = None
        self.grammar = None
        
        self.scene = None
        
        self.atten = None
        self.next_atten = None
        self.vis_update = True
        self.per_regions = []
        
        self.utter = ''
        self.incomp_utter = False
        self.rd_str = INST.CXN_STRUCT()
        self.rd_phons = []
        
        self.instances = []
        self.sem_insts = []
        self.cxn_insts = []
        self.cxn_strs = []
        self.comp_traces =[]
        
        self.time = 0
        self.max_time = 0
        self.utter_time = 0
        
        self.thresh_time = -1
        self.thresh_cxn = -1
        self.thresh_syll= -1
        
        self.prema_prod = True
        self.utter_cont = True
        self.verb_guide = True
    
    def initialize(self, myGrammar, myScene, mySemNet, maxTime, threshTime, threshCxn, threshSyll,
                   premaProd, utterCont, verbGuide, clearData = False):
        """
        Initialize the simulator.
        
        Args:
            - myGrammar (GRAMMAR): A grammatical knowledge
            - myScene (SCENCE): The input scene
            - mySemNet (SEM_NET): The semantic knowledge
            - maxTime (INT): Max simulation duration
            - threshTime (INT): Time threshold (-1 for infinity)
            - threshCxn (INT): Construction number limit (-1 for infinity)
            - threshSyll (INT): Syllable length limit (-1 for infinity)
            - premaProd (BOOL): Premature production principle
            - utterCont (BOOL): Utterance continuity principle
            - verbGuide (BOOL): Verbal guidance principles
            - clearData (BOOL): If True, grammatical knowlegde, semantic knowledge and visual input are cleared.
        """
        self.grammar = myGrammar
        self.scene = myScene
        self.SemNet = mySemNet
        CPT.CONCEPT.SEMANTIC_NETWORK = self.SemNet
        
        self.time = 0
        self.max_time = maxTime
        self.utter_time = self.time
        self.comp_traces = []
        
        self.thresh_time = threshTime
        self.thresh_syll = threshSyll
        self.thresh_cxn = threshCxn
        
        self.prema_prod = premaProd
        self.utter_cont = utterCont
        self.verb_guide = verbGuide
        
        self.atten = None
        self.next_atten = None
        self.vis_update = True
        self.per_regions = []
        
        self.utter = ''
        self.incomp_utter = False
        self.rd_str.clear()
        self.rd_phons = []
        
        self.instances = []
        self.sem_insts = []
        self.cxn_insts = []
        
        if clearData:
            self.SemNet = None
            self.grammar = None
            self.scene = None
        
    ###########################################################################
    # PRIVATE METHODS
    ###########################################################################
    def _randmax(self, i, j):
        if i > j:
            return 0
        elif i < j:
            return 1
        else:
            return random.randint(0,1)
    ###########################################################################
    
    def add_schema_inst(self, sc_inst):
        """
        Add a schema instance to the working memory
        
        Args:
            - sc_inst (SCHEMA_INST)
        """
        
        if not(sc_inst):
            return
        
        if (sc_inst.type == INST.SCHEMA_INST.NODE or sc_inst.type == INST.SCHEMA_INST.RELATION):
            self.instances.append(sc_inst)
            self.sem_insts.append(sc_inst)
        elif (sc_inst.type == INST.SCHEMA_INST.CONSTRUCTION):
            self.instances.append(sc_inst)
            self.cxn_insts.append(sc_inst)
    
    def ellapsed_time(self):
        """
        Maintenance process.
        
        Steps:
            - Set cxn_inst with activity <= 0 to dead
            - Set old cxn_inst to activity = 0 (old means it has been read out)
            - Set cxn_inst to Fresh = False (Fresh only when it has just been invoked)
            - Validate all instances
            - Remove dead instances
            - Advance time
        """
        for sc_inst in self.instances:
            if not(sc_inst.alive):
                continue
            
            # When activation drops to zero, an instance dies
            if (sc_inst.activation <= 0):
                sc_inst.Alive(False)
            
            # When old, activation falls down (to 0)
            if (sc_inst.old):
                sc_inst.activation = 0
                # Employ a more subtle policy later for treating already produced instances
            
            # Not fresh anymore
            sc_inst.Fresh(False)
        
        # Validate all instances (iteratively find dead ones)
        while True:
            someone_died = False
            for sc_inst in self.instances:
                if not(sc_inst.alive):
                    continue
                
                #  Do maintenance
                sc_inst.validate()
                someone_died = someone_died or not(sc_inst.alive)
            if not(someone_died):
                break
        
        # Remove dead instances
        for sc_inst in self.instances[:]:
            if not(sc_inst.alive):
                if(sc_inst in self.sem_insts):
                    self.sem_insts.remove(sc_inst)
                if(sc_inst in self.cxn_insts):
                    self.cxn_insts.remove(sc_inst)
                if(sc_inst in self.rd_str.insts):
                    self.rd_str.insts.remove(sc_inst)
                
                self.instances.remove(sc_inst)
        
        # Advance time
        self.time += 1
                
    ###########################################################################
    def deploy_attention(self):
        """
        Orient attention to most salient scene region and keep it under focus until the region's uncertainty < = 0.
        Include inhibition of return.
        
        This method simulate the effect of (bottom-up) visual saliency on the attention process.
        IMPORTANT: It can be overridden by verbal guidance (see produce_utterance()). If an utterance is produced orematurely while some information is
        still missing that would be needed to complete it, the next attentional region is set to the region that contains the piece of infomration
        needed.
        
        Steps:
            1. Pick most salient region whose uncertainty >=0 (i.e. that has not yet been perceived)
            2. Keep it under attentional focus until it's uncertainty <=0. Decrease uncertainty value by 1 ever time step.
            3. Go back to 1.
        """
        # Visual update
        self.vis_update = True
        
        # Set the current attention focus
        self.atten = self.next_atten
        
        # Inspect region (incrementally reduce uncertainty)
        if (self.atten and self.atten.uncertainty > 0):
            self.atten.uncertainty -= 1
        
        # Find the next target (if no region curently inspected or no uncertainty anymore)
        if (not(self.atten) or self.atten.uncertainty <= 0):
            
            # Saccade to the most salient region
            max_saliency = 0
            for reg in self.scene.regions:
                if reg.uncertainty <= 0:
                    continue # Already inspected, inhibition of return
                
                if self._randmax(max_saliency, reg.saliency) == 1:
                    max_saliency = reg.saliency
                    self.next_atten = reg
            
            if max_saliency <= 0:
                self.vis_update = False # No more region to attend
                self.next_atten = None
                
    ###########################################################################
    def get_semrep_inst(self, schema):
        """
        Look for the SemRep instance linked to a given perceptual schema.
        Return the SemRep instance if it exists, None otherwise.
        """
        for s in self.sem_insts:
            if not(s.alive):
                continue
            if s.schema == schema:
                return s
        return None
    
    def perceive_schema(self, aPercept, new_rels):
        """
        For a given percept, update or create associated SemRep nodes and relations.
        
        Notes:
            - Newly created SemRep relations instances are added to new_rels.
        """
        if not(aPercept):
            return
        # Case: Object percept
        if (aPercept.schema.type == SCN.SCHEMA.OBJECT):
            node = self.get_semrep_inst(aPercept.schema)
            # If there already is a corresponding SemRep node instance -> update
            if node:
                if aPercept.replace_concept:
                    node.Update(aPercept.concept)
                else:
                    node.Update(aPercept.schema.concept)
            # Else, create it.
            else:
                node = INST.NODE_INST()
                node.Instantiate(aPercept.schema, 100)
                if aPercept.replace_concept:
                    node.Update(aPercept.concept)
                
                self.add_schema_inst(node)
        # Case: Relation percept
        if (aPercept.schema.type == SCN.SCHEMA.RELATION):
            relation = self.get_semrep_inst(aPercept.schema)
            # If there already is a corresponding SemRep relation instance -> update
            if relation:
                if aPercept.replace_concept:
                    relation.Update(aPercept.concept)
                else:
                    relation.Update(aPercept.schema.concept)
            # Else, create it
            else:
                relation = INST.REL_INST()
                relation.Instantiate(aPercept.schema, 100)
                if aPercept.replace_concept:
                    relation.Update(aPercept.concept)
                
                self.add_schema_inst(relation)
                new_rels.append(relation)
        
    def perceive_scene(self):
        """
        Perceive all regions that are certain (uncertainty == 0) and set their uncertainty to -1 so that they won't be perceived again.
        """
        new_rels = []
        
        # Reset perceived regions
        self.per_regions = []
        
        # Perceive regions that are certain (uncertainty == 0)
        for rgn in self.scene.regions:
            if rgn.uncertainty == 0:
                # Perceive schemas
                for percept in rgn.percepts:
                    self.perceive_schema(percept, new_rels)
                
                rgn.uncertainty -= 1 # Region won't be perceived anymore
                
                # Append traces for perceived regions
                self.per_regions.append(rgn)
        
        # Establish connection of the newly created SemRep relations
        for rel in new_rels:
            sc_rel = rel.schema
            
            # Connect node instances
            rel.pFrom  = self.get_semrep_inst(sc_rel.pFrom)
            rel.pTo = self.get_semrep_inst(sc_rel.pTo)
            
            # Alive only when the full connection is valid
            if not(rel.pFrom) or not(rel.pTo):
                alive = False
            else:
                alive = True
                
            rel.Alive(alive)
    
    ###########################################################################
    def pair_node(self, node_inst, node_elem, aCxn, attaches):
        """
        WRITE DOCSTRING!!
        """
        idx = 0
        for semrep_inst in attaches:
            if semrep_inst == node_inst:
                return aCxn.SemFrame[idx] == node_elem
            idx += 1
            
        return False
        
    def invoke_cxn_inst(self, aCxn, sf_idx, attaches):
        """
        WRITE DOCSTRING!!
        SUBGRAPH MATCHING ALGORITHM.        
        
        Try to match the SemFrame of a construction onto a SemRep subgraph. If
        success, instantiate construction.
        
        Args:
            - aCxn (CXN): A construction in the grammar.
            - sf_idx (INT): Index of SemFrame element in aCXN.SemFrame.
            - attaches ([SEMREP_INST]): Keeps track of the SemRep instances that have been matched during
            recursive search of matching subgraphs.
        
        Notes:
            - Only instantiates construction that match onto a SemRep sugraph that has
            at least one element alive.
            - Checks that a similar instance doesn't already exist before adding to working
            memory.
            - Algorithm steps:
                - For first element of SemFrame, try to find matching SemRep instance
                - Then recursively try to find matches for other elements of the SemFrame
                - Then check that topology match between SemFrame and list of matching attached SemFrame 
                instances (i.e. check that toplogy match between SemFrame and Attatches)
            - Algorithm comments:
                - This does not make use of the directed graph structure during the first search phase since
                it only checks the topology afterwards.
                - If SemRep = N1 elements, SemFrame = N2 elements, number of test during search = N1^N2 !! + 
                then the cost of the topology checks... this algorithm is clearly NOT optimal, but works for now
                since SemRep and SemFrames are small.
            
            - The matching of concept is very simple here (match or no match).   
        """
        if sf_idx < len(aCxn.SemFrame): # Still some SemFrame elements to process
            sf_elem = aCxn.SemFrame[sf_idx]
            
            # Iterate for all SemRep instances to find a potential match
            for sr_inst in self.sem_insts:
                if not(sr_inst.alive):
                    continue
                
                # Need to have the same type
                if ((sr_inst.type == INST.SCHEMA_INST.NODE and sf_elem.type != CXN.TP_ELEM.NODE) or
                    (sr_inst.type == INST.SCHEMA_INST.RELATION and sf_elem.type != CXN.TP_ELEM.RELATION)):
                    continue
                
                # Check if the SemRep instances has already been matched with another SemFrame element of aCxn
                if (sr_inst in attaches):
                    continue
                
                # Check if concepts match
                if not(CPT.CONCEPT.match(sr_inst.concept, sf_elem.concept)):
                    continue
                
                attaches.append(sr_inst)
                
                # Recursively call function for next SemFrame element of the consrtruction
                self.invoke_cxn_inst(aCxn, sf_idx+1, attaches)
                
                attaches.pop()
        else:
            # Topology check
            fresh = False
            for sr_inst in attaches:
                if sr_inst.fresh: # At least one instance has to be fresh
                    fresh = True
                if sr_inst.type != INST.SCHEMA_INST.RELATION:
                    continue # Only look at relations to determine topology match.
                    
                rel_elem = aCxn.SemFrame[attaches.index(sr_inst)] # SemFrame relation element corresponding to the SemRep relation
                
                if (not self.pair_node(sr_inst.pFrom, rel_elem.pFrom, aCxn, attaches) or
                    not self.pair_node(sr_inst.pTo, rel_elem.pTo, aCxn, attaches)):
                    return # Stop invocation
            
            if not(fresh):
                return # Stop invocation
            
            # Invoke a new construction instance
            new_cxn_inst = INST.CXN_INST()
            new_cxn_inst.instantiate(aCxn, attaches[:], 100)
            
            # Check if there already is an indentical construction instance
            for anInst in self.cxn_insts:
                if not(anInst.alive):
                    continue
                if new_cxn_inst.compare(anInst):
                    return # Identical instance already exists
            
            self.add_schema_inst(new_cxn_inst)
    
    def invoke_constructions(self):
        """
        Invoke all constructions whose SemFrame match SemRep subgraphs (no duplicate).
        """
        attaches = []
        for aCxn in self.grammar.constructions:            
            # Match SemFrame elements of aCxn against SemRep subgraphs.
            self.invoke_cxn_inst(aCxn, 0, attaches)

    ###########################################################################
    def find_cxn_struct(self, cxn_str, cxn_str_list, comp_val):
        """
        WRITE DOCSTRING!!
        """
        for aCxn_str in cxn_str_list:
            if cxn_str == aCxn_str:
                continue
            if cxn_str.compare(aCxn_str) == comp_val:
                return True
        
        return False
    
    def do_cooperation(self):
        """
        WRITE DOCSTRING!!
        """
        # Clear all the previously spawned construction structures
        self.cxn_strs = []
        for cxn_inst in self.cxn_insts:
            cxn_inst.cxn_struct = None
        
        # Initialize construction hiearchy structures, a cxn_str for each alive cxn_inst
        for cxn_inst in self.cxn_insts:
            if not(cxn_inst.alive):
                continue
            # Spawn a new structure
            new_cxn_str = INST.CXN_STRUCT()
            new_cxn_str.create(cxn_inst)
            self.cxn_strs.append(new_cxn_str)
            
        #
        # Cooperation process (iteratively spawn all possible construction structures)
        #
        while True:
            new_structs = []
            for i in range(len(self.cxn_strs)-1):
                cxn_str1 = self.cxn_strs[i]
                for j in range(i+1,len(self.cxn_strs)):
                    cxn_str2 = self.cxn_strs[j]
                    
                    if not(cxn_str1.fresh or cxn_str2.fresh):
                        continue # At least one structure has to be fresh
                    
                    # Try to combine two structures to spawn a new structure
                    new_cxn_str = INST.CXN_STRUCT.combine(cxn_str1, cxn_str2)
                    
                    # Check if there is already an identical structure
                    if(new_cxn_str and 
                        not(self.find_cxn_struct(new_cxn_str, new_structs, 3)) and
                        not(self.find_cxn_struct(new_cxn_str, self.cxn_strs, 3))):
                        new_structs.append(new_cxn_str)
            
            # Reset freshness of structures
            for cxn_str in self.cxn_strs:
                cxn_str.fresh = False
            
            # Add newly spawned structures
            for new_str in new_structs:
                self.cxn_strs.append(new_str)
            
            if not(new_structs):
                break # No more structure spawned                                
                                
    def create_comp_trace(self, winner, loser):
        """
        WRITE DOCSTRING!!
        
        Args:
            - winner (CXN_INST)
            - loser (CXN_INST)
        """
        comp_trace = COMP_TRACE()
        comp_trace.winner = winner
        comp_trace.loser = loser
        comp_trace.winSuit = winner.cxn_struct.suitability
        comp_trace.losSuit = loser.cxn_struct.suitability
        
        self.comp_traces.append(comp_trace)
        
    def do_competition(self):
        """
        WRITE DOCSTRING!!
        """
        # Clear all previous competition traces
        self.comp_traces = []
        
        # Initialize alive construction instances
        alive_insts = []
        for cxn_inst in self.cxn_insts:
            if cxn_inst.alive:
                alive_insts.append(cxn_inst)
        
        #
        # Competition process (even if an instance is dead during competition, it still can kill others)
        #
        for i in range(len(alive_insts)-1):
            cxn_inst1 = alive_insts[i]
            for j in range(i+1,len(alive_insts)):
                cxn_inst2 = alive_insts[j]
                
                mat_info = INST.MATCH_INFO()
                
                if(not(INST.CXN_INST.match(cxn_inst1, cxn_inst2, mat_info)) and
                    cxn_inst1.cxn_struct and
                    cxn_inst2.cxn_struct):
                ###############################################################
                # Alternative version
                ###############################################################
#                INST.CXN_INST.match(cxn_inst1, cxn_inst2, mat_info)
#                if (mat_info.overlap and
#                    cxn_inst1.cxn_struct and
#                    not(cxn_inst1.cxn_struct.check_membership(cxn = cxn_inst2)) and
#                    cxn_str2 and
#                    not(cxn_inst2.cxn_struct.check_membership(cxn = cxn_inst1))):
                ###############################################################    
                    # Do not tie break in order to prevent reciprocal elimination
                    if (cxn_inst1.cxn_struct.suitability > cxn_inst2.cxn_struct.suitability and cxn_inst2.alive):
                        cxn_inst2.Alive(False)
                        self.create_comp_trace(cxn_inst1, cxn_inst2)
                    if (cxn_inst1.cxn_struct.suitability < cxn_inst2.cxn_struct.suitability and cxn_inst1.alive):
                        cxn_inst1.Alive(False)
                        self.create_comp_trace(cxn_inst2, cxn_inst1)
                        
    def process_constructions(self):
        """
        WRITE DOCSTRING!!
        """
        # Cooperation process
        self.do_cooperation()
        
        # Trim obsolete structures (i.e. covering old cxn instances only)
        for cxn_str in self.cxn_strs[:]:
            if cxn_str.check_obsolete():
                self.cxn_strs.remove(cxn_str)
        
        # Trim redundant construction structures
        for cxn_str in self.cxn_strs[:]:
            if(self.find_cxn_struct(cxn_str, self.cxn_strs, 2)): # cxn_str is included in another structure
            
            ###################################################################
            # Alternative version
            ###################################################################
#            if (not(cxn_str.check_complete) and 
#                self.find_cxn_struct(cxn_str, self.cxn_strs, 2)):
            ###################################################################            
                self.cxn_strs.remove(cxn_str)
        
        # Utterance continuity principle
        if self.utter_cont:
            # Adjust suitability
            for cxn_str in self.cxn_strs:
                # Estimate the number of overlapped syntactic components
                overlap = 0
                for cxn_inst in self.rd_str.insts:
                    if cxn_str.check_membership(cxn = cxn_inst):
                        overlap +=1
                for cxn_link in self.rd_str.links:
                    if cxn_str.check_membership(link = cxn_link):
                        overlap +=1
                
                continued = False
                
                if self.rd_str.check_lineage(cxn_str):
                    # Produce subvocal utterace (vocal = False)
                    phons = []
                    cxn_str.readout(cxn_str.top, -1, phons, False)
                    skip = self.match_phon_lists(self.rd_phons, phons)
                    if (len(self.rd_phons) <= 0 or skip > 0): # Check if utterance can be made continuously
                        continued = True

                if continued:
                    # Continuity reward
                    cxn_str.suitability += overlap * INST.CXN_STRUCT.RDD_WEIGHT
                else:
                    # Redundancy penalty
                    cxn_str.suitability -= overlap * INST.CXN_STRUCT.RDD_WEIGHT
        
        # Associate construction instances with structure of maximum suitability
        for cxn_inst in self.cxn_insts:
            if not(cxn_inst.alive):
                continue
            
            for cxn_str in self.cxn_strs:
                if not(cxn_str.check_membership(cxn = cxn_inst)):
                    continue
                
                if (not(cxn_inst.cxn_struct) or
                    self._randmax(cxn_inst.cxn_struct.suitability, cxn_str.suitability) == 1):
                    cxn_inst.cxn_struct = cxn_str
        
        # Competition process
        self.do_competition()
        
        # Invalidate construction structures that contain dead construction instances
        for cxn_str in self.cxn_strs:
            for cxn_inst in self.cxn_insts:
                if cxn_inst.alive:
                    continue
                if cxn_str.check_membership(cxn = cxn_inst):
                    cxn_str.valid = False
            
            
    ###########################################################################
    def match_phon_lists(self, prev_phonlist, next_phonlist):
        """
        Check if there is an i such that prev_phonlist[i:] is a sublist of next_phonlist
        
        Example:
            prev_phonlist = [I, saw, that, the, man, kicks]
            next_phonlist = [The, man, kicks, a, ball]
            Return -> matches = 3, corresponds to index of 'a' in next_phon_list.
            
            prev_phonlist = [I, saw, that, the, man, kicks]
            next_phonlist = [the, man, eats, a, cake]
            Return -> matches = 0, prev_phonlist is not a sublist of next_phonlist.
        
        """
        matches = 0
        for i in range(len(prev_phonlist)):
            for j in range(len(next_phonlist)):
                if i+j <len(prev_phonlist) and prev_phonlist[i+j] == next_phonlist[j]:
                    continue
                elif i+j >= len(prev_phonlist):
                    matches = j
                    break
                else:
                    break
        
        return matches
                
    
    def produce_utterance(self, verbose = True):
        """
        WRITE DOCSTRING!!
        """
        # Reset utterance
        self.utter = ''
        
        # Bypass threshold if no more update from vision or previous utterance was incomplete
        if self.vis_update and not(self.incomp_utter):
            # Calculate the total syllable length
            totLen = 0
            if(self.thresh_syll >=0):
                for cxn_inst in self.cxn_insts:
                    if not(cxn_inst.alive):
                        continue
                    
                    for form_elem in cxn_inst.base_cxn.SynForm:
                        if form_elem.type != CXN.TP_ELEM.SLOT:
                            totLen += len(form_elem.phonetics)
        
            # Check utterance thresholds are reached
            if ((self.thresh_time < 0 or self.thresh_time > (self.time - self.utter_time)) and
                (self.thresh_cxn < 0 or self.thresh_cxn > len(self.cxn_insts)) and
                (self.thresh_syll < 0 or self.thresh_syll > totLen)):
                return # thretholds not reached yet
        
        # Select construction structure to be read out
        select_str = None
        for cxn_str in self.cxn_strs:
            if(not(select_str) or
                self._randmax(select_str.suitability, cxn_str.suitability) == 1):
                    select_str = cxn_str
                    
        
        if not(select_str):
            # Reset utterance variables
            self.incomp_utter = False
            self.rd_phons = []
            self.rd_str.clear()
        else:
            # Read out phonetic notations
            phons = []
            unspoken = select_str.readout(select_str.top, 100, phons)
            
            # Skip previously spoken utterance (only within the same lineage)
            skip = 0
            if self.rd_str.check_lineage(select_str):
                skip = self.match_phon_lists(self.rd_phons, phons)
            
            # reset utterance variables
            self.incomp_utter = False
            self.utter_time = self.time
            self.rd_phons = phons[:]
            self.rd_str.clear()
            self.rd_str.top = select_str.top
            self.rd_str.merge(select_str)
            
            # If there are unspoken elements, verbal guidance and premature production kick in.
            if unspoken:
                self.incomp_utter = True
                
                # Verbal guidance principle
                if self.verb_guide:
                    rgn = unspoken.schema.region
                    if rgn.uncertainty>0:
                        self.next_atten = rgn # Sets the next attentional focus.
                
                # Premature production principle
                if not(self.prema_prod):
                    if not(select_str.check_complete()):
                        self.rd_phons = [] # If the structure is not complete and no premature prod -> do not utter anything.
            
            # Render utterance.
            if verbose: # Adding the already uttered part in parenthesis
                if skip > 0:
                    self.utter += '('
                    for p in range(skip):
                        if p > 0:
                            self.utter += ' '
                        self.utter += self.rd_phons[p].phonetics
                    self.utter += ')'
            for p in range(skip, len(self.rd_phons)):
                phon = self.rd_phons[p].phonetics
                if (phon[0] != '-' and len(self.utter)>0 and self.utter[-1] != '-'):
                    self.utter += ' '
                self.utter += phon
            
            # Append prolonged pause
            if (unspoken and len(self.utter) > 0):
                self.utter += '...' # Incomplete utterance
            
            # Append verbalized pause when nothing to produce
            if len(self.utter) <= 0:
                self.utter += 'uh...'
    ###########################################################################
    # PUBLIC METHODS
    ###########################################################################
    def proceed(self, verbose = True):
        """
        WRITE DOCSTRING!!
        """
        if (self.time >= self.max_time):
            return False
        
        INST.SCHEMA_INST.inst_activity = False
        
        # Maintenance processes
        self.ellapsed_time()
        
        # Vision processes
        self.deploy_attention()
        self.perceive_scene()
        
        # TCG processes
        self.invoke_constructions()

        self.process_constructions()
        
        # Utterance processes
        self.produce_utterance(verbose = True)
        
        return (INST.SCHEMA_INST.inst_activity or self.vis_update)
    
###############################################################################

if __name__=='__main__':
    print "No test case implemented"
    
        
        
        
        
    

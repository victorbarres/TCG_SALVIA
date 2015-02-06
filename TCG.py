# -*- coding: utf-8 -*-
"""
Created on Tue May 13 15:02:26 2014

@author: Victor Barres

Define main() function and output printing functions for TCG1.0
"""
import sys

import loader as LD
import simulator as SIM
import instance as INST
import construction as CXN

TCG_ABOUT = "Template Construction Grammar (TCG) Simulator v1.0\n\
\n\
Victor Barres (barres@usc.edu) May 14. 2014\n\
USC Brain Project and  Neuroscience Graduate Program\n\
University of Southern California (USC)\n\
[PYTHON reimplementation of C++ code:\n\
\tTemplate Construction Grammar (TCG) Simulator v2.5\n\
\tJinyong Lee (jinyongl@usc.edu), June 23. 2012\n\
\tUSC Brain Project, Computer Science Department\n\
\tUniversity of Southern California (USC)]\n"


def print_inst_status(sc_inst):
    """
    Print status of schema instance
        ! = Fresh, the instance was just invoked.
        X = Dead, the instance will be pruned out of the working memory next time step.
        x = Alive instance with activation < 0
        O = Alive instance with activation > 0 and not Old (Basic status of active instances)
        @ = Alive instance with activation > 0 and Old -> The Old flag means that the instance has already been used for read-out.
    """
    p = ''
    p += "["
    if sc_inst.fresh:
        p += "!"
    else:
        p += " "
    if not(sc_inst.alive):
        p += "X"
    else:
        if sc_inst.activation>0:
            if sc_inst.old:
                p += "@"
            else:
                p += "O"
        else:
            p +="x"
    p += "] "
    return p

def print_struct_status(cxn_str, rd_str):
    """
    Print status of construction structure (cxn_str) with respect to the structure that is used for read out (rd_str)
        * = This is the cxn_str used for production
        X = The structure is not Valid (contains dead instances).
    """
    p = '['
    if cxn_str.valid:
        if rd_str.compare(cxn_str) == 3:
            p += "*"
        else:
            p += " "
    else:
        p += "X"
    p += "] "
    p += str(cxn_str.suitability) + ": "
    return p

def print_semrep_inst(sr_inst):
    """
    Print SemRep instance as MEANINING_ID
    """
    p = ''
#    p += str(sr_inst.schema.name)
    p += str(sr_inst.concept.meaning)
    p += "_" + str(sr_inst.id)
    return p
    
def print_cxn_inst(cxn_inst):
    """
    Print construction instance as BASE-CXN-NAME_ID
    """
    p = ''
    p += str(cxn_inst.base_cxn.name)
    p += "_" + str(cxn_inst.id)
    return p
    
def print_cxn_struct(cxn_str, cxn_inst, recursive = True):
    """
    Print construction structure (cxn_str) starting from a given construction instance (cxn_inst) (usually Top instance).
    If recursive = True, recursively print sub-structures.
    """
    p = ''    
    if recursive:
        p += "%s " % print_cxn_inst(cxn_inst)
    
    for i in range(len(cxn_inst.base_cxn.SynForm)):
        TpSynElem = cxn_inst.base_cxn.SynForm[i]
        if TpSynElem.type != CXN.TP_ELEM.SLOT:
            p += "'%s'" % TpSynElem.phonetics
        else:
            p += "["
            if cxn_str:
                child = cxn_str.get_child(cxn_inst, i)
            else:
                child = None
            
            if child:
                if recursive:
                    p += print_cxn_struct(cxn_str, child, recursive)
                else:
                    p +=  print_cxn_inst(child)
            else:
                p += " "
            p += "]"
        if i < (len(cxn_inst.base_cxn.SynForm) -1):
            p += " "
    
    return p
    
def print_region(rgn):
    """
    Print regions (rgn) including the amount of uncertainty left.
    """
    p = ''
    if(rgn):
        p += rgn.name
        if rgn.uncertainty > 0:
            p += " (uncertainty left: %i)" % rgn.uncertainty
        else:
            p += " (perception done)"
    else:
        p += "None"
    p += "\n"
    return p

def print_current_state(sim):
    """
    Print the current simulator state.
    """
    p = ''
    p += ''.join(["=" for i in range(80)]) + "\n"
    p += " Simulation Time: %i\n" % sim.time
    p += ''.join(["=" for i in range(80)]) + "\n"
    
    p += "> Current Attention\n"
    p += "  %s\n" % print_region(sim.atten)
    
    if len(sim.per_regions) > 0:
        p += "> Perceived Regions\n"
        p += "  "
        for rgn in sim.per_regions:
            if sim.per_regions.index(rgn) > 0:
                p += ", "
            p += rgn.name
        p += "\n\n"
    
    if len(sim.instances) > 0:
        p += "> Schema Instances\n"
        for sc_inst in sim.instances:
            p += print_inst_status(sc_inst)
            
            if sc_inst.type == INST.SCHEMA_INST.NODE:
                p += "SemRep-N "
                p += "%s\n" % print_semrep_inst(sc_inst)
            
            elif sc_inst.type == INST.SCHEMA_INST.RELATION:
                p += "SemRep-R "
                p += print_semrep_inst(sc_inst)
                p += " from "
                if sc_inst.pFrom:
                    p += print_semrep_inst(sc_inst.pFrom)
                else:
                    p += "??"
                p += " to "
                if sc_inst.pTo:
                    p += print_semrep_inst(sc_inst.pTo)
                else:
                    p += "??"
                p += "\n"
            
            elif sc_inst.type == INST.SCHEMA_INST.CONSTRUCTION:
                p += "Construction "
                p += print_cxn_inst(sc_inst)
                p += " covering "
                for i in range(len(sc_inst.covers)):
                    p += print_semrep_inst(sc_inst.covers[i])
                    p += " "
                p += "for %s\n" % print_cxn_struct(sc_inst.cxn_struct, sc_inst, False)
            
        p += "\n"
    
    if len(sim.comp_traces) > 0:
        p += "> Competition traces\n"
        for comp_tr in sim.comp_traces:
            p += "  %s (%i) " % (print_cxn_inst(comp_tr.winner), comp_tr.winSuit)
            p += "eliminated %s (%i)\n" % (print_cxn_inst(comp_tr.loser), comp_tr.losSuit)
        
        p += "\n"
    
    if len(sim.cxn_strs) > 0:
        p += "> Construction Structures\n"
        for cxn_str in sim.cxn_strs:
            p += print_struct_status(cxn_str, sim.rd_str)
            p += print_cxn_struct(cxn_str, cxn_str.top, True)
            p += "\n"
        p += "\n"
    
    if len(sim.utter) > 0:
        p += "> Produced Utterance\n"
        p += "'%s'\n\n" % sim.utter
        
    p += "> Next Attention\n"
    p += "  %s\n" % print_region(sim.next_atten)
    return p

def load_init_file(file_name, sim):
    """
    Load intialization file and initialize simulator (sim).
    
    Args:
        - file_name (STR): initialization file name (.ini file)
        - sim (SIMULATOR): simulator to initialize.
    """
    p = ''
    p += "Loading Initialization File '%s' ...\n" % file_name
    
    try:
        f = open(file_name, 'r')
    except:
        p += "\nFailed to open file '%s'.\n" % file_name
        return (False, p)
    
    f_content = f.read()
    f.close()
    f_data = f_content.splitlines()
    
    fields = {'semantics file':'', 'grammar file':'', 'scene file':'', 
              'threshold time':-1, 'threshold constructions':-1, 
              'threshold syllables':-1, 'premature production':1,
              'utterance continuity':1, 'verbal guidance':1, 'max time':100}

    comment_sign = '#'
    
    for line in f_data:
        if not(line) or line[0] == comment_sign:
            continue
        
        line_data = [t.strip() for t in line.split('=')]
        
        if len(line_data) != 2:
            p += "\nInvalid command line: %s\n" % line
            return (False, p)
        
        key_word = line_data[0]
        default_value = fields.get(key_word)
        if default_value == None:
            p += "\nInvalid command line: %s\n" % line
            return (False, p)
        
        fields[key_word] = line_data[1]
    
    if not(fields['semantics file'] and fields['grammar file'] and fields['scene file']):
        p += "\nInput file name missing.\n"
        return (False, p)
    
    lod = LD.LOADER()
    
    okay = False
    p += "Loading Semantic Network '%s'...\n" % fields['semantics file']
    mySemNet = lod.load_SemNet(fields['semantics file'])
    if mySemNet:
        p += "Loading TCG Grammar '%s'...\n" % fields['grammar file']
        myGrammar = lod.load_grammar(fields['grammar file'])
        if myGrammar:
            p += "Loading TCG Scene '%s'...\n" % fields['scene file']
            myScene = lod.load_scene(fields['scene file'])
            if myScene:
                okay = True
    
    if not(okay):
        p += "LOADER ERROR"
        return (False, p)
    
    # Initialize simulator
    p += "\nInitializing Simulator...\n"
    
    try:
        max_time = int(fields['max time'])
        thresh_time = int(fields['threshold time'])
        thresh_cxn = int(fields['threshold constructions'])
        thresh_syll = int(fields['threshold syllables'])
        prem_prod = bool(int(fields['premature production']))
        utter_cont = bool(int(fields['utterance continuity']))
        verb_guide = bool(int(fields['verbal guidance']))
    except:
        p += "\nInvalid simulator parameter.\n"
        return (False, p)
    
    sim.initialize(myGrammar, myScene, mySemNet, max_time, thresh_time, thresh_cxn, thresh_syll, prem_prod, utter_cont, verb_guide)
                   
    p += "- Max Simulation Time : %i\n" % sim.max_time
    p += "- Premature Production : %s\n" % sim.prema_prod
    p += "- Utterance Continuity : %s\n" % sim.utter_cont
    p += "- Verbal Guidance : %s\n" % sim.verb_guide
    p += "- Threshold of Utterance : "
    t = ['', '', '']
    i = 0
    for val in [sim.thresh_time, sim.thresh_cxn, sim.thresh_syll]:
        if val < 0:
            t[i] = 'infinite'
        else:
            t[i] = str(val)
        
        i +=1
    p += "Time = %s, CXNs = %s, Syllables = %s\n" % (t[0], t[1], t[2])
    
    return (True, p)

def main():
    """
    Run simulation
    """
    p = ''
    p += "\n%s\n" % TCG_ABOUT
    if len(sys.argv) != 2:
        p += "Usage: python TCG.py [file.ini]\n"
        return p
    
    # Initialization
    mySim = SIM.SIMULATOR()
    
    # Load init file
    load_res = load_init_file(sys.argv[1], mySim)
    print load_res[1]
    p += load_res[1]
    flag = load_res[0]
    if not(flag):
        return p
    
    # Simulation
    p += "\nBeginning Simulation...\n"
    while (mySim.proceed(verbose = False)):
        state_report = print_current_state(mySim)
        print state_report
        p += state_report
    
    p += "\nSimulation complete: "
    if mySim.time < mySim.max_time:
        p += "inactivity termination."
    else:
        p += "max time reached."
    p += "\n"
    
    return p
    
if __name__=='__main__':
    out = main()
#    f = open('output.txt', 'w')
#    f.write(out)
#    f.close()


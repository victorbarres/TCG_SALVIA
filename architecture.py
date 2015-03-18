# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:49:39 2015

@author: Victor Barres
Model architecture
"""
import schema_theory as st
import brain_system as bs

### Brain system ###
my_system = bs.SYSTEM('TCG Production Brain System')

### Working memories modules and schemas ###
visual_WM_mod = bs.MODULE('visualWM')
visual_WM = st.PROCEDURAL_SCHEMA(name='visualWM')
visual_WM_mod.set_function(visual_WM)

semantic_WM_mod = bs.MODULE('SemanticWM')
semantic_WM = st.PROCEDURAL_SCHEMA(name='SemanticWM')
semantic_WM_mod.set_function(semantic_WM)

grammatical_WM_mod = bs.MODULE('GrammaticalWM')
grammatical_WM = st.WM(name='GrammaticalWM')
grammatical_WM_mod.set_function(grammatical_WM)

phon_WM_mod = bs.MODULE('PhonologicalWM')
phon_WM = st.PROCEDURAL_SCHEMA(name='PhonologicalWM')
phon_WM_mod.set_function(phon_WM)

my_system.add_modules([visual_WM_mod, semantic_WM_mod, grammatical_WM_mod, phon_WM_mod])

my_system.connect(visual_WM_mod, semantic_WM_mod)
my_system.connect(semantic_WM_mod, grammatical_WM_mod)
my_system.connect(grammatical_WM_mod, phon_WM_mod)

### Long term memories modules and schemas ###
grammatical_LTM_mod = bs.MODULE('GrammaticalLTM')
grammatical_LTM = st.LTM(name='GrammaticalLTM')
grammatical_LTM.set_WM(grammatical_WM)
grammatical_LTM_mod.set_function(grammatical_LTM)

wk_LTM_mod = bs.MODULE('WorldKowledgeLTM')
wk_LTM = st.PROCEDURAL_SCHEMA(name='WorldKnowledgeLTM')
wk_LTM_mod.set_function(wk_LTM)




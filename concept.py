# -*- coding: utf-8 -*-
"""
@author: Victor Barres

Define semantic network related classes for TCG.
"""
from __future__ import division
from knowledge_rep import K_ENT, K_REL, K_NET, FRAME

class CONCEPT(K_ENT):
    """
    Conceptual knowledge entity
    
    Data:
        - id (INT): Unique identifier of the entity.
        - meaning (STR): Meaning associated with the semantic entity. A string for now.
        - conceptual_knowledge (CONCEPTUAL_KNOWLEDGE): The conceptual knowledge instance the concept is part of.

    """
    CONCEPTUAL_KNOWLEDGE= None  
    def __init__(self, name='',  meaning='', conceptual_knowledge=None):
        K_ENT.__init__(self, name=name, meaning=meaning)
        self.conceptual_knowledge = conceptual_knowledge
    
    def match(self, cpt, match_type = "is_a"):
        """
        Check if it matches cpt. 
        Uses CONCEPTUAL_KNOWLEDGE.match() method.
            Type = "is_a":  concept1 matches concept2 if concept1 is a hyponym of concept2 (or equal to concept2)
            Type = "equal": concept1 matches concept2 if concept1 is equal to concept2.
        """
        if self.conceptual_knowledge:
            return self.conceptual_knowledge.match(self, cpt, match_type)
        else:
            print "ERROR: The concept is not linked to any conceptual knowledge."
    
    def similarity(self, cpt):
        """
        Returns a similarity score with cpt.
        Uses CONCEPTUAL_KNOWLEDGE.similarity() method.
        """
        if self.conceptual_knowledge:
            return self.conceptual_knowledge.similarity(self ,cpt)
        else:
            print "ERROR: The concept is not linked to any conceptual knowledge."
    
class SEM_REL(K_REL):
    """
    Semantic relation between concept
    
    Data:
        - type (STR): Type of relation.
        - pFrom (CONCEPT):  Source concept.
        - pTo (CONCEPT): Target concept.
    
    Note: ONLY is_a IMPLEMENTED FOR NOW.
    """    
    def __init__(self, aType = 'UNDEFINED', from_cpt = None, to_cpt = None):
        K_REL.__init__(self,aType = aType, from_ent=from_cpt, to_ent = to_cpt)


class CONCEPTUAL_KNOWLEDGE(K_NET):
    """
    Conceptual knowledge. Implemented as a semantic network.
    
    Data(inherited):
        - nodes ([CONCEPT]): List of concepts.
        - edges ([SEM_REL]): List of semantic relations.
        - graph (networkx.DiGraph): A NetworkX implementation of the semantic net.
            Each node has an additional attributes meaning = concept.meaning
            Each edge has an additional attribute type = sem_rel.type
    
    Data:
        - neutral (CONCEPT): A neutral concept that is similar to to and matches any concept.
    
    """
    NEUTRAL_CONCEPT = "?"
    
    def __init__(self, nodes=[], edges=[]):
        K_NET.__init__(self, nodes=nodes[:], edges=edges[:])
        self.neutral = None
        self._set_neutral(CONCEPTUAL_KNOWLEDGE.NEUTRAL_CONCEPT)
        
    def _set_neutral(self, val=None):
        """
        Set the meaning and name of the neutral element to val.
        The neutral element in the CONCEPTUAL_KNOWLEDGE is such that it is similar to and matches every other element in the network.
        Args:
            - val (STR): The arbitrary value of the neutral element.
            
        Note:
            - In the contex of subsumption network, I could define the neutral element as the bottom of the inverted tree.
            Note however, that this would lead to a different treatment in terms of similarity based on distances.
        """
        self.neutral = CONCEPT(name=val, meaning=val, conceptual_knowledge=self)
        self.nodes.append(self.neutral)
    
    def add_ent(self, concept):
        """
        Adds a concept to the the conceptual knowlege while also linking the conceptual knowledge back to the concept.
        """
        flag  = super(CONCEPTUAL_KNOWLEDGE, self).add_ent(concept)
        if flag:
            concept.conceptual_knowledge = self
        return flag
       
    def concepts(self):
        """
        Returns all the concepts
        """
        return self.nodes
    
    def has_concept(self, concept_name):
        """
        Returns concept iff there is a concept with name "name".
        
        Args:
            - concept_name (STR):
        """
        return self._has_entity(concept_name)
        
    def find_meaning(self, meaning):
        """
        Find concept with meaning "meaning". Returns the concept if found, else returns None.
        
        Args:
            - meaning (): Meaning of a concept
        """
        return super(CONCEPTUAL_KNOWLEDGE, self).find_meaning(meaning)
                     
    def similarity(self, cpt1, cpt2):
        """
        Returns a similarity score between cpt1 and cpt2.
        Uses path similarity.
        Args:
            - cpt1 (CONCEPT):
            - cpt2 (CONCEPT):
        
        Examples for is-a taxonomy (e.g. Wordnet):
            Path similarity: 1/(L+1), L=shortest path distance
            Leackock-Chodrow Similarity: -log(L/2*D) where L=shortest path length, D=taxonomy depth
            Wu-Palmer Similarlity: 2*depth(lcs)/(depth(s1) + depth(s2)), lcs = Least Common Subsumer.
            Resnik Similarity (Corpus dependent): IC(lcs)
            Lin Similarity (Corpus dependent): 2*IC(lcs)/(IC(s1) + IC(s2))
            Jiang & Conrath Similarity:  1/jcn_distance, jcn_distance =  IC(concept1) + IC(concept2) - 2 * IC(lcs). 
            See: http://maraca.d.umn.edu/umls_similarity/similarity_measures.html
        Note:
            - ONLY PATH SIMILARITY IMPLEMENTED
            - Question: What does it mean how similar is DOG to ANIMAL? Using path lengths, DALMATIAN being an hyponym of DOG, is necessarily less similar to ANIMAL than DOG...
        """
        # First check if one of the concept is the neutral element.
        if self.neutral and ((cpt1 == self.neutral) or (cpt2 == self.neutral)):
            sim = 1
            return sim
            
        return super(CONCEPTUAL_KNOWLEDGE, self).similarity(cpt1, cpt2)        
    
    def match(self, cpt1, cpt2, match_type = "is_a"):
        """        
        Check if cpt1 matches cpt2. 
        Type = "is_a":  cpt1 matches cpt2 if cpt2 is a hyponym of cpt2 (or equal to cpt2)
        Type = "equal": cpt1 matches cpt2 iff cpt1 is equal to cpt2.
        
        Args:
            - cpt1 (CONCEPT)
            - cpt2 (CONCEPT)
            - match_type (STR): "is_a" or "equal"
        
        Notes:
            - In the currrent version matching is boolean. No impact of distance on similarity.
            See similarity()
        
        """
        # First check if one of the concept is the neutral element.
        if self.neutral and ((cpt1 == self.neutral) or (cpt2 == self.neutral)):
            return True
            
        return super(CONCEPTUAL_KNOWLEDGE, self).match(cpt1, cpt2, match_type = match_type)

###############################################################################
if __name__=='__main__':
    import viewer # I have a bug in the module loading (circularity). This is a cheap hack to make it work for now.
    from loader import TCG_LOADER
    my_conceptual_knowledge = TCG_LOADER.load_conceptual_knowledge("TCG_semantics.json", "./data/semantics/")
    clothing = my_conceptual_knowledge.find_meaning('CLOTHING')
    dress =  my_conceptual_knowledge.find_meaning('DRESS')
    print dress.match(clothing)
    
    color = my_conceptual_knowledge.find_meaning('COLOR')
    blue =  my_conceptual_knowledge.find_meaning('BLUE')
    print blue.match(color)
    
    human = my_conceptual_knowledge.find_meaning('HUMAN')
    woman =  my_conceptual_knowledge.find_meaning('WOMAN')
    obj=  my_conceptual_knowledge.find_meaning('OBJECT')
    print woman.match(human)
    
    clothing = my_conceptual_knowledge.find_meaning('CLOTHING')
    neutral =  my_conceptual_knowledge.find_meaning('?')
    print clothing.match(neutral)
    print neutral.match(clothing)
    

    
    
    
    
    
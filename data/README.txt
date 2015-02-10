Victor Barres
TCG1.1

TCG GRAMMAR: 

1. Construction are rewritten as JSON objects.

2. In the new JSON format, the definitions is more verbose but clearer and similar to a feature-structure definition.
	- Features: Name, Class, Preference, SemFrame, SynForm, SymLinks.
	With all those elements themeself feature structure or arrays of FS.
	The SemFrame is now defined more directly as a graph separating nodes and edges. 
		The clarity gained with respect to graph definition is in a way counterbalanced by the 
		lack of semantic transparency (in TCG1.0 the edges belonging to a predicate can be kept near 
		the predicate...).
	The SynForm is defined as an array of element of type SLOT or PHON.
	SymLinks are clearly defined as a set of relations between nodes and slots (partial function).

3. JSON validation schema for constructions defined in "cxn_schema.json"
	TO DO -> FINISH VALIDATION SCHEMAS!

4. The phon feature of a PHON SynForm element of a construction might be better defined as an ARRAY of PHONEMES or SYLLABLES 
	so that the length of an utterance can be easily captured.

5. The preference feature for a construction is currently left optional (not all constructions have it). 
	In TCG1.0 it is used to indicate the preference for some constructions over others in calculating suitability. 
	It is set to 0 if not defined. I suggest that this should be a value assigned to the schema (participating in the initial activation 
		level for an instance in addition with the quality of match).
	Later work will need to address how to better structure the grammatical LTM and have the preference and network weights adapt through use.

TCG SEMANTICS:

1. The semantic knowledge is rewritten in JSON format. This can keep the input in a form very close to that of TCG1.0.

2. The main issue is that of how the knowledge should be devided.
	"SEMANTIC RELATION" are SemRep related knowledge ie what are the type of relations used in SemRep. 
		It is used to match edge "concept" as this is called in TCG1.0: the type of semantic relations need to match during the invocation of a construction. I don't think that edges can match if they are in any other relations than symbolic equality (has to be a perfect match).
	"ENTITY" are object related conceptual knowledge. This is a part of the WK as conceptual knowledge.
	"ACTION" is a bit awkward since it defines simply two conceptal classes: TRANSITIVE and INTRANSITIVE actions.
		It is an important question to decide what type of knowledge this is. 
		If it is linguistic knowledge, then this is a classic subcategorization of verbs. 
		If it is action WK knowledge, is there a basis to suggest that transitive and intransitive are the right of classifying?
	"PROPERTY" this is fine. Note however that none of the properties are used to actually define elements of the ENTITY ontology (ie: SKY is BLUE etc..)!
		If the relations like "IN" are only defined in SEMANTIC RELATIONS then relations are missing from conceptual WK. 
		Think about VISION system: it would be nice to be able to express things like SKY is above things, HUMAN have HANDS etc...

3. In SandBox/TestWorldKnowledge I show how NetworkX can be used to implement WK as actual graph allowing for 
	fast computation of things like: is_ascendant, is_descendant, distance between nodes (possibly weighted by edges weights) etc..

4. It might be worth adding distinctions between: perceptual knowledge, conceptual knowledge, event knowledge [scripts/schemas]... 
	This will play a role in TCG comprehension.

5. For TCG comprehension, I would need a simple inference system: Bayesian net or something like that.

N. go back to my quals and look at WK models in TD attention systems.

TCG SCENE:

1. A scene input is now also defined as a JSON object.

2. At the highest level, a scene JSON object contains the fields:
	- image -> Provides the file name for the scene image.
	- Resolution
	- and a array of region JSON objects.

3. region JSON objects are defined by:
	- A name
	- a location (x,y)
	- A size (w,l)
	- A saliency
	- An uncertainty
	- A list of schemas that are perceived when the attention is focused on the region
		Each schema can be either of OBJ or REL type -> define a graph
	- A perceive array listing all the schemas that are perceived
	- An optional update field defining a dict type indicating how schemas should be updated.



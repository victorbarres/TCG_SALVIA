Date: 2014_04_28
Author: Victor Barres
Email: barres@usc.edu
University of Southern California
USC Brain Project and USC Neuroscience

Template Construction Grammar 1.1

TCG 1.1 extends TCG1.0

Main changes:
- JSON input and output format
	All inputs (grammar, scenes, world knowledge) are now encoded in json.
	The loader is much simpler than the TCG1.0 version.
	-> New versions of TCG.py and loader.py

- Viewer
	An HTML/javascript viewer is added to display the output of the model.
	The viewer runs in the browser.
	To see output of computation: localhost:8080

#############
### TO DO ###

- Make sure all the scenes are available in json format.


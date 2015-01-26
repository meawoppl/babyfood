babyfood
========

[![Build Status](https://travis-ci.org/meawoppl/babyfood.svg?branch=master)](https://travis-ci.org/meawoppl/babyfood)

Tools for the generation of Printed Circuit Boards (PCBs).  This includes 
primitives for gerber, and XLN Drill files.  

There are several submodules:

1. io - Basic input/output of file formats.
2. layers - anything that can be though of in 2d, currently supports:
 1. Gerber Layer 
 2. Drill Layer (xln format)
 3. Cairo layer (coming soon!)
 4. Shapely layer (coming soon!)
3. features - Graphical elements that span one or more layers including:
 1. Pads (square/round)
 2. Via's
 3. JDEC Package footprints (coming soon)
4. components - Elements that have both a graphical rep and some other things
 1. SMA resistors
 2. Some LED's

Coming soon
===========

1. Design rules
2. IPC Compliant footprints
3. Design optimization

GerberWriter Limitations:

1. Does not check polygon legitimacy (complicated!)
2. Does not check for polygon closure wrt. to file precision, only exact values

Next steps:
===========

1. Adding examples to the testing process.  
2. Shapely layer.  Used to do DRU checks.
3. Cairo layer.  Use for visualization.
4. Dumb route generation approach
5. Work out of tiny-turtle PCB and test fab runs!

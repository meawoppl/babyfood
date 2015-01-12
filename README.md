babyfood
========

[![Build Status](https://travis-ci.org/meawoppl/babyfood.svg?branch=master)](https://travis-ci.org/meawoppl/babyfood)

Tools for the generation of Gerber files.  XLN Drill files, and 
PCB's based on these primitives.  

Coming soon:

1. Design rules
2. IPC Compliant footprints
3. Design optimization

GerberWriter Limitations:

1. Does not check polygon legitimacy (complicated!)
2. Does not check for polygon closure wrt. to file precision, only exact values

Next steps:

1. Testing gerber/drill for proper behavior with united calls
2. Adding examples to the testing process.  
3. Shapely layer.  Used to do DRU checks.
4. Cairo layer.  Use for visualization.
5. Dumb route generation approach
6. Work out of tiny-turtle PCB and test fab runs!

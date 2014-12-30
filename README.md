babyfood
========

[![Build Status](https://travis-ci.org/meawoppl/babyfood.svg?branch=master)](https://travis-ci.org/meawoppl/babyfood)

Tools for the generation of Gerber files.  XLN Drill files, and 
PCB's based on these primitives.  

Coming soon:

1. Cascading features
2. Design rules
3. IPC Compliant footprints
4. Design optimization

GerberWriter Limitations:
1. Does not check polygon legitimacy
2. Does not check aperature sizing
3. Does not check for poly closure wrt. to file precision
4. Non circular aperatures are not supported

DrillWriter Limitations:
1. Only capable of generating "plated slots"
2. Has no idea of "tool library" counts on mfg to fit tools to holes.
#!/usr/local/bin/python
#
# execute program
#
# jan@uwinloc.com   
#

import sys
from myhdl import *
import json

import conf

from proc import bench

# read file
with open(sys.argv[1]) as f:
    (labels,prog) = json.load(f)

print prog

# execute
tb = traceSignals(bench, prog)
sim = Simulation(tb)
sim.run(50000)


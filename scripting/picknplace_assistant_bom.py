#!/usr/bin/python2
"""
    @package
    Run kicad_picknplace_assistant.py as a bom plugin to get
    a netlist with DNP info.

    Command line:
    python "pathToFile/picknplace_assistant_bom.py" "%I" "%O"
"""

import argparse
import kicad_picknplace_assistant
from collections import OrderedDict
import pcbnew
import os

parser = argparse.ArgumentParser(
    description='KiCad PCB pick and place assistant')
parser.add_argument('NETLIST', type=str, help="XML BOM")
parser.add_argument(
    '-s',
    '--side',
    choices=kicad_picknplace_assistant.layerchoices,
    default="top",
    help="Board side (default top)")
parser.add_argument('OUTPUT', type=str, help="Output Prefix")

args = parser.parse_args()

args.side = kicad_picknplace_assistant.layerchoices[args.side]

pcbfile = os.path.splitext(args.NETLIST)[0] + ".kicad_pcb"
sidename = "top" if args.side == pcbnew.F_Cu else "bottom"
outfile = args.OUTPUT + "_place_" + sidename + ".pdf"

kicad_picknplace_assistant.process(pcbfile, args.side, args.NETLIST, outfile)
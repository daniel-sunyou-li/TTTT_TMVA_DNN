#!/usr/bin/env python

import os, sys, glob
from argparse import ArgumentParser
import numpy as np
from ROOT import TMVA, TFile
from array import array
from json import loads as load_json
import varsList

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# read in arguments
parser = ArgumentParser()
parser.add_argument("-i","--inputDir",required=True)
parser.add_argument("-f","--fileName",required=True)
parser.add_argument("-o","--outName",required=True)

args = parser.parse_args()

# load json parameters file
jsonFile = None
jsonCheck = glob.glob("parameters*.json")
if len(jsonCheck) > 0:
    jsonFile = open(jsonCheck[0])
    jsonFile = load_json(jsonFile.read())
    
variables = jsonFile[list(jsonFile.keys())[0]]["parameters"]["variables"]

inputDir = args.inputDir
fileName = args.fileName
outName  = args.outName

reader = TMVA.Reader("Color:!Silent")

file = TFile.Open(inputDir + "/" + fileName)
tree = file.Get("ljmet")

branches = {}

for var in varsList.varList["DNN"]:
    if var[0] in variables:
        branches[var[0]] = array( "f", [-999] )
        reader.AddVariable( var[0], branches[var[0]] )
        tree.SetBranchAddress( var[0], branches[var[0]] )

out = TFile( outName, "RECREATE" );
out.cd()
new_tree = tree.CloneTree(0);

DNN_disc = array("f", [0])
new_tree.Branch( "DNN_disc", DNN_disc, "DNN_disc/F" );

reader.BookMVA( "PyKeras", TString("weights.xml") )

for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    DNN_disc[0] = reader.EvaluateMVA( "PyKeras" )
    new_tree.Fill()
    
new_tree.Write()
out.Close()
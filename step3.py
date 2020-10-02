#!/usr/bin/env python

import os, sys, glob
from argparse import ArgumentParser
import numpy as np
from ROOT import TFile, TTree
from array import array
from json import loads as load_json
import os, sys

os.environ["KERAS_BACKEND"] = "tensorflow"

import keras
import varsList

# read in arguments
parser = ArgumentParser()
parser.add_argument("-i","--inputDir",required=True)
parser.add_argument("-f","--fileName",required=True)
parser.add_argument("-o","--outDir",required=True)
args = parser.parse_args()

# load the .json parameters
jsonFile = None
jsonCheck = glob.glob("*.json")
if len(jsonCheck) > 0:
    print("Using parameters file: {}".format(jsonCheck[0]))
    jsonFile = open(jsonCheck[0])
    jsonFile = load_json(jsonFile.read())
# load in the model
model = None
modelCheck = glob.glob("*.h5")
if len(modelCheck) > 0:
    print("Using model: {}".format(modelCheck[0]))
    model = keras.models.load_model(modelCheck[0])
    
variables = list(jsonFile["variables"])

print("Using {} variables".format(len(variables)))
for i, variable in enumerate(variables): print(" {:<4} {}".format(str(i)+".",variable))

inputDir   = args.inputDir
fileName   = args.fileName
outDir     = args.outDir
step3_file = fileName + "_step3.root" 

# load in the sample

rootFile = TFile.Open(inputDir + "/" + fileName + ".root")
rootTree = rootFile.Get("ljmet")
events = np.asarray( rootTree.AsMatrix( [ variable.encode("ascii","ignore") for variable in variables ] ) )

discriminators = model.predict(events)

out = TFile( step3_file, "RECREATE" );
out.cd()
new_tree = rootTree.CloneTree(0);

DNN_disc = array("f", [0])

new_tree.Branch( "DNN_disc", DNN_disc, "DNN_disc/F" );

print("Processing {} events...".format(len(discriminators)))

for i in range(rootTree.GetEntries()):
    DNN_disc[0] = discriminators[i]
    new_tree.Fill()
    
out.Write()
out.Close()

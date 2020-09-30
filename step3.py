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
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers = import Adam
from sklearn.metrics import roc_auc_score, roc_curve, auc

import varsList

# read in arguments
parser = ArgumentParser()
parser.add_argument("-i","--inputDir",required=True)
parser.add_argument("-f","--fileName",required=True)
parser.add_argument("-o","--outName",required=True)
args = parser.parse_args()

# load the .json parameters
jsonFile = None
jsonCheck = glob.glob("parameters*.json")
if len(jsonCheck) > 0:
    jsonFile = open(jsonCheck[0])
    jsonFile = load_json(jsonFile.read())
# load in the model
model = None
modelCheck = glob.glob("*.h5")
if len(modelCheck) > 0:
    model = keras.models.load_model(modelCheck[0])
    
variables = jsonFile[list(jsonFile.keys())[0]]["parameters"]["variables"]

print("Using {} variables".format(len(variables)))
for i, variable in enumerate(variables): print(" {:<4} {}".format(i+".",variable))

inputDir = args.inputDir
fileName = args.fileName
outName  = args.outName

# load in the sample

rootFile = TFile.Open(inputDir + "/" + fileName)
rootTree = rootFile.Get("ljmet")
events = np.asarray( rootTree.AsMatrix( variables ) )

discriminators = model.predict(events)

out = TFile( outName, "RECREATE" );
out.cd()
new_tree = rootTree.CloneTree(0);

new_tree.Branch( "DNN_disc", discriminators, "DNN_disc/F" );

for i in range(rootTree.GetEntries()):
    new_tree.Fill()
    
out.Write()
out.Close()

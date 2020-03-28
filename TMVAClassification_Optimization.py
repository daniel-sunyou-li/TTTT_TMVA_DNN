#!/usr/bin/env python

import numpy as np
import os, sys, shutil
from subprocess import call
from os.path import isfile
import time, datetime
import getopt
import ROOT
from ROOT import TMVA, TFile, TTree, TCut, TRandom3, gSystem, gApplication, gROOT
import varsList

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

os.environ['KERAS_BACKEND'] = 'tensorflow'
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

# Define some variables defaults
MODEL_NAME =        "dummy_opt_model.h5"
EPOCHS =            10
BATCH_SIZE =        1028
PATIENCE =          5
outf_key =          "Keras"
WHERE =             "lpc"

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

try: # retrieve command line options
  shortopts   = "b:e:o:w:" # possible command line options
  opts, args = getopt.getopt( sys.argv[1:], shortopts ) # associates command line inputs to variables
  
except getopt.GetoptError: # output error if command line argument invalid
  print("ERROR: unknown options in argument %s" %sys.argv[1:])
  usage()
  sys.exit(1)

for opt, arg in opts:
    if ("b") in opt: BATCH_SIZE = int(arg)
    elif ('e') in opt: EPOCHS = int(arg)
    elif ('o') in opt: outf_key = str(arg)
    elif ('w') in opt: WHERE = str(arg)


######################################################
######################################################
######                                          ######
######         P R E P A R E   D A T A          ######
######                                          ######
######################################################
######################################################

NSIG =        0
NSIG_TEST =   0
NBKG =        0
NBKG_TEST =   0

# Set cut and weight values
weightStrC = varsList.weightStr
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = varsList.cutStr
cutStrS = cutStrC
cutStrB = cutStrC

# Initialize some containers
varList = []
bkg_list = []
sig_list = []
bkg_trees_list = []
sig_trees_list = []
hist_list = []
weightsList = []

#print("Output file: dataset/weights/TMVAOpt_" + outf_key + ".root")
if WHERE == "brux":
  inputDir = varsList.inputDirBrux
else:
  inputDir = varsList.inputDirLPC  # edit if not running on LPC

#print("Input file: {}".format(INPUTFILE))
READ = False
with open( "dataset/optimize_" + outf_key + "/varsListHPO.txt") as file:
  for line in file.readlines():
    if READ == True:
      varList.append(str(line).strip())
    if "Variable List:" in line: READ = True

numVars = len(varList)

outputfile = TFile( "dataset/weights/TMVAOptimization_"+ str(numVars) +"vars.root", "RECREATE" )

loader = TMVA.DataLoader( "dataset/optimize_" + outf_key )

for var in varList:
  if var == 'NJets_MultiLepCalc': loader.AddVariable(var,"","","I")
  else: loader.AddVariable(var,"","","F")
  
# add signal to loader
for i in range( len( varsList.sig1 ) ):
  sig_list.append( TFile.Open( inputDir + varsList.sig1[i] ) )
  sig_trees_list.append( sig_list[i].Get( "ljmet" ) )
  sig_trees_list[i].GetEntry(0)
  loader.AddSignalTree( sig_trees_list[i], 1 )
  
# add background to loader
for i in range( len( varsList.bkg1 ) ):
  bkg_list.append( TFile.Open( inputDir + varsList.bkg1[i] ) )
  #print( inputDir + varsList.bkg1[i] )
  bkg_trees_list.append( bkg_list[i].Get( "ljmet" ) )
  bkg_trees_list[i].GetEntry(0)
    
  if bkg_trees_list[i].GetEntries() == 0:
    continue
  loader.AddBackgroundTree( bkg_trees_list[i], 1 )
    
loader.SetSignalWeightExpression( weightStrS )
loader.SetBackgroundWeightExpression( weightStrB )
  
mycutSig = TCut( cutStrS )
mycutBkg = TCut( cutStrB )
 
loader.PrepareTrainingAndTestTree( 
  mycutSig, mycutBkg, 
  "nTrain_Signal=" + str(NSIG) +\
  ":nTrain_Background=" + str(NBKG) +\
  ":nTest_Signal=" + str(NSIG_TEST) +\
  ":nTest_Background=" + str(NBKG_TEST) +\
  ":SplitMode=Random:NormMode=NumEvents:!V"
)
  
  
factory = TMVA.Factory(
  "Optimization",
  '!V:!ROC:!Silent:Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification'
)

(TMVA.gConfig().GetIONames()).fWeightFileDir = '/weights'

kerasSetting = '!H:!V:VarTransform=G:FilenameModel=' + MODEL_NAME +\
               ':SaveBestOnly=true' +\
               ':NumEpochs=' + str(EPOCHS) +\
               ':BatchSize=' + str(BATCH_SIZE) +\
               ':TriesEarlyStopping=' + str(PATIENCE)
  
factory.BookMethod(
  loader,
  TMVA.Types.kPyKeras,
  "PyKeras",
  kerasSetting
)
  
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
  
ROC = factory.GetROCIntegral( 'dataset/optimize_' + outf_key, 'PyKeras' )
  
factory.DeleteAllMethods()
factory.fMethodsMap.clear()

outputfile.Close()

tempfile = open("dataset/temp_file.txt",'w')
tempfile.write(str(ROC))
tempfile.close()

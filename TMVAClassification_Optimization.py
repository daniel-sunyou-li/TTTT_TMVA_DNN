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

os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

# Define some variables defaults
MODEL_NAME =        "dummy_opt_model.h5"
EPOCHS =            10
BATCH_SIZE =        1028
PATIENCE =          5
outf_key =          "Keras"
INPUTFILE =         varsList.inputDirBRUX + "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"
TEMPFILE =          "dataset/temp_file.txt"
numVars =           len(varsList.varList["BigComb"])

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

try: # retrieve command line options
  shortopts   = "b:o:e:i" # possible command line options
  opts, args = getopt.getopt( sys.argv[1:], shortopts ) # associates command line inputs to variables
  
except getopt.GetoptError: # output error if command line argument invalid
  print("ERROR: unknown options in argument %s" %sys.argv[1:])
  usage()
  sys.exit(1)
  
for opt, arg in opts:
    if opt in ('b'): BATCH_SIZE = int(arg)
    elif opt in ('e'): EPOCHS = int(arg)
    elif opt in ('i'): INPUTFILE = str(arg)
    elif opt in ('o'): outf_key = str(arg)

######################################################
######################################################
######                                          ######
######         P R E P A R E   D A T A          ######
######                                          ######
######################################################
######################################################

NSIG =        50000
NSIG_TEST =   20000
NBKG =        500000
NBKG_TEST =   200000

# Set cut and weight values
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && " +\
          "((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
cutStrS = cutStrC
cutStrB = cutStrC

# Initialize some containers
bkg_list = []
bkg_trees_list = []
hist_list = []
weightsList = []

print("Output file: dataset/weights/TMVAOpt_" + outf_key + ".root")
outputfile =    TFile( "dataset/weights/TMVAOptimization_"+ numVars +"vars.root", "RECREATE" )

print("Input file: {}".format(INPUTFILE))
iFileSig =      TFile.Open( INPUTFILE )
sigChain =      iFileSig.Get( "ljmet" )

loader = TMVA.DataLoader( "dataset/optimize_" + outf_key )

for var in varsList.varList["BigComb"]:
  if var[0] == 'NJets_MultiLepCalc': loader.AddVariable(var[0],var[1],var[2],'I')
  else: loader.AddVariable(var[0],var[1],var[2],'F')
  
loader.AddSignalTree(sigChain)
  
for i in range(len(varsList.bkg)):
  bkg_list.append(TFile.Open( varsList.inputDirBRUX + varsList.bkg[i] ))
  print( varsList.inputDirBRUX + varsList.bkg[i] )
  bkg_trees_list.append( bkg_list[i].Get('ljmet') )
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

kerasSetting = '!H:!V:VarTransform=I:FilenameModel=' + MODEL_NAME +\
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

tempfile = open(TEMPFILE,'w')
tempfile.write(str(ROC))
tempfile.close()

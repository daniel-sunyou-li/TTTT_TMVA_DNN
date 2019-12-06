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

os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# Define some variables defaults
MODEL_NAME =        "dummy_opt_model.h5"
EPOCHS =            20
BATCH_SIZE =        1028
PATIENCE =          5
outf_key =          "PyKeras"
INPUTFILE =         varsList.inputDir + "TTTT_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"
TEMPFILE =          "dataset/temp_file.txt"

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

try: # retrieve command line options
  shortopts   = "e:b:p:o" # possible command line options
  opts, args = getopt.getopt( sys.argv[1:], shortopts ) # associates command line inputs to variables
  
except getopt.GetoptError: # output error if command line argument invalid
  print("ERROR: unknown options in argument %s" %sys.argv[1:])
  usage()
  sys.exit(1)
  
for opt, arg in opts:
    if opt in ('b'): BATCH_SIZE = int(arg)
    elif opt in ('o'): outf_key = str(arg)

######################################################
######################################################
######                                          ######
######         P R E P A R E   D A T A          ######
######                                          ######
######################################################
######################################################

NSIG =        10000
NSIG_TEST =   100000
NBKG =        20000
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
outputfile =    TFile( "dataset/weights/TMVAOpt_" + outf_key + ".root", "RECREATE" )

print("Input file",INPUTFILE)
iFileSig =      TFile.Open( INPUTFILE )
sigChain =      iFileSig.Get( "ljmet" )

loader = TMVA.DataLoader( "dataset/optimize_" + outf_key )

for var in varsList.varList["BigComb"]:
  if var[0] == 'NJets_singleLepCalc': loader.AddVariable(var[0],var[1],var[2],'I')
  else: loader.AddVariable(var[0],var[1],var[2],'F')
  
loader.AddSignalTree(sigChain)
  
for i in range(len(varsList.bkg)):
  bkg_list.append(TFile.Open( varsList.inputDir + varsList.bkg[i] ))
  print( varsList.inputDir + varsList.bkg[i] )
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
  
factory_name = 'DNNOptimizer'  
factory = TMVA.Factory(
  factory_name,
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
  
print("Training all methods...")
factory.TrainAllMethods()
print("Testing all methods...")
factory.TestAllMethods()
print("Evaluating all methods...")
factory.EvaluateAllMethods()
  
print("Evaluating ROC Integral")
ROC = factory.GetROCIntegral( 'dataset/optimize_' + outf_key, 'PyKeras' )
  
factory.DeleteAllMethods()
factory.fMethodsMap.clear()

outputfile.Close()

tempfile = open(TEMPFILE,'w')
tempfile.write(str(ROC))
tempfile.close()
  
print("Finished optimization round.")  
  
  
  
  

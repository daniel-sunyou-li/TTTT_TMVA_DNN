#!/usr/bin/env python

import numpy as np
import os, sys
from subprocess import call
from os.path import isfile
import time
import getopt
import ROOT
from ROOT import TMVA, TFile, TTree, TCut, TRandom3
from ROOT import gSystem, gApplication, gROOT
import varsList

os.environ['KERAS_BACKEND'] = 'tensorflow'

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

START_TIME = time.time()

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# weight calculation equation
weightStrC = varsList.weightStr
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = varsList.cutStr
cutStrS = cutStrC
# cutStrS = cutStrC + 'eventNumBranch%3' ## edit this
cutStrB = cutStrC

# default command line arguments
DEFAULT_OUTFNAME = "dataset/weights/TMVA.root" 	# this file to be read

######################################################
######################################################
######                                          ######
######              M E T H O D S               ######
######                                          ######
######################################################
######################################################

def usage(): # conveys what command line arguments can be used for main()
  print(" ")
  print("Usage: python %s [options]" % sys.argv[0])
  print("  -o | --outputfile : name of output ROOT file containing results (default: '%s')" % DEFAULT_OUTFNAME)
  print("  -v | --verbose")
  print("  -? | --usage      : print this help message")
  print("  -h | --help       : print this help message")
  print(" ")

def checkRootVer():
    if gROOT.GetVersionCode() >= 332288 and gROOT.GetVersionCode() < 332544:
      print "*** You are running ROOT version 5.18, which has problems in PyROOT such that TMVA"
      print "*** does not run properly (function calls with enums in the argument are ignored)."
      print "*** Solution: either use CINT or a C++ compiled version (see TMVA/macros or TMVA/examples),"
      print "*** or use another ROOT version (e.g., ROOT 5.19)."
      sys.exit(1)
  
def treeSplit_(arg): # takes in the tree argument and splits into signal and background
  arg.strip()
  trees = arg.rsplit( ' ' )
  trees.sort()
  trees.reverse()
  if len(trees)  - trees.count('') != 2:
    print('ERROR: need to give two trees')
    print(trees)
    sys.exit(1)
  return trees

def build_model(hidden, nodes, lrate, regulator, pattern, activation):
  model = Sequential()
  model.add(Dense(
      nodes,
      input_dim = len(varsList.varList["BigComb"]),
      kernel_initializer = 'glorot_normal',
      activation = activation
    )
  )
  partition = int( nodes / hidden )
  for i in range(hidden):
    if regulator in ['normalization','both']: model.add(BatchNormalization())
    if pattern in ['dynamic']:
      model.add(Dense(
          nodes - ( partition * i),
          kernel_initializer = 'glorot_normal',
          activation = activation
        )
      )
    if pattern in ['static']:
      model.add(Dense(
          nodes,
          kernel_initializer = 'glorot_normal',
          activation = activation
        )
      )
    if regulator in ['dropout','both']: model.add(Dropout(0.5))
  model.add(Dense(
      2, # signal or background classification
      activation = 'sigmoid'
    )
  )
  model.compile(
    optimizer = Adam(lr = lrate),
    loss = 'categorical_crossentropy',
    metrics = ['accuracy']
  )
  return model
  
def main(): # runs the program
  checkRootVer() # check that ROOT version is correct
  
  try: # retrieve command line options
    shortopts   = "o:v:h?" # possible command line options
    longopts    = ["outputfile=",
                   "verbose",
                   "help",
                   "usage"]
    opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
  except getopt.GetoptError: # output error if command line argument invalid
    print("ERROR: unknown options in argument %s" %sys.argv[1:])
    usage()
    sys.exit(1)
  
  myArgs = np.array([ # Stores the command line arguments   
    ['-o','--outputfile','outfname',    DEFAULT_OUTFNAME],    
    ['-v','--verbose','verbose',        True],                
  ])
  
  for opt, arg in opts:
    if opt in myArgs[:,0]:
      index = np.where(myArgs[:,0] == opt)[0][0] # np.where returns a tuple of arrays
      myArgs[index,3] = arg # override the variables with the command line argument
    elif opt in myArgs[:,1]:
      index = np.where(myArgs[:,1] == opt)[0][0] 
      myArgs[index,3] = arg
    if opt in ("-?", "-h", "--help", "--usage"): # provides command line help
      usage()
      sys.exit(0)
  
  # Initialize some containers
  bkg_list = []
  bkg_trees_list = []
  sig_list = []
  sig_trees_list = []
  
  # Initialize some variables after reading in arguments
  outfname_index = np.where(myArgs[:,2] == 'outfname')[0][0]
  verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]

  varList = varsList.varList["BigComb"]
  numVars = len(varList)
  outf_key = str("Keras_" + str(numVars) + "vars") 
  myArgs[outfname_index,3] = "dataset/weights/TMVA_" + outf_key + ".root"
  
  
  outputfile = TFile( myArgs[outfname_index,3], "RECREATE" )
  inputDir = varsList.inputDirLPC     # edit-me if not running on FNAL LPC, see varsList.py for options
  
  # initialize and set-up TMVA factory
  
  factory = TMVA.Factory( "Training", outputfile,
    "!V:!ROC:Silent:Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification" )
    
  factory.SetVerbose(bool( myArgs[verbose_index,3] ) )
  (TMVA.gConfig().GetIONames()).fWeightFileDir = "weights/" + outf_key
  
  # initialize and set-up TMVA loader
  
  loader = TMVA.DataLoader( "dataset" )
  
  for var in varList:
    if var[0] == "NJets_MultiLepCalc": loader.AddVariable(var[0],var[1],var[2],'I')
    else: loader.AddVariable(var[0],var[1],var[2],"F")
  
  # add signal files
  for i in range( len( varsList.sig ) ):
    sig_list.append( TFile.Open( inputDir + varsList.sig[i] ) )
    sig_trees_list.append( sig_list[i].Get("ljmet") )
    sig_trees_list[i].GetEntry(0)
    loader.AddSignalTree( sig_trees_list[i] )
  
  # add background files
  for i in range( len( varsList.bkg ) ):
    bkg_list.append( TFile.Open( inputDir + varsList.bkg[i] ) )
    bkg_trees_list.append( bkg_list[i].Get( "ljmet" ) )
    bkg_trees_list[i].GetEntry(0)
    
    if bkg_trees_list[i].GetEntries() == 0:
      continue
    loader.AddBackgroundTree( bkg_trees_list[i] )
  
  loader.SetSignalWeightExpression( weightStrS )
  loader.SetBackgroundWeightExpression( weightStrB )
  
  mycutSig = TCut( cutStrS )
  mycutBkg = TCut( cutStrB )
  
  loader.PrepareTrainingAndTestTree( mycutSig, mycutBkg, 
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
  )
 
######################################################
######################################################
######                                          ######
######            K E R A S   D N N             ######
######                                          ######
######################################################
######################################################
  
  # modify this when implementing hyper parameter optimization:
  model_name = 'TTTT_' + str(numVars) + 'vars_model.h5'
  
  EPOCHS = 30
  PATIENCE = 5
  
  # edit these based on hyper parameter optimization results
  HIDDEN = 3
  NODES = 100
  LRATE = 0.01
  PATTERN = 'static'
  REGULATOR = 'none'
  ACTIVATION = 'relu'
  BATCH_SIZE = 256
  
  kerasSetting = '!H:!V:VarTransform=G:FilenameModel=' + model_name + \
                 ':SaveBestOnly=true' + \
                 ':NumEpochs=' + str(EPOCHS) + \
                 ':BatchSize=' + str(BATCH_SIZE) + \
                 ':TriesEarlyStopping=' + str(PATIENCE)
  
  model = build_model(HIDDEN,NODES,LRATE,REGULATOR,PATTERN,ACTIVATION)
  model.save( model_name )
  model.summary()
  
  factory.BookMethod(
    loader,
    TMVA.Types.kPyKeras,
    'PyKeras',
    kerasSetting
  )
  
  factory.TrainAllMethods()
  factory.TestAllMethods()
  factory.EvaluateAllMethods()
  
  outputfile.Close()
  
  print("Finished training in " + str((time.time() - START_TIME) / 60.0) + " minutes.")
  
  ROC = factory.GetROCIntegral( 'dataset', 'PyKeras')
  print('ROC value is: {}'.format(ROC))

main()
os.system('exit') 

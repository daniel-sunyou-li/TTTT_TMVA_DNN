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

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.optimizers import Adam

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

START_TIME = time.time()

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# weight calculation equation
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && ((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
cutStrS = cutStrC
# cutStrS = cutStrC + 'eventNumBranch%3' ## edit this
cutStrB = cutStrC

# default command line arguments
DEFAULT_METHODS		  = "Keras"      # how was the .root file trained
DEFAULT_OUTFNAME	  = "dataset/weights/TMVA.root" 	# this file to be read
DEFAULT_INFNAME		  = "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"
DEFAULT_MASS   		  = "180"
DEFAULT_VARLISTKEY	= "BigComb"

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
  print("  -m | --methods    : gives methods to be run (default: all methods)")
  print("  -i | --inputfile  : name of input ROOT file (default: '%s')" % DEFAULT_INFNAME)
  print("  -o | --outputfile : name of output ROOT file containing results (default: '%s')" % DEFAULT_OUTFNAME)
  print("  -l | --varListKey : BDT input variable list (default: '%s')" %DEFAULT_VARLISTKEY)
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
  
def printMethods_(methods): # prints a list of the methods being used
  mlist = methods.replace(' ',',').split(',')
  print('=== TMVAClassification: using method(s)...')
  for m in mlist:
    if m.strip() != '':
      print('=== - <%s>'%m.strip())
      
def main(): # runs the program
  checkRootVer() # check that ROOT version is correct
  
  try: # retrieve command line options
    shortopts   = "m:i:l:o:v:h?" # possible command line options
    longopts    = ["methods=", 
                   "inputfile=",
                   "varListKey=",
                   "outputfile=",
                   "verbose",
                   "help",
                   "usage"]
    opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
  except getopt.GetoptError: # output error if command line argument invalid
    print("ERROR: unknown options in argument %s" %sys.argv[1:])
    usage()
    sys.exit(1)
  
  myArgs = np.array([ # Stores the command line arguments
    ['-m','--methods','methods',        DEFAULT_METHODS],     #0  Reference Indices
    ['-l','--varListKey','varListKey',  DEFAULT_VARLISTKEY],  #3
    ['-i','--inputfile','infname',      DEFAULT_INFNAME],     #4
    ['-o','--outputfile','outfname',    DEFAULT_OUTFNAME],    #5
    ['-v','--verbose','verbose',        True],                #8
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
  hist_list = []
  weightsList = []
  
  # Initialize some variables after reading in arguments
  varListKey_index = np.where(myArgs[:,2] == 'varListKey')[0][0]

  method_index = np.where(myArgs[:,2] == 'methods')[0][0]
  infname_index = np.where(myArgs[:,2] == 'infname')[0][0]
  outfname_index = np.where(myArgs[:,2] == 'outfname')[0][0]
  verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]  

  varList = varsList.varList[myArgs[varListKey_index,3]]
  nVars = str(len(varList)) + 'vars'
  var_length = len(varList)
  outf_key = str(myArgs[method_index,3] +  '_' + myArgs[varListKey_index,3] + '_' + nVars) 
  myArgs[outfname_index,3] = 'dataset/weights/TMVA_' + outf_key + '.root'
  
  
  outputfile = TFile( myArgs[outfname_index,3], 'RECREATE' )
  inputDir = varsList.inputDir
  iFileSig = TFile.Open( inputDir + myArgs[infname_index,3] )
  sigChain = iFileSig.Get( 'ljmet' )
  
  printMethods_(myArgs[method_index,3]) # references myArgs array method string and prints
  
  # initialize and set-up TMVA factory
  
  factory = TMVA.Factory( 'TMVAClassification', outputfile,
    '!V:!Silent:Color:DrawProgressBar:Transformations=I;:AnalysisType=Classification' )
    
  factory.SetVerbose(bool( myArgs[verbose_index,3] ) )
  (TMVA.gConfig().GetIONames()).fWeightFileDir = 'weights/' + outf_key
  
  # initialize and set-up TMVA loader
  
  loader = TMVA.DataLoader( 'dataset' )
  
  for var in varList:
    if var[0] == 'NJets_MultiLepCalc': loader.AddVariable(var[0],var[1],var[2],'I')
    else: loader.AddVariable(var[0],var[1],var[2],"F")
  
  loader.AddSignalTree(sigChain)
  
  for i in range(len(varsList.bkg)):
    bkg_list.append(TFile.Open( inputDir + varsList.bkg[i] ))
    print( inputDir + varsList.bkg[i] )
    bkg_trees_list.append( bkg_list[i].Get('ljmet') )
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
  
  # modify this when implementing hyper parameter optimization:
  model_name = 'TTTT_TMVA_model.h5'
  kerasSetting = 'H:!V:VarTransform=G:FilenameModel=' + model_name + ':NumEpochs=15:BatchSize=256'
 
######################################################
######################################################
######                                          ######
######            K E R A S   D N N             ######
######                                          ######
######################################################
######################################################
  
  model = Sequential()
  '''
  model.add(Dense(var_length*4, activation='softplus', input_dim=var_length,
    kernel_initializer = 'glorot_normal'))
  model.add(Dropout(0.5))
  model.add((Dense(var_length*2, activation='softplus',
    kernel_initializer = 'glorot_normal')))
  model.add(Dropout(0.5))
  model.add((Dense(var_length, activation='softplus',
    kernel_initializer = 'glorot_normal')))
  model.add(Dropout(0.5))
  model.add((Dense(int(var_length/2), activation='softplus',
    kernel_initializer = 'glorot_normal')))
  model.add((Dense(2, activation='sigmoid')))
  '''
  model.add(Dense(100, activation='softplus', input_dim=var_length,
    kernel_initializer = 'glorot_normal'))
  model.add(Dense(100, activation='softplus',
    kernel_initializer = 'glorot_normal'))
  model.add(Dense(100, activation='softplus',
    kernel_initializer = 'glorot_normal'))
  model.add(Dense(2, activation='sigmoid'))

  # set loss and optimizer
  model.compile(
    loss = 'categorical_crossentropy',
    optimizer = Adam(),
    metrics = ['accuracy']
  )
  
  # save the model
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

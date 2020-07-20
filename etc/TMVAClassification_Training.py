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
cutStrB = cutStrC

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
  print("  -o | --option     : Use 0 for default run, Use 1 for optimized run.")
  print("  -v | --verbose")
  print("  -? | --usage      : print this help message")
  print("  -h | --help       : print this help message")
  print("  -d | --dataset    : dataset directory with Hyper Parameter Optimization Results")
  print("  -w | --where      : where the script is being run (LPC or BRUX)")
  print("  -y | --year       : production year (2017 or 2018)")
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

def build_model(hidden, nodes, lrate, regulator, pattern, activation, numVars):
  model = Sequential()
  model.add(Dense(
      nodes,
      input_dim = numVars,
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
    shortopts   = "d:o:v:w:y:h?" # possible command line options
    longopts    = ["dataset=",
                   "option=",
                   "where=",
                   "year=",
                   "verbose",
                   "help",
                   "usage"]
    opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
  except getopt.GetoptError: # output error if command line argument invalid
    print("ERROR: unknown options in argument %s" %sys.argv[1:])
    usage()
    sys.exit(1)
  
  myArgs = np.array([ # Stores the command line arguments   
    ['-d','--dataset','dataset','dataset'],
    ['-w','--where','where','lpc'],
    ['-y','--year','year',2017],
    ['-o','--option','option', 0],    
    ['-v','--verbose','verbose', True]
  ], dtype = "object")
  
  for opt, arg in opts:
    if opt in myArgs[:,0]:
      index = np.where(myArgs[:,0] == opt)[0][0] # np.where returns a tuple of arrays
      myArgs[index,3] = str(arg) # override the variables with the command line argument
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
  option_index = np.where(myArgs[:,2] == 'option')[0][0]
  dataset_index = np.where(myArgs[:,2] == 'dataset')[0][0]
  verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]
  where_index = np.where(myArgs[:,2] == 'where')[0][0]
  year_index = np.where(myArgs[:,2] == 'year')[0][0]

  DATASETPATH = myArgs[dataset_index][3]
  DATASET = DATASETPATH.split("/")[0]
  OPTION = myArgs[option_index][3]
  VERBOSE = myArgs[verbose_index][3]
  WHERE = myArgs[where_index][3]
  YEAR = myArgs[year_index][3]
  
  if WHERE == "lpc":
    if YEAR == 2017:
      inputDir = varsList.inputDirLPC2017
    elif YEAR == 2018:
      inputDir = varsList.inputDirLPC2018
  else:
    if YEAR == 2017:
      inputDir = varsList.inputDirBRUX2017
    elif YEAR == 2018:
      inputDir = varsList.inputDirBRUX2018
 
  if OPTION == "0":
    print("Using Option 0: default varList")
    varList = varsList.varList["DNN"]
  
  elif OPTION == "1":
    print("Using Option 1: selected data from {}".format(DATASETPATH))
    varsListHPO = open( DATASETPATH + "/varsListHPO.txt", "r" ).readlines()
    varList = []
    START = False
    for line in varsListHPO:
      if START == True:
        varList.append(str(line.strip()))
      if "Variable List:" in line:
        START = True

  numVars = len(varList)
  outf_key = str("Keras_" + str(numVars) + "vars") 
  OUTF_NAME = DATASET + "/weights/TMVA_" + outf_key + ".root"
  outputfile = TFile( OUTF_NAME, "RECREATE" )

  # initialize and set-up TMVA factory
  
  factory = TMVA.Factory( "Training", outputfile,
    "!V:!ROC:Silent:Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification" )
    
  factory.SetVerbose(bool( myArgs[verbose_index,3] ) )
  (TMVA.gConfig().GetIONames()).fWeightFileDir = "weights/" + outf_key
  
  # initialize and set-up TMVA loader
  
  loader = TMVA.DataLoader( DATASET )
  
  if OPTION == "0":
    for var in varList:
      if var[0] == "NJets_MultiLepCalc": loader.AddVariable(var[0],var[1],var[2],'I')
      else: loader.AddVariable(var[0],var[1],var[2],"F")
  if OPTION == "1":
    for var in varList:
      if var == "NJets_MultiLepCalc": loader.AddVariable(var,"","","I")
      else: loader.AddVariable(var,"","","F")
 
  # add signal files
  if YEAR == 2017:
    for i in range( len( varsList.sig2017_2 ) ):
      sig_list.append( TFile.Open( inputDir + varsList.sig2017_2[i] ) )
      sig_trees_list.append( sig_list[i].Get("ljmet") )
      sig_trees_list[i].GetEntry(0)
      loader.AddSignalTree( sig_trees_list[i] )
      
  elif YEAR == 2018:
    for i in range( len( varsList.sig2018_2 ) ):
      sig_list.append( TFile.Open( inputDir + varsList.sig2018_2[i] ) )
      sig_trees_list.append( sig_list[i].Get("ljmet") )
      sig_trees_list[i].GetEntry(0)
      loader.AddSignalTree( sig_trees_list[i] )
  
  # add background files
  if YEAR == 2017:
    for i in range( len( varsList.bkg2017_2 ) ):
      bkg_list.append( TFile.Open( inputDir + varsList.bkg2017_2[i] ) )
      bkg_trees_list.append( bkg_list[i].Get( "ljmet" ) )
      bkg_trees_list[i].GetEntry(0)

      if bkg_trees_list[i].GetEntries() == 0:
        continue
      loader.AddBackgroundTree( bkg_trees_list[i] )

  elif YEAR == 2018:
    for i in range( len( varsList.bkg2018_2 ) ):
      bkg_list.append( TFile.Open( inputDir + varsList.bkg2018_2[i] ) )
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
  HIDDEN=0
  NODES=0
  LRATE=0.
  PATTERN=""
  REGULATOR=""
  ACTIVATION=""
  BATCH_SIZE=0 
  # modify this when implementing hyper parameter optimization:
  model_name = 'TTTT_' + str(numVars) + 'vars_model.h5'
  
  EPOCHS = 100
  PATIENCE = 20
  
  # edit these based on hyper parameter optimization results
  if OPTION == "0":
    HIDDEN = 3
    NODES = 100
    LRATE = 0.01
    PATTERN = 'static'
    REGULATOR = 'none'
    ACTIVATION = 'relu'
    BATCH_SIZE = 256
  if OPTION == "1":
    datasetDir = os.listdir(DATASETPATH)
    for file in datasetDir:
      if "params" in file: optFileName = file
    optFile = open(DATASETPATH + "/" + optFileName,"r").readlines()
    START = False
    for line in optFile:
      if START == True:
        if "Hidden" in line: HIDDEN = int(line.split(":")[1].strip())
        if "Initial" in line: NODES = int(line.split(":")[1].strip())
        if "Batch" in line: BATCH_SIZE = 2**int(line.split(":")[1].strip())
        if "Learning" in line: LRATE = float(line.split(":")[1].strip())
        if "Pattern" in line: PATTERN = str(line.split(":")[1].strip())
        if "Regulator" in line: REGULATOR = str(line.split(":")[1].strip())
        if "Activation" in line: ACTIVATION = str(line.split(":")[1].strip())
      if "Optimized Parameters:" in line: START = True
  kerasSetting = '!H:!V:VarTransform=G:FilenameModel=' + model_name + \
                 ':SaveBestOnly=true' + \
                 ':NumEpochs=' + str(EPOCHS) + \
                 ':BatchSize=' + str(BATCH_SIZE) + \
                 ':TriesEarlyStopping=' + str(PATIENCE)
  
  model = build_model(HIDDEN,NODES,LRATE,REGULATOR,PATTERN,ACTIVATION,numVars)
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
  
  ROC = factory.GetROCIntegral( DATASET, 'PyKeras')
  print('ROC value is: {}'.format(ROC))
  if OPTION == "1":
   varsListHPOtxt = open(DATASETPATH + "varsListHPO.txt","a")
   varsListHPOtxt.write("ROC Value: {}".format(ROC))

main()
os.system('exit') 

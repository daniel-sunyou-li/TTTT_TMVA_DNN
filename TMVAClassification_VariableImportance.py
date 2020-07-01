#!/usr/bin/env python

import os, sys
from os.path import isfile
import time
import numpy as np
import getopt
import ROOT
from ROOT import TMVA, TFile, TTree, TCut, TRandom3
from ROOT import gSystem, gApplication, gROOT
import varsList
from subprocess import call

os.environ['KERAS_BACKEND'] = 'tensorflow'

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam

os.system( 'bash' )
os.system( 'source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh' )

# weight calculation equation
weightStrC = varsList.weightStr
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = varsList.cutStr
cutStrS = cutStrC
cutStrB = cutStrC

# default command line arguments
DEFAULT_OUTFNAME = "dataset/weights/TMVA.root" 	# this file to be read
DEFAULT_SEED     = 1

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
  print("  -w | --where : where the script is being run (LPC or BRUX)")
  print("  -y | --year : production year of sample (2017 or 2018)")
  print("  -s | --seed : random seed for selecting variable (default: '%s')" %DEFAULT_SEED) 
  print("  -v | --verbose")
  print("  -? | --usage      : print this help message")
  print("  -h | --help       : print this help message")
  print(" ")

def checkRootVer():
    if gROOT.GetVersionCode() >= 332288 and gROOT.GetVersionCode < 332544:
      print "*** You are running ROOT version 5.18, which has problems in PyROOT such that TMVA"
      print "*** does not run properly (function calls with enums in the argument are ignored)."
      print "*** Solution: either use CINT or a C++ compiled version (see TMVA/macros or TMVA/examples),"
      print "*** or use another ROOT version (e.g., ROOT 5.19)."
      sys.exit(1)
      
def main(): # runs the program
  try: # retrieve command line options
    shortopts   = "o:w:y:v:s:h?" # possible command line options
    longopts    = ["outputfile=",
		   "where=",
		   "year=",
                   "verbose",
		   "seed=",
                   "help",
                   "usage"]
    opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
  except getopt.GetoptError: # output error if command line argument invalid
    print( "ERROR: unknown options in argument %s" %sys.argv[1:] )
    usage()
    sys.exit(1)
  
  myArgs = np.array([ # Stores the command line arguments    
    ['-o','--outputfile','outfname',    DEFAULT_OUTFNAME],    
    ['-v','--verbose','verbose',        True],
    ['-w','--where','where',		"lpc"],
    ['-y','--year','year',		2017],
    ['-s','--seed','SeedN',             DEFAULT_SEED],        
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
  
  # Initialize some variables after reading in arguments
  SeedN_index = np.where(myArgs[:,2] == 'SeedN')[0][0]
  outfname_index = np.where(myArgs[:,2] == 'outfname')[0][0]
  verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]
  where_index = np.where(myArgs[:,2] == 'where')[0][0]
  year_index = np.where(myArgs[:,2] == 'year')[0][0]

  seed = myArgs[SeedN_index,3]
  where = myArgs[where_index,3]
  year = int(myArgs[year_index,3])
  varList = varsList.varList["DNN"]
  var_length = len(varList)

  str_xbitset = '{:0{}b}'.format(long(myArgs[SeedN_index,3]),var_length)
  nVars = str_xbitset.count('1')
  outf_key =  "DNN_" + str(nVars) + "vars"
  myArgs[outfname_index,3] = "dataset/weights/TMVA_" + outf_key + ".root"   
  
  print( "Seed: {}".format(str_xbitset) )

  outputfile = TFile( myArgs[outfname_index,3], 'RECREATE' ) 

  checkRootVer() # check that ROOT version is correct 
 
######################################################
######################################################
######                                          ######
######                  T M V A                 ######
######                                          ######
######################################################
######################################################
  
  # Declare some containers
  sig_list = []
  sig_trees_list = []
  bkg_list = []
  bkg_trees_list = []
  hist_list = []
  weightsList = []
  
  if where == "brux":
	if year == 2017:
  		inputDir = varsList.inputDirBRUX2017
	elif year == 2018:
		inputDir = varsList.inputDirBRUX2018
  else: 
	inputDir = varsList.inputDirCondor
		
  # Set up TMVA
  ROOT.TMVA.Tools.Instance()
  ROOT.TMVA.PyMethodBase.PyInitialize()

  fClassifier = TMVA.Factory( 'VariableImportance',
        '!V:!ROC:Silent:!Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification' )

  fClassifier.SetVerbose( bool( myArgs[verbose_index,3] ) )

  loader = TMVA.DataLoader( "dataset/" + str_xbitset )
	
  for indx,var in enumerate( varList ):
    if ( str_xbitset[indx] == '1' ):
      if var[0] == "NJets_MultiLepCalc": loader.AddVariable( var[0], var[1], var[2], "I" )
      else: loader.AddVariable( var[0], var[1], var[2], "F" )
  
  # add signals to loader
  if year == 2017:
    for i in range( len( varsList.sig2017_0 ) ):
      sig_list.append( TFile.Open( inputDir + varsList.sig2017_0[i] ) )
      sig_trees_list.append( sig_list[i].Get( "ljmet" ) )
      sig_trees_list[i].GetEntry(0)
      loader.AddSignalTree( sig_trees_list[i] )
  elif year == 2018:
    for i in range( len( varsList.sig2018_0 ) ):
      sig_list.append( TFile.Open( inputDir + varsList.sig2018_0[i] ) )
      sig_trees_list.append( sig_list[i].Get( "ljmet" ) )
      sig_trees_list[i].GetEntry(0)
      loader.AddSignalTree( sig_trees_list[i] )
	
  # add backgrounds to loader
  if year == 2017:
    for i in range( len( varsList.bkg2017_0 ) ):
      bkg_list.append( TFile.Open( inputDir + varsList.bkg2017_0[i] ) )
      bkg_trees_list.append( bkg_list[i].Get( "ljmet" ) )
      bkg_trees_list[i].GetEntry(0)
      if bkg_trees_list[i].GetEntries() == 0: continue
      loader.AddBackgroundTree( bkg_trees_list[i] )
			
  elif year == 2018:
    for i in range( len( varsList.bkg2018_0 ) ):
      bkg_list.append( TFile.Open( inputDir + varsList.bkg2018_0[i] ) )
      bkg_trees_list.append( bkg_list[i].Get( "ljmet" ) )
      bkg_trees_list[i].GetEntry(0)

      if bkg_trees_list[i].GetEntries() == 0: continue
      loader.AddBackgroundTree( bkg_trees_list[i] )
			
  # set signal and background weights 
  loader.SetSignalWeightExpression( weightStrS )
  loader.SetBackgroundWeightExpression( weightStrB )
  
  # set cut thresholds for signal and background
  mycutSig = TCut( cutStrS )
  mycutBkg = TCut( cutStrB )

  NSIG =	0
  NSIG_TEST =	0
  NBKG =	0
  NBKG_TEST =	0

  loader.PrepareTrainingAndTestTree(
    mycutSig, mycutBkg,
    "nTrain_Signal=" + str(NSIG) + \
    ":nTrain_Background=" + str(NBKG) + \
    ":nTest_Signal=" + str(NSIG_TEST) + \
    ":nTest_Background=" + str(NBKG_TEST) + \
    ":SplitMode=Random:NormMode=NumEvents:!V"
  )

#####################################################
#####################################################
######                                         ######
######            K E R A S   D N N            ######
######                                         ######
#####################################################
#####################################################                         

  model_name = "TTTT_TMVA_model.h5"

  model = Sequential()
  model.add( Dense(
    100, input_dim = nVars,
    kernel_initializer = "glorot_normal", 
    activation = "relu"
    )
  )
  for i in range(2):
    model.add( BatchNormalization() )
    model.add( Dense(
      100,
      kernel_initializer = "glorot_normal",
      activation = "relu"
      )
    )
  model.add( Dense(
    2,
    activation = "sigmoid"
    )
  )

  model.compile(
	loss = "categorical_crossentropy",
	optimizer = Adam(),
	metrics = ["accuracy"]
  )

  model.save( model_name )
  model.summary()
 
######################################################
######################################################
######                                          ######
######                  T M V A                 ######
######                                          ######
######################################################
######################################################
  
  # Declare some containers
  kerasSetting = "!H:!V:VarTransform=G:FilenameModel=" + model_name + \
		 ":NumEpochs=15:BatchSize=512" # the trained model has to be specified in this string
  
  # run the classifier
  fClassifier.BookMethod(
    loader,
    TMVA.Types.kPyKeras,
    "PyKeras",
    kerasSetting) 

  ( TMVA.gConfig().GetIONames() ).fWeightFileDir = str_xbitset + "/weights/" + outf_key
  #print("New weight file directory: {}".format((TMVA.gConfig().GetIONames()).fWeightFileDir))
  
  fClassifier.TrainAllMethods()
  fClassifier.TestAllMethods()
  fClassifier.EvaluateAllMethods()
  
  SROC = fClassifier.GetROCIntegral( "dataset/"+ str_xbitset, "PyKeras" )
  print( "ROC-integral: {}".format(SROC) )
  fClassifier.DeleteAllMethods()
  fClassifier.fMethodsMap.clear()
  
  outputfile.Close()

main()
os.system('exit')

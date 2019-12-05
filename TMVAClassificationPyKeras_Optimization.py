#!/usr/bin/env python

import numpy as np
import os, sys, shutil
from subprocess import call
from os.path import isfile
import time, datetime
import getopt
import ROOT
from ROOT import TMVA, TFile, TTree, TCut, TRandom3, gSystem, gApplication, gROOT
#import tmva as TMVA
import varsList

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.optimizers import Adam
from keras import backend

sys.path.insert(0, "/home/dli50/.local/lib/python2.7/site-packages")

from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

#print('Root version: {}'.format(gROOT.GetVersion()))

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')
  
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

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
  print("  -k | --mass : mass of the signal (default: '%s')" %DEFAULT_MASS)
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
# Start Program

START_TIME = time.time()

NSIG =        10000
NSIG_TEST =   100000
NBKG =        20000
NBKG_TEST =   200000

# weight calculation equation
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && " +\
          "((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
cutStrS = cutStrC
# cutStrS = cutStrC + 'eventNumBranch%3' ## edit this
cutStrB = cutStrC

# default command line arguments
DEFAULT_METHODS		  = "Keras"      # how was the .root file trained
DEFAULT_OUTFNAME	  = "dataset/weights/TMVA.root" 	# this file to be read
DEFAULT_INFNAME		  = "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"
DEFAULT_MASS		    = "180"
DEFAULT_VARLISTKEY	= "BigComb"

myArgs = np.array([ # Stores the command line arguments
  ['-m','--methods','methods',        DEFAULT_METHODS],     #0  Reference Indices
  ['-k','--mass','mass',              DEFAULT_MASS],        #2
  ['-l','--varListKey','varListKey',  DEFAULT_VARLISTKEY],  #3
  ['-i','--inputfile','infname',      DEFAULT_INFNAME],     #4
  ['-o','--outputfile','outfname',    DEFAULT_OUTFNAME],    #5
  ['-v','--verbose','verbose',        True],                #8
])
 
try: # retrieve command line options
  shortopts   = "m:i:k:l:o:vh?" # possible command line options
  longopts    = ["methods=", 
                 "inputfile=",
                 "mass=",
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
for opt, arg in opts:
  if opt in myArgs[:,0]:
    index = np.where(myArgs[:,0] == opt)[0][0] # np.where returns a tuple of arrays
    myArgs[index,3] = arg # override the variables with the command line argument
  elif opt in myArgs[:,1]:
    index = np.where(myArgs[:,1] == opt)[0][0] 
    myArgs[index,3] = arg
  if opt in ('-t', '--inputtrees'): # handles assigning tree signal and background
    index_sig = np.where(myArgs[:,2] == 'treeNameSig')[0][0]
    index_bkg = np.where(myArgs[:,2] == 'treeNameBkg')[0][0]
    myArgs[index_sig,3], myArgs[index_bkg,3] == treeSplit_(arg) # override signal, background tree
 
# Initialize some variables after reading in arguments
method_index = np.where(myArgs[:,2] == 'methods')[0][0]
infname_index = np.where(myArgs[:,2] == 'infname')[0][0]
outfname_index = np.where(myArgs[:,2] == 'outfname')[0][0]
verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]  
varListKey_index = np.where(myArgs[:,2] == 'varListKey')[0][0]

varList = varsList.varList[myArgs[varListKey_index,3]]
nVars = str(len(varList)) + 'vars'
var_length = len(varList)

outf_key = str(myArgs[method_index,3] + '_' + myArgs[varListKey_index,3] + '_' + nVars)
myArgs[outfname_index,3] = 'dataset/weights/TMVAOpt_' + outf_key + '.root'

# Create directory for hyper parameter optimization for # of input variables if it doesn't exit
if not os.path.exists('dataset/optimize_' + outf_key):
  os.mkdir('dataset/optimize_' + outf_key)
  os.mkdir('dataset/optimize_' + outf_key + '/weights')

# Initialize some containers
bkg_list = []
bkg_trees_list = []
hist_list = []
weightsList = []

print("Output file:",myArgs[outfname_index,3])
inputDir =      varsList.inputDir
iFileSig =      TFile.Open( inputDir + myArgs[infname_index,3] )
print("Input file",inputDir + myArgs[infname_index,3])
sigChain =      iFileSig.Get( "ljmet" )

loader = TMVA.DataLoader( "dataset/optimize_" + outf_key )

for var in varList:
  if var[0] == 'NJets_singleLepCalc': loader.AddVariable(var[0],var[1],var[2],'I')
  else: loader.AddVariable(var[0],var[1],var[2],'F')
    
loader.AddSignalTree(sigChain)
  
for i in range(len(varsList.bkg)):
  bkg_list.append(TFile.Open( inputDir + varsList.bkg[i] ))
  print( inputDir + varsList.bkg[i] )
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

######################################################
######################################################
######                                          ######
######         O P T I M I Z A T I O N          ######
######                                          ######
######################################################
######################################################

### Define some static model parameters

PATIENCE =    5
EPOCHS =      10
DROPOUT =     True
NODE_DROP =   False
MODEL_NAME =  "dummy_opt_model.h5"
TAG_NUM =     str(datetime.datetime.now().hour)
TAG =         datetime.datetime.today().strftime('%m-%d') + '(' + TAG_NUM + ')'
LOG_FILE =    open('dataset/optimize_' + outf_key + '/optimize_log_' + TAG + '.txt','w')

### Hyper parameter survey range

HIDDEN =      [1,3]
NODES =       [var_length,var_length*10]
BATCH_POW =   [7,10] # used as 2 ^ BATCH_POW
LRATE =       [1e-4,1e-2]

### Optimization parameters
NCALLS =      2
NSTARTS =     1

space = [
  Integer(HIDDEN[0],      HIDDEN[1],      name = "hidden_layers"),
  Integer(NODES[0],       NODES[1],       name = "initial_nodes"),
  Integer(BATCH_POW[0],   BATCH_POW[1],   name = "batch_power"),
  Real(LRATE[0],          LRATE[1],       name = "learning_rate")
]

def build_custom_model(hidden, nodes, lrate, dropout):
  model = Sequential()
  model.add(Dense(
      nodes,
      input_dim = var_length,
      kernel_initializer = 'glorot_normal',
      activation = 'softplus'
    )
  )
  partition = int( nodes / hidden )
  for i in range(hidden):
    if dropout == True: model.add(Dropout(0.5))
    if NODE_DROP == True:
      model.add(Dense(
          nodes - ( partition * i),
          kernel_initializer = 'glorot_normal',
          activation = 'softplus'
        )
      )
    else:
      model.add(Dense(
          nodes,
          kernel_initializer = 'glorot_normal',
          activation = 'softplus'
        )
      )  
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
  
@use_named_args(space)
def objective(**X):
  print('New configuration: {}'.format(X))
  
  outputfile =    TFile( myArgs[outfname_index,3], "RECREATE" )
  
  model = build_custom_model(
    hidden =  X["hidden_layers"],
    nodes =   X["initial_nodes"],
    lrate =   X["learning_rate"],
    dropout = DROPOUT
  )
  model.save( MODEL_NAME )
  model.summary()  
 
  BATCH_SIZE = int(2 ** X["batch_power"])
  factory_name = 'DNNOptimizer'  
  factory = TMVA.Factory(
    factory_name, outputfile,
    '!V:!ROC:!Silent:Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification'
  )

  factory.SetVerbose(bool( myArgs[verbose_index,3] ))
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

  # Reset the session
  del model
  backend.clear_session()
  backend.reset_uids()
  #TMVA.MethodBase.Delete()
  factory.DeleteAllMethods()
  factory.fMethodsMap.clear()
  
  #TMVA.Results.Delete('dataset/weights/TMVAOpt_'+outf_key+'.root')
  outputfile.Close()
  print("Results stored in {}".format(outputfile.GetName()))
  
  folder = 'dataset/optimize_' + outf_key + '/weights'
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
        print("Removing",file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
        print("Removing",file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' %(file_path, e))
  #file_path = 'dataset/weights/TMVAOpt_' + outf_key + '.root'
  #os.system('rm ' + file_path) 
  
  # Record the optimization iteration
  LOG_FILE.write('{:7}, {:7}, {:7}, {:7}, {:7}\n'.format(
    str(X["hidden_layers"]),
    str(X["initial_nodes"]),
    str(np.around(X["learning_rate"],5)),
    str(BATCH_SIZE),
    str(np.around(ROC,5))
    )
  )
  
  return (1.0 - ROC) # since the optimizer tries to minimize this function and we want a larger ROC value

def main():
  checkRootVer() # check the ROOT version
 
  start_time = time.time()
  LOG_FILE.write('{:7}, {:7}, {:7}, {:7}, {:7}\n'.format(
      'Hidden',
      'Nodes',
      'Rate',
      'Batch',
      'ROC'
    )
  )
  res_gp = gp_minimize(
    func = objective,
    dimensions = space,
    n_calls = NCALLS,
    n_random_starts = NSTARTS,
    verbose = True
  )
  LOG_FILE.close()

  print("Writing optimized parameter log to: dataset/optimize/")
  result_file = open('dataset/optimize_' + outf_key + '/params_' + TAG  + '.txt','w')
  result_file.write('TTTT TMVA DNN Hyper Parameter Optimization Parameters \n')
  result_file.write('Static Parameters:\n')
  result_file.write(' Patience: {}'.format(PATIENCE))
  result_file.write(' Epochs: {}'.format(EPOCHS))
  result_file.write(' Signal, Background: {},{}'.format(NSIG,NBKG))
  result_file.write(' Dropout: {}'.format(DROPOUT))
  result_file.write(' Node Drop: {}'.format(NODE_DROP))
  result_file.write('Parameter Space:\n')
  result_file.write(' Hidden Layers: [{},{}]\n'.format(HIDDEN[0],HIDDEN[1]))
  result_file.write(' Initial Nodes: [{},{}]\n'.format(NODES[0],NODES[1]))
  result_file.write(' Batch Power: [{},{}]\n'.format(BATCH_POW[0],BATCH_POW[1]))
  result_file.write(' Learning Rate: [{},{}]\n'.format(LRATE[0],LRATE[1]))
  result_file.write('Optimized Parameters:\n')
  result_file.write(' Hidden Layers: {}\n'.format(res_gp.x[0]))
  result_file.write(' Initial Nodes: {}\n'.format(res_gp.x[1]))
  result_file.write(' Batch Power: {}\n'.format(res_gp.x[2]))
  result_file.write(' Learning Rate: {}\n'.format(res_gp.x[3]))
  result_file.close()
  print('Finished optimization in: {} s'.format(time.time()-start_time))

main()
os.system("exit")
  

















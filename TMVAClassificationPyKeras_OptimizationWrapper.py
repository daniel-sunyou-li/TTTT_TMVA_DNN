#!/usr/bin/env python

######################################################
######################################################
######                                          ######
######              S T A R T U P               ######
######                                          ######
######################################################
######################################################

import numpy as np
import os, sys, shutil
from subprocess import call
from os.path import isfile
import time, datetime
import getopt
import ROOT
from ROOT import TMVA, TFile, TTree, TCut, TRandom3, gSystem, gApplication, gROOT
import varsList

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.optimizers import Adam
from keras import backend

sys.path.insert(0, "/home/dli50/.local/lib/python2.7/site-packages")

from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

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
  
def printMethods_(methods): # prints a list of the methods being used
  mlist = methods.replace(' ',',').split(',')
  print('=== TMVAClassification: using method(s)...')
  for m in mlist:
    if m.strip() != '':
      print('=== - <%s>'%m.strip())
      
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

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

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

INPUTFILE =     varsList.inputDir + myArgs[infname_index,3]

# Create directory for hyper parameter optimization for # of input variables if it doesn't exit
if not os.path.exists('dataset/optimize_' + outf_key):
  os.mkdir('dataset/optimize_' + outf_key)
  os.mkdir('dataset/optimize_' + outf_key + '/weights')

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

HIDDEN =      [1,5]
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
######################################################
######################################################
######                                          ######
######         M O R E   M E T H O D S          ######
######                                          ######
######################################################
######################################################

@use_named_args(space)
def objective(**X):
  print('New configuration: {}'.format(X))
  
  model = build_custom_model(
    hidden =  X["hidden_layers"],
    nodes =   X["initial_nodes"],
    lrate =   X["learning_rate"],
    dropout = DROPOUT
  )
  model.save( MODEL_NAME )
  model.summary()  
 
  BATCH_SIZE = int(2 ** X["batch_power"])
  
  TEMP_NAME = 'dataset/optimize_' + outf_key + '/temp_file.txt'
  os.system("python TMVAOptimization.py -m {} -e {} -b {} -p {} -i {} -o {} -t {}".format(MODEL_NAME, EPOCHS, BATCH_SIZE, PATIENCE,
    INPUTFILE, outf_key, TEMPFILE))   
  ROC = float(open(TEMP_NAME, 'r').read())
  os.system("rm {}".format(TEMP_NAME))
    
  # Reset the session
  del model
  backend.clear_session()
  backend.reset_uids()
  
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

  print("Writing optimized parameter log to: dataset/optimize_" + outf_key)
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
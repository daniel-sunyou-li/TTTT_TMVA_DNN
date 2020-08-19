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

os.environ['KERAS_BACKEND'] = 'tensorflow'

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras import backend

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

DEFAULT_DATASET       = "dataset"
DEFAULT_NVARS         = 20
DEFAULT_WHERE         = "lpc"
DEFAULT_YEAR          = 2017
DEFAULT_OPTION        = 1

myArgs = np.array([ # Stores the command line arguments 
  ['-v','--verbose','verbose',        True],                
  ['-w','--where','where',            DEFAULT_WHERE],
  ['-y','--year','year',              DEFAULT_YEAR],
  ['-o','--option','option',          DEFAULT_OPTION],
  ['-d','--dataset','dataset',        DEFAULT_DATASET],
  ['-n','--nvars','nvars',            DEFAULT_NVARS]
])    

try: # retrieve command line options
  shortopts   = "w:y:o:d:n:vh?" # possible command line options
  longopts    = [
                 "verbose=",
                 "where=",
                 "year=",
                 "option=",
                 "dataset=",
                 "nvars=",
                 "help",
                 "usage"
  ]
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

# Initialize some variables after reading in arguments
verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]  
where_index = np.where(myArgs[:,2] == 'where')[0][0]
year_index = np.where(myArgs[:,2] == 'year')[0][0]
option_index = np.where(myArgs[:,2] == 'option')[0][0]
nvars_index = np.where(myArgs[:,2] == 'nvars')[0][0]
dataset_index = np.where(myArgs[:,2] == 'dataset')[0][0]
        
option = myArgs[option_index,3]
numVars = int(myArgs[nvars_index,3])
where = myArgs[where_index,3]
year = int(myArgs[year_index,3])
dataset = str(myArgs[dataset_index,3])

# import scikit optimize

if where == "brux":
  sys.path.insert(0, "/home/{}/.local/lib/python2.7/site-packages".format(bruxUserName)) # add if on BRUX, LPC adds path automatically

from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
             
outf_key = str("Keras_" + str(numVars) + "vars")

# Create directory for hyper parameter optimization for # of input variables if it doesn't exit
if not os.path.exists(dataset + "/optimize_" + outf_key):
  os.mkdir(dataset + "/optimize_" + outf_key)
  os.mkdir(dataset + "/optimize_" + outf_key + "/weights")

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
  print("  -o | --option     : variable importance option")
  print("  -d | --dataset    : directory containing variable importance results")
  print("  -w | --where      : where the script is being run (LPC or BRUX)")
  print("  -y | --year       : production year (2017 or 2018)")
  print("  -n | --nvars      : number of input variables to use (in order)")
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
   
def build_custom_model(hidden, nodes, lrate, regulator, pattern, activation):
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

def getRankedInputs(importancePath,outPath,varList,numVars,option):
  numVarsFull = len(varList)
  variableList = []
  valueList = []
  start_reading = False
  importanceFile = open(importancePath + "/VariableImportanceResults_" + str(numVarsFull) + "vars_opt" + str(option) + ".txt")
  for line in importanceFile.readlines():
    if start_reading == True:
      content = line.split("/")
      if option == 1:
        variableList.append(content[0].split(".")[1].strip())
        valueList.append(float(content[4].strip()))
      else:
        variableList.append(content[0].split(".")[1].strip())
        valueList.append(float(content[2].strip()))
    if "Variable Name" in line: start_reading = True
  
  rankedValues, rankedVariables = zip(*sorted(zip(
    valueList, variableList
  )))
  if "varsListHPO.txt" in os.listdir(outPath): os.system("rm {}/varsListHPO.txt".format(outPath))
  varsListHPO = open(outPath + "/varsListHPO.txt","w")
  varsListHPO.write("Sum Variable Importance Significance = {}\n".format(np.sum(rankedValues[-numVars:])))
  varsListHPO.write("Variable List:\n")
  for variable in rankedVariables[-numVars:]:
    varsListHPO.write("{}\n".format(variable))
  varsListHPO.close()
  return rankedVariables[-numVars:]

# new variable list with reduced size to be used in TMVAClassification_Optimization.py
varList = getRankedInputs(os.getcwd() + "/" + dataset, os.getcwd() + "/" + dataset + "/optimize_" + outf_key,varsList.varList["DNN"],int(numVars),int(option))

######################################################
######################################################
######                                          ######
######         O P T I M I Z A T I O N          ######
######                                          ######
######################################################
######################################################

### Define some static model parameters

epochs		  = "15"
patience	  = 5
modelName  	= "dummy_opt_model.h5"
tagNum   	  = str(datetime.datetime.now().hour)
tag		      = datetime.datetime.today().strftime('%m-%d') + '(' + tagNum + ')'
logFile 	  = open(dataset + "/optimize_" + outf_key + "/optimize_log_" + tag + ".txt","w")

### Hyper parameter survey range

HIDDEN =      [1,3]
NODES =       [numVars,numVars*10]
PATTERN =     ['static', 'dynamic']
BATCH_POW =   [8,11] # used as 2 ^ BATCH_POW
LRATE =       [1e-5,1e-2]
REGULATOR =   ['none', 'dropout', 'normalization', 'both']
ACTIVATION =  ['relu','softplus','elu']

### Optimization parameters
NCALLS =      50
NSTARTS =     30

space = [
  Integer(HIDDEN[0],       HIDDEN[1],                     name = "hidden_layers"),
  Integer(NODES[0],        NODES[1],                      name = "initial_nodes"),
  Integer(BATCH_POW[0],    BATCH_POW[1],                  name = "batch_power"),
  Real(LRATE[0],           LRATE[1],       "log-uniform", name = "learning_rate"),
  Categorical(PATTERN,                                    name = "node_pattern"),
  Categorical(REGULATOR,                                  name = "regulator"),
  Categorical(ACTIVATION,                                 name = "activation_function")
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
    hidden =        X["hidden_layers"],
    nodes =         X["initial_nodes"],
    lrate =         X["learning_rate"],
    regulator =     X["regulator"],
    pattern =       X["node_pattern"],
    activation =    X["activation_function"]
  )
  model.save( modelName )
  model.summary()  
 
  batchSize = str(2 ** X["batch_power"])
  commandString = "python TMVAClassification_Optimization.py -o {} -b {} -e {} -w {} -y {} -d {}".format(
    outf_key,
    batchSize,
    epochs,
    where,
    year,
    dataset
  )
  os.system(commandString)  
  temp_name = "dataset/temp_file.txt"
  ROC = float(open(temp_name, "r").read())
    
  # Reset the session
  del model
  backend.clear_session()
  backend.reset_uids()
  
  # Record the optimization iteration
  logFile.write('{:7}, {:7}, {:7}, {:7}, {:9}, {:14}, {:10}, {:7}\n'.format(
    str(X["hidden_layers"]),
    str(X["initial_nodes"]),
    str(np.around(X["learning_rate"],5)),
    str(batchSize),
    str(X["node_pattern"]),
    str(X["regulator"]),
    str(X["activation_function"]),
    str(np.around(ROC,5))
    )
  )
  opt_metric = (1.0 - ROC)
  print("Optimization metric value obtained = {:.5f}".format(opt_metric))
  os.system("rm dataset/temp_file.txt")
  return opt_metric # since the optimizer tries to minimize this function and we want a larger ROC value

def main():
  checkRootVer() # check the ROOT version
 
  start_time = time.time()
  logFile.write('{:7}, {:7}, {:7}, {:7}, {:9}, {:14}, {:10}, {:7}\n'.format(
      'Hidden',
      'Nodes',
      'Rate',
      'Batch',
      'Pattern',
      'Regulator',
      'Activation',
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
  result_file = open('dataset/optimize_' + outf_key + '/params_' + tag  + '.txt','w')
  result_file.write('TTTT TMVA DNN Hyper Parameter Optimization Parameters \n')
  result_file.write('Static Parameters:\n')
  result_file.write(' Patience: {}\n'.format(patience))
  result_file.write(' Epochs: {}\n'.format(epochs))
  result_file.write('Parameter Space:\n')
  result_file.write(' Hidden Layers: [{},{}]\n'.format(HIDDEN[0],HIDDEN[1]))
  result_file.write(' Initial Nodes: [{},{}]\n'.format(NODES[0],NODES[1]))
  result_file.write(' Batch Power: [{},{}]\n'.format(BATCH_POW[0],BATCH_POW[1]))
  result_file.write(' Learning Rate: [{},{}]\n'.format(LRATE[0],LRATE[1]))
  result_file.write(' Pattern: {}\n'.format(PATTERN))
  result_file.write(' Activation: {}\n'.format(ACTIVATION))
  result_file.write(' Regulator: {}\n'.format(REGULATOR))
  result_file.write('Optimized Parameters:\n')
  result_file.write(' Hidden Layers: {}\n'.format(res_gp.x[0]))
  result_file.write(' Initial Nodes: {}\n'.format(res_gp.x[1]))
  result_file.write(' Batch Power: {}\n'.format(res_gp.x[2]))
  result_file.write(' Learning Rate: {}\n'.format(res_gp.x[3]))
  result_file.write(' Node Pattern: {}\n'.format(res_gp.x[4]))
  result_file.write(' Regulator: {}\n'.format(res_gp.x[5]))
  result_file.write(' Activation Function: {}\n'.format(res_gp.x[6]))
  result_file.close()
  print('Finished optimization in: {} s'.format(time.time()-start_time))


main()
os.system("exit")
=======
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

os.environ['KERAS_BACKEND'] = 'tensorflow'

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras import backend

os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

######################################################
######################################################
######                                          ######
######       R E A D   A R G U M E N T S        ######
######                                          ######
######################################################
######################################################

DEFAULT_DATASET       = "dataset"
DEFAULT_NVARS         = 20
DEFAULT_WHERE         = "lpc"
DEFAULT_YEAR          = 2017
DEFAULT_OPTION        = 1

myArgs = np.array([ # Stores the command line arguments 
  ['-v','--verbose','verbose',        True],                
  ['-w','--where','where',            DEFAULT_WHERE],
  ['-y','--year','year',              DEFAULT_YEAR],
  ['-o','--option','option',          DEFAULT_OPTION],
  ['-d','--dataset','dataset',        DEFAULT_DATASET],
  ['-n','--nvars','nvars',            DEFAULT_NVARS]
],dtype=object)    

try: # retrieve command line options
  shortopts   = "w:y:o:d:n:vh?" # possible command line options
  longopts    = [
                 "verbose=",
                 "where=",
                 "year=",
                 "option=",
                 "dataset=",
                 "nvars=",
                 "help",
                 "usage"
  ]
  opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
except getopt.GetoptError: # output error if command line argument invalid
  print("ERROR: unknown options in argument %s" %sys.argv[1:])
  sys.exit(1)
for opt, arg in opts:
  if opt in myArgs[:,0] or opt in myArgs[:,1]:
    index = np.where(myArgs[:,0] == opt)[0][0] # np.where returns a tuple of arrays
    myArgs[index,3] = arg # override the variables with the command line argument
    print(myArgs[index,3])

# Initialize some variables after reading in arguments
verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]  
where_index = np.where(myArgs[:,2] == 'where')[0][0]
year_index = np.where(myArgs[:,2] == 'year')[0][0]
option_index = np.where(myArgs[:,2] == 'option')[0][0]
nvars_index = np.where(myArgs[:,2] == 'nvars')[0][0]
dataset_index = np.where(myArgs[:,2] == 'dataset')[0][0]
        
option = myArgs[option_index,3]
numVars = int(myArgs[nvars_index,3])
where = myArgs[where_index,3]
year = int(myArgs[year_index,3])
dataset = str(myArgs[dataset_index,3])
# import scikit optimize

if where == "brux":
  sys.path.insert(0, "/home/{}/.local/lib/python2.7/site-packages".format(bruxUserName)) # add if on BRUX, LPC adds path automatically

from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
             
outf_key = str("Keras_" + str(numVars) + "vars")

# Create directory for hyper parameter optimization for # of input variables if it doesn't exit
if not os.path.exists(dataset + "/optimize_" + outf_key):
  os.mkdir(dataset + "/optimize_" + outf_key)
  os.mkdir(dataset + "/optimize_" + outf_key + "/weights")

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
  print("  -o | --option     : variable importance option")
  print("  -d | --dataset    : directory containing variable importance results")
  print("  -w | --where      : where the script is being run (LPC or BRUX)")
  print("  -y | --year       : production year (2017 or 2018)")
  print("  -n | --nvars      : number of input variables to use (in order)")
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
   
def build_custom_model(hidden, nodes, lrate, regulator, pattern, activation):
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

def getRankedInputs(importancePath,outPath,varList,numVars,option):
  numVarsFull = len(varList)
  variableList = []
  valueList = []
  start_reading = False
  importanceFile = open(importancePath + "/VariableImportanceResults_" + str(numVarsFull) + "vars_opt" + str(option) + ".txt")
  for line in importanceFile.readlines():
    if start_reading == True:
      content = line.split("/")
      if option == 1:
        variableList.append(content[0].split(".")[1].strip())
        valueList.append(float(content[4].strip()))
      else:
        variableList.append(content[0].split(".")[1].strip())
        valueList.append(float(content[2].strip()))
    if "Variable Name" in line: start_reading = True
  
  rankedValues, rankedVariables = zip(*sorted(zip(
    valueList, variableList
  )))
  if "varsListHPO.txt" in os.listdir(outPath): os.system("rm {}/varsListHPO.txt".format(outPath))
  varsListHPO = open(outPath + "/varsListHPO.txt","w")
  varsListHPO.write("Sum Variable Importance Significance = {}\n".format(np.sum(rankedValues[-numVars:])))
  varsListHPO.write("Variable List:\n")
  for variable in rankedVariables[-numVars:]:
    varsListHPO.write("{}\n".format(variable))
  varsListHPO.close()
  return rankedVariables[-numVars:]

# new variable list with reduced size to be used in TMVAClassification_Optimization.py
varList = getRankedInputs(os.getcwd() + "/" + dataset, os.getcwd() + "/" + dataset + "/optimize_" + outf_key,varsList.varList["DNN"],int(numVars),int(option))

######################################################
######################################################
######                                          ######
######         O P T I M I Z A T I O N          ######
######                                          ######
######################################################
######################################################

### Define some static model parameters

epochs		  = "15"
patience	  = 5
modelName  	= "dummy_opt_model.h5"
tagNum   	  = str(datetime.datetime.now().hour)
tag		      = datetime.datetime.today().strftime('%m-%d') + '(' + tagNum + ')'
logFile 	  = open(dataset + "/optimize_" + outf_key + "/optimize_log_" + tag + ".txt","w")

### Hyper parameter survey range

HIDDEN =      [1,3]
NODES =       [numVars,numVars*10]
PATTERN =     ['static', 'dynamic']
BATCH_POW =   [8,11] # used as 2 ^ BATCH_POW
LRATE =       [1e-5,1e-2]
REGULATOR =   ['none', 'dropout', 'normalization', 'both']
ACTIVATION =  ['relu','softplus','elu']

### Optimization parameters
NCALLS =      5
NSTARTS =     3

space = [
  Integer(HIDDEN[0],       HIDDEN[1],                     name = "hidden_layers"),
  Integer(NODES[0],        NODES[1],                      name = "initial_nodes"),
  Integer(BATCH_POW[0],    BATCH_POW[1],                  name = "batch_power"),
  Real(LRATE[0],           LRATE[1],       "log-uniform", name = "learning_rate"),
  Categorical(PATTERN,                                    name = "node_pattern"),
  Categorical(REGULATOR,                                  name = "regulator"),
  Categorical(ACTIVATION,                                 name = "activation_function")
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
    hidden =        X["hidden_layers"],
    nodes =         X["initial_nodes"],
    lrate =         X["learning_rate"],
    regulator =     X["regulator"],
    pattern =       X["node_pattern"],
    activation =    X["activation_function"]
  )
  model.save( modelName )
  model.summary()  
 
  batchSize = str(2 ** X["batch_power"])
  commandString = "python TMVAClassification_Optimization.py -o {} -b {} -e {} -w {} -y {} -d {}".format(
    outf_key,
    batchSize,
    epochs,
    where,
    year,
    dataset
  )
  os.system(commandString)  
  temp_name = dataset+"/temp_file.txt"
  ROC = float(open(temp_name, "r").read())
    
  # Reset the session
  del model
  backend.clear_session()
  backend.reset_uids()
  
  # Record the optimization iteration
  logFile.write('{:7}, {:7}, {:7}, {:7}, {:9}, {:14}, {:10}, {:7}\n'.format(
    str(X["hidden_layers"]),
    str(X["initial_nodes"]),
    str(np.around(X["learning_rate"],5)),
    str(batchSize),
    str(X["node_pattern"]),
    str(X["regulator"]),
    str(X["activation_function"]),
    str(np.around(ROC,5))
    )
  )
  opt_metric = (1.0 - ROC)
  print("Optimization metric value obtained = {:.5f}".format(opt_metric))
  os.system("rm dataset/temp_file.txt")
  return opt_metric # since the optimizer tries to minimize this function and we want a larger ROC value

def main():
  checkRootVer() # check the ROOT version
 
  start_time = time.time()
  logFile.write('{:7}, {:7}, {:7}, {:7}, {:9}, {:14}, {:10}, {:7}\n'.format(
      'Hidden',
      'Nodes',
      'Rate',
      'Batch',
      'Pattern',
      'Regulator',
      'Activation',
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
  result_file = open('dataset/optimize_' + outf_key + '/params_' + tag  + '.txt','w')
  result_file.write('TTTT TMVA DNN Hyper Parameter Optimization Parameters \n')
  result_file.write('Static Parameters:\n')
  result_file.write(' Patience: {}\n'.format(patience))
  result_file.write(' Epochs: {}\n'.format(epochs))
  result_file.write('Parameter Space:\n')
  result_file.write(' Hidden Layers: [{},{}]\n'.format(HIDDEN[0],HIDDEN[1]))
  result_file.write(' Initial Nodes: [{},{}]\n'.format(NODES[0],NODES[1]))
  result_file.write(' Batch Power: [{},{}]\n'.format(BATCH_POW[0],BATCH_POW[1]))
  result_file.write(' Learning Rate: [{},{}]\n'.format(LRATE[0],LRATE[1]))
  result_file.write(' Pattern: {}\n'.format(PATTERN))
  result_file.write(' Activation: {}\n'.format(ACTIVATION))
  result_file.write(' Regulator: {}\n'.format(REGULATOR))
  result_file.write('Optimized Parameters:\n')
  result_file.write(' Hidden Layers: {}\n'.format(res_gp.x[0]))
  result_file.write(' Initial Nodes: {}\n'.format(res_gp.x[1]))
  result_file.write(' Batch Power: {}\n'.format(res_gp.x[2]))
  result_file.write(' Learning Rate: {}\n'.format(res_gp.x[3]))
  result_file.write(' Node Pattern: {}\n'.format(res_gp.x[4]))
  result_file.write(' Regulator: {}\n'.format(res_gp.x[5]))
  result_file.write(' Activation Function: {}\n'.format(res_gp.x[6]))
  result_file.close()
  print('Finished optimization in: {} s'.format(time.time()-start_time))


main()
os.system("exit")
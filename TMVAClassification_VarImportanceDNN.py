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


from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam


os.system('bash')
os.system('source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh')

# weight calculation equation
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

# cut calculation equation
cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && ((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
cutStrS = cutStrC # + " && ( isTraining == 1 || isTraining == 2 )"
cutStrB = cutStrC

# default command line arguments
DEFAULT_METHODS		  = "Keras" 			        # how was the .root file trained
DEFAULT_OUTFNAME	  = "dataset/weights/TMVA.root" 	# this file to be read
DEFAULT_INFNAME		  = "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"
DEFAULT_TREESIG		  = "TreeS"
DEFAULT_TREEBKG		  = "TreeB"
DEFAULT_NTREES		  = "400"
DEFAULT_MDEPTH		  = "2"
DEFAULT_MASS		  = "180"
DEFAULT_SEED              = 1
DEFAULT_VARLISTKEY        = "BigComb"

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
  print("  -n | --nTrees : amount of trees for BDT study (default: '%s')" %DEFAULT_NTREES)
  print("  -d | --maxDepth : maximum depth for BDT study (default: '%s')" %DEFAULT_MDEPTH)
  print("  -k | --mass : mass of the signal (default: '%s')" %DEFAULT_MASS)
  print("  -l | --varListKey : BDT input variable list (default: '%s')" %DEFAULT_VARLISTKEY)
  print("  -t | --inputtrees : input ROOT Trees for signal and background (default: '%s %s')" \
        % (DEFAULT_TREESIG, DEFAULT_TREEBKG))
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
  try: # retrieve command line options
    shortopts   = "m:i:n:d:k:l:t:o:s:vh?" # possible command line options
    longopts    = ["methods=", 
                   "inputfile=",
                   "nTrees=",
                   "maxDepth=",
                   "mass=",
                   "varListKey=",
                   "inputtrees=",
                   "outputfile=",
                   "verbose",
		   "seed=",
                   "help",
                   "usage"]
    opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts ) # associates command line inputs to variables
  
  except getopt.GetoptError: # output error if command line argument invalid
    print("ERROR: unknown options in argument %s" %sys.argv[1:])
    usage()
    sys.exit(1)
  
  myArgs = np.array([ # Stores the command line arguments
    ['-m','--methods','methods',        DEFAULT_METHODS],     #0  Reference Indices
    ['-d','--maxDepth','mDepth',        DEFAULT_MDEPTH],      #1
    ['-k','--mass','mass',              DEFAULT_MASS],        #2
    ['-l','--varListKey','varListKey',  DEFAULT_VARLISTKEY],  #3
    ['-i','--inputfile','infname',      DEFAULT_INFNAME],     #4
    ['-o','--outputfile','outfname',    DEFAULT_OUTFNAME],    #5
    ['-n','--nTrees','nTrees',          DEFAULT_NTREES],      #6
    ['-t','--inputtrees','inputtrees',  DEFAULT_NTREES],      #7
    ['-v','--verbose','verbose',        True],                #8
    ['-s','--seed','SeedN',             DEFAULT_SEED],        #9
    ['','','treeNameSig',               DEFAULT_TREESIG],     #10  No command line option
    ['','','treeNameBkg',               DEFAULT_TREEBKG]     #11  No command line option]
  ])
  
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
    if opt in ("-?", "-h", "--help", "--usage"): # provides command line help
      usage()
      sys.exit(0)
  
  # Initialize some variables after reading in arguments
  varListKey_index = np.where(myArgs[:,2] == 'varListKey')[0][0]
  mDepth_index = np.where(myArgs[:,2] == 'mDepth')[0][0]
  method_index = np.where(myArgs[:,2] == 'methods')[0][0]
  SeedN_index = np.where(myArgs[:,2] == 'SeedN')[0][0]
  infname_index = np.where(myArgs[:,2] == 'infname')[0][0]
  outfname_index = np.where(myArgs[:,2] == 'outfname')[0][0]
  verbose_index = np.where(myArgs[:,2] == 'verbose')[0][0]
 
  str_xbitset = '{:06b}'.format(long(myArgs[SeedN_index,3]))

  varList = varsList.varList[myArgs[varListKey_index,3]]
  nVars = str(str_xbitset.count('1')) + 'vars'
  var_length = len(varList)
  outf_key = str(myArgs[method_index,3] +  '_' + myArgs[varListKey_index,3] + '_' + nVars + '_mDepth' + myArgs[mDepth_index,3])
  myArgs[outfname_index,3] = 'dataset/weights/TMVA_' + outf_key + '.root'   

  outputfile = TFile( myArgs[outfname_index,3], 'RECREATE' ) 

  print("Outputfile: " + myArgs[outfname_index,3])

  checkRootVer() # check that ROOT version is correct 

#####################################################
#####################################################
######                                         ######
######            K E R A S   D N N            ######
######                                         ######
#####################################################
#####################################################                         

  model_name = 'TTTT_TMVA_model.h5'

  model = Sequential()
  model.add(Dense(100, activation = 'softplus', input_dim = str_xbitset.count('1')))
  model.add(Dense(100, activation = 'softplus'))
  model.add(Dense(100, activation = 'softplus'))
  model.add(Dense(100, activation = 'softplus'))
  model.add(Dense(2, activation = 'sigmoid'))

  model.compile(
	loss = 'categorical_crossentropy',
	optimizer = Adam(),
	metrics = ['accuracy']
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
  bkg_list = []
  bkg_trees_list = []
  hist_list = []
  weightsList = []
  signalWeight = 1
  
  # Setting up TMVA
  
  print( 'str_xbitset is : ' + str_xbitset )
  loader = TMVA.DataLoader(str_xbitset)
  
  index = len(varList) - 1

  for var in varList:
    if (str_xbitset[index] == '1'):
      loader.AddVariable(var[0], var[1], var[2], 'F')
      #print('Testing variable: ' + str(var[0]))
    index = index - 1
  
  (TMVA.gConfig().GetIONames()).fWeightFileDir = "weights/" + outf_key
   
  inputDir = varsList.inputDir # get current input directory path
  iFileSig = TFile.Open(inputDir + myArgs[infname_index,3])
  #print("Input directory path: " + inputDir + myArgs[infname_index,3])
  sigChain = iFileSig.Get("ljmet") 
 
  loader.AddSignalTree(sigChain)
  
  bkgList = varsList.bkg
  
  for i in range(len(varsList.bkg)):
    bkg_list.append(TFile.Open(inputDir + bkgList[i]))
    #print( inputDir + varsList.bkg[i] )
    bkg_trees_list.append(bkg_list[i].Get("ljmet"))
    bkg_trees_list[i].GetEntry(0)
  
    if bkg_trees_list[i].GetEntries() == 0:
      continue
    loader.AddBackgroundTree( bkg_trees_list[i], 1 )
   
  # Set up TMVA
  ROOT.TMVA.Tools.Instance()
  ROOT.TMVA.PyMethodBase.PyInitialize()

  fClassifier = TMVA.Factory( 'VariableImportance', outputfile,
       '!V:!ROC:!ModelPersistence:!Silent:Color:!DrawProgressBar:AnalysisType=Classification' )

  fClassifier.SetVerbose(bool( myArgs[verbose_index,3] ) )


  
  # set signal and background weights 
  loader.SetSignalWeightExpression( weightStrS )
  loader.SetBackgroundWeightExpression( weightStrB )
  
  # set cut thresholds for signal and background
  mycutSig = TCut( cutStrS )
  mycutBkg = TCut( cutStrB )

  loader.PrepareTrainingAndTestTree(
    mycutSig, mycutBkg,
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
  )

  kerasSetting = 'H:!V:VarTransform=G:FilenameModel=' + model_name + ':NumEpochs=10:BatchSize=1028' # the trained model has to be specified in this string
  
  # run the classifier
  fClassifier.BookMethod(loader,
    TMVA.Types.kPyKeras,
    'PyKeras',
    kerasSetting)
  print('Training all methods...')
  fClassifier.TrainAllMethods()
  print('Testing all methods...')
  fClassifier.TestAllMethods()
  print('Evaluating all methods...')
  fClassifier.EvaluateAllMethods()
  
  SROC = fClassifier.GetROCIntegral(str_xbitset, "PyKeras")
  print("ROC-integral: " + str_xbitset + " " + SROC)
  print("Seed: " + str_xbitset + " DONE")
  fClassifier.DeleteAllMethods()
  fClassifier.fMethodsMap.clear()
  
  outputfile.Close()

  print("===================================")
  print("===================================")


main()
os.system('exit')

#!/usr/bin/env python

import os, sys
import numpy as np
import getopt
import random
import ROOT
import itertools
from ROOT import TMVA, TFile, TTree, TCut
from ROOT import gSystem, gApplication, gROOT
import varsList

# methods

def condorJob(SeedN="",SubSeedN="",count=0,options=['','','']): # submits a single condor job
    runDir = options[0]
    condorDir = options[1]
    numVars = options[2]
    SubmitSeedN = ""
    if SubSeedN == "": 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN)
        SubmitSeedN = SeedN
    else: 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN) + "_Subseed_" + str(SubSeedN)
        SubmitSeedN = SubSeedN
    dict = {
        "RUNDIR": runDir,           # run directory
        "METHOD": "Keras",          # tmva method, should be "Keras"
        "SubmitSeedN": SubmitSeedN,
        "TAG": str(count),
        "FILENAME": fileName
    }
    jdfName = condorDir + "%(FILENAME)s.job"%dict
    jdf = open(jdfName, "w")
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/submitCondorVariableImportance.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 4025
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(TAG)s %(SubmitSeedN)s
Queue 1"""%dict)
    jdf.close()
    os.chdir("%s/"%(condorDir))
    os.system("condor_submit %(FILENAME)s.job"%dict)
    os.system("sleep 0.5")
    os.chdir("%s"%(runDir))
    
    count += 1
    print("{} jobs submitted.".format(count))
    return count
    
def submitSeedJob(SeedN,used_seeds,count,options): # submits seed job and corresponding subseed jobs
    numVars = options[2]
    used_seeds.append(SeedN)
    count = condorJob(str(SeedN),count=count,options=options)
    for num in range(0, numVars):
        if(SeedN & (1 << num)):
            SubSeedN = SeedN & ~(1 << num)
            count = condorJob(str(SeedN),str(SubSeedN),count,options) 
    return used_seeds, count

def getCorrelationMatrix(sigFile, bkgFile, weightStr, cutStr, varList): # gets the correlation matrix as np array
    varNames = []
    loader = TMVA.DataLoader("dataset")
    for var in varList:
        if var[0] in "NJets_MultiLepCalc": loader.Addvariable( var[0], var[1], var[2], "I" )
        else:                               loader.AddVariable( var[0], var[1], var[2], "F" )
        varNames.append(var[0])
    
    # open the root files
    input_sig = TFile.Open(sigFile)
    signal = input_sig.Get("ljmet")
    input_bkg = TFile.Open(bkgFile)
    background = input_bkg.Get("ljmet")
    
    # load in the trees 
    loader.AddSignalTree( signal )
    loader.fTreeS = signal
    loader.AddBackgroundTree( background )
    loader.fTreeB = background
    
    # set weights
    loader.SetSignalWeightExpression( weightStr )
    loader.SetBackgroundWeightExpression( weightStr )
    
    # set cuts
    loader.PrepareTrainingAndTestTree(
        cutStr, cutStr,
        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
    )
    
    # set the pointer to the right histogram
    loader.GetDefaultDataSetInfo().GetDataSet().GetEventCollection()
    
    # retrieve the signal correlation matrix
    sig_th2 = loader.GetCorrelationMatrix("Signal")
    # bkg_th2 = loader.GetCorrelationMatrix("Background")
    
    # convert to numpy array
    n_bins = sig_th2.GetNbinsX()
    sig_corr = np.zeros((n_bins,n_bins))
    
    for x in range(n_bins):
        for y in range(n_bins):
            sig_corr[x,y] = sig_th2.GetBinContent(x+1,y+1)
    
    return sig_corr, varNames
          
def seedReplace(bitstring,val,indices):
    new_bitstring = bitstring
    for index in indices:
        new_bitstring = new_bitstring[:index] + str(val) + new_bitstring[index+1:]
    return new_bitstring

os.system("bash")
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()


# lists
inputDir = varsList.inputDir            # string for path to ljmet samples
varList = varsList.varList["BigComb"]   # contains all the input variables
corr_seeds = []                         # stores seeds generated for high correlation consideration
used_seeds = []                         # stores which seeds have been used
options = [                             # contains arguments for condor job submission functions
    os.getcwd(),
    os.getcwd() + "/condor_log/",
    len(varList)
]

# variable parameters
method = "Keras"    
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && ((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
binary_str = "1" * len(varList)         # bitstring full of '1' 
max_int = int(binary_str,2)             # integer corresponding to bitstring full of '1'
corr_cut = 80                           # set this between 0 and 100
maxSeeds = 100                          # maximum number of generated seeds
count = 0                               # counts the number of jobs submitted
correlation_option = 1                  # default option (1 = manual seed generation, 2 = corr. var. exclusion)

try:
    shortopts = "o"
    longopts = [
        "correlation_option"
    ]
    opt, arg = getopt.getopt( sys.argv[1:], shortopts, longopts)
    correlation_option = arg
except getopt.GetoptError: sys.exit(1)


# get the signal correlation matrix and the variable names, used in correlation options
sig_corr, varNames = getCorrelationMatrix(
    inputDir + "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root",
    inputDir + varsList.bkg[0],     # choose a random background sample since we only care about signal
    weightStrC,
    TCut(cutStrC),
    varList
)

print("Using {} inputs...".format(len(varNames)))

# generate seeds to test based on correlation coefficients

if correlation_option == 1 or 2:
    corr_group = {}                 # holds all the correlated groups
    # generate the seeds by searching for correlated variables above the threshold
    for i in range(len(varList)):        
      corr_group[i] = [i]
      for j in np.arange(i+1 , len(varList)):
        if abs(sig_corr[i,j]) >= corr_cut:
          print("{} and {} are {} % correlated.".format(
            varNames[i],varNames[j],sig_corr[i,j]
            )
          )
          corr_group[i].append(j)
      if len(corr_group[i]) > 1:
        tot_diff = np.sum(2**np.array(corr_group[i]))
        for var in corr_group[i]:
          this_group = np.array(corr_group[i])
          new_mask = this_group != var
          new_seed = seedReplace(binary_str,0,this_group[new_mask]) # set variables that aren't val to 0
          corr_seeds.append(int(new_seed,2)) # convert from int to binary string
      else:
        del corr_group[i] # we want correlation group to only contain identified highly correlated variables
    print("Manually generated {} seeds using a threshold of {}.".format(len(corr_seeds),corr_cut))
    if correlation_option == 1:
        print("Using correlation option 1: seed generation.")
        for seed in set(corr_seeds): # submit the generated seed jobs here
          used_seeds, count = submitSeedJob(seed,used_seeds,count,options)
    elif correlation_option == 2:
        print("Using correlation option 1: input variable exclusion.")
        corr_seeds.clear()


# submit remaining randomly generated seed jobs

while len(used_seeds) < (min(len(varList)*len(varList),maxSeeds) - len(corr_seeds)):
  SeedN = random.randint(0,int(binary_str,2))
  this_seed = '{:0{}b}'.format(SeedN,len(varList))
  var_count = this_seed.count('1')
  if (SeedN not in used_seeds) and (var_count > 1): # only use unique seeds
    if correlation_option == 2:
      new_seeds = []
      corr_pairs = []
      for pair_key in corr_group:
        corr_pairs.append(corr_group[pair_key])
      string_combs = list(itertools.product(*corr_pairs))
      for comb in string_combs:
        new_seeds.append(int(seedReplace(this_seed,0,comb),2))
      for seed in new_seeds:
        used_seeds, count = submitSeedJob(seed,used_seeds,count,options)
    else:
      used_seeds, count = submitSeedJob(SeedN,used_seeds,count,options)

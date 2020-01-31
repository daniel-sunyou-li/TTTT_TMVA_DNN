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
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3 GB
request_cpus = 4
request_disk = 40 GB
image_size = 3 GB
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
    
def getCorrelatedPairs(corrMatrix,corrCut,varNames):
    correlated_paris = {}
    for i in np.arange(np.shape(corrMatrix)[0] - 1):
        correlated_pairs[i] = [i]
        for j in np.arange(i+1,np.shape(corrMatrix)[1]):
            if abs(corrMatrix[i,j]) >= corrCut:
                print("{} and {} are {:.2f} % correlated.".format(
                    varNames[i], varNames[j], 100*corrMatrix[i,j]
                    )
                )
                correlated_pairs.append(j)
        if len(correlated_pairs[i]) == 1: del correlated_pairs[i]
    return correlated_pairs

def generateUncorrSeeds(seed,correlated_pairs):
    new_seeds = []
    correlated_pair_list = []
    for pair_key in correlated_pairs:
        correlated_pairs_list.append(correlated_pairs[pair_key])
    correlation_combos = list(itertools.product(*correlated_pairs_list))
    for combo in correlation_combos:
        new_seeds.append((seedReplace(seed,0,combo)))
    return new_seeds
    
os.system("bash")
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# lists
inputDir = varsList.inputDir            # string for path to ljmet samples
varList = varsList.varList["BigComb"]   # contains all the input variables
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
maxSeeds = 60                           # maximum number of generated seeds
count = 0                               # counts the number of jobs submitted

# get the signal correlation matrix and the variable names, used in correlation options
sig_corr, varNames = getCorrelationMatrix(
    inputDir + "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root",
    inputDir + varsList.bkg[0],     # choose a random background sample since we only care about signal
    weightStrC,
    TCut(cutStrC),
    varList
)

print("Using {} inputs...".format(len(varNames)))

# submit jobs

correlated_pairs = getCorrelatedPairs(sig_corr, corr_cut, varNames)

while len(used_seeds) < maxSeeds:
    NewSeed = random.randint(0,int(binary_str,2))
    NewSeedStr = '{:0{}b}'.format(NewSeed,len(varList))
    gen_seeds = generateUncorrSeeds(NewSeedStr,correlated_pairs)
    for gen_seed in gen_seeds:
        var_count = gen_seed.count("1")
        if ( gen_seed not in used_seeds ) and ( var_count > 1 ):
            used_seeds, count = submitSeedJob(int(gen_seed,2),used_seeds,count,options)

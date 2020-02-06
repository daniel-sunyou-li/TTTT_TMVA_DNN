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

def condor_job(SeedN="",SubSeedN="",count=0,options=['','',''],maxSeeds=0): # submits a single condor job
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
        "SubmitSeedN": SubmitSeedN,
        "FILENAME": fileName
    }
    jdfName = condorDir + "%(FILENAME)s.job"%dict
    jdf = open(jdfName, "w")
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/VariableImportanceLPC_step2.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 4 GB
request_cpus = 4
request_disk = 40 GB
image_size = 4 GB
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(SubmitSeedN)s
Queue 1"""%dict)
    jdf.close()
    os.chdir("%s/"%(condorDir))
    os.system("condor_submit %(FILENAME)s.job"%dict)
    os.system("sleep 0.5")
    os.chdir("%s"%(runDir))
    
    count += 1
    print("{} jobs submitted, {} out of {} seeds generated.".format(count,len(used_seeds),maxSeeds)
    return count
    
def submit_seed_job(SeedN,used_seeds,maxSeeds,count,options): # submits seed job and corresponding subseed jobs
    numVars = options[2]
    used_seeds.append(SeedN)
    count = condor_job(str(SeedN),count=count,options=options,maxSeeds=maxSeeds)
    for num in range(0, numVars):
        if(SeedN & (1 << num)):
            SubSeedN = SeedN & ~(1 << num)
            count = condor_job(str(SeedN),str(SubSeedN),count,options,maxSeeds) 
    return used_seeds, count

def get_correlation_matrix(sigFile, bkgFile, weightStr, cutStr, varList): # gets the correlation matrix as np array
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
    
    # set the pointer to the right histogram, very important step
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
          
def seed_replace(bitstring,val,indices):
    new_bitstring = bitstring
    for index in indices:
        new_bitstring = new_bitstring[:index] + str(val) + new_bitstring[index+1:]
    return new_bitstring
    
def get_correlated_pairs(corrMatrix,corrCut,varNames):
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

def generate_uncorr_seeds(seed,correlated_pairs):
    new_seeds = []
    correlated_pair_list = []
    for pair_key in correlated_pairs:
        correlated_pairs_list.append(correlated_pairs[pair_key])
    correlation_combos = list(itertools.product(*correlated_pairs_list))
    for combo in correlation_combos:
        new_seeds.append((seed_replace(seed,0,combo)))
    return set(new_seeds)

def variable_inclusion(used_seeds,correlated_pairs,count,options):
    count_arr = np.zeros(len(varList))      # holds count of input variable usage in seed generation
    # get a list of variables not included yet
    for seed in used_seeds:
        seed_str = "{:0{}b}".format(seed,len(varList))
        for indx, variable in enumerate(seed_str):
            if variable == "1": count_arr[indx] += 1

    # generate seeds that include the excluded variables
    if 0 in count_arr:
        Seed = random.randint(0,int(binary_str,2))
        SeedStr = "{:0{}b}".format(Seed,len(varList))
        seed_mask = count_arr == 0
        index_mask = []
        for indx, entry in enumerate(seed_mask):
            if entry == True: index_mask.append(indx)
        NewSeed = seed_replace(bitstring=SeedStr,val=1,indices=index_mask)
        gen_seeds = generate_uncorr_seeds(NewSeed,correlated_pairs)
        for gen_seed in gen_seeds:
            used_seeds, count = submit_seed_job(int(gen_seed,2),used_seeds,count,options)
    else: print("All variables were included in the prior seed generation.")
    return used_seeds, count
    
def variable_occurence(used_seeds,varNames):
    count_arr = np.zeros(len(varList))
    for seed in used_seeds:
        seed_str = "{:0{}b}".format(int(seed),len(count_arr))
        for indx, variable in enumerate(seed_str):
            if variable == "1": count_arr[indx] += 1
    for indx, varName in enumerate(varNames):
        print("{:32}: {:3}".format(len(used_seeds)))
          
os.system("bash")
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# lists
inputDir = varsList.inputDirLPC         # string for path to ljmet samples
varList = varsList.varList["BigComb"]   # contains all the input variables
used_seeds = []                         # stores which seeds have been used
options = [                             # contains arguments for condor job submission functions
    os.getcwd(),
    os.getcwd() + "/condor_log/",
    len(varList)
]

# variable parameters  
weightStrC = varsList.weightStr
cutStrC = varsList.cutStr
binary_str = "1" * len(varList)         # bitstring full of '1' 
max_int = int(binary_str,2)             # integer corresponding to bitstring full of '1'
corr_cut = 80                           # set this between 0 and 100
maxSeeds = 60                           # maximum number of generated seeds
count = 0                               # counts the number of jobs submitted

# get the signal correlation matrix and the variable names, used in correlation options
sig_corr, varNames = get_correlation_matrix(
    inputDir + "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root",
    inputDir + varsList.bkg[0],     # choose a random background sample since we only care about signal
    weightStrC,
    TCut(cutStrC),
    varList
)

print("Using {} inputs...".format(len(varNames)))

# submit jobs

correlated_pairs = get_correlated_pairs(sig_corr, corr_cut, varNames)

while len(used_seeds) < maxSeeds:
    NewSeed = random.randint(0,int(binary_str,2))
    NewSeedStr = '{:0{}b}'.format(NewSeed,len(varList))
    gen_seeds = generate_uncorr_seeds(NewSeedStr,correlated_pairs)
    for gen_seed in gen_seeds:
        var_count = gen_seed.count("1")
        if ( gen_seed not in used_seeds ) and ( var_count > 1 ) and ( len(used_seeds) < maxSeeds ):
            used_seeds, count = submit_seed_job(int(gen_seed,2),used_seeds,count,options)

used_seeds, count = variable_inclusion(used_seeds,correlated_pairs,count,options)

#variable_occurence(used_seeds, varNames)   # include if you want to see the frequency of variables considered in seeds
          

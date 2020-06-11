#!/usr/bin/env python

import os, sys
import numpy as np
import getopt
import random
import ROOT
import itertools
from ROOT import TMVA, TFile, TTree, TCut
from ROOT import gSystem, gApplication, gROOT
from subprocess import check_output

sys.path.insert(0, "../TTTT_TMVA_DNN")

CONDOR_TEMPLATE = """universe = vanilla
Executable = %(RUNDIR)s/LPC/VariableImportanceLPC_step2.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3.5 GB
request_cpus = 2
image_size = 3.5 GB
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(SubmitSeedN)s %(EOSDIR)s %(eosUserName)s %(YEAR)s
Queue 1"""

import varsList

# methods

def condor_job(SeedN="", SubSeedN="", count=0, options=['','','','','',''], maxSeeds=0): # submits a single condor job
    runDir      = options[0]
    condorDir   = options[1]
    numVars     = options[2]
    eosDir      = options[3]
    eosUserName = options[4]
    year        = options[5]
    
    SubmitSeedN = ""
    fileName = ""
    if SubSeedN == "": 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN)
        SubmitSeedN = SeedN
    else: 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN) + "_Subseed_" + str(SubSeedN)
        SubmitSeedN = SubSeedN
        
    job_spec = {
        "SubmitSeedN":  SubmitSeedN,
        "FILENAME":     fileName,
        "RUNDIR":       runDir,
        "EOSDIR":       eosDir,
        "eosUserName":  eosUserName,
        "YEAR":         year
    }
    
    jdfName = condorDir + "%(FILENAME)s.job"%job_spec
    jdf = open(jdfName, "w")
    jdf.write(CONDOR_TEMPLATE%job_spec)
    jdf.close()
    
    os.chdir("%s/"%(condorDir))
    os.system("condor_submit %(FILENAME)s.job"%job_spec)
    os.system("sleep 0.25")
    os.chdir("%s"%(runDir))
    
    count += 1
    print("{} jobs submitted,  {} out of {} seeds generated.".format(count, len(used_seeds), maxSeeds))
    return count
    
def submit_seed_job(SeedN, used_seeds, maxSeeds, count, options): # submits seed job and corresponding subseed jobs
    numVars = options[2]
    used_seeds.append(SeedN)
    count = condor_job(str(SeedN), count=count, options=options, maxSeeds=maxSeeds)
    for num in range(0, numVars):
        if(SeedN & (1 << num)):
            SubSeedN = SeedN & ~(1 << num)
            count = condor_job(str(SeedN), str(SubSeedN), count, options, maxSeeds) 
    return used_seeds, count

def get_correlation_matrix(sigFile, bkgFile, weightStr, cutStr, varList): # gets the correlation matrix as np array
    varNames = []
    loader = TMVA.DataLoader("dataset")
    for var in varList:
        if var[0] in "NJets_MultiLepCalc": loader.Addvariable( var[0], var[1], var[2], "I" )
        else:                              loader.AddVariable( var[0], var[1], var[2], "F" )
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
    sig_corr = np.zeros((n_bins, n_bins))
    
    for x in range(n_bins):
        for y in range(n_bins):
            sig_corr[x, y] = sig_th2.GetBinContent(x+1, y+1)
    
    return sig_corr, varNames
          
def seed_replace(bitstring, val, indices):
    new_bitstring = bitstring
    for index in indices:
        new_bitstring = new_bitstring[:index] + str(val) + new_bitstring[index+1:]
    return new_bitstring
    
def get_correlated_pairs(corrMatrix, corrCut, varNames):
    correlated_pairs = {}
    for i in np.arange(np.shape(corrMatrix)[0] - 1):
        correlated_pairs[i] = [i]
        for j in np.arange(i+1, np.shape(corrMatrix)[1]):
            if abs(corrMatrix[i, j]) >= corrCut:
                print("{} and {} are {:.2f} % correlated.".format(
                    varNames[i], varNames[j], corrMatrix[i, j]
                    )
                )
                correlated_pairs[i].append(j)
        if len(correlated_pairs[i]) == 1: del correlated_pairs[i]
    return correlated_pairs

def generate_uncorr_seeds(seed, numCorrSeed, correlated_pairs):
    new_seeds = []
    correlated_pairs_list = []
    for pair_key in correlated_pairs:
        correlated_pairs_list.append(correlated_pairs[pair_key])
    for pair in correlated_pairs_list:
        seed = seed_replace(seed, 0, pair)
    correlation_combos = [list(set(combo)) for combo in list(itertools.product(*correlated_pairs_list))]
    for combo in correlation_combos:
        new_seeds.append((seed_replace(seed, 1, combo)))
    new_seeds = list(set(new_seeds))
    if len(new_seeds) > numCorrSeed:
        random_selection = random.sample(range(0, len(new_seeds)), numCorrSeed)
        return np.asarray(new_seeds)[random_selection]
    else:
        return np.asarray(new_seeds)

def variable_inclusion(used_seeds, numCorrSeed, correlated_pairs, maxSeeds, count, options):
    count_arr = np.zeros(len(varList))      # holds count of input variable usage in seed generation
    # get a list of variables not included yet
    for seed in used_seeds:
        seed_str = "{:0{}b}".format(seed, len(varList))
        for indx, variable in enumerate(seed_str):
            if variable == "1": count_arr[indx] += 1

    # generate seeds that include the excluded variables
    if 0 in count_arr:
        Seed = random.randint(0, int(binary_str, 2))
        SeedStr = "{:0{}b}".format(Seed, len(varList))
        seed_mask = count_arr == 0
        index_mask = []
        for indx, entry in enumerate(seed_mask):
            if entry == True: index_mask.append(indx)
        NewSeed = seed_replace(bitstring=SeedStr, val=1, indices=index_mask)
        gen_seeds = generate_uncorr_seeds(NewSeed, numCorrSeed, correlated_pairs)
        print("{} additional seeds generated based on Variable Inclusion...".format(len(gen_seeds)))
        for gen_seed in gen_seeds:
            used_seeds, count = submit_seed_job(int(gen_seed, 2), used_seeds, maxSeeds, count, options)
    else: print("All variables were included in the prior seed generation.")
    return used_seeds, count
    
def variable_occurence(used_seeds, varNames):
    count_arr = np.zeros(len(varList))
    for seed in used_seeds:
        seed_str = "{:0{}b}".format(int(seed), len(count_arr))
        for indx, variable in enumerate(seed_str):
            if variable == "1": count_arr[indx] += 1
    for indx, varName in enumerate(varNames):
        print("{:32}: {:3}".format(len(used_seeds)))

#Check VOMS
def check_voms():
    # Returns True if the VOMS proxy is already running
    print "Checking VOMS"
    try:
        check_output("voms-proxy-info", shell=True)
        print "[OK ] VOMS found"
        return True
    except:
        return False
    
def voms_init():
    #Initialize the VOMS proxy if it is not already running
    if not check_voms():
        print "Initializing VOMS"
        os.system("voms-proxy-init --rfc --voms cms")
        print "VOMS initialized"
          
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# lists
year = int(sys.argv[1])
inputDirLPC, inputDirEOS, step2Sample = None, None, None
if year == 2017: 
    inputDirLPC = varsList.inputDirLPC2017
    inputDirEOS = varsList.inputDirEOS2017
    step2Sample = varsList.step2Sample2017
elif year == 2018: 
    inputDirLPC = varsList.inputDirLPC2018
    inputDirEOS = varsList.inputDirEOS2018
    step2Sample = varsList.step2Sample2017

varList = varsList.varList["DNN"]       # contains all the input variables
used_seeds = []                         # stores which seeds have been used

# variable parameters  
weightStrC = varsList.weightStr
cutStrC = varsList.cutStr
binary_str = "1" * len(varList)         # bitstring full of '1' 
max_int = int(binary_str, 2)            # integer corresponding to bitstring full of '1'
corr_cut = 80                           # set this between 0 and 100
maxSeeds = 1                            # maximum number of generated seeds
numCorrSeed = 5                         # number of de-correlated seeds randomly chosen to submit
count = 0                               # counts the number of jobs submitted
sig_corr = None                         # will hold signal correlation matrix
varNames = None                         # list of input variable names

condor_folder = "condor_log"

# adjust seed generation if seed and cut arguments are provided
if len(sys.argv) > 2:
    maxSeeds = int(sys.argv[2])
    corr_cut = int(sys.argv[3])
    if len(sys.argv) > 4:
        condor_folder = sys.argv[4]

#Args are ...step1.py year maxSeeds corr_cut [condor_folder]
        
options = [                             # contains arguments for condor job submission functions
    os.getcwd(),                        # running/working directory
    os.getcwd() + "/" + condor_folder + "/",# condor job result directory
    len(varList),                       # number of input variables
    inputDirEOS,                        # EOS directory
    varsList.eosUserName,               # EOS User name
    year                                # production year
]


# get the signal correlation matrix and the variable names, used in correlation options
if year == 2017:
    sig_corr, varNames = get_correlation_matrix(
        os.getcwd() + "/" + step2Sample + "/" + varsList.sig2017_0[0],
        os.getcwd() + "/" + step2Sample + "/" + varsList.bkg2017_0[0],     # choose a random background sample since we only care about signal
        weightStrC,
        TCut(cutStrC),
        varList
    )
elif year == 2018:
    sig_corr, varNames = get_correlation_matrix(
        os.getcwd() + "/" + step2Sample + "/" + varsList.sig2018_0[0],
        os.getcwd() + "/" + step2Sample + "/" + varsList.bkg2018_0[0],     # choose a random background sample since we only care about signal
        weightStrC,
        TCut(cutStrC),
        varList
    )
else:
    print "Invalid year specified."
    sys.exit(1)

print("Using {} inputs...".format(len(varNames)))

# submit jobs

voms_init()

correlated_pairs = get_correlated_pairs(sig_corr, corr_cut, varNames)

while len(used_seeds) < maxSeeds:
    NewSeed = random.randint(0, int(binary_str, 2))
    NewSeedStr = '{:0{}b}'.format(NewSeed, len(varList))
    gen_seeds = generate_uncorr_seeds(NewSeedStr, numCorrSeed, correlated_pairs)
    for gen_seed in gen_seeds:
        var_count = gen_seed.count("1")
        if ( gen_seed not in used_seeds ) and ( var_count > 1 ) and ( len(used_seeds) < maxSeeds ):
            used_seeds, count = submit_seed_job(int(gen_seed, 2), used_seeds, maxSeeds, count, options)
        if count > maxSeeds: break
        
used_seeds, count = variable_inclusion(used_seeds, numCorrSeed, correlated_pairs, maxSeeds, count, options)

#variable_occurence(used_seeds, varNames)   # include if you want to see the frequency of variables considered in seeds
          

#!/usr/bin/env python

import os, sys
import numpy as np
import getopt
import random
import ROOT
from ROOT import TMVA, TFile, TTree, TCut
from ROOT import gSystem, gApplication, gROOT
import varsList

os.system("bash")
os.system("source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-centos7-gcc62-opt/setup.sh")

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# some parameters
inputDir = varsList.inputDir

# define weight and cut expressions, these should match with those in TMVAClassification_VarImportanceDNN.py
weightStrC = "pileupWeight*lepIdSF*EGammaGsfSF*MCWeight_MultiLepCalc/abs(MCWeight_MultiLepCalc)"
weightStrS = weightStrC # weight equation for Signal
weightStrB = weightStrC # weight equation for Background

cutStrC = "(NJets_JetSubCalc >= 5 && NJetsCSV_JetSubCalc >= 2) && ((leptonPt_MultiLepCalc > 35 && isElectron) || (leptonPt_MultiLepCalc > 30 && isMuon))"
cutStrS = TCut(cutStrC) # cut expression for Signal
cutStrB = TCut(cutStrC) # cut expression for Background

# load the signal and a background file into a ROOT.TMVA.DataLoader object and apply the weights and cuts
loader = TMVA.DataLoader("dataset")
varNames = []
for var in varsList.varList["BigComb"]:
  if var[0] in "NJets_MultiLepCalc":  loader.Addvariable( str(var[0]), "I" )
  else:                               loader.AddVariable( str(var[0]), "F" )
  varNames.append(var[0])
  
inFile = TFile.Open(inputDir + "TTTT_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root")
signal = inFile.Get("ljmet") # retrieves the ljmet branch from the signal tree
bkgFile = TFile.Open(inputDir + varsList.bkg[0]) # read in a random background file to be able to use loader functions
background = bkgFile.Get("ljmet")

# add trees to the data loader object
loader.AddSignalTree( signal )
loader.fTreeS = signal
loader.AddBackgroundTree( background )
loader.fTreeB = background

# set weights
loader.SetSignalWeightExpression( weightStrS )
loader.SetBackgroundWeightExpression( weightStrB )

# set cuts using DataLoader.PrepareTrainingAndTestTree
loader.PrepareTrainingAndTestTree(
  cutStrS, cutStrB,
  "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
)

# set the pointer to the correct TH2 (histogram)--very important 
loader.GetDefaultDataSetInfo().GetDataSet().GetEventCollection()

# retrieve the signal correlation matrix 
sig_th2 = loader.GetCorrelationMatrix("Signal")
# bkg_th2 = loader.GetCorrelationMatrix("Background")

# define parameters for creating numpy array for the correlation matrix and generating seeds
n_bins = sig_th2.GetNbinsX()

sig_corr = np.zeros((n_bins,n_bins))
# bkg_corr = np.zeros((n_bins,n_bins))
for x in range(n_bins):
  for y in range(n_bins):
    sig_corr[x,y] = sig_th2.GetBinContent(x+1,y+1)
    # bkg_corr[x,y] = bkg_th2.GetBinContent(x+1,y+1)

max_int = int("1"*n_bins,2)
corr_cut = 80 # set this
corr_seeds = []
corr_count = 0

# generate the seeds by searching for correlated variables above the threshold
for i in range(n_bins):
  corr_group = [i]
  for j in np.arange(i+1 , n_bins):
    if abs(sig_corr[i,j]) > corr_cut:
      corr_group.append(j)
  if len(corr_group) > 1:
    tot_diff = sum(2**np.array(corr_group))
    for var in corr_group:
      corr_seeds.append('{:0{}b}'.format(max_int - tot_diff + 2**var, n_bins)) # convert from int to binary string
corr_seeds = set(corr_seeds) # remove duplicate seeds
print("Manually generated {} seeds using a threshold of {}.".format(len(corr_seeds),corr_cut))

varListKeys = ['BigComb']
runDir = os.getcwd()
condorDir = runDir + '/condor_log/'
os.system('mkdir -p ' + condorDir)

method = "Keras"

varList = varsList.varList["BigComb"]
num_seeds = min(len(varList)*len(varList),150) - len(corr_seeds) # optionally cap the number of seeds generated
binary_str = "1" * len(varList)

# submit manually generated seed jobs
count = 0 # counts the number of jobs submitted

used_seeds = [] # keep track of which seeds have been used

for seed in corr_seeds:
  SeedN = int(seed,2)
  used_seeds.append(SeedN)
  outf_key = "Seed_" + str(SeedN)
  fileName = method + "_BigComb" + "_" + str(len(varList)) + "vars_" + outf_key
  dict = {
    "RUNDIR":runDir,
    "METHOD":method,
    "vListKey":"BigComb",
    "SeedN":SeedN,
    "FILENAME":fileName
    }
  jdfName = condorDir + "%(FILENAME)s.job"%dict
  print(jdfName)
  jdf = open(jdfName, "w")
  jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SeedN)s
Queue 1"""%dict)
  jdf.close()
  os.chdir("%s/"%(condorDir))
  os.system("condor_submit %(FILENAME)s.job"%dict)
  os.system("sleep 0.5")
  os.chdir("%s"%(runDir))
  count += 1 # iterate the job count
  print("{} jobs submitted.".format(count))
  
  for num in range(0, len(varList)):
    if(SeedN & (1 << num)):
      SubSeedN = SeedN & ~(1<<num)
      outf_key = 'Seed_' + str(SeedN) + '_Subseed_' + str(SubSeedN)
      fileName = method + '_' + 'BigComb' + '_' + str(len(varList)) + 'vars_' + outf_key
      dict_sub = {
        'RUNDIR':runDir,
        'METHOD':method,
        'vListKey':'BigComb',
        'SeedN':SeedN,
        'FILENAME':fileName,
        'SubSeedN':SubSeedN
      }
      jdfName = condorDir + '%(FILENAME)s.job'%dict_sub
      print(jdfName)
      jdf = open(jdfName,'w')
      jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SubSeedN)s
Queue 1"""%dict_sub)
      jdf.close()
      os.chdir('%s/'%(condorDir))
      os.system('condor_submit %(FILENAME)s.job'%dict_sub)
      os.system('sleep 0.5')
      os.chdir('%s'%(runDir))
      count += 1
      print('{} jobs submitted.'.format(count))


# submit remaining randomly generated seed jobs

while len(used_seeds) != num_seeds:
  SeedN = random.randint(0,int(binary_str,2))
  if SeedN not in used_seeds: # only use unique seeds
    used_seeds.append(SeedN)
    outf_key = 'Seed_' + str(SeedN)
    fileName = method + '_' + 'BigComb' + '_' + str(len(varList)) + 'vars_' + outf_key
    dict = {
      'RUNDIR':runDir,
      'METHOD':method,
      'vListKey':'BigComb',
      'SeedN':SeedN,
      'FILENAME':fileName
      }
    jdfName = condorDir + '%(FILENAME)s.job'%dict
    print(jdfName)
    jdf = open(jdfName, 'w')
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SeedN)s
Queue 1"""%dict)
    jdf.close()
    os.chdir('%s/'%(condorDir))
    os.system('condor_submit %(FILENAME)s.job'%dict)
    os.system('sleep 0.5')
    os.chdir('%s'%(runDir))
    count += 1 # iterate the job count
    print('{} jobs submitted.'.format(count))
  
    for num in range(0, len(varList)):
      if(SeedN & (1 << num)):
        SubSeedN = SeedN & ~(1<<num)
        outf_key = 'Seed_' + str(SeedN) + '_Subseed_' + str(SubSeedN)
        fileName = method + '_' + 'BigComb' + '_' + str(len(varList)) + 'vars_' + outf_key
        dict_sub = {
          'RUNDIR':runDir,
          'METHOD':method,
          'vListKey':'BigComb',
          'SeedN':SeedN,
          'FILENAME':fileName,
          'SubSeedN':SubSeedN
        }
        jdfName = condorDir + '%(FILENAME)s.job'%dict_sub
        print(jdfName)
        jdf = open(jdfName,'w')
        jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SubSeedN)s
Queue 1"""%dict_sub)
        jdf.close()
        os.chdir('%s/'%(condorDir))
        os.system('condor_submit %(FILENAME)s.job'%dict_sub)
        os.system('sleep 0.5')
        os.chdir('%s'%(runDir))
        count += 1
        print('{} jobs submitted.'.format(count))

#!/usr/bin/env python

# this will take a while since it has to copy files from BRUX to FNAL and then split the files and finally copy them to EOS

import os, sys
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

# set-up the working area
lpcHomeDir = os.path.expanduser("~/nobackup/")

os.system("voms-proxy-init --rfc --voms cms")
if varsList.step2Sample not in os.listdir(lpcHomeDir): os.system("mkdir {}{}".format(lpcHomeDir,varsList.step2Sample))

# transfer files from BRUX to LPC
# will need to input BRUX password

print("Transferring files from {} to {}...".format(
    varsList.bruxUserName + "@brux.hep.brown.edu:" + varsList.inputDirBRUX,
    lpcHomeDir + varsList.step2Sample
))

for sample in (varsList.sig + varsList.bkg):
    if sample not in os.listdir("{}{}".format(lpcHomeDir,varsList.step2Sample)):
        print("Transferring {}...".format(sample))
	os.system("scp -r {}@brux.hep.brown.edu:{}{} {}{}".format(
            varsList.bruxUserName,
            varsList.inputDirBRUX,
            sample,
	    lpcHomeDir,
            varsList.step2Sample
        )
                  )
    else: print("{} has been transferred. Proceeding to next sample...".format(sample))
        
# prevent the setup from proceeding if not all samples are present
PROCEED = True
for sample in (varsList.sig + varsList.bkg):
  if sample not in os.listdir(lpcHomeDir + varsList.step2Sample):
     print("{} was not transferred properly. Please resubmit this script.".format(sample))
     PROCEED = False
if PROCEED == False: sys.exit(0)

# compile the root splitting script
print("Splitting ROOT files...")
if "splitROOT.out" in os.listdir(os.getcwd() + "/Tools/"): os.system("rm {}/Tools/splitROOT.out".format(os.getcwd()))
os.system("g++ `root-config --cflags` `root-config --libs` -o ./Tools/splitROOT.out ./Tools/splitROOT.cpp")
os.system("./Tools/splitROOT.out")
    
# make the eos directory
os.system("eosmkdir /store/user/{}/{}/".format(
    varsList.eosUserName,
    varsList.step2Sample
    )
)

samples0 = varsList.sig0 + varsList.bkg0

for sample in samples0:
  os.system("xrdcp {}{}/{} root://cmseos.fnal.gov//store/user/{}/{}".format(
    lpcHomeDir,
    varsList.step2Sample,
    sample,
    varsList.eosUserName,
    varsList.step2Sample
  )
)

# tar the CMSSW framework 
if "CMSSW946.tgz" in os.listdir(lpcHomeDir): 
  os.system("rm {}{}".format(lpcHomeDir,"CMSSW946.tgz"))
  os.system("rm /store/user/{}/CMSSW946.tgz".format(varsList.eosUserName))
os.system("tar -zcvf {}CMSSW946.tgz {}CMSSW_9_4_6_patch1/".format(lpcHomeDir,lpcHomeDir))

# copy the framework to EOS 

os.system("xrdcp {}CMSSW946.tgz root://cmseos.fnal.gov//store/user/{}".format(
  lpcHomeDir,
  varsList.eosUserName
  )
)

# create TMVA DNN training result directories
if "condor_log" not in os.listdir("../"): os.system("mkdir {}CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/condor_log".format(lpcHomeDir))
if "dataset" not in os.listdir("../"):
  os.system("mkdir {}CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset".format(lpcHomeDir))
  os.system("mkdir {}CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset/weights".format(lpcHomeDir))

# now, submit the 'submit_VariableImportance.sh' script

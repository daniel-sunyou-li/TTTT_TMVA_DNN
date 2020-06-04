#!/usr/bin/env python

# this will take a while since it has to copy files from BRUX to FNAL and then split the files and finally copy them to EOS

import os, sys
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

# set-up the working area
lpcHomeDir = os.path.expanduser("~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/")

os.system("voms-proxy-init --rfc --voms cms")

# compile the sample splitting c++ script
if "splitROOT.out" in os.listdir(os.getcwd() + "/Tools/"): os.system("rm {}/Tools/splitROOT.out".format(os.getcwd()))
print("Compiling splitROOT.cpp...")
os.system("g++ `root-config --cflags` `root-config --libs` -o ./Tools/splitROOT.out ./Tools/splitROOT.cpp")

# transfer files from BRUX to LPC
# will need to input BRUX password

# setup parameters that will differ between 2017 and 2018 samples
step2Sample  = None
inputDirBRUX = None
inputDirLPC  = None
inputDirEOS  = None
samples      = None
samples_0    = None

for year in ["2017","2018"]: # only include the years you want
# assign the setup parameters accordingly
    if year == "2017":
        step2Sample  = varsList.step2Sample2017
        inputDirBRUX = varsList.inputDirBRUX2017
        inputDirLPC  = varsList.inputDirLPC2017
        inputDirEOS  = varsList.inputDirEOS2017
        samples      = varsList.sig2017 + varsList.bkg2017
        samples_0    = varsList.sig2017_0 + varsList.bkg2017_0
    elif year == "2018":
        step2Sample  = varsList.step2Sample2018
        inputDirBRUX = varsList.inputDirBRUX2018
        inputDirLPC  = varsList.inputDirLPC2018
        inputDirEOS  = varsList.inputDirEOS2018
        samples      = varsList.sig2018 + varsList.bkg2018
        samples_0    = varsList.sig2018_0 + varsList.bkg2018_0

# output sample origin and destination when running setup
    if step2Sample not in os.listdir(lpcHomeDir): os.system("mkdir {}{}".format(lpcHomeDir,step2Sample))
    print("Transferring files from {} to {}...".format(
        varsList.bruxUserName + "@brux.hep.brown.edu:" + inputDirBRUX,
        lpcHomeDir + step2Sample
    ))

    for sample in samples:
        if sample not in os.listdir("{}{}".format(lpcHomeDir,step2Sample)):
            print("Transferring {}...".format(sample))
	    os.system("scp -r {}@brux.hep.brown.edu:{}{} {}{}".format(
                varsList.bruxUserName,
                inputDirBRUX,
                sample,
	        lpcHomeDir,
                step2Sample
            )
                      )
        else: print("{} has been transferred. Proceeding to next sample...".format(sample))
        
# prevent the setup from proceeding if not all samples are present
    PROCEED = True
    for sample in samples:
        if sample not in os.listdir(lpcHomeDir + step2Sample):
            print("{} was not transferred properly. Please resubmit this script.".format(sample))
            PROCEED = False
    if PROCEED == False: sys.exit(0)

# run the root file splitting script
    print("Splitting {} ROOT files...".format(year))
    for sample in samples:
        os.system("./Tools/splitROOT.out {} {} {} {}".format(
            lpcHomeDir + step2Sample,    # location of sample to split
            lpcHomeDir + step2Sample,    # destination of split sample(s)
            sample,                      # sample to split
            3                            # number of files to split into
        ))

# transfer one of the split samples to EOS
    print("Transferring {} to EOS...".format(sample))
    os.system("xrdcp {}*split0.root root://cmseos.fnal.gov//store/user/{}".format(
        "./" + step2Sample + "/",
        varsList.eosUserName + "/" + step2Sample + "/"
        )
    )

# tar the CMSSW framework
if "CMSSW946.tgz" in os.listdir(lpcHomeDir):
    print("Deleting existing CMSSW946.tgz...")
    os.system("rm {}{}".format(lpcHomeDir,"CMSSW946.tgz"))
os.system("tar -C ~/nobackup/ -zcvf CMSSW946.tgz --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' --exclude=\'{}\' {}".format(
    "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/" + varsList.step2Sample2017,
    "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/" + varsList.step2Sample2018,
    "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/condor_log*",
    "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset_*",
    "CMSSW_9_4_6_patch1/"
)
    )
print("Transferring CMSSW946.tgz to EOS...")
os.system("xrdcp -f CMSSW946.tgz root://cmseos.fnal.gov//store/user/{}".format(varsList.eosUserName))

# create TMVA DNN training result directories
if "condor_log" not in os.listdir("./"): os.system("mkdir {}condor_log".format(lpcHomeDir))
if "dataset" not in os.listdir("./"):
  os.system("mkdir {}dataset".format(lpcHomeDir))
  os.system("mkdir {}dataset/weights".format(lpcHomeDir))

# now, submit the 'submit_VariableImportance.sh' script

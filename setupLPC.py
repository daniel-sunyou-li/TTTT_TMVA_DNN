#!/usr/bin/env python

# this will take a while since it has to copy files from BRUX to FNAL and then split the files and finally copy them to EOS

import os, sys
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

bruxUserName = "dli50"
eosUserName = "dali"
bruxPath = "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2/nominal/"
folderName = "FWLJMET102X_1lpe2017_Oct2019_4t_03032020_step2"

# set-up the working area
os.system("voms-proxy-init --rfc --voms cms")
os.system("mkdir ~/nobackup/{}".format(folderName))

# transfer files from BRUX to LPC
# will need to input BRUX password

for sample in (varsList.sig + varsList.bkg):
    os.system("scp -r {}@brux.hep.brown.edu:{}{} ~/nobackup/{}/".format(
        bruxUserName,
        bruxPath,
        sample,
        folderName
    )
             )

# compile the root splitting script
os.system("g++ `root-config --cflags` `root-config --libs` -o splitROOT.out splitROOT.cpp")
os.system("./splitROOT.out")
    
# make the eos directory
os.system("eosmkdir /store/user/{}/{}".format(
    eosUserName,
    folderName
    )
)

samples0 = varsList.sig0 + varsList.bkg0

for sample in samples0:
  os.system("xrdcp ~/nobackup/{}/{} root://cmseos.fnal.gov//store/user/{}/".format(
    folderName,
    sample,
    eosUserName
  )
)

# tar the CMSSW framework 

os.system("tar -zcvf ~/nobackup/CMSSW946.tgz ~/nobackup/CMSSW_9_4_6_patch1/")

# copy the framework to EOS 

os.system("xrdcp ~/nobackup/CMSSW946.tgz root://cmseos.fnal.gov//store/user/{}".format(
    eosUserName
  )
)

# create TMVA DNN training result directories
os.system("mkdir ~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/condor_log")
os.system("mkdir ~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset")
os.system("mkdir ~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset/weights")

# now, submit the 'submit_VariableImportance.sh' script

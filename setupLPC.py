#!/usr/bin/env python

import os, sys
import varsList

bruxUserName = "dli50"
eosUserName = "dali"
filePath = "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_12122019_step2/nominal/"
folderName = "FWLJMET102X_1lpe2017_Oct2019_4t_12122019_step2"

# transfer files from BRUX to LPC
# will need to input BRUX password

os.system("scp -r {}@brux.hep.brown.edu:{} ~/nobackup/{}/".format(
    bruxUserName,
    filePath,
    folderName
  )
)

# the LPC nodes can only host up to 40GB of files remotely, so it's necessary to limit the bkg samples, thus not transferring all files

for bkg in varsList.bkg:
  os.system("xrdcp ~/nobackup/{}/{} root://cmseos.fnal.gov//store/user/{}/".format(
    folderName,
    bkg,
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











import numpy as np
import os,sys
import ROOT as root

#file_path = "/mnt/hadoop/store/user/daili/TTTT/FWLJMET102X_1lep2017_4t_081019_step2hadds/nominal/TTTT_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"

file_path = "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_12122019_step2/nominal/"
file_name = "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"

root_file = root.TFile.Open(file_path+file_name)
root_tree = root_file.Get("ljmet")

branch_file = open(os.getcwd() + "/TTTT_variables.txt",'w')
branch_file.write("2017 TTTT TMVA DNN Step 2 Variable List\n")
branch_file.write("=======================================\n")

branches = root_tree.GetListOfBranches()

for branch in branches :
  branch_file.write(branch.GetName()+"\n")

branch_file.close()

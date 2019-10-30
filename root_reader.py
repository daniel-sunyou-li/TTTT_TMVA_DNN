import numpy as np
import os,sys
import ROOT as root

file_path = "/mnt/hadoop/store/user/dali/TTTT/FWLJMET102X_1lep2017_4t_081019_step2hadds/nominal/TTTT_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"

root_file = root.TFile.Open(file_path)
root_tree = root_file.Get("ljmet")

branch_file = open(os.getcwd() + "/TTTT_variables.txt",'w')
branch_file.write("2017 TTTT TMVA DNN Step 2 Variable List\n")
branch_file.write("=======================================\n")

branches = root_tree.GetListOfBranches()

for branch in branches :
  branch_file.write(branch.GetName()+"\n")

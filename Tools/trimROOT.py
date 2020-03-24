#!/usr/bin/env python

import numpy as np
import os, sys
import ROOT as root
import varsList
from tqdm import tqdm

def progress_bar(filename,current,total):
  fillLength = int(50*current//total)
  bar = "=" * fillLength + "-" * (50 - fillLength)
  percent = 100*float(current/total)
  print("\r{:<100} |{}| {:.2f} %".format(
    filename+" :",bar,percent
    ))
  if current == total: print()

# define some parameters
TRIM_ALL = False   # set to true if wanting to trim all files at once
MB_CAP   = 35000   # the hard cap on the FNAL remote nodes is 40 GB

# instantiate variables
MB_TOT   = 0       # will add the file sizes together in MB
BKG_SIZE_TOT = 0   # total size of background samples in MB
SIG_SIZE_TOT = 0   # total size of signal samples in MB
BKG_EVENTS_TOT = 0 # total number of background events
SIG_EVENTS_TOT = 0 # total number of signal events

bkg_N_list = []    # this will hold all the event numbers

file_path = "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_02132020_step2/nominal/"
out_path  = os.getcwd()
bkg_names = varsList.bkg
sig_names = varsList.sig

file_name = "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"
trim_name = file_name.split("hadd")[0] + "trim.root"

# loop over all background files and get some numbers
print("Directory: {}".format(file_path))
print("{:<100} {:<12} {:<14} {}".format("Background Sample Name","Events","File Size (MB)","Event Size (B)"))
for bkg in bkg_names:
  bkg_size = os.path.getsize(file_path + bkg) / 1E6 # report as MB
  bkg_file = root.TFile.Open(file_path + bkg)
  N_bkg    = bkg_file.Get("ljmet").GetEntriesFast()
  BKG_SIZE_TOT += bkg_size
  BKG_EVENTS_TOT += N_bkg
  bkg_N_list.append(N_bkg)
  event_size = 1E6 * bkg_size / N_bkg 
  print("{:<100} {:<12} {:<14.2f} {:.2f}".format(bkg,N_bkg,bkg_size,event_size))
print("_________________________________________________________________")
print("Total Background Events: {}, Total Background Size: {:.2f} (GB)\n".format(BKG_EVENTS_TOT,BKG_SIZE_TOT/1E3))

# loop over all signal files and get some numbers
print("{:<100} {:<12} {:<14} {}".format("Signal Sample Name","Events","File Size (MB)","Event Size (B)"))
for sig in sig_names:
  sig_size = os.path.getsize(file_path + sig) / 1E6
  sig_file = root.TFile.Open(file_path + bkg)
  N_sig    = sig_file.Get("ljmet").GetEntriesFast()
  SIG_SIZE_TOT += sig_size
  SIG_EVENTS_TOT += N_sig
  event_size = 1E6 * sig_size / N_sig
  print("{:<100} {:<12} {:<14.2f} {:.2f}".format(sig,N_sig,sig_size,event_size))
print("_________________________________________________________________")
print("Total Signal Events: {}, Total Signal Size: {:.2f} (GB)\n".format(SIG_EVENTS_TOT,SIG_SIZE_TOT/1E3))

EVENT_SCALE = MB_CAP / BKG_SIZE_TOT                 # this will scale the number of events for each sample 
bkg_scales = np.asarray(bkg_N_list) * EVENT_SCALE   # scale the event numbers

if TRIM_ALL == True: # only trimming backgrounds because signal precious
  print("Trimming all backgrounds...")
  for bkg in bkg_names:
    bkg_file = root.TFile.Open(file_path + bkg)
    bkg_tree = bkg_file.Get("ljmet")
    bkg_branch = bkg_tree.GetListOfBranches()
    branch_list = [branch.GetName() for branch in bkg_branch]
    
    trim_bkg_name = bkg.split("hadd")[0] + "trim.root"
    trim_bkg_events = int( bkg_tree.GetEntriesFast() * EVENT_SCALE )
    trim_bkg_file = root.TFile(trim_bkg_name, "recreate")
    trim_bkg_tree = bkg_tree.CloneTree(0)
    random_indx = np.random.randint(0,bkg_tree.GetEntriesFast(),size=trim_bkg_events)
    for event_indx in tqdm(random_indx):
      bkg_tree.GetEntry( event_indx )
      trim_bkg_tree.Fill()
    trim_bkg_file.Write()
    print("Trimmed File \"{}\" ({:.2f} MB) written to \"{}\"".format(
      trim_bkg_name,
      os.path.getsize(out_path + "/" + trim_bkg_name),
      out_path))

else:
  print("Trimming {}...".format(file_name))
  root_file = root.TFile.Open(file_path + file_name)        # load in the desired file
  root_tree = root_file.Get("ljmet")                        # get the ljmet tree
  branches  = root_tree.GetListOfBranches()                 # get the ljmet branches/variables
  branch_list = [branch.GetName() for branch in branches]   # make a list of the branch names
  
  trim_events = int( root_tree.GetEntriesFast() * EVENT_SCALE ) 
  trim_file = root.TFile(trim_name, "recreate")
  trim_tree = root_tree.CloneTree(0)
  random_indx = np.random.randint(0,root_tree.GetEntriesFast(),size=trim_events)
  for event_indx in tqdm(range(10)):
    root_tree.GetEntry( event_indx )
    trim_tree.Fill()
  trim_file.Write()
  print("Trimmed File \"{}\" ({:.2f} MB) written to \"{}\"".format(
    trim_name,
    os.path.getsize(out_path + "/" + trim_name)/1E6,
    out_path))

print("Finished trimming .root files.")

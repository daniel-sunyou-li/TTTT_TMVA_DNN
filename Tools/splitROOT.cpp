// run by first making on lpc with: g++ `root-config --cflags` `root-config --libs` -o splitROOT.out splitROOT.cpp
#include<iostream>
#include<vector>
#include<string>
#include "TTree.h"
#include "TFile.h"

using namespace std;

int n_split = 3;  // set at 3 for the three different steps for this analysis
string in_path =  "~/nobackup/FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2/";
string out_path = "~/nobackup/FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2/";
cout << "Looking for samples in: " << in_path << endl;
cout << "If samples are not in specified path, please edit the correct in_path." << endl;
cout << "Writing new samples to: " << out_path << endl;
vector<string> bkg = {
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_hadd.root",
  "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_hadd.root",
  "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
  "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
  "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root",
  "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
  "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
  "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root",
  "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
  "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
  "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"
};

void progress(string filename, int current, int total){
  cout << "Processing " << filename << ": " << current << " / " << total << " events transferred... " << "\r" << flush;
}

void split_file(string in_path, string sample, string out_path, int this_split, int tot_split){
  // load in the root file
  TFile root_file( ( in_path + sample ).c_str() );
  TTree *root_tree;
  root_file.GetObject("ljmet", root_tree);
  // define some file parameters
  int n_entries = root_tree->GetEntriesFast();
  int split_entries = int ( n_entries / tot_split );
  string split_name_str = out_path + sample.substr(0, sample.find("hadd")) + "trim_" + to_string(this_split) + ".root";
  // build the trimmed root file
  TFile split_file( split_name_str.c_str() , "recreate");
  auto split_tree = root_tree->CloneTree(0);
  // populate the trimmed root file
  for( int i = this_split*split_entries; i < ( this_split + 1 )*split_entries; ++i ){
    progress( split_name_str, i, n_entries );
    root_tree->GetEntry(i);
    trim_tree->Fill();
  }
  cout << endl;
  trim_file.Write();
  // delete the old hadd file to save space
  str command_str = "rm " + in_path + sample;
  const char *command_ch = command_str.c_str();
  system(command_ch);
}

int main(){
  for( string bkg_sample : bkg ){
    for( int i = 0; i < n_split; ++i ){
       split_file(in_path, bkg_sample, out_path, i, n_split);
    }
  }
  cout << "Finished processing..." << endl;
  
  return 0;
}
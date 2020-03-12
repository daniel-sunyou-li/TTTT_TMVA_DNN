// run by first making on lpc with: g++ `root-config --cflags` `root-config --libs` -o splitROOT.out splitROOT.cpp
#include<iostream>
#include<vector>
#include<string>
#include "TTree.h"
#include "TFile.h"

using namespace std;

int n_split = 3;
string in_path =  "./FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2/";
string out_path = "./FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2_trim/";
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

void trim_file(string in_path, string sample, string out_path, int this_split, int tot_split){
  // load in the root file
  TFile root_file( ( in_path + sample ).c_str() );
  TTree *root_tree;
  root_file.GetObject("ljmet", root_tree);
  // define some file parameters
  int n_entries = root_tree->GetEntriesFast();
  int trim_entries = int ( n_entries / tot_split );
  string trim_name_str = out_path + sample.substr(0, sample.find("hadd")) + "trim_" + to_string(this_split) + ".root";
  // build the trimmed root file
  TFile trim_file( trim_name_str.c_str() , "recreate");
  auto trim_tree = root_tree->CloneTree(0);
  // populate the trimmed root file
  for( int i = this_split*trim_entries; i < ( this_split + 1 )*trim_entries; ++i ){
    progress( trim_name_str, i, n_entries );
    root_tree->GetEntry(i);
    trim_tree->Fill();
  }
  cout << endl;
  trim_file.Write();
}

int main(){
  for( string bkg_sample : bkg ){
    for( int i = 0; i < n_split; ++i ){
       trim_file(in_path, bkg_sample, out_path, i, n_split);
    }
  }
  cout << "Finished processing..." << endl;
  
  return 0;
}

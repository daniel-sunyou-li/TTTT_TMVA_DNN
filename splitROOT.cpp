#include<iostream>
#include<vector>
#include "TTree.h"
#include "TFile.h"

using namespace std;

void progress(string filename, int current, int total){
  cout << "Processing " << filename << " ..." << endl;
  cout << current << " / " << total << " events transferred... " << "\r" << flush;
}

int main(){
  string in_path = "./FWLJMET102X_1lep2017_Oct2019_4t_03032020_step2/"
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
  
  const char root_path = ( in_path + bkg[0] ).c_str();
  TFile root_file(root_path);
  TTree *root_tree;
  root_file.GetObject("ljmet", root_tree);
  
  int num_entries = root_tree->GetEntriesFast();
  int trim_entries = int ( num_entries / 3 );
  
  // get the first trim file
  TFile trim_file_1("trim_1.root", "RECREATE");
  auto trim_tree_1 = root_tree->CloneTree(0);
  
  for( int i = 0; i < trim_entries; ++i ){
    progress(bkg[0],i,num_entries);
    root_tree->GetEntry(i);
    trim_tree_1->Fill();
  }
  cout << endl;
  //trim_tree_1->Print();
  trim_file_1.Write();

  // get the second trim file
  TFile trim_file_2("trim_2.root", "RECREATE");
  auto trim_tree_2 = root_tree->CloneTree(0);
  
  for( int i = trim_entries; i < 2*trim_entries; ++i ){
    progress(bkg[0],i,num_entries);
    root_tree->GetEntry(i);
    trim_tree_2->Fill();
  }
  cout << endl;
  //trim_tree_2->Print();
  trim_file_2.Write();
  
  // get the third trim file
  TFile trim_file_3("trim_3.root", "RECREATE");
  auto trim_tree_3 = root_tree->CloneTree(0);
  
  for( int i = 2*trim_entries; i < num_entries; ++i ){
    progress(bkg[0],i,num_entries);
    root_tree->GetEntry(i);
    trim_tree_3->Fill();
  }
  cout << endl;
  //trim_tree_3->Print();
  trim_file_3.Write();
  
  cout << "Finished processing..." << endl;
  
  return 0;
}

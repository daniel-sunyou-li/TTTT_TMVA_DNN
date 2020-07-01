// run by first making on lpc with: g++ `root-config --cflags` `root-config --libs` -o splitROOT.out splitROOT.cpp
#include<iostream>
#include<vector>
#include<string>
#include "TTree.h"
#include "TFile.h"

using namespace std;

void progress(string filename, int current, int total){
  cout << "Processing " << filename << ": " << current << " / " << total << " events transferred... " << "\r" << flush;
}

void split_file(string in_path, string sample, string out_path, int this_split, int tot_split){
  // load in the root file
  TFile root_file( ( in_path + "/" + sample ).c_str() );
  TTree *root_tree;
  root_file.GetObject("ljmet", root_tree);
  // define some file parameters
  int n_entries = root_tree->GetEntriesFast();
  int split_entries = int ( n_entries / tot_split );
  string split_name_str = sample.substr(0, sample.find("hadd")) + "split" + to_string(this_split) + ".root";
  string split_name_path = out_path + "/" + split_name_str;
  // build the split root file
  TFile split_file( split_name_path.c_str() , "recreate");
  auto split_tree = root_tree->CloneTree(0);
  // populate the split root file
  for( int i = this_split*split_entries; i < ( this_split + 1 )*split_entries; ++i ){
    progress( split_name_str, i, n_entries );
    root_tree->GetEntry(i);
    split_tree->Fill();
  }
  cout << endl;
  split_file.Write();
}

int main( int argc, char *argv[] ){
  string in_path = argv[1];
  string out_path = argv[2];
  string sample = argv[3];
  int n_split = stoi(argv[4]);
  cout << "Looking for samples in: " << in_path << endl;
  cout << "If samples are not in specified path, please edit the correct in_path." << endl;
  cout << "Writing new samples to: " << out_path << endl;
  for( int i = 0; i < n_split; ++i ){
     split_file(in_path, sample, out_path, i, n_split);
  // delete the old hadd file to save space
  }
  string command_str = "rm " + in_path + "/" + sample;
  const char *command_ch = command_str.c_str();
  system(command_ch);
  
  return 0;
}

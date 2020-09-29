#include <cstdlib>
#include <vector>
#include <iostream>
#include <map>
#include <string>

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TStopwatch.h"

#include "TMVA/Tools.h"
#include "TMVA/Reader.h"
#include "TMVA/MethodCuts.h"

using namespace TMVA;

void TMVAClassificationApplication( TString myMethodList = "", TString inputFile="", TString outputFile="" ) 
{   
   // This loads the library
   TMVA::Tools::Instance();

   // Default MVA methods to be trained + tested
   std::map<std::string,int> Use;

   // --- Neural Networks (all are feed-forward Multilayer Perceptrons)
   Use["PyKeras"] = 1; // Keras DNN

   std::cout << std::endl;
   std::cout << "Start TMVA Classification Application" << std::endl;
   
   // Select methods (don't look at this code - not of interest)
   if (myMethodList != "") {
      for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) it->second = 0;

      std::vector<TString> mlist = gTools().SplitString( myMethodList, ',' );
      for (UInt_t i=0; i<mlist.size(); i++) {
         std::string regMethod(mlist[i]);

         if (Use.find(regMethod) == Use.end()) {
            std::cout << "Method \"" << regMethod 
                      << "\" not known in TMVA under this name. Choose among the following:" << std::endl;
            for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) {
               std::cout << it->first << " ";
            }
            std::cout << std::endl;
            return;
         }
         Use[regMethod] = 1;
      }
   }
   
   // --- Create the Reader object

   TMVA::Reader *reader = new TMVA::Reader( "!Color:!Silent" );    

   // Create a set of variables and declare them to the reader
   // - the variable names MUST corresponds in name and type to those given in the weight file(s) used
   Float_t var<number>;
   reader->AddVariable( "<var>", &var<number>);//order needs to match the order in varsList.py
 
   // --- Book the MVA methods

   // Book method(s)
   reader->BookMVA("PyKeras", <weightFilePathMass> );
   
   // Prepare input tree (this must be replaced by your data source)
   // in this example, there is a toy tree with signal and one with background events
   // we'll later on use only the "signal" events for the test in this example.
   //   
   TFile *input(0);
   
   if (!gSystem->AccessPathName( inputFile )){ 
      input = TFile::Open( inputFile ); // check if file in local directory exists 
      } 
   if (!input) {
      std::cout << "ERROR: could not open data file: "<<inputFile << std::endl;
      exit(1);
   }
   std::cout << "--- TMVAClassificationApp    : Using input file: " << input->GetName() << std::endl;
   
   // --- Event loop

   // Prepare the event tree
   // - here the variable names have to correspond to your tree
   // - you can use the same variables as above which is slightly faster,
   //   but of course you can use different ones and copy the values inside the event loop
   //
   std::cout << "--- Select sample" << std::endl;
   TTree* theTree = (TTree*)input->Get("ljmet");
   theTree->SetBranchAddress( "<var>", &var<number>);//order needs to match the order in varsList.py

   TFile *target  = new TFile( outputFile,"RECREATE" );
   target->cd();
   TTree *newTree = theTree->CloneTree(0);   
   Float_t kDNN<mass>; TBranch *b_kDNN<mass> = newTree->Branch("kDNN",&kDNN<mass>,"kDNN<mass>/F");

   // Efficiency calculator for cut method
   Int_t    nSelCutsGA = 0;
   Double_t effS       = 0.7;

   std::cout << "--- Processing: " << theTree->GetEntries() << " events" << std::endl;
   TStopwatch sw;
   sw.Start();
   for (Long64_t ievt=0; ievt<theTree->GetEntries();ievt++) {

      if (ievt%1000 == 0) std::cout << "--- ... Processing event: " << ievt << std::endl;

      theTree->GetEntry(ievt);

      // --- Return the MVA outputs and fill into histograms
      
      kDNN<mass> = reader->EvaluateMVA( "kDNN" );
      
      newTree->Fill();
    }
	
   // Get elapsed time
   sw.Stop();
   std::cout << "--- End of event loop: "; sw.Print();

   // --- Write tree
   newTree->Write();
   target->Close();

   std::cout << "--- Created root file: \"TMVApp.root\" containing the MVA output histograms" << std::endl;
  
   delete reader;
    
   std::cout << "==> TMVAClassificationApplication is done!" << std::endl << std::endl;
} 
	
   
   
   
   
   
   
   
   
   
   
   

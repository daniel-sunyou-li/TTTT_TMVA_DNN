#!/usr/bin/env python

#input variables
varList = {}

# EDIT ME 
bruxUserName = "dli50"
lpcUserName = "dsunyou"
eosUserName = "dali"
date = "10072020" # production date
#date = "08122020"

step2Sample = {
  "2017": "FWLJMET102X_1lep2017_Oct2019_4t_{}_step2".format( date ),
  "2018": "FWLJMET102X_1lep2018_Oct2019_4t_{}_step2".format( date )
}

step3Sample = {
  "2017": "FWLJMET102X_1lep2017_Oct2019_4t_{}_step3".format( date ),
  "2018": "FWLJMET102X_1lep2018_Oct2019_4t_{}_step3".format( date )
}

step2DirBRUX = {
  "2017": "/mnt/hadoop/store/group/bruxljm/{}/".format( step2Sample[ "2017" ] ),
  "2018": "/mnt/hadoop/store/group/bruxljm/{}/".format( step2Sample[ "2018" ] )
}

step2DirLPC = {
  "2017": "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step2Sample[ "2017" ] ),
  "2018": "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step2Sample[ "2018" ] )
}

step3DirLPC = {
  "2017": "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step3Sample[ "2017" ] ),
  "2018": "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step3Sample[ "2018" ] )
}

step2DirEOS = {
  "2017": "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step2Sample[ "2017" ] ),
  "2018": "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step2Sample[ "2018" ] )
}

step3DirEOS = {
  "2017": "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step3Sample[ "2017" ] ),
  "2018": "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step3Sample[ "2018" ] )
}

# full signal sample to be used in training
sig_training = {
  "2017": [ "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root" ],
  "2018": [ "TTTT_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root" ]
}

# manual splitting of samples is optional, default is to use isTraining = 1/2/3 to divide samples
# first set of manually split samples to be used in training models
sig_split0 = {
  "2017": [ sample.replace( "hadd", "split0" ) for sample in sig_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split0" ) for sample in sig_training["2018"] ]
}

# second set of manually split samples to be used in testing models
sig_split1 = {
  "2017": [ sample.replace( "hadd", "split1" ) for sample in sig_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split1" ) for sample in sig_training["2018"] ]
}

# third set of manually split samples to be used for obtaining limits
sig_split2 = {
  "2017": [ sample.replace( "hadd", "split2" ) for sample in sig_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split2" ) for sample in sig_training["2018"] ]
}

# full background samples to be used in training
bkg_training = {
  "2017": [
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt1b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt2b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt1b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt2b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttbb_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttcc_hadd.root",
    "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttjj_hadd.root",
    "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root",
    "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"  
  ],
  "2018": [
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_tt1b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_tt2b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_tt1b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_tt2b_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttbb_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttcc_hadd.root",
    "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttjj_hadd.root",
    "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root",
    "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root",
    "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root"
  ]
}

bkg_split0 = {
  "2017": [ sample.replace( "hadd", "split0" ) for sample in bkg_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split0" ) for sample in bkg_training["2018"] ]
}

bkg_split1 = {
  "2017": [ sample.replace( "hadd", "split1" ) for sample in bkg_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split1" ) for sample in bkg_training["2018"] ]
}

bkg_split2 = {
  "2017": [ sample.replace( "hadd", "split2" ) for sample in bkg_training["2017"] ],
  "2018": [ sample.replace( "hadd", "split2" ) for sample in bkg_training["2018"] ]
}

# generalized efficiency values
eff = {
  "TTJetsSemiLepNjet9": 0.0057,
  "TTJets0mtt":         0.8832,
  "TTJets700mtt":       0.0921,
  "TTJets1000mtt":      0.02474
}

# generalized branching ratio values
BR = {
  "TTJetsHad":     0.457,
  "TTJetsSemiLep": 0.438,
  "TTJets2L2nu":   0.105
}

# generalized cross section values
xsec = {
  "TTJets":             831.76,
  "TTJetsSemiLepNjet9": 831.76 * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"]
}

# generalized number of processed MC events  
nrun = {
  "TTJetsHad":            { "2017": 129092906.0, "2018": 132368556.0 },
  "TTJetsHadUEdn":        { "2017": 25943263.0,  "2018": 26459542.0 },
  "TTJetsHadUEup":        { "2017": 26986311.0,  "2018": 23298972.0 },
  "TTJetsHadHDAMPdn":     { "2017": 26007959.0,  "2018": 25988142.0 },
  "TTJetsHadHDAMPup":     { "2017": 25586551.0,  "2018": 24851988.0 },
  "TTJets2L2nu":          { "2017": 68448328.0,  "2018": 63791484.0 },
  "TTJets2L2nuUEdn":      { "2017": 5431150.0,   "2018": 4914480.0 },
  "TTJets2L2nuUEup":      { "2017": 5455598.0,   "2018": 5401744.0 },
  "TTJets2L2nuHDAMPdn":   { "2017": 5248352.0,   "2018": 5368300.0 },
  "TTJets2L2nuHDAMPup":   { "2017": 5389169.0,   "2018": 5368300.0 },
  "TTJetsSemiLep":        { "2017": 109124472.0, "2018": 100579948.0 },
  "TTJetsSemiLepUEdn":    { "2017": 26885578.0,  "2018": 20274614.0 },
  "TTJetsSemiLepUEup":    { "2017": 25953874.0,  "2018": 26729924.0 },
  "TTJetsSemiLepHDAMPdn": { "2017": 26359926.0,  "2018": 25270096.0 },
  "TTJetsSemiLepHDAMPup": { "2017": 27068397.0,  "2018": 26841790.0 },
  "TTJetsSemiLepNjet9":   { "2017": 8648145.0,   "2018": 8398387.0 }
}

# all samples for step3, ( Name, # Processed MC events, xsec [pb] )

all_samples = { 
  "2017": {
    "TTTT": ("TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root", 849964.0, 0.012 ),
  
    "TTHH": ( "TTHH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 199371.0, 0.0007408 ),
    "TTTJ": ( "TTTJ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 198546.0, 0.0004741 ),
    "TTTW": ( "TTTW_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 199699.0, 0.0007330 ),
    "TTWH": ( "TTWH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 198978.0, 0.0013590 ),
    "TTWl": ( "TTWJetsToLNu_TuneCP5_PSweights_13TeV-amcatnloFXFX-madspin-pythia8_hadd.root", 2686141.0, 0.2043 ),
    "TTWW": ( "TTWW_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 199008.0, 0.0078830 ),
    "TTWZ": ( "TTWZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 198756.0, 0.0029740 ),
    "TTZH": ( "TTZH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 199285.0, 0.0012530 ),
    "TTZZ": ( "TTZZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 199363.0, 0.0015720 ),
    "TTZlM10": ( "TTZToLLNuNu_M-10_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root", 5239484.0, 0.2529 ),
    "TTZlM1to10": ( "TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root", 129114.0, 0.2529 ),
    "TTHnoB": ( "ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root", 7814711.0, 0.215 ),
    "TTHB": ( "ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root", 7833734.0, 0.2934 ),
 
# weights don't matter for data 
    "DataE": ("SingleElectron_hadd.root", 1., 1. ),
    "DataM": ("SingleMuon_hadd.root", 1., 1. ),
    "DataJ": ("JetHT_hadd.root", 1., 1.),
  
    "DYMG200": ( "DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 10699051.0, 40.99*1.23 ),
    "DYMG400": ( "DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 10174800.0, 5.678*1.23 ),
    "DYGM600": ( "DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 8691608.0, 1.367*1.23 ),
    "DYGM800": ( "DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 3089712.0, 0.6304*1.23 ),
    "DYMG1200": ( "DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 616906.0, 0.1514*1,23 ),
    "DYMG2500": ( "DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 401334.0, 0.003565*1.23 ),
  
    "QCDht200": ( "QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 59360369.0, 1712000.0 ),
    "QCDht300": ( "QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 59459614.0, 347700.0 ),
    "QCDht500": ( "QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 56041018.0, 32100.0 ),
    "QCDht700": ( "QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 135551578.0, 6831.0 ),
    "QCDht1000": ( "QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 16770762.0, 1207.0 ),
    "QCDht1500": ( "QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 11508604.0, 119.9 ),
    "QCDht2000": ( "QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 5825566.0, 25.24 ),
  
    "Tbs": ( "ST_s-channel_antitop_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root", 2952214.0, 4.16/3. ),
    "Ts": ( "ST_s-channel_top_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root", 6895750.0, 7.20/3. ),
    "Tbt": ( "ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root", 64818800.0, 80.95 ),
    "Tt": ( "ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root", 122688200.0, 136.02 ),
    "TbtW": ( "ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root", 7686032.0, 35.83 ),
    "TtW": ( "ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root", 7884388.0, 35.83 ),
  
    "TTJets2L2nuTT1b": ( "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJets2L2nu"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuTT2b": ( "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJets2L2nu"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuTTbb": ( "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJets2L2nu"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuTTcc": ( "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJets2L2nu"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuTTjj": ( "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJets2L2nu"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
  
    "TTJets2L2nuUEdnTT1b": ( "TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJets2L2nuUEdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEdnTT2b": ( "TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJets2L2nuUEdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEdnTTbb": ( "TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJets2L2nuUEdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEdnTTcc": ( "TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJets2L2nuUEdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEdnTTjj": ( "TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJets2L2nuUEdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEupTT1b": ( "TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJets2L2nuUEup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEupTT2b": ( "TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJets2L2nuUEup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEupTTbb": ( "TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJets2L2nuUEup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEupTTcc": ( "TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJets2L2nuUEup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuUEupTTjj": ( "TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJets2L2nuUEup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPdnTT1b": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJets2L2nuHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPonTT2b": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJets2L2nuHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPonTTbb": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJets2L2nuHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPonTTcc": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJets2L2nuHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPonTTjj": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJets2L2nuHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPupTT1b": ( "TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJets2L2nuHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPupTT2b": ( "TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJets2L2nuHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPupTTbb": ( "TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJets2L2nuHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPupTTcc": ( "TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJets2L2nuHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
    "TTJets2L2nuHDAMPupTTjj": ( "TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJets2L2nuHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJets2L2nu"] ),
  
    "TTJetsHadTT1b": ( "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsHad"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadTT2b": ( "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsHad"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadTTbb": ( "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsHad"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadTTcc": ( "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsHad"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadTTjj": ( "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsHad"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsSemiLepNjet9binTT1b": ( "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] * ( 1. - eff["TTJetsSemiLepNjet9"] ) ),
    "TTJetsSemiLepNjet9binTT2b": ( "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] * ( 1. - eff["TTJetsSemiLepNjet9"] ) ),
    "TTJetsSemiLepNjet9binTTbb": ( "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] * ( 1. - eff["TTJetsSemiLepNjet9"] ) ),
    "TTJetsSemiLepNjet9binTTcc": ( "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] * ( 1. - eff["TTJetsSemiLepNjet9"] ) ),
    "TTJetsSemiLepNjet9binTTjj": ( "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] * ( 1. - eff["TTJetsSemiLepNjet9"] ) ),
    "TTJetsSemiLepNjet0TT1b": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt1b_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TT2b": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt2b_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTbb": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTcc": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTjj1": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTjj2": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTjj3": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTjj4": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet0TTjj5": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_hadd.root", nrun["TTJetsSemiLep"]["2017"] * ( 1. - eff["TTJetsSemiLepNjet9"] ), xsec["TTJets"] * BR["TTJetsSemiLep"] * eff["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet9TT1b": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt1b_hadd.root", nrun["TTJetsSemiLep"]["2017"] * eff["TTJetsSemiLepNjet9"] + nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet9TT2b": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt2b_hadd.root", nrun["TTJetsSemiLep"]["2017"] * eff["TTJetsSemiLepNjet9"] + nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet9TTbb": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttbb_hadd.root", nrun["TTJetsSemiLep"]["2017"] * eff["TTJetsSemiLepNjet9"] + nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet9TTcc": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttcc_hadd.root", nrun["TTJetsSemiLep"]["2017"] * eff["TTJetsSemiLepNjet9"] + nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJetsSemiLepNjet9"] ),
    "TTJetsSemiLepNjet9TTjj": ( "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttjj_hadd.root", nrun["TTJetsSemiLep"]["2017"] * eff["TTJetsSemiLepNjet9"] + nrun["TTJetsSemiLepNjet9"]["2017"], xsec["TTJetsSemiLepNjet9"] ),
  
    "TTJetsHadUEdnTT1b": ( "TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsHadUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEdnTT2b": ( "TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsHadUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEdnTTbb": ( "TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsHadUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEdnTTcc": ( "TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsHadUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEdnTTjj": ( "TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsHadUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEupTT1b": ( "TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsHadUEup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEupTT2b": ( "TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsHadUEup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEupTTbb": ( "TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsHadUEup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEupTTcc": ( "TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsHadUEup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadUEupTTjj": ( "TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsHadUEup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPdnTT1b": ( "TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsHadHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPdnTT2b": ( "TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsHadHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPdnTTbb": ( "TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsHadHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPdnTTcc": ( "TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsHadHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPdnTTjj": ( "TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsHadHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPupTT1b": ( "TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsHadHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPupTT2b": ( "TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsHadHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPupTTbb": ( "TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsHadHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPupTTcc": ( "TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsHadHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
    "TTJetsHadHDAMPupTTjj": ( "TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsHadHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsHad"] ),
  
    "TTJetsSemiLepUEdnTT1b": ( "TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsSemiLepUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEdnTT2b": ( "TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsSemiLepUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEdnTTbb": ( "TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsSemiLepUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEdnTTcc": ( "TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsSemiLepUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEdnTTjj": ( "TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsSemiLepUEdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEupTT1b": ( "TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsSemiLepUEup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEupTT2b": ( "TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsSemiLepUEup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEupTTbb": ( "TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsSemiLepUEup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEupTTcc": ( "TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsSemiLepUEup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepUEupTTjj": ( "TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsSemiLepUEup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPdnTT1b": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsSemiLepHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPdnTT2b": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsSemiLepHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPdnTTbb": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsSemiLepHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPdnTTcc": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsSemiLepHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPdnTTjj": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsSemiLepHDAMPdn"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPupTT1b": ( "TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root", nrun["TTJetsSemiLepHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPupTT2b": ( "TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root", nrun["TTJetsSemiLepHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPupTTbb": ( "TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root", nrun["TTJetsSemiLepHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPupTTcc": ( "TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root", nrun["TTJetsSemiLepHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
    "TTJetsSemiLepHDAMPupTTjj": ( "TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root", nrun["TTJetsSemiLepHDAMPup"]["2017"], xsec["TTJets"] * BR["TTJetsSemiLep"] ),
  
    "WJetsMG200": ( "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 16118580.0, 359.7 * 1.21 ),
    "WJetsMG400": ( "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 14237953.0, 48.91 * 1.21),
    "WJetsMG600": ( "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 21570948.0, 12.05 * 1.21 ),
    "WJetsMG800": ( "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 20182034.0, 5.501 * 1.21 ),
    "WJetsMG12001": ( "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root", 39694923.0, 1.329 * 1.21 ),
    "WJetsMG12002": ( "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root", 39694923.0, 1.329 * 1.21 ),
    "WJetsMG12003": ( "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root", 39694923.0, 1.329 * 1.21 ),
    "WJetsMG25001": ( "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root", 34500020.0, 0.03216 * 1.21 ),
    "WJetsMG25002": ( "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root", 34500020.0, 0.03216 * 1.21 ),
    "WJetsMG25003": ( "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root", 34500020.0, 0.03216 * 1.21 ),
    "WJetsMG25004": ( "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_4_hadd.root", 34500020.0, 0.03216 * 1.21 ),
  
    "WW": ( "WW_TuneCP5_13TeV-pythia8_hadd.root", 7765828.0, 118.7 ),
    "WZ": ( "WZ_TuneCP5_13TeV-pythia8_hadd.root", 3928567.0, 47.13 ),
    "ZZ": ( "ZZ_TuneCP5_13TeV-pythia8_hadd.root", 1925931.0, 16.523 )
  }, 
  "2018": { 
    "TTHH": ( "TTHH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTTJ": ( "TTTJ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTTT": ( "TTTT_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root", 0, 0 ),
    "TTTW": ( "TTTW_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTWH": ( "TTWH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTWl": ( "TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_hadd.root", 0, 0 ),
    "TTWW": ( "TTWW_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTWZ": ( "TTWZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTZH": ( "TTZH_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTZlM10": ( "TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root", 0, 0 ),
    "TTZlM1to10": ( "TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root", 0, 0 ),
    "TTZZ": ( "TTZZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "TTHnoB": ( "ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root", 0, 0 ),
    "TTHB": ( "ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root", 0, 0 ),
  
# weights don't matter for data
    "DataM": ( "SingleMuon_hadd.root", 1., 1. ), 
    "DataE": ( "EGamma_hadd.root", 1., 1. ),
    "DataJ": ( "JetHT_hadd.root", 1., 1. ),  

    "DYMG200": ( "DYJetsToLL_M-50_HT-200to400_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "DYMG400": ( "DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "DYMG600": ( "DYJetsToLL_M-50_HT-600to800_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "DYMG800": ( "DYJetsToLL_M-50_HT-800to1200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "DYMG1200": ( "DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "DYMG2500": ( "DYJetsToLL_M-50_HT-2500toInf_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
  
    "QCDht200": ( "QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht300": ( "QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht500": ( "QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht700": ( "QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht1000": ( "QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht1500": ( "QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "QCDht2000": ( "QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
  
    "Ts": ( "ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8_hadd.root", 0, 0 ),
    "Tbt": ( "ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_hadd.root", 0, 0 ),
    "Tt": ( "ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_hadd.root", 0, 0 ),
    "TbtW": ( "ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_hadd.root", 0, 0 ),
    "TtW": ( "ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_hadd.root", 0, 0 ),
  
    "TTJets2L2nuTT1b": ( "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJets2L2nuTT2b": ( "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJets2L2nuTTbb": ( "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJets2L2nuTTcc": ( "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJets2L2nuTTjj": ( "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
  
    "TTJets2L2nuUEdnTT1b": ( "TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJets2L2nuUEdnTT2b": ( "TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJets2L2nuUEdnTTbb": ( "TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJets2L2nuUEdnTTcc": ( "TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJets2L2nuUEdnTTjj": ( "TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJets2L2nuUEupTT1b": ( "TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJets2L2nuUEupTT2b": ( "TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJets2L2nuUEupTTbb": ( "TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJets2L2nuUEupTTcc": ( "TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJets2L2nuUEupTTjj": ( "TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPdnTT1b": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPdnTT2b": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPdnTTbb": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPdnTTcc": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPdnTTjj": ( "TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPupTT1b": ( "TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPupTT2b": ( "TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPupTTbb": ( "TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPupTTcc": ( "TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJets2L2nuHDAMPupTTjj": ( "TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
  
    "TTJetsHadTT1b": ( "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0),
    "TTJetsHadTT2b": ( "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsHadTTbb": ( "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsHadTTcc": ( "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsHadTTjj": ( "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
  
    "TTJetsHadUEdnTT1b": ( "TTToHadronic_TuneCP5down_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsHadUEdnTT2b": ( "TTToHadronic_TuneCP5down_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0),
    "TTJetsHadUEdnTTbb": ( "TTToHadronic_TuneCP5down_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsHadUEdnTTcc": ( "TTToHadronic_TuneCP5down_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsHadUEdnTTjj": ( "TTToHadronic_TuneCP5down_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsHADUEupTT1b": ( "TTToHadronic_TuneCP5up_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsHADUEupTT2b": ( "TTToHadronic_TuneCP5up_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsHADUEupTTbb": ( "TTToHadronic_TuneCP5up_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsHADUEupTTcc": ( "TTToHadronic_TuneCP5up_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsHADUEupTTjj": ( "TTToHadronic_TuneCP5up_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPdnTT1b": ( "TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPdnTT2b": ( "TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPdnTTbb": ( "TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPdnTTcc": ( "TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPdnTTjj": ( "TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPupTT1b": ( "TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPupTT2b": ( "TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPupTTbb": ( "TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPupTTcc": ( "TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsHADHDAMPupTTjj": ( "TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
  
    "TTJetsSemiLepNjet9binTT1b": ( "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9binTT2b": ( "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9binTTbb": ( "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9binTTcc": ( "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9binTTjj": ( "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TT1b": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TT2b": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TTbb": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TTcc": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TTjj1": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet0TTjj2": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9TT1b": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9TT2b": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9TTbb": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9TTcc": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepNjet9TTjj": ( "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_ttjj_hadd.root", 0, 0 ),
  
    "TTJetsSemiLepUEdnTT1b": ( "TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEdnTT2b": ( "TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEdnTTbb": ( "TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEdnTTcc": ( "TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEdnTTjj": ( "TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEupTT1b": ( "TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEupTT2b": ( "TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEupTTbb": ( "TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEupTTcc": ( "TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepUEupTTjj": ( "TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPdnTT1b": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPdnTT2b": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPdnTTbb": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPdnTTcc": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPdnTTjj": ( "TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPupTT1b": ( "TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt1b_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPupTT2b": ( "TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8_tt2b_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPupTTbb": ( "TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttbb_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPupTTcc": ( "TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttcc_hadd.root", 0, 0 ),
    "TTJetsSemiLepHDAMPupTTjj": ( "TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8_ttjj_hadd.root", 0, 0 ),

    "WJetsMG200": ( "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "WJetsMG400": ( "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "WJetsMG600": ( "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "WJetsMG800": ( "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "WJetsMG1200": ( "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
    "WJetsMG2500": ( "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root", 0, 0 ),
  
    "WW": ( "WW_TuneCP5_PSweights_13TeV-pythia8_hadd.root", 0, 0 ),
    "WZ": ( "WZ_TuneCP5_PSweights_13TeV-pythia8_hadd.root", 0, 0 ),
    "ZZ": ( "ZZ_TuneCP5_13TeV-pythia8_hadd.root", 0, 0 )
  }
}

#[<variable in trees>, <variable name for axes and titles>, <unit>]

varList["DNN"] = [
  ("AK4HTpMETpLepPt", "S_{T} [GeV]" , 0, 4000, 101),
  ("minMleppBjet", "min[M(l,b)] [GeV]", 0, 1000, 101),
  ("mass_minBBdr", "M(b,b) with min[#DeltaR(b,b)] [GeV]", 0, 1400, 51),
  ("deltaR_lepBJet_maxpt", "#DeltaR(l,b) with max[p_{T}(l,b)]", 0, 6.0, 51),
  ("lepDR_minBBdr", "#DeltaR(l,bb) with min[#DeltaR(b,b)]", -1, 10, 51),
  ("centrality", "Centrality", 0, 1.0, 51),
  ("deltaEta_maxBB", "max[#Delta#eta(b,b)]", -6, 11, 51),
  ("aveCSVpt", "ave(p_{T} weighted CSVv2) [GeV]", -0.3, 1.1, 101),
  ("aveBBdr", "ave[#DeltaR(b,b)]", 0, 6.0, 51),
  ("FW_momentum_0", "0^{th} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_1", "1^{st} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_2", "2^{nd} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_3", "3^{rd} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_4", "4^{th} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_5", "5^{th} FW moment [GeV]", 0, 1, 51),
  ("FW_momentum_6", "6^{th} FW moment [GeV]", 0, 1, 51),
  ("mass_maxJJJpt", "M(jjj) with max[p_{T}(jjj)] [GeV]", 0, 3000, 101),
  ("BJetLeadPt", "p_{T}{b_{1}) [GeV]", 0, 2000, 101),
  ("deltaR_minBB", "min[#DeltaR(b,b)]", 0, 6.0, 51),
  ("minDR_lepBJet", "min[#DeltaR(l,b)]", 0, 6.0, 51),
  ("MT_lepMet", "M_{T}(l,#slash{E}_{T}) [GeV]", 0, 250, 51),
  ("AK4HT", "H_{T} [GeV]", 0, 3000, 121),
  ("hemiout", "Hemiout [GeV]", 0, 3000, 101),
  ("theJetLeadPt", "p_{T}(j_{1}) [GeV]", 0, 1500, 101),
  ("corr_met_MultiLepCalc", "p_{T}^{miss} [GeV]", 0, 1500, 51),
  ("leptonPt_MultiLepCalc", "Lepton p_{T} [GeV]", 0, 600, 121),
  ("mass_lepJets0", "M(l,j_{1}) [GeV]", 0, 2200, 101), 
  ("mass_lepJets1", "M(l,j_{2}) [GeV]", 0, 3000, 101),
  ("mass_lepJets2", "M(l,j_{3}) [GeV]", 0, 3000, 101),
  ("MT2bb", "MT2bb [GeV]", 0, 400, 51),
  ("mass_lepBJet0", "M(l,b_{1}) [GeV]", 0, 1800, 101),
  ("mass_lepBJet_mindr", "M(l,b) with min[#DeltaR(l,b)] [GeV]", 0, 800, 51),
  ("secondJetPt", "p_{T}(j_{2}) [GeV]", 0, 2500, 101),
  ("fifthJetPt", "p_{T}(j_{5}) [GeV]", 0, 400, 101),
  ("sixthJetPt", "p_{T}(j_{6}) [GeV]", 0, 400, 51),
  ("PtFifthJet", "5^{th} jet p_{T} [GeV]", -1, 2000, 101),
  ("mass_minLLdr", "M(j,j) with min[#DeltaR(j,j)], j #neq b [GeV]", 0, 600, 51),
  ("mass_maxBBmass", "max[M(b,b)] [GeV]", 0, 2000, 101),
  ("deltaR_lepJetInMinMljet", "#DeltaR(l,j) with min M(l, j)", 0, 4.5, 101),
  ("deltaPhi_lepJetInMinMljet", "#DeltaPhi(l,j) with min M(l, j)", -4, 4, 51),
  ("deltaR_lepbJetInMinMlb", "#DeltaR(l,b) with min M(l, b)", 0, 6.0, 51),
  ("deltaPhi_lepbJetInMinMlb", "#DeltaPhi(l,b) with min M(l, b)", -11, 5, 101),
  ("M_allJet_W", "M(J_{all}, W_{lep}) [GeV]", 0, 10000, 201),
  ("HT_bjets", "HT(bjets) [GeV]", 0, 1800, 101),
  ("ratio_HTdHT4leadjets", "HT/HT(4 leading jets)", 0, 2.6, 51),
  ("csvJet3", "DeepCSV(3rdPtJet)", -2.2, 1.2, 101),
  ("csvJet4", "DeepCSV(4thPtJet)", -2.2, 1.2, 101),
  ("firstcsvb_bb", "DeepCSV(1stDeepCSVJet)", -2, 1.5, 51),
  ("secondcsvb_bb", "DeepCSV(2ndDeepCSVJet)", -2, 1.5, 51),
  ("thirdcsvb_bb", "DeepCSV(3rdDeepCSVJet)", -2, 1.5, 51),
  ("fourthcsvb_bb", "DeepCSV(4thDeepCSVJet)", -2, 1.5, 51),
  ("NJets_JetSubCalc", "AK4 jet multiplicity", 0, 15, 16),
  ("HT_2m", "HTwoTwoPtBjets [GeV]", -20, 5000, 201),
  ("Sphericity", "Sphericity", 0, 1.0, 51),
  ("Aplanarity", "Aplanarity", 0, 0.5, 51),
  ("minDR_lepJet", "min[#DeltaR(l,j)]", 0, 4, 51),
  ("BDTtrijet1", "trijet1 discriminator", -1, 1, 101),
  ("BDTtrijet2", "trijet2 discriminator", -1, 1, 101),
  ("BDTtrijet3", "trijet3 discriminator", -1, 1, 101),
  ("BDTtrijet4", "trijet4 discriminator", -1, 1, 51),
  ("NresolvedTops1pFake", "resolved t-tagged jet multiplicity", 0, 5, 6),
  ("NJetsTtagged", "t-tagged jet multiplicity", 0, 4, 5),
  ("NJetsWtagged", "W-tagged multiplicity", 0, 5, 6),
  ("NJetsCSV_MultiLepCalc", "b-tagged jet multiplicity", 0, 10, 11),
  ("HOTGoodTrijet1_mass", "HOTGoodTrijet1_mass [GeV]", 0, 300, 51),               # Trijet variables
  ("HOTGoodTrijet1_dijetmass", "HOTGoodTrijet1_dijetmass [GeV]", 0, 250, 51),
  ("HOTGoodTrijet1_pTratio", "HOTGoodTrijet1_pTratio" , 0, 1, 51),
  ("HOTGoodTrijet1_dRtridijet", "HOTGoodTrijet1_dRtridijet", 0, 4, 51),
  ("HOTGoodTrijet1_csvJetnotdijet", "HOTGoodTrijet1_csvJetnotdijet", -2.2, 1.2, 101),
  ("HOTGoodTrijet1_dRtrijetJetnotdijet", "HOTGoodTrijet1_dRtrijetJetnotdijet", 0, 4, 51),
  ("HOTGoodTrijet2_mass", "HOTGoodTrijet2_mass [GeV]", 0, 300, 51),
  ("HOTGoodTrijet2_dijetmass", "HOTGoodTrijet2_dijetmass [GeV]", 0, 250, 51),
  ("HOTGoodTrijet2_pTratio", "HOTGoodTrijet2_pTratio", 0, 1, 51),
  ("HOTGoodTrijet2_dRtridijet", "HOTGoodTrijet2_dRtridijet", 0, 4, 51),
  ("HOTGoodTrijet2_csvJetnotdijet", "HOTGoodTrijet2_csvJetnotdijet", -2.2, 1.2, 101),
  ("HOTGoodTrijet2_dRtrijetJetnotdijet", "HOTGoodTrijet2_dRtrijetJetnotdijet", 0, 4, 51)
]

varList["Step3"] = varList["DNN"][:] 
varList["Step3"].append( tuple( ( "DNN_disc_4j_40vars", "tttt discriminator (4j, 40vars)", 0, 1, 101) ) )
varList["Step3"].append( tuple( ( "DNN_disc_4j_50vars", "tttt discriminator (4j, 50vars)", 0, 1, 101) ) )
varList["Step3"].append( tuple( ( "DNN_disc_4j_76vars", "tttt discriminator (4j, 76vars)", 0, 1, 101) ) )
varList["Step3"].append( tuple( ( "DNN_disc_4j_40vars", "tttt discriminator (4j, 40vars)", 0, 1, 101) ) )
varList["Step3"].append( tuple( ( "DNN_disc_4j_50vars", "tttt discriminator (4j, 50vars)", 0, 1, 101) ) )
varList["Step3"].append( tuple( ( "DNN_disc_4j_76vars", "tttt discriminator (4j, 76vars)", 0, 1, 101) ) )

# weight event count

weightStr = "triggerXSF * pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc * " + \
            "(MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) ) * xsecEff * tthfWeight * njetsWeight * btagCSVWeight * btagCSVRenormWeight"

# step3 weight event
targetLumi = 41530. # 1/pb
uncertainties = {
  "LUMINOSITY": { "2017": 0.023, "2018": 0.025 },
  "ELECTRON": { 
    "TRIGGER": { "2017": 0.0, "2018": 0.0 },
    "ID": { "2017": 0.03, "2018": 0.03 },
    "ISOLATION": { "2017": 0.0, "2018": 0.0 },
    "TOTAL": { "2017": 0, "2018": 0 } },
  "MUON": {
    "TRIGGER": { "2017": 0.0, "2018": 0.0 },
    "ID": { "2017": 0.03, "2018": 0.03 },
    "ISOLATION": { "2017": 0.0, "2018": 0.0 },
    "TOTAL": { "2017": 0, "2018": 0 } }
}

for lepton in [ "ELECTRON", "MUON" ]:
  for year in uncertainties[ lepton ][ "TOTAL" ]:
    uncertainties[ lepton ][ "TOTAL" ][ year ] = ( uncertainties[ lepton ][ "TRIGGER" ][ year ] + 
                                                   uncertainties[ lepton ][ "ID" ][ year ] + 
                                                   uncertainties[ lepton ][ "ISOLATION" ][ year ] +
                                                   uncertainties[ "LUMINOSITY" ][ year ] )**0.5
                                                     
# weight events
#weights = {
#  year: { sample: targetLumi * all_samples[ year ][ sample ][1] / all_samples[ year ][ sample ][2] for sample in all_samples[ year ] } for year in all_samples.keys()
#}

# general cut, add selection based cuts in training scripts
cutStr =  "( ( leptonPt_MultiLepCalc > 20 && isElectron ) || " + \
          "( leptonPt_MultiLepCalc > 20 && isMuon ) ) && " + \
          "( corr_met_MultiLepCalc > 60 ) && " + \
          "( MT_lepMet > 60 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[0] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[1] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[2] > 0 ) && " + \
          "( minDR_lepJet > 0.4 ) && " + \
          "( AK4HT > 500 ) && " + \
          "( DataPastTriggerX == 1 ) && ( MCPastTriggerX == 1 )"

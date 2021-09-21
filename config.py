#!/usr/bin/env python

#input variables
varList = {}

# EDIT ME 
bruxUserName = "dli50"
lpcUserName = "dsunyou"
eosUserName = "dali"
#date = "10072020" # production date
date = "02182021"

step2Sample = {
  "2017": "FWLJMET102X_1lep2017_Oct2019_3t_{}_step2".format( date ),
  "2018": "FWLJMET102X_1lep2018_Oct2019_3t_{}_step2".format( date )
}

step3Sample = { year: "FWLJMET102X_1lep{}_Oct2019_4t_{}_step3".format( str( year ), date ) for year in step2Sample.keys() }

step2DirBRUX = { year: "/mnt/hadoop/store/group/bruxljm/{}/".format( step2Sample[ year ] ) for year in step2Sample.keys() }

#step2DirLPC = { year: "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step2Sample[ year ] ) for year in step2Sample.keys() }
step2DirLPC = { year: "~/nobackup/TTT-singleLep/CMSSW_9_4_6_patch1/src/TTT-singleLep/DNN/{}/".format( step2Sample[ year ] ) for year in step2Sample.keys() }

step3DirLPC = { year: "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/{}/".format( step3Sample[ year ] ) for year in step2Sample.keys() }

step2DirEOS = { year: "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step2Sample[ year ] ) for year in step2Sample.keys() }

step3DirEOS = { year: "root://cmseos.fnal.gov///store/user/{}/{}/".format( eosUserName, step3Sample[ year ] ) for year in step2Sample.keys() }

# full signal sample to be used in training
sig_training = {
  "2017": [ "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root" ],
  "2018": [ "TTTT_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root" ]
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

# all samples for step3, ( Name, # Processed MC events, xsec [pb] )

shift_keys = {
  "": "",
  "UEdn": "down",
  "UEup": "up",
  "HDAMPup": "hdampUP",
  "HDAMPdn": "hdampDN"
}

all_samples = {
  "2017": {
    "TTTT": "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root",
    "TTHH": "TTHH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTTJ": "TTTJ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTTW": "TTTW_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWH": "TTWH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWl": "TTWJetsToLNu_TuneCP5_PSweights_13TeV-amcatnloFXFX-madspin-pythia8_hadd.root",
    "TTWW": "TTWW_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWZ": "TTWZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTZH": "TTZH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTZZ": "TTZZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTZlM10": "TTZToLLNuNu_M-10_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root",
    "TTZlM1to10": "TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root",
    "TTHnoB": "ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root",
    "TTHB": "ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root",

    "DataE": "SingleElectron_hadd.root",
    "DataM": "SingleMuon_hadd.root",
    "DataJ": "JetHT_hadd.root",

    "DYMG200": "DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG400": "DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYGM600": "DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYGM800": "DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG1200": "DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG2500": "DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",

    "QCDht200": "QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht300": "QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht500": "QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht700": "QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht1000": "QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht1500": "QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "QCDht2000": "QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8_hadd.root",

    "Tbs": "ST_s-channel_antitop_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root",
    "Ts": "ST_s-channel_top_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root",
    "Tbt": "ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root",
    "Tt": "ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root",
    "TbtW": "ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root",
    "TtW": "ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root",

    "WJetsMG200": "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG400": "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG600": "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG800": "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG12001": "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root",
    "WJetsMG12002": "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root",
    "WJetsMG12003": "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root",
    "WJetsMG25001": "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root",
    "WJetsMG25002": "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root",
    "WJetsMG25003": "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root",
    "WJetsMG25004": "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_4_hadd.root",

    "WW": "WW_TuneCP5_13TeV-pythia8_hadd.root",
    "WZ": "WZ_TuneCP5_13TeV-pythia8_hadd.root",
    "ZZ": "ZZ_TuneCP5_13TeV-pythia8_hadd.root"
  },
  "2018": {
    "TTHH": "TTHH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTTJ": "TTTJ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTTT": "TTTT_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root",
    "TTTW": "TTTW_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWH": "TTWH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWl": "TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_hadd.root",
    "TTWW": "TTWW_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTWZ": "TTWZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTZH": "TTZH_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTZlM10": "TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root",
    "TTZlM1to10": "TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root",
    "TTZZ": "TTZZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "TTHnoB": "ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root",
    "TTHB": "ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root",

    "DataM": "SingleMuon_hadd.root",
    "DataE": "EGamma_hadd.root",
    "DataJ": "JetHT_hadd.root",

    "DYMG200": "DYJetsToLL_M-50_HT-200to400_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG400": "DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG600": "DYJetsToLL_M-50_HT-600to800_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG800": "DYJetsToLL_M-50_HT-800to1200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG1200": "DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",
    "DYMG2500": "DYJetsToLL_M-50_HT-2500toInf_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8_hadd.root",

    "QCDht200": "QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht300": "QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht500": "QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht700": "QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht1000": "QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht1500": "QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "QCDht2000": "QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",

    "Ts": "ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8_hadd.root",
    "Tbt": "ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_hadd.root",
    "Tt": "ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_hadd.root",
    "TbtW": "ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_hadd.root",
    "TtW": "ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_hadd.root",

    "WJetsMG200": "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG400": "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG600": "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG800": "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG1200": "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",
    "WJetsMG2500": "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root",

    "WW": "WW_TuneCP5_PSweights_13TeV-pythia8_hadd.root",
    "WZ": "WZ_TuneCP5_PSweights_13TeV-pythia8_hadd.root",
    "ZZ": "ZZ_TuneCP5_13TeV-pythia8_hadd.root"
  }
}

for jj in [ "TT1b", "TT2b", "TTbb", "TTcc", "TTjj" ]:
  for shift in [ "", "UEdn", "UEup", "HDAMPdn", "HDAMPup" ]:
    if shift == "":
      # 2017 nominal ttbar samples
      all_samples[ "2017" ][ "TTJets2L2nu{}{}".format( shift, jj ) ] = "TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2017" ][ "TTJetsHad{}{}".format( shift, jj ) ] = "TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2017" ][ "TTJetsSemiLepNjet9bin{}{}".format( shift, jj ) ] = "TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2017" ][ "TTJetsSemiLepNjet9{}{}".format( shift, jj ) ] = "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_{}_hadd.root".format( jj.lower() )
      # 2018 nominal ttbar samples
      all_samples[ "2018" ][ "TTJets2L2nu{}{}".format( shift, jj ) ] = "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2018" ][ "TTJetsHad{}{}".format( shift, jj ) ] = "TTToHadronic_TuneCP5_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2018" ][ "TTJetsSemiLepNjet9bin{}{}".format( shift, jj ) ] = "TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8_{}_hadd.root".format( jj.lower() )
      all_samples[ "2018" ][ "TTJetsSemiLepNjet9{}{}".format( shift, jj ) ] = "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT500Njet9_{}_hadd.root".format( jj.lower() )
      if jj == "TTjj":
        for n in [ "1", "2", "3", "4", "5" ]:
          all_samples[ "2017" ][ "TTJetsSemiLepNjet0{}{}{}".format( shift, jj, n ) ] = "TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_{}_{}_hadd.root".format( jj, n )
        for n in [ "1", "2" ]:
          all_samples[ "2018" ][ "TTJetsSemiLepNjet0{}{}{}".format( shift, jj, n ) ] = "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_HT0Njet0_{}_{}_hadd.root".format( jj, n )
    elif "UE" in shift:
      all_samples[ "2017" ][ "TTJets2L2nu{}{}".format( shift, jj ) ] = "TTTo2L2Nu_TuneCP5{}_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )
      all_samples[ "2017" ][ "TTJetsHad{}{}".format( shift, jj ) ] =  "TTToHadronic_TuneCP5{}_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )
      all_samples[ "2017" ][ "TTJetsSemiLep{}{}".format( shift, jj ) ] = "TTToSemiLeptonic_TuneCP5{}_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )
    elif "HDAMP" in shift:
      all_samples[ "2017" ][ "TTJets2L2nu{}{}".format( shift, jj ) ] = "TTTo2L2Nu_{}_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )
      all_samples[ "2017" ][ "TTJetsHad{}{}".format( shift, jj ) ] = "TTToHadronic_{}_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )
      all_samples[ "2017" ][ "TTJetsSemiLep{}{}".format( shift, jj ) ] = "TTToSemiLeptonic_{}_TuneCP5_PSweights_13TeV-powheg-pythia8_{}_hadd.root".format( shift_keys[ shift ], jj.lower() )

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

# weight event count

weightStr = "triggerXSF * pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc * " + \
            "(MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) ) * xsecEff * tthfWeight * njetsWeight * btagCSVWeight * btagCSVRenormWeight"

# general cut, add selection based cuts in training scripts
cuts = {
  "ELECTRONPT": 20,
  "MUONPT": 20,
  "HT": 500,
  "MET": 60,
  "MT": 60,
  "MINDR": 0.4,
}

base_cut =  "( isTraining == 1 || isTraining == 2 ) && ( DataPastTriggerX == 1 ) && ( MCPastTriggerX == 1 )"
base_cut += " && ( ( leptonPt_MultiLepCalc > {} && isElectron == 1 ) || ( leptonPt_MultiLepCalc > {} && isMuon == 1 ) )".format( cuts[ "ELECTRONPT" ], cuts[ "MUONPT" ] )
base_cut += " && AK4HT > {} && corr_met_MultiLepCalc > {} && MT_lepMet > {} && minDR_lepJet > {}".format( cuts[ "HT" ], cuts[ "MET" ], cuts[ "MT" ], cuts[ "MINDR" ] )


#!/usr/bin/env python

#input variables
varList = {}

# edit me 
bruxUserName = "dli50"
lpcUserName = "dsunyou"
eosUserName = "dali"

step2Sample2017    = "FWLJMET102X_1lep2017_Oct2019_4t_08122020_step2"                    # current 2017 sample
step2Sample2018    = "FWLJMET102X_1lep2018_Oct2019_4t_08122020_step2"                    # current 2018 sample
inputDirBRUX2017   = "/mnt/hadoop/store/group/bruxljm/" + step2Sample2017 + "/nominal/"  # Brown Linux path
inputDirBRUX2018   = "/mnt/hadoop/store/group/bruxljm/" + step2Sample2018 + "/nominal/"  
inputDirLPC2017    = "~/nobackup/" + step2Sample2017 + "/"                               # LHC Physics Center path
inputDirEOS2017    = step2Sample2017		                                                  # EOS storage path
inputDirLPC2018    = "~/nobackup/" + step2Sample2018 + "/"                               
inputDirEOS2018    = step2Sample2018		                                                  
inputDirCondor2017 = "root://cmseos.fnal.gov///store/user/" + lpcUserName + "/" + step2Sample2017 + "/" # Condor remote node path to EOS
inputDirCondor2018 = "root://cmseos.fnal.gov///store/user/" + lpcUserName + "/" + step2Sample2018 + "/"

# full signal sample
sig2017 = [
  "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"                         
]

sig2018 = [
  "TTTT_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root" 
]

# signal sample partitioned into three equal parts
# to be used in variable importance
sig2017_0 = [
  sample.split("hadd")[0] + "split0.root" for sample in sig2017
]
# to be used in hyper parameter optimization
sig2017_1 = [
  sample.split("hadd")[0] + "split1.root" for sample in sig2017
]
# to be used in full training
sig2017_2 = [
  sample.split("hadd")[0] + "split2.root" for sample in sig2017
]

sig2018_0 = [
  sample.split("hadd")[0] + "split0.root" for sample in sig2018
]
# to be used in hyper parameter optimization
sig2018_1 = [
  sample.split("hadd")[0] + "split1.root" for sample in sig2018
]
# to be used in full training
sig2018_2 = [
  sample.split("hadd")[0] + "split2.root" for sample in sig2018
]

# bkg samples for training
bkg2017 = [
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
]

bkg2018 = [
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

bkg2017_0 = [
  sample.split("hadd")[0] + "split0.root" for sample in bkg2017
]
bkg2017_1 = [
  sample.split("hadd")[0] + "split1.root" for sample in bkg2017
]
bkg2017_2 = [
  sample.split("hadd")[0] + "split2.root" for sample in bkg2017
]

bkg2018_0 = [
  sample.split("hadd")[0] + "split0.root" for sample in bkg2018
]
bkg2018_1 = [
  sample.split("hadd")[0] + "split1.root" for sample in bkg2018
]
bkg2018_2 = [
  sample.split("hadd")[0] + "split2.root" for sample in bkg2018
]

# all samples for step3
all2017 = {
  "TTTT": ("TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"),
  
  "TTHH": ("TTHH_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTTJ": ("TTTJ_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTTW": ("TTTW_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTWH": ("TTWH_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTWl": ("TTWJetsToLNu_TuneCP5_PSweights_13TeV-amcatnloFXFX-madspin-pythia8_hadd.root"),
  "TTWW": ("TTWW_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTWZ": ("TTWZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTZH": ("TTZH_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTZZ": ("TTZZ_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "TTZlM10": ("TTZToLLNuNu_M-10_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"),
  "TTZlM1to10": ("TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8_hadd.root"),
  "TTHnoB": ("ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root"),
  "TTHB": ("ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_hadd.root"),
  
  "DataE": ("SingleElectron_hadd.root"),
  "DataM": ("SingleMuon_hadd.root"),
  "DataJ": ("JetHT_hadd.root"),
  
  "DYMG200": ("DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "DYMG400": ("DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "DYGM600": ("DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "DYGM800": ("DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "DYMG1200": ("DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "DYMG2500": ("DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  
  "QCDht200": ("QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht300": ("QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht500": ("QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht700": ("QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht1000": ("QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht1500": ("QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  "QCDht2000": ("QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8_hadd.root"),
  
  "Tbs": ("ST_s-channel_antitop_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root"),
  "Ts": ("ST_s-channel_top_leptonDecays_13TeV-PSweights_powheg-pythia_hadd.root"),
  "Tbt": ("ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"),
  "Tt": ("ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"),
  "TbtW": ("ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"),
  "TtW": ("ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_hadd.root"),
  
  "TTJets2L2nuTT1b": ("TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJets2L2nuTT2b": ("TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJets2L2nuTTbb": ("TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJets2L2nuTTcc": ("TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJets2L2nuTTjj": ("TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  
  "TTJets2L2nuUEdnTT1b": ("TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJets2L2nuUEdnTT2b": ("TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJets2L2nuUEdnTTbb": ("TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJets2L2nuUEdnTTcc": ("TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJets2L2nuUEdnTTjj": ("TTTo2L2Nu_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJets2L2nuUEupTT1b": ("TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJets2L2nuUEupTT2b": ("TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJets2L2nuUEupTTbb": ("TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJets2L2nuUEupTTcc": ("TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJets2L2nuUEupTTjj": ("TTTo2L2Nu_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJets2L2nuHDAMPdnTT1b": ("TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJets2L2nuHDAMPonTT2b": ("TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJets2L2nuHDAMPonTTbb": ("TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJets2L2nuHDAMPonTTcc": ("TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJets2L2nuHDAMPonTTjj": ("TTTo2L2Nu_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJets2L2nuHDAMPupTT1b": ("TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJets2L2nuHDAMPupTT2b": ("TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJets2L2nuHDAMPupTTbb": ("TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJets2L2nuHDAMPupTTcc": ("TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJets2L2nuHDAMPupTTjj": ("TTTo2L2Nu_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  
  "TTJetsHadTT1b": ("TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsHadTT2b": ("TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsHadTTbb": ("TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsHadTTcc": ("TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsHadTTjj": ("TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsSemiLepNjet9binTT1b": ("TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsSemiLepNjet9binTT2b": ("TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsSemiLepNjet9binTTbb": ("TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsSemiLepNjet9binTTcc": ("TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsSemiLepNjet9binTTjj": ("TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsSemiLepNjet0TT1b": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt1b_hadd.root"),
  "TTJetsSemiLepNjet0TT2b": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_tt2b_hadd.root"),
  "TTJetsSemiLepNjet0TTbb": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root"),
  "TTJetsSemiLepNjet0TTcc": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root"),
  "TTJetsSemiLepNjet0TTjj1": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root"),
  "TTJetsSemiLepNjet0TTjj2": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root"),
  "TTJetsSemiLepNjet0TTjj3": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_hadd.root"),
  "TTJetsSemiLepNjet0TTjj4": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_hadd.root"),
  "TTJetsSemiLepNjet0TTjj5": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_hadd.root"),
  "TTJetsSemiLepNjet9TT1b": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt1b_hadd.root"),
  "TTJetsSemiLepNjet9TT2b": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_tt2b_hadd.root"),
  "TTJetsSemiLepNjet9TTbb": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttbb_hadd.root"),
  "TTJetsSemiLepNjet9TTcc": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttcc_hadd.root"),
  "TTJetsSemiLepNjet9TTjj": ("TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT500Njet9_ttjj_hadd.root"),
  
  "TTJetsHadUEdnTT1b": ("TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsHadUEdnTT2b": ("TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsHadUEdnTTbb": ("TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsHadUEdnTTcc": ("TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsHadUEdnTTjj": ("TTToHadronic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsHadUEupTT1b": ("TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsHadUEupTT2b": ("TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsHadUEupTTbb": ("TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsHadUEupTTcc": ("TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsHadUEupTTjj": ("TTToHadronic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsHadHDAMPdnTT1b": ("TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsHadHDAMPdnTT2b": ("TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsHadHDAMPdnTTbb": ("TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsHadHDAMPdnTTcc": ("TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsHadHDAMPdnTTjj": ("TTToHadronic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsHadHDAMPupTT1b": ("TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsHadHDAMPupTT2b": ("TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsHadHDAMPupTTbb": ("TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsHadHDAMPupTTcc": ("TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsHadHDAMPupTTjj": ("TTToHadronic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  
  "TTJetsSemiLepUEdnTT1b": ("TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsSemiLepUEdnTT2b": ("TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsSemiLepUEdnTTbb": ("TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsSemiLepUEdnTTcc": ("TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsSemiLepUEdnTTjj": ("TTToSemiLeptonic_TuneCP5down_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsSemiLepUEupTT1b": ("TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsSemiLepUEupTT2b": ("TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsSemiLepUEupTTbb": ("TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsSemiLepUEupTTcc": ("TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsSemiLepUEupTTjj": ("TTToSemiLeptonic_TuneCP5up_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsSemiLepHDAMPdnTT1b": ("TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsSemiLepHDAMPdnTT2b": ("TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsSemiLepHDAMPdnTTbb": ("TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsSemiLepHDAMPdnTTcc": ("TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsSemiLepHDAMPdnTTjj": ("TTToSemiLeptonic_hdampDOWN_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  "TTJetsSemiLepHDAMPupTT1b": ("TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt1b_hadd.root"),
  "TTJetsSemiLepHDAMPupTT2b": ("TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_tt2b_hadd.root"),
  "TTJetsSemiLepHDAMPupTTbb": ("TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root"),
  "TTJetsSemiLepHDAMPupTTcc": ("TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root"),
  "TTJetsSemiLepHDAMPupTTjj": ("TTToSemiLeptonic_hdampUP_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root"),
  
  "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root"),
  "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root"),
  "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root"),
  "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_1_hadd.root"),
  "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_2_hadd.root"),
  "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_3_hadd.root"),
  "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_4_hadd.root"),
  "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8_hadd.root"),
  
  "WW": ("WW_TuneCP5_13TeV-pythia8_hadd.root"),
  "WZ": ("WZ_TuneCP5_13TeV-pythia8_hadd.root"),
  "ZZ": ("ZZ_TuneCP5_13TeV-pythia8_hadd.root")
}

#[<variable in trees>, <variable name for axes and titles>, <unit>]

varList['DNN'] = [
  ('AK4HTpMETpLepPt','S_{T}','GeV',0,4000,101),
  ('minMleppBjet','min[M(l,b)]','GeV',0,1000,101),
  ('mass_minBBdr','M(b,b) with min[#DeltaR(b,b)]','GeV',0,1400,51),
  ('deltaR_lepBJet_maxpt','#DeltaR(l,b)] with max[p_{T}(l,b)]','',0,6.0,51),
  ('lepDR_minBBdr','#DeltaR(l,bb) with min[#DeltaR(b,b)]','',-1,10,51),
  ('centrality','Centrality','',0,1.0,51),
  ('deltaEta_maxBB','max[#Delta#eta(b,b)]','',-6,11,51),
  ('aveCSVpt','p_{T} weighted CSVv2','',-0.3,1.1,101),
  ('aveBBdr','ave[#DeltaR(b,b)]','',0,6.0,51),
  ('FW_momentum_0','0^{th} FW moment','GeV',0,1,51),
  ('FW_momentum_1','1^{st} FW moment','GeV',0,1,51),
  ('FW_momentum_2','2^{nd} FW moment','GeV',0,1,51),
  ('FW_momentum_3','3^{rd} FW moment','GeV',0,1,51),
  ('FW_momentum_4','4^{th} FW moment','GeV',0,1,51),
  ('FW_momentum_5','5^{th} FW moment','GeV',0,1,51),
  ('FW_momentum_6','6^{th} FW moment','GeV',0,1,51),
  ('mass_maxJJJpt','M(jjj) with max[p_{T}(jjj)]','GeV',0,3000,101),
  ('BJetLeadPt','p_{T}(b_{1})','GeV',0,2000,101),
  ('deltaR_minBB','min[#DeltaR(b,b)]','',0,6.0,51),
  ('minDR_lepBJet','min[#DeltaR(l,b)]','',0,6.0,51),
  ('MT_lepMet','M_{T}(lep,E_{T}^{miss})','GeV',0,250,51),
  ('AK4HT','H_{T}','GeV',0,4000,101),
  ('hemiout','Hemiout','GeV',0,3000,101),
  ('theJetLeadPt','p_{T}(j_{1})','GeV',0,1500,101),
  ('corr_met_MultiLepCalc','E_{T}^{miss}','GeV',0,1500,51),
  ('leptonPt_MultiLepCalc','p_{T}(lep)','GeV',0,600,121),
  ('mass_lepJets0','M(l,j_{1})','GeV',0,2200,101), 
  ('mass_lepJets1','M(l,j_{2})','GeV',0,3000,101),
  ('mass_lepJets2','M(l,j_{3})','GeV',0,3000,101),
  ('MT2bb','MT2bb','GeV',0,400,51),
  ('mass_lepBJet0','M(l,b_{1})','GeV',0,1800,101),
  ('mass_lepBJet_mindr','M(l,b) with min[#DeltaR(l,b)]','GeV',0,800,51),
  ('secondJetPt','p_{T}(j_{2})','GeV',0,2500,101),
  ('fifthJetPt','p_{T}(j_{5})','GeV',0,400,101),
  ('sixthJetPt','p_{T}(j_{6})','GeV',0,400,51),
  ('PtFifthJet','5^{th} jet p_{T}','GeV',-1,2000,101),
  ('mass_minLLdr','M(j,j) with min[#DeltaR(j,j)], j #neq b','GeV',0,600,51),
  ('mass_maxBBmass','max[M(b,b)]','GeV',0,2000,101),
  ('deltaR_lepJetInMinMljet','#DeltaR(l,j) with min M(l, j)','',0,4.5,101),
  ('deltaPhi_lepJetInMinMljet','#DeltaPhi(l,j) with min M(l, j)','',-4,4,51),
  ('deltaR_lepbJetInMinMlb','#DeltaR(l,b) with min M(l, b)','',0,6.0,51),
  ('deltaPhi_lepbJetInMinMlb','#DeltaPhi(l,b) with min M(l, b)','',-11,5,101),
  ('M_allJet_W','M(allJets, leptoninc W)','GeV',0,10000,201),
  ('HT_bjets','HT(bjets)','GeV',0,1800,101),
  ('ratio_HTdHT4leadjets','HT/HT(4 leading jets)','',0,2.6,51),
  ('csvJet3','DeepCSV(3rdPtJet)','',-2.2,1.2,101),
  ('csvJet4','DeepCSV(4thPtJet)','',-2.2,1.2,101),
  ('firstcsvb_bb','DeepCSV(1stDeepCSVJet)','',-2,1.5,51),
  ('secondcsvb_bb','DeepCSV(2ndDeepCSVJet)','',-2,1.5,51),
  ('thirdcsvb_bb','DeepCSV(3rdDeepCSVJet)','',-2,1.5,51),
  ('fourthcsvb_bb','DeepCSV(4thDeepCSVJet)','',-2,1.5,51),
  ('NJets_JetSubCalc','AK4 jet multiplicity','',0,15,16),
  ('HT_2m','HTwoTwoPtBjets','GeV',-20,5000,201),
  ('Sphericity','Sphericity','Sphericity',0,1.0,51),
  ('Aplanarity','Aplanarity','Aplanarity',0,0.5,51),
  ('minDR_lepJet','min[#DeltaR(l,j)]','',0,4,51),
  ('BDTtrijet1','trijet1 discriminator','',-1,1,101),
  ('BDTtrijet2','trijet2 discriminator','',-1,1,101),
  ('BDTtrijet3','trijet3 discriminator','',-1,1,101),
  ('BDTtrijet4','trijet4 discriminator','',-1,1,51),
  ('NresolvedTops1pFake','resolvedTop multiplicity','',0,5,6),
  ('NJetsTtagged','top multiplicity','',0,4,5),
  ('NJetsWtagged','W multiplicity','',0,5,6),
  ('NJetsCSVwithSF_MultiLepCalc','bjet multiplicity','',0,10,11),
  ('HOTGoodTrijet1_mass','','GeV',0,300,51),               # Trijet variables
  ('HOTGoodTrijet1_dijetmass','','GeV',0,250,51),
  ('HOTGoodTrijet1_pTratio','','',0,1,51),
  ('HOTGoodTrijet1_dRtridijet','','',0,4,51),
  ('HOTGoodTrijet1_csvJetnotdijet','','',-2.2,1.2,101),
  ('HOTGoodTrijet1_dRtrijetJetnotdijet','','',0,4,51),
  ('HOTGoodTrijet2_mass','','GeV',0,300,51),
  ('HOTGoodTrijet2_dijetmass','','GeV',0,250,51),
  ('HOTGoodTrijet2_pTratio','','',0,1,51),
  ('HOTGoodTrijet2_dRtridijet','','',0,4,51),
  ('HOTGoodTrijet2_csvJetnotdijet','','',-2.2,1.2,101),
  ('HOTGoodTrijet2_dRtrijetJetnotdijet','','',0,4,51)
]

weightStr = "triggerXSF * pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc * " + \
            "(MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) ) * xsecEff * tthfWeight * njetsWeight"

# general cut, add selection based cuts in training scripts
cutStr =  "( ( leptonPt_MultiLepCalc > 50 && isElectron == 1 ) || " + \
          "( leptonPt_MultiLepCalc > 50 && isMuon == 1 ) ) && " + \
          "( corr_met_MultiLepCalc > 60 ) && " + \
          "( MT_lepMet > 60 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[0] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[1] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[2] > 0 ) && " + \
          "( minDR_lepJet > 0.4 ) && " + \
          "( AK4HT > 510 ) && " + \
          "( DataPastTriggerX == 1 ) && ( MCPastTriggerX == 1 ) && " + \
          "( NJetsCSVwithSF_MultiLepCalc >= 2 ) &&" + \
          "( NJets_JetSubCalc >= 6 )"                                     

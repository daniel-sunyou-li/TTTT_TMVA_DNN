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

# full background samples
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

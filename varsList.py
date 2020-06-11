#!/usr/bin/env python

#input variables
varList = {}

# edit me 
bruxUserName = "afurman2"
lpcUserName = "afurman"
eosUserName = "afurman"

step2Sample2017   = "FWLJMET102X_1lep2017_Oct2019_4t_05072020_step2"                    # current 2017 sample
step2Sample2018   = "FWLJMET102X_1lep2018_Oct2019_4t_05072020_step2"                    # current 2018 sample
inputDirBRUX2017  = "/mnt/hadoop/store/group/bruxljm/" + step2Sample2017 + "/nominal/"  # Brown Linux path
inputDirBRUX2018  = "/mnt/hadoop/store/group/bruxljm/" + step2Sample2018 + "/nominal/"  
inputDirLPC2017   = "~/nobackup/" + step2Sample2017 + "/"                               # LHC Physics Center path
inputDirEOS2017   = step2Sample2017		                                                  # EOS storage path
inputDirLPC2018   = "~/nobackup/" + step2Sample2018 + "/"                               
inputDirEOS2018   = step2Sample2018		                                                  
inputDirCondor    = "./"                                                                # Condor remote node path 

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
  sample.split("hadd")[0] + "split0.root" for sample in bkg2017
]
bkg12018_1 = [
  sample.split("hadd")[0] + "split1.root" for sample in bkg2017
]
bkg2018_2 = [
  sample.split("hadd")[0] + "split2.root" for sample in bkg2017
]

#[<variable in trees>, <variable name for axes and titles>, <unit>]

varList['DNN'] = [
  ['AK4HTpMETpLepPt','S_{T}','GeV'],
  ['minMleppBjet','min[M(l,b)]','GeV'],
  ['mass_minBBdr','M(b,b) with min[#DeltaR(b,b)]','GeV'],
  ['deltaR_lepBJet_maxpt','#DeltaR(l,b)] with max[p_{T}(l,b)]',''],
  ['lepDR_minBBdr','#DeltaR(l,bb) with min[#DeltaR(b,b)]',''],
  ['centrality','Centrality',''],
  ['deltaEta_maxBB','max[#Delta#eta(b,b)]',''],
  ['aveCSVpt','p_{T} weighted CSVv2',''],
  ['aveBBdr','ave[#DeltaR(b,b)]',''],
  ['FW_momentum_0','0^{th} FW moment','GeV'],
  ['FW_momentum_1','1^{st} FW moment','GeV'],
  ['FW_momentum_2','2^{nd} FW moment','GeV'],
  ['FW_momentum_3','3^{rd} FW moment','GeV'],
  ['FW_momentum_4','4^{th} FW moment','GeV'],
  ['FW_momentum_5','5^{th} FW moment','GeV'],
  ['FW_momentum_6','6^{th} FW moment','GeV'],
  ['mass_maxJJJpt','M(jjj) with max[p_{T}(jjj)]','GeV'],
  ['BJetLeadPt','p_{T}(b_{1})','GeV'],
  ['deltaR_minBB','min[#DeltaR(b,b)]',''],
  ['minDR_lepBJet','min[#DeltaR(l,b)]',''],
  ['MT_lepMet','M_{T}(lep,E_{T}^{miss})','GeV'],
  ['AK4HT','H_{T}','GeV'],
  ['hemiout','Hemiout','GeV'],
  ['theJetLeadPt','p_{T}(j_{1})','GeV'],
  ['corr_met_MultiLepCalc','E_{T}^{miss}','GeV'],
  ['leptonPt_MultiLepCalc','p_{T}(lep)','GeV'],
  ['mass_lepJets0','M(l,j_{1})','GeV'], 
  ['mass_lepJets1','M(l,j_{2})','GeV'],
  ['mass_lepJets2','M(l,j_{3})','GeV'],
  ['MT2bb','MT2bb','GeV'],
  ['mass_lepBJet0','M(l,b_{1})','GeV'],
  ['mass_lepBJet_mindr','M(l,b) with min[#DeltaR(l,b)]','GeV'],
  ['secondJetPt','p_{T}(j_{2})','GeV'],
  ['fifthJetPt','p_{T}(j_{5})','GeV'],
  ['sixthJetPt','p_{T}(j_{6})','GeV'],
  ['PtFifthJet','5^{th} jet p_{T}','GeV'],
  ['mass_minLLdr','M(j,j) with min[#DeltaR(j,j)], j #neq b','GeV'],
  ['mass_maxBBmass','max[M(b,b)]','GeV'],
  ['deltaR_lepJetInMinMljet','#DeltaR(l,j) with min M(l, j)',''],
  ['deltaPhi_lepJetInMinMljet','#DeltaPhi(l,j) with min M(l, j)',''],
  ['deltaR_lepbJetInMinMlb','#DeltaR(l,b) with min M(l, b)',''],
  ['deltaPhi_lepbJetInMinMlb','#DeltaPhi(l,b) with min M(l, b)',''],
  ['M_allJet_W','M(allJets, leptoninc W)','GeV'],
  ['HT_bjets','HT(bjets)','GeV'],
  ['ratio_HTdHT4leadjets','HT/HT(4 leading jets)',''],
  ['csvJet3','DeepCSV(3rdPtJet)',''],
  ['csvJet4','DeepCSV(4thPtJet)',''],
  ['firstcsvb_bb','DeepCSV(1stDeepCSVJet)',''],
  ['secondcsvb_bb','DeepCSV(2ndDeepCSVJet)',''],
  ['thirdcsvb_bb','DeepCSV(3rdDeepCSVJet)',''],
  ['fourthcsvb_bb','DeepCSV(4thDeepCSVJet)',''],
  ['NJets_JetSubCalc','AK4 jet multiplicity',''],
  ['HT_2m','HTwoTwoPtBjets','GeV'],
  ['Sphericity','Sphericity','Sphericity'],
  ['Aplanarity','Aplanarity','Aplanarity'],
  ['minDR_lepBJet','min[#DeltaR(l,j)]',''],
  ['BDTtrijet1','trijet1 discriminator',''],
  ['BDTtrijet2','trijet2 discriminator',''],
  ['BDTtrijet3','trijet3 discriminator',''],
  ['BDTtrijet4','trijet4 discriminator',''],
  ['NresolvedTops1pFake','resolvedTop multiplicity',''],
  ['NJetsTtagged','top multiplicity',''],
  ['NJetsWtagged','W multiplicity',''],
  ['NJetsCSVwithSF_MultiLepCalc','bjet multiplicity',''],
  ['HOTGoodTrijet1_mass','','GeV'],               # Trijet variables
  ['HOTGoodTrijet1_dijetmass','','GeV'],
  ['HOTGoodTrijet1_pTratio','',''],
  ['HOTGoodTrijet1_dRtridijet','',''],
  ['HOTGoodTrijet1_csvJetnotdijet','',''],
  ['HOTGoodTrijet1_dRtrijetJetnotdijet','',''],
  ['HOTGoodTrijet2_mass','','GeV'],
  ['HOTGoodTrijet2_dijetmass','','GeV'],
  ['HOTGoodTrijet2_pTratio','',''],
  ['HOTGoodTrijet2_dRtridijet','',''],
  ['HOTGoodTrijet2_csvJetnotdijet','',''],
  ['HOTGoodTrijet2_dRtrijetJetnotdijet','','']
]

weightStr = "triggerXSF * pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc * " + \
            "(MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) ) * xsecEff"

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

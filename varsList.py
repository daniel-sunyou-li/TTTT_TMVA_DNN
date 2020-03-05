#!/usr/bin/env python

#input variables
varList = {}

#inputDirBRUX =  "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_12122019_step2/nominal/"   # BRUX 2017 step 2 path
inputDirBRUX =  "/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_02052020_step2/nominal/"   # BRUX 2017 step 2 path
inputDirLPC =   "~/nobackup/FWLJMET102X_1lep2017_Oct2019_4t_02052020_step2/"                                 # LPC 2017 step 2 path
inputDirEOS =   "./FWLJMET102X_1lep2017_Oct2019_4t_02052020_step2/"                                         # LPC Remote Node 2017 step 2 path
inputDirCondor = "./"

sig = [
  "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root"   # 2017 step 2
]

bkg = [
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
]

#[<variable in trees>, <variable name for axes and titles>, <unit>]

varList['BigComb'] = [
  ['AK4HTpMETpLepPt','S_{T}','GeV'],
  ['minMleppBjet','min[M(l,b)]','GeV'],
  #['mass_minBBdr','M(b,b) with min[#DeltaR(b,b)]','GeV'],
  ['deltaR_lepBJet_maxpt','#DeltaR(l,b)] with max[p_{T}(l,b)]',''],
  #['lepDR_minBBdr','#DeltaR(l,bb) with min[#DeltaR(b,b)]',''],
  ['centrality','Centrality',''],
  ['deltaEta_maxBB','max[#Delta#eta(b,b)]',''],
  ['aveCSVpt','p_{T} weighted CSVv2',''],
  ['aveBBdr','ave[#DeltaR(b,b)]',''],
  ['FW_momentum_0','0^{th} FW moment','GeV'],
  ['FW_momentum_1','1^{st} FW moment','GeV'],
  #['FW_momentum_2','2^{nd} FW moment','GeV'],
  ['FW_momentum_3','3^{rd} FW moment','GeV'],
  #['FW_momentum_4','4^{th} FW moment','GeV'],
  #['FW_momentum_5','5^{th} FW moment','GeV'],
  ['FW_momentum_6','6^{th} FW moment','GeV'],
  ['mass_maxJJJpt','M(jjj) with max[p_{T}(jjj)]','GeV'],
  ['BJetLeadPt','p_{T}(b_{1})','GeV'],
  ['deltaR_minBB','min[#DeltaR(b,b)]',''],
  ['minDR_lepBJet','min[#DeltaR(l,b)]',''],
  ['MT_lepMet','M_{T}(lep,E_{T}^{miss})','GeV'],
  ['AK4HT','H_{T}','GeV'],
  ['hemiout','Hemiout','GeV'],
  #['theJetLeadPt','p_{T}(j_{1})','GeV'],
  ['corr_met_MultiLepCalc','E_{T}^{miss}','GeV'],
  ['leptonPt_MultiLepCalc','p_{T}(lep)','GeV'],
  ['mass_lepJets0','M(l,j_{1})','GeV'], 
  ['mass_lepJets1','M(l,j_{2})','GeV'],
  ['mass_lepJets2','M(l,j_{3})','GeV'],
  ['MT2bb','MT2bb','GeV'],
  ['mass_lepBJet0','M(l,b_{1})','GeV'],
  ['mass_lepBJet_mindr','M(l,b) with min[#DeltaR(l,b)]','GeV'],
  #['secondJetPt','p_{T}(j_{2})','GeV'],
  ['fifthJetPt','p_{T}(j_{5})','GeV'],
  ['sixthJetPt','p_{T}(j_{6})','GeV'],
  ['PtFifthJet','5^{th} jet p_{T}','GeV'],
  ['mass_minLLdr','M(j,j) with min[#DeltaR(j,j)], j #neq b','GeV'],
  ['mass_maxBBmass','max[M(b,b)]','GeV'],
  ['deltaR_lepMinMlj','#DeltaR(l,j) with min M(l, j)',''],
  #['deltaPhi_lepJetInMinMljet','#DeltaPhi(l,j) with min M(l, j)',''],
  ['deltaR_lepMinMlb','#DeltaR(l,b) with min M(l, b)',''],
  #['deltaPhi_lepbJetInMinMlb','#DeltaPhi(l,b) with min M(l, b)',''],
  ['M_allJet_W','M(allJets, leptoninc W)','GeV'],
  ['HT_bjets','HT(bjets)','GeV'],
  ['ratio_HTdHT4leadjets','HT/HT(4 leading jets)',''],
  ['csvJet3','DeepCSV(3rdPtJet)',''],
  ['csvJet4','DeepCSV(4thPtJet)',''],
  ['thirdcsvb_bb','DeepCSV(3rdDeepCSVJet)',''],
  ['fourthcsvb_bb','DeepCSV(4thDeepCSVJet)',''],
  ['NJets_JetSubCalc','AK4 jet multiplicity',''],
  ['HT_2m','HTwoTwoPtBjets','GeV'],
  #['Sphericity','Sphericity','Sphericity'],
  #['Aplanarity','Aplanarity','Aplanarity'],
  #['mass_lepJJ_minJJdr','M(l,jj) with min[#DeltaR(j,j)], j #neq b','GeV'],
  ['deltaR_lepBJets0','#DeltaR(l,b_{1})',''],
  ['minDR_lepJet','min[#DeltaR(l,j)]',''],
  #['mass_maxBBpt','M(b,b) with max[p_{T}(b,b)]','GeV'],
  #['deltaR_lepJets','#DeltaR(l,j)',''],
  #['mass_lepBB_minBBdr','M(l,bb) with min[#DeltaR(b,b)]','GeV'],
  ['corr_met','E_{T}^{miss}','GeV'],
  ['BDTtrijet1','trijet1 discriminator',''],
  ['BDTtrijet2','trijet2 discriminator',''],
  ['BDTtrijet3','trijet3 discriminator',''],
  #['BDTtrijet4','trijet4 discriminator',''],
  ['NresolvedTops1pFake','resolvedTop multiplicity',''],
  ['NJetsTtagged','top multiplicity',''],
  ['NJetsWtagged','W multiplicity',''],
  ['NJetsCSVwithSF_JetSubCalc','bjet multiplicity',''],
  #['topJet1Index_HOTTaggerCalc','',''],           # added HOT Tagger variables
  ['topJet2Index_HOTTaggerCalc','',''],
  ['topJet3Index_HOTTaggerCalc','',''],
  ['topNAK4_HOTTaggerCalc','',''],
  ['topNtops_HOTTaggerCalc','',''],
  #['topDRmax_HOTTaggerCalc','max[#DeltaR(t,t)]',''],
  #['topDThetaMax_HOTTaggerCalc','max[#DeltaTheta(t,t)]',''],
  ['topDiscriminator_HOTTaggerCalc','',''],
  #['topEta_HOTTaggerCalc','',''],
  ['topMass_HOTTaggerCalc','','GeV'],
  #['topPhi_HOTTaggerCalc','',''],
  #['topPt_HOTTaggerCalc','','GeV'],
  ['HOTGoodTrijet1_mass','','GeV'],               # added more Trijet variables
  ['HOTGoodTrijet1_dijetmass','','GeV'],
  ['HOTGoodTrijet1_pTratio','',''],
  ['HOTGoodTrijet1_dRtridijet','',''],
  ['HOTGoodTrijet1_csvJetnotdijet','',''],
  ['HOTGoodTrijet2_mass','','GeV'],
  ['HOTGoodTrijet2_dijetmass','','GeV'],
  ['HOTGoodTrijet2_pTratio','',''],
  ['HOTGoodTrijet2_dRtridijet','',''],
  ['HOTGoodTrijet2_csvJetnotdijet','',''],
  ['HOTGoodTrijet3_mass','','GeV'],
  ['HOTGoodTrijet3_dijetmass','','GeV'],
  ['HOTGoodTrijet3_pTratio','',''],
  ['HOTGoodTrijet3_dRtridijet','',''],
  ['HOTGoodTrijet3_csvJetnotdijet','',''],
  ['HOTGoodTrijet4_mass','','GeV'],
  ['HOTGoodTrijet4_dijetmass','','GeV'],
  ['HOTGoodTrijet4_pTratio','',''],
  ['HOTGoodTrijet4_dRtridijet','',''],
  ['HOTGoodTrijet4_csvJetnotdijet','',''],
  ['HOTBadTrijet1_mass','','GeV'],
  ['HOTBadTrijet1_dijetmass','','GeV'],
  ['HOTBadTrijet1_pTratio','',''],
  ['HOTBadTrijet1_dRtridijet','',''],
  ['HOTBadTrijet1_csvJetnotdijet','',''],
  ['HOTBadTrijet2_mass','','GeV'],
  ['HOTBadTrijet2_dijetmass','','GeV'],
  ['HOTBadTrijet2_pTratio','',''],
  ['HOTBadTrijet2_dRtridijet','',''],
  ['HOTBadTrijet2_csvJetnotdijet','',''],
  ['HOTBadTrijet3_mass','','GeV'],
  ['HOTBadTrijet3_dijetmass','','GeV'],
  ['HOTBadTrijet3_pTratio','',''],
  ['HOTBadTrijet3_dRtridijet','',''],
  ['HOTBadTrijet3_csvJetnotdijet','',''],
  ['HOTBadTrijet4_mass','','GeV'],
  ['HOTBadTrijet4_dijetmass','','GeV'],
  ['HOTBadTrijet4_pTratio','',''],
  ['HOTBadTrijet4_dRtridijet','',''],
  ['HOTBadTrijet4_csvJetnotdijet','','']
]

weightStr = "pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc * " + \
            "(MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) )"

cutStr =  "( ( leptonPt_MultiLepCalc > 50 && isElectron == 1 ) || " + \
          "( leptonPt_MultiLepCalc > 50 && isMuon == 1 ) ) && " + \
          "( corr_met_MultiLepCalc > 60 ) && " + \
          "( MT_lepMet > 60 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[0] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[1] > 0 ) && " + \
          "( theJetPt_JetSubCalc_PtOrdered[2] > 0 ) && " + \
          "( minDR_lepJet > 0.4 ) && " + \
          "( AK4HT > 510 )"

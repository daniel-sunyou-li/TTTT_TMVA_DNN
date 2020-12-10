#!/usr/bin/python

from ROOT import TH1D, TH2D, TTree, TFile
from array import array
import varsList

def analyze( rootTree, process, flv, doAllSys, doPDF, iPlot, plotDetails, catStr, year, verbose ):
# 'rootTree' is a dict that contains ROOT rootTrees of all the processes
# 'process' is a string of the physics process
# 'flv' is a string for the final state flavor (i.e. _ttlf, _ttcc, _ttbb")
# 'doAllSys' is a boolean to include hists of the correction plots
# 'doPDF' is a boolean to compute the PDF for the process
# 'plotDetails' = [ tree name, number of bins, x axis label ] 
# 'catStr' is a string describing the control/signal region parameters
# 'iPlot' is the variable tag
  plotTreeName = plotDetails[0]
  xbins = array("d", plotDetails[1])
  xAxisLabel = plotDetails[2]

  lumiStr = str(varsList.targetLumi / 1000.).replace(".","p") + "fb" # 1/fb  
  weightStr = "1"
  cutStr = varsList.cutStr
	
  plot2D = False if len(plotDetails) < 4 else True
  if plot2D:
    ybins = array("d", plotDetails[3])
    yAxisLabel = plotDetails[4]

  systList = varsList.systList
		
  print("Processing: {} {}".format(process, flv))
	
  # define the categories
  isEM  = catStr.split("_")[0][2:]
  nhott = catStr.split("_")[1][4:]
  nttag = catStr.split("_")[2][2:]
  nWtag = catStr.split("_")[3][2:]
  nbtag = catStr.split("_")[4][2:]
  njets = catStr.split("_")[5][2:]
	
  if process.lower().startswith("ttjetssemilepnjet0"): cutStr += " && (isHTgt500Njetge9 == 0)"
  if process.lower().startswith("ttjetssemilepnjet9"): cutStr += " && (isHTgt500Njetge9 == 1)"
  if process.lower().startswith("ttjets"):
    cutStr += " && (isTraining == 3)"
    weightStr = "3 * " + weightStr
    topPt13TeVstr = "topPtWeight13TeV"
    if flv == "_ttlf": cutStr += " && genTtbarIdCategory_TTbarMassCalc[0]==0"
    elif flv == "_ttcc": cutStr += " && genTtbarIdCategory_TTbarMassCalc[0]==1"
    elif flv == "_ttbb": cutStr += " && (genTtbarIdCategory_TTbarMassCalc[0]==2 || genTtbarIdCategory_TTbarMassCalc[0]==3 || genTtbarIdCategory_TTbarMassCalc[0]==4)"
	
  weights = varsList.weight2017 if year == "2017" else varsList.weight2018
	
  if "Data" not in process:
    weightStr += "* {}".format(weights[process])
    weightStrNoNjet = weightStr
    weightTriggerUpStr = weightStr.replace("triggerXSF","(triggerXSF+triggerXSFUncert)")
    weightTriggerDnStr = weightStr.replace("triggerXSF","(triggerXSF-triggerXSFUncert)")
    weightPileupUpStr = weightStr.replace("pileupWeight","pileupWeightUp")
    weightPileupDnStr = weightStr.replace("pileupWeight","pileupWeightDown")
    weightPrefireUpStr = weightStr.replace("L1NonPrefiringProb_CommonCalc","L1NonPrefiringProbUp_CommonCalc")
    weightPrefireDnStr = weightStr.replace("L1NonPrefiringProb_CommonCalc","L1NonPrefiringProbDn_CommonCalc")
    weightmuRFcorrdUpStr = "renormWeights[5] * {}".format(weightStr)
    weightmuRFcorrdDnStr = "renormWeights[3] * {}".format(weightStr)
    weightmuRUpStr = "renormWeights[4] * {}".format(weightStr)
    weightmuRDnStr = "renormWeights[2] * {}".format(weightStr)
    weightmuFUpStr = "renormWeigths[1] * {}".format(weightStr)
    weightmuFDnStr = "renormWeights[0] * {}".format(weightStr)
    weightIsrUpStr = "renormPSWeights[0] * {}".format(weightStr)
    weightIsrDnStr = "renormPSWeights[2] * {}".format(weightStr)
    weightFsrUpStr = "renormPSWeights[1] * {}".format(weightStr)
    weightFsrDnStr = "renormPSWeights[3] * {}".format(weightStr)  
    weighttopptUpStr = "(topPtWeight13TeV) * {}".format(weightStr)
    weighttopptDnStr = "(1/topPtWeight13TeV) * {}".format(weightStr)
    weightNjetUpStr = weightStr
    weightNjetDnStr = weightStr
    weightNjetSFUpStr = weightStrNoNjet
    weightNjetSFDnStr = weightStrNoNjet
		
    # modify cuts
  if "softdropmassnm1w" in iPlot.lower(): cutStr += " && ( theJetAK8NjettinessTau2_JetSubCalc_PtOrdered/theJetAK8NjettinessTau1_JetSubCalc_PtOrdered < 0.45 )"
  if "softdropmassnm1t" in iPlot.lower(): cutStr += " && ( theJetAK8NjettinessTau3_JetSubCalc_PtOrdered/theJetAK8NjettinessTau2_JetSubCalc_PtOrdered < 0.80 )"
  if "tau21nm1" in iPlot.lower(): cutStr += " && ( theJetAK8SoftDropCorr_JetSubCalc_PtOrdered > 65 && theJetAK8SoftDropCorr_JetSubCalc_PtOrdered < 105 )"
  if "tau32nm1" in iPlot.lower(): cutStr += " && ( theJetAK8SoftDropCorr_JetSubCalc_PtOrdered > 105 && theJetAK8SoftDropCorr_JetSubCalc_PtOrdered < 220 )"
        
  isEMCut = ""
  if isEM == "E": isEMCut = " && isElectron==1"
  elif isEM == "M": isEMCut = " && isMuon==1"
	
  nhottCut = ""
  if "p" in nhott: nhottCut = " && NresolvedTops1pFake >= {}".format(nhott[:-1])
  else: nhottCut = " && NresolvedTops1pFake == {}".format(nhott)
    
  nttagCut = ""
  if "p" in nttag: nttagCut = " && NJetsTtagged >= {}".format(nttag[:-1])
  else: nttagCut = " && NJetsTtagged == {}".format(nttag)
	
  nWtagCut = ""
  if "p" in nWtag: nWtagCut = " && NJetsWtagged >= {}".format(nWtag[:-1])
  else: nWtagCut = " && NJetsWtagged == {}".format(nWtag)
	
  nbtagCut = ""
  if "p" in nbtag: nbtagCut = " && NJetsCSVwithSF_MultiLepCalc >= {}".format(nbtag[:-1])
  else: nbtagCut = " && NJetsCSVwithSF_MultiLepCalc == {}".format(nbtag)
	
  njetsCut = ""
  if "p" in njets: njetsCut = " && NJets_JetSubCalc >= {}".format(njets[:-1])
  else: njetsCut = " && NJets_JetSubCalc == {}".format(njets)
	
  if nbtag == "0" and "minmlb" in iPlot.lower():
    originalLJMETName = plotTreeName
    plotTreeName = "minMleppJet"
    
  fullCut = cutStr + isEMCut + nhottCut + nttagCut + nWtagCut + nbtagCut + njetsCut
    
  # modify the cuts for shifts
  cut_btagUp = fullCut.replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_bSFup")
  cut_btagDn = fullCut.replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_bSFdn")
  cut_mistagUp = fullCut.replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_lSFup")
  cut_mistagDn = fullCut.replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_lSFdn")
	
  cut_tau21Up = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[0]")
  cut_tau21Dn = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[1]")
  cut_jmsWUp = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[2]")
  cut_jmsWDn = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[3]")
  cut_jmrWUp = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[4]")
  cut_jmrWDn = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[5]")
  cut_tau21ptUp = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[6]")
  cut_tau21ptDn = fullCut.replace("NJetsWtagged","NJetsWtagged_shifts[7]")
	
  cut_tau32Up = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[0]")
  cut_tau32Dn = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[1]")
  cut_jmstUp = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[2]")
  cut_jmstDn = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[3]")
  cut_jmrtUp = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[4]")
  cut_jmrtDn = fullCut.replace("NJetsTtagged","NJetsTtagged_shifts[5]")
	
  cut_hotstatUp = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[0]")
  cut_hotstatDn = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[1]")
  cut_hotcspurUp = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[2]")
  cut_hotcspureDn = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[3]")
  cut_hotclosureUp = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[4]")
  cut_hotclosureDn = fullCut.replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[5]")
	
  # declare histograms
  hists = {}
  if plot2D: 
    if verbose: print("Using 2D hists...")
    hists["{}_{}_{}_{}{}".format(iPlot,lumiStr,catStr,process,flv)] = TH2D(
    iPlot+"_"+lumiStr+"_"+catStr+"_"+process+flv,
    yAxisLabel+xAxisLabel,
    len(ybins)-1,ybins,
    len(xbins)-1,xbins
    )
  else:
    if verbose: print("Using 1D hists...") 
    hists["{}_{}_{}_{}{}".format(iPlot,lumiStr,catStr,process,flv)] = TH1D(
    iPlot+"_"+lumiStr+"_"+catStr+"_"+process+flv,
    xAxisLabel,
    len(xbins)-1,xbins
    )
  if doAllSys:
    for syst in systList:
      for dir in ["Up","Down"]:
        if plot2D: hists[iPlot+syst+dir+"_"+lumiStr+"_"+catStr+"_"+process+flv] = TH2D(
          iPlot+syst+dir+"_"+lumiStr+"_"+catStr+"_"+process+flv,
          yAxisLabel+xAxisLabel,
          len(ybins)-1,ybins,
          len(xbins)-1,xbins
        )
        else: hists[iPlot+sys+dir+"_"+lumiStr+"_"+catStr+"_"+process+flv] = TH1D(
          iPlot+syst+dir+"_"+lumiStr+"_"+catStr+"_"+process+flv,
          xAxisLabel,
          len(xbins)-1,xbins
        )
    for i in range(100):
      if plot2D: hists[iPlot+"pdf"+str(i)+"_"+lumiStr+"_"+catStr+"_"+process+flv] = TH2D(
        iPlot+"pdf"+str(i)+"_"+lumiStr+"_"+catStr+"_"+process+flv,
        yAxisLabel+xAxisLabel,
        len(ybins)-1,ybins,
        len(xbins)-1,xbins
        )
      else: hists[iPlot+"pdf"+str(i)+"_"+lumiStr+"_"+catStr+"_"+process+flv] = TH1D(
        iPlot+"pdf"+str(i)+"_"+lumiStr+"_"+catStr+"_"+process+flv,
        xAxisLabel,
        len(xbins)-1,xbins
        )
  for hist in hists: hists[hist].Sumw2()
  # draw histograms
  
  if verbose:
    print("Plotting tree: {}".format(plotTreeName))
    print("Using parameters:")
    print(" > Flavor: {}".format(isEM))
    print(" > # HOT-tagged jets: {}".format(nhott))
    print(" > # T-tagged jets: {}".format(nttag))
    print(" > # W-tagged jets: {}".format(nWtag))
    print(" > # b-tagged jets: {}".format(nbtag))
    print(" > # jets: {}".format(njets))
    print("Weights: {}".format(weightStr))
    print("Cuts: {}".format(fullCut))
    
  # check for shifts
  tshift = ["","","","","",""]
  Wshift = ["","","","","","","",""]
  bSF = ["","","",""]
    
  rootTree[process].Draw(
    "{} >> {}_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
    "{} * ( {} )".format(weightStr,fullCut),
    "GOFF"
    )
  if verbose: print("Finished drawing nominal {}".format(process))
  if doAllSys:
    rootTree[process].Draw(
      "{} >> {}pileupUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightPileupUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}pileupDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightPileupDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}prefireUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightPrefireUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}prefireDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightPrefireDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muRFcorrdUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuRFcorrdUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muRFcorrdDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuRFcorrdDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muRUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuRUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muRDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuRDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muFUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuFUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}muFDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightmuFDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}isrUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightIsrUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}isrDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightIsrDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}fsrUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightFsrUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}fsrDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightFsrDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}njetUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightNjetUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}njetDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightNjetDnStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}njetsfUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightNjetSFUpStr,fullCut),
      "GOFF"
      )
    rootTree[process].Draw(
      "{} >> {}njetsfDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
      "{} * ( {} )".format(weightNjetSFDnStr,fullCut),
      "GOFF"
      )
        
    
  # hot-tagging plots
    if nhott != "0p":
      rootTree[process].Draw(
        "{} >> {}hotstatUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotstatUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{} >> {}hotstatDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotstatDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{} >> {}hotcspurUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotcspurUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{} >> {}hotstatDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotstatDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{} >> {}hotclosureUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotclosureUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{} >> {}hotclosureDn_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,proces,flv),
        "{} * ( {} )".format(weightStr,cut_hotclosureDn),
        "GOFF"
        )
        
  # t-tagging plots
    if "ttagged" in plotTreeName.lower() or "tjet" in plotTreeName.lower():
      tshift = ["_shift[0]","_shift[1]","_shift[2]","_shift[3]","_shift[4]","_shift[5]"]
    if nttag != "0p":
      rootTree[process].Draw(
        "{}{} >> {}tau32Up_{}_{}_{}{}".format(plotTreeName,tshift[0],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau32Up),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}tau32Down_{}_{}_{}{}".format(plotTreeName,tshift[1],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau32Dn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmstUp_{}_{}_{}{}".format(plotTreeName,tshift[2],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmstUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmstDown_{}_{}_{}{}".format(plotTreeName,tshift[3],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmstDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmrtUp_{}_{}_{}{}".format(plotTreeName,tshift[4],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmrtUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmrtDown_{}_{}_{}{}".format(plotTreeName,tshift[5],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmrtDn),
        "GOFF"
        )
            
        
  # W-tagging plots
    if "wtagged" in plotTreeName.lower() or "wjet" in plotTreeName.lower():
      Wshift = ["_shift[0]","_shift[1]","_shift[2]","_shift[3]","_shift[4]","_shift[5]","_shift[6]","_shift[7]"]
    if nWtag != "0p":
      rootTree[process].Draw(
        "{}{} >> {}tau21Up_{}_{}_{}{}".format(plotTreeName,Wshift[0],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau21Up),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}tau21Down_{}_{}_{}{}".format(plotTreeName,Wshift[1],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau21Dn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmsWUp_{}_{}_{}{}".format(plotTreeName,Wshift[2],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmsWUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmsWDown_{}_{}_{}{}".format(plotTreeName,Wshift[3],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmsWDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmrWUp_{}_{}_{}{}".format(plotTreeName,Wshift[4],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmrWUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}jmrWDown_{}_{}_{}{}".format(plotTreeName,Wshift[5],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_jmrWDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}tau21ptUp_{}_{}_{}{}".format(plotTreeName,Wshift[6],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau21ptUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}tau21ptDown_{}_{}_{}{}".format(plotTreeName,Wshift[7],iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_tau21ptDn),
        "GOFF"
        )
            
  # b-tagging plots
    if "csvwithsf" in plotTreeName.lower() or "htag" in plotTreeName.lower() or "mleppb" in plotTreeName.lower() or "bjetlead" in plotTreeName.lower() or "minmlb" in plotTreeName.lower():
      bSF = ["_bSFup","_bSFdn","_lSFup","_lSFdn"]
    if nbtag != "0p":
      rootTree[process].Draw(
        "{}{} >> {}btagUp_{}_{}_{}{}".format(plotTreeName.replace("_lepBJets","_bSFup_lepBJets"),bSF[0],iPlot,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_btagUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}btagDn_{}_{}_{}{}".format(plotTreeName.replace("_lepBJets","_bSFdn_lepBJets"),bSF[1],iPlot,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_btagDn),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}mistagUp_{}_{}_{}{}".format(plotTreeName.replace("_lepBJets","_lSFup_lepBJets"),bSF[2],iPlot,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_mistagUp),
        "GOFF"
        )
      rootTree[process].Draw(
        "{}{} >> {}mistagUp_{}_{}_{}{}".format(plotTreeName.replace("_lepBJets","_lSFdn_lepBJets"),bSF[3],iPlot,catStr,process,flv),
        "{} * ( {} )".format(weightStr,cut_mistagDn),
        "GOFF"
        )
            
    if rootTree[process+"jecUp"]:
      rootTree[process+"jecUp"].Draw(
        "{} >> {}jecUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr, fullCut),
        "GOFF"
        )
      rootTree[process+"jecDown"].Draw(
        "{} >> {}jecDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr, fullCut),
        "GOFF"
        )
    if rootTree[process+"jerUp"]:
      rootTree[process+"jerUp"].Draw(
        "{} >> {}jerUp_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr, fullCut),
        "GOFF"
        )
      rootTree[process+"jerDown"].Draw(
        "{} >> {}jerDown_{}_{}_{}{}".format(plotTreeName,iPlot,lumiStr,catStr,process,flv),
        "{} * ( {} )".format(weightStr, fullCut),
        "GOFF"
        )
    if doPDF:
      for i in range(100):
        print("Running PDF {}/100...\r".format(i))
        rootTree[process].Draw(
          "{} >> {}pdf{}_{}_{}_{}{}".format(plotTreeName,iPlot,str(i),lumiStr,catStr,process,flv),
          "pdfWeights[{}] * {} * ( {} )".format(str(i),weightStr,fullCut),
          "GOFF"
          )
  for hist in hists: hists[hist].SetDirectory(0)
  if verbose: print("Finished producing hists for {}".format(process))
  return hists

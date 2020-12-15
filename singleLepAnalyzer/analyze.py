#!/usr/bin/python

from ROOT import TH1D, TH2D, TTree, TFile
from array import array
import varsList

def analyze( rootTree, process, doAllSys, doPDF, iPlot, plotDetails, catStr, systList, year, verbose ):
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
  process_weights = varsList.weights[ str(year) ]

  lumiStr = str( varsList.targetLumi / 1000. ).replace(".","p") + "fb" # 1/fb  
	weights = {
	  "Nominal": "3" if process.lower().startswith( "ttjets" ) else "1"
	}
	cuts = {
	  "Base": varsList.cutStr	
	}
	
  # define the categories
  isEM  = catStr.split("_")[0][2:]
  nhott = catStr.split("_")[1][4:]
  nttag = catStr.split("_")[2][2:]
  nWtag = catStr.split("_")[3][2:]
  nbtag = catStr.split("_")[4][2:]
  njets = catStr.split("_")[5][2:]
	
  if process.lower().startswith("ttjetssemilepnjet0"): cuts[ "Base" ] += " && (isHTgt500Njetge9 == 0)"
  if process.lower().startswith("ttjetssemilepnjet9"): cuts[ "Base" ] += " && (isHTgt500Njetge9 == 1)"
  if process.lower().startswith("ttjets"): cuts[ "Base" ] += " && (isTraining == 3)"
	
	print( ">> Processing {} for {}, {}".format( iPlot, year, process ) )
	print( ">> Lepton: {}".format( isEM ) )
	print( ">> # HOT jets: {}".format( nhott ) )
	print( ">> # t jets: {}".format( nttag ) )
	print( ">> # W jets: {}".format( nWtag ) )
	print( ">> # b jets: {}".format( nbtag ) )
	print( ">> # jets: {}".format( njets ) )
	
	# modify weights
	
  if "Data" not in process:
	  weights[ "Nominal" ] += " * triggerXSF * pileupWeight * lepIdSF * EGammaGsfSF * isoSF * L1NonPrefiringProb_CommonCalc "
	  weights[ "Nominal" ] += " * ( MCWeight_MultiLepCalc / abs(MCWeight_MultiLepCalc) ) * {}".format( process_weights[process] )
    weights[ "NoNjet" ] = weights[ "Nominal" ]
    weights[ "trigger" ] = { "Up": weights[ "Nominal" ].replace("triggerXSF","(triggerXSF+triggerXSFUncert)"),
                             "Down": weights[ "Nominal" ].replace("triggerXSF","(triggerXSF-triggerXSFUncert)") }
    weights[ "pileup" ] = { "Up": weights[ "Nominal" ].replace("pileupWeight","pileupWeightUp"),
                            "Down": weights[ "Nominal" ].replace("pileupWeight","pileupWeightDown") }
    weights[ "prefire" ] = { "Up": weights[ "Nominal" ].replace("L1NonPrefiringProb_CommonCalc","L1NonPrefiringProbUp_CommonCalc"),
                             "Down": weights[ "Nominal" ].replace("L1NonPrefiringProb_CommonCalc","L1NonPrefiringProbDn_CommonCalc") }
    weights[ "muRFcorrd" ] = { "Up": "renormWeights[5] * {}".format( weights[ "Nominal" ] ),
															 "Down": "renormWeights[3] * {}".format( weights[ "Nominal" ] ) }
    weights[ "muR" ] = { "Up": "renormWeights[4] * {}".format( weights[ "Nominal" ] ),
												 "Down":  "renormWeights[2] * {}".format( weights[ "Nominal" ] ) }
    weights[ "muF" ] = { "Up": "renormWeights[1] * {}".format( weights[ "Nominal" ] ),
													 "Down": "renormWeights[0] * {}".format( weights[ "Nominal" ] ) }
		weights[ "isr" ] = { "Up": "renormPSWeights[0] * {}".format( weights[ "Nominal" ] ),
												 "Down": "renormPSWeights[2] * {}".format( weights[ "Nominal" ] ) }
    weights[ "isr" ] = { "Up": "renormPSWeights[1] * {}".format( weights[ "Nominal" ] ),
												 "Down": "renormPSWeights[3] * {}".format( weights[ "Nominal" ] ) }
		weights[ "toppt" ] = { "Up": "({}) * {}".format( "1" if "ttjets" in process.lower() else "topPtWeight13TeV", weights[ "Nominal" ] ),
													 "Down": "(1/{}) * {}".format( "1" if "ttjets" in process.lower() else "topPtWeight13TeV", weights[ "Nominal" ] ) }
    weights[ "njet" ] = { "Up": weights[ "Nominal" ],
												  "Down": weights[ "Nominal" ] }
		weights[ "njetsf" ] = { "Up": weights[ "Nominal" ],
													  "Down": weights[ "Nominal" ] }
		weights[ "CSVshapelf" ] = { "Up": weights[ "Nominal" ].replace("btagCSVWeight","btagCSVWeight_LFup"),
															  "Down": weights[ "Nominal" ].replace("btagCSVWeight","btagCSVWeight_LFdn") }
		weights[ "CSVshapehf" ] = { "Up": weights[ "Nominal" ].replace("btagCSVWeight","btagCSVWeight_HFup"),
															  "Down": weights[ "Nominal" ].replace("btagCSVWeight","btagCSVWeight_HFdn") }
		
	# modify cuts
  isEMCut  = " && isElectron==1" if isEM == "E" else " && isMuon==1"
  nhottCut = " && NresolvedTops1pFake {}= {}".format( ">" if "p" in nhott else "=", nhott[:-1] if "p" in nhott else nhott )
  nttagCut = " && NJetsTtagged {}= {}".format( ">" if "p" in nttag else "=", nttag[:-1] if "p" in nttag else nttag )
  nWtagCut = " && NJetsWtagged {}= {}".format( ">" if "p" in nWtag else "=", nWtag[:-1] if "p" in nWtag else nWtag )
  nbtagCut = " && NJetsCSVwithSF_MultiLepCalc {}= {}".format( ">" if "p" in nbtag else "=", nbtag[:-1] if "p" in nbtag else nbtag )
  njetsCut = " && NJets_JetSubCalc {}= {}".format( ">" if "p" in njets else "=", njets[:-1] if "p" in njets else njets )
 
  if nbtag == "0" and "minmlb" in iPlot.lower():
    originalLJMETName = plotTreeName
    plotTreeName = "minMleppJet"
    
	cuts[ "Nominal" ] = cuts[ "Base" ] + isEMcut + nhotCut + nttagCut + nWtagCut + nbtagCut + njetsCut
    
  # modify the cuts for shifts
  cuts[ "btag" ] = { "Up": cuts[ "Nominal" ].replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_bSFup"),
										 "Down": cuts[ "Nominal" ].replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_bSFdn") }
  cuts[ "mistag" ] = { "Up": cuts[ "Nominal" ].replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_lSFup"),
											 "Down": cuts[ "Nominal" ].replace("NJetsCSVwithSF_MultiLepCalc","NJetsCSVwithSF_MultiLepCalc_lSFdn") }
  cuts[ "tau21" ] = { "Up": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[0]"),
										  "Down": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[1]") }
  cuts[ "jmsW" ] = { "Up": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[2]"),
										 "Down": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[3]") }
  cuts[ "jmrW" ] = { "Up": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[4]"),
										 "Down": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[5]") }
  cuts[ "tau21pt" ] = { "Up": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[6]"),
											  "Down": cuts[ "Nominal" ].replace("NJetsWtagged","NJetsWtagged_shifts[7]") }
	cuts[ "tau32" ] = { "Up": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[0]"),
										  "Down": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[1]") }
  cuts[ "jmst" ] = { "Up": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[2]"),
										 "Down": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[3]") }
  cuts[ "jmrt" ] = { "Up": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[4]"),
										 "Down": cuts[ "Nominal" ].replace("NJetsTtagged","NJetsTtagged_shifts[5]") }
  cuts[ "hotstat" ] = { "Up": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[0]"),
											  "Down": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[1]") }
  cuts[ "hotcspur" ] = { "Up": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[2]"),
												 "Down": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[3]") }
  cuts[ "hotclosure" ] = { "Up": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[4]"),
													 "Down": cuts[ "Nominal" ].replace("NresolvedTops1pFake","NresolvedTops1pFake_shifts[5]") }
	
  # declare histograms
  hists = {}
	with "{}_{}_{}_{}".format( iPlot, lumiStr, catStr, process ) as key:
		hists[ key ] = TH1D( key, xAxisLabel, len(xbins) - 1, xbinS )
  if doAllSys:
    for syst in systList:
      for dir in [ "Up","Down" ]:
				with "{}_{}_{}_{}".format( iPlot+syst+dir, lumiStr, catStr, process ) as key:
					hists[ key ] = TH1D( key, xAxisLabel, len(xbins) - 1, xbins )
	if doPDF:
    for i in range(100):
			with "{}pdf{}_{}_{}_{}".format( iPlot, i, lumiStr, catStr, process ) as key:
				hists[ key ] = TH1D( key, xAxisLabel, len(xbins) - 1, xbins )
				
	# Sumw2() tells the hist to also store the sum of squares of weights
  for key in hists: hists[ key ].Sumw2()
		
  # draw histograms
  rootTree[process].Draw( "{} >> {}_{}_{}_{}".format(plotTreeName,iPlot,lumiStr,catStr,process), "{} * ( {} )".format( weights[ "Nominal" ], cuts[ "Nominal" ] ), "GOFF" )
  if verbose: print("[OK ] Finished drawing nominal histogram" )
	syst_hist_count = 0
  if doAllSys:
		for syst in systList:
			for dir in [ "Up", "Down" ]:
				with "{}_{}_{}_{}".format( iPlot + syst + dir, lumiStr, catStr, process ) as key:
					if syst in [ "pileup", "prefire", "muRFcorrd", "muR", "muF", "isr", "fsr", "njet", "njetsf", "CSVshapelf", "CSVshapehf" ]:
						rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ syst ][ dir ], cuts[ "Nominal" ] ), "GOFF" )
					# hot-tagging plots
					if ( syst in [ "hotstat", "hotcspur", "hotclosure" ] ) and ( nhott != "0p" ):
						rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
					# t-tagging plots
					if ( syst in [ "tau32", "jmst", "jmrt" ] ) and ( nttag != "0p" ):
						if "ttagged" in plotTreeName.lower() or "tjet" in plotTreeName.lower():
							shift_indx = 2*np.argwhere( np.array([ "tau32", "jmst", "jmrt" ]) == syst )[0,0] + np.argwhere( np.array([ "Up", "Down" ]) == dir )[0,0]
							rootTree[ process ].Draw( "{}_shifts[{}] >> {}".format( plotTreeName, shift_indx, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
						else: rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
					# W-tagging plots
					if ( syst in [ "tau21", "jmsW", "jmrW", "tau21pt" ] ) and ( nWtag != "0p" ):
						if "wtagged" in plotTreeName.lower() or "wjet" in plotTreeName.lower():
							shift_indx = 2*np.argwhere( np.array([ "tau21", "jmsW", "jmrW", "tau21pt" ]) == syst )[0,0] + np.argwhere( np.array([ "Up", "Down" ]) == dir )[0,0]
							rootTree[ process ].Draw( "{}_shifts[{}] >> {}".format( plotTreeName, shift_indx, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
						else: rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
					# b-tagging plots
					if ( syst in [ "btag", "mistag" ] ) and ( nbtag != "0p" ):
						if "csvwithsf" in plotTreeName.lower() or "htag" in plotTreeName.lower() or "mleppb" in plotTreeName.lower() or "bjetlead" in plotTreeName.lower() or "minmlb" in plotTreeName.lower():
							if syst == "btag": rootTree[ process ].Draw( "{}_bSF{} >> {}".format( plotTreeName, dir.lower(), key ), "{} * ({})".format( weights[ "Nominal" ], cut[ syst ][ dir ] ), "GOFF" )
							if syst == "mistag": rootTree[ process ].Draw( "{}_lSF{} >> {}".format( plotTreeName, dir.lower(), key ), "{} * ({})".format( weights[ "Nominal" ], cut[ syst ][ dir ] ), "GOFF" )
						else: rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ syst ][ dir ] ), "GOFF" )
					# process jec and jer
					if ( syst in [ "jec", "jer" ] ) and rootTree[ process + syst + dir ]: rootTree.Draw( "{} >> {}".format( plotTreeName, key ), "{} * ({})".format( weights[ "Nominal" ], cuts[ "Nominal" ] ), "GOFF" )
		print( "[OK ] Finished drawing systematic histograms" )
	
	if doPDF:
		for i in range(100):
			with "{}pdf{}_{}_{}_{}".format( iPlot, i, lumiStr, catStr, process ) as key:
				rootTree[ process ].Draw( "{} >> {}".format( plotTreeName, key ), "pdfWeights[{}] * {} * ({})".format( i, weights[ "Nominal" ], cuts[ "Nominal" ] ), "GOFF" )
		print( "[OK ] Finished drawing PDF histograms" )
							
  for key in hists: hists[ key ].SetDirectory(0)
  if verbose: print( "[OK ] Finished" )
  return hists

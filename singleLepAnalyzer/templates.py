#!/usr/bin/python
# this is the equivalent of singleLepAnalyzer/makeTemplates/doTemplates.py

import os, sys, json, time, math, datetime, pickle, itertools, fnmatch
from argparse import ArgumentParser
from ROOT import gROOT, TFile, TH1F
import numpy as np
from array import array
from utils import *
import varsList

gROOT.SetBatch(1)

parser = ArgumentParser()
parser.add_argument( "-y", "--year", required = True )
parser.add_argument( "-j", "--config", required = True )
args = parser.parse_args()

with open( args.config, "r" ) as file:
  jsonFile = json.load( file )

allSamples = varsList.all_samples[ args.year ]
weights = varsList.weights[ args.year ]

configuration = jsonFile[ "CONFIGURATION" ]
step2_configuration = jsonFile[ "STEP 2" ][ "CONFIGURATION" ]

systematics = configuration[ "USE_SYSTEMATICS" ]
systematics_list = configuration[ "SYSTEMATICS" ]
test = configuration[ "UNIT_TEST" ]
pdf = configuration[ "USE_PDF" ]

summary = step2_configuration[ "SUMMARY" ]
scale_to_1_pb = step2_configuration[ "SCALE_TO_1_PB" ]
cr_systematic = step2_configuration[ "CR_SYS" ]
normalize_pdf = step2_configuration[ "NORMALIZE_PDF" ]
br_scan = step2_configuration[ "BR_SCAN" ]
rebin = step2_configuration[ "REBIN" ]
lumiscale = step2_configuration[ "LUMISCALE" ]
zero = step2_configuration[ "ZERO" ]
remove_threshold = step2_configuration[ "REMOVE_THRESHOLD" ]
ttHFsf = step2_configuration[ "ttHFsf" ]
ttLFsf = step2_configuration[ "ttLFsf" ]

categories = jsonFile[ "CATEGORIES" ][ "FULL" ] if not test else jsonFile[ "CATEGORIES" ][ "TEST" ]
category_list = [
  "is{}_nhot{}_nt{}_nw{}_nb{}_nj{}".format( cat[0], cat[1], cat[2], cat[3], cat[4], cat[5] ) for cat in list( itertools.product(
    categories[ "LEP" ], categories[ "NHOT" ], categories[ "NTOP" ], categories[ "NW" ], categories[ "NBOT" ], categories[ "NJET" ] ) )  
]

variables = configuration[ args.year ][ "INPUTS" ]

lumiStr = str(varsList.targetLumi/1000.).replace(".","p") + "fb" 
uncertainties = varsList.uncertainties

bkg = {}
sig = {}
data = {}
# begin by specifying the individual processes
with [ "TTJetsHad", "TTJets2L2nu", "TTJetsSemiLepNjet9bin", "TTJetsSemiLepNjet0", "TTJetsSemiLepNjet9" ] as tt_list:
  # corresponds to bkgProcList
  bkg[ "PROCESS" ] = { 
    "WJets": [ "WJetsMG200", "WJetsMG400", "WJetsMG600", "WJetsMG800" ],
    "ZJets": [ "DYMG200", "DYMG400", "DYMG600", "DYMG800", "DYMG1200", "DYMG2500" ],
    "VV": [ "WW", "WZ", "ZZ" ],
    "T": [ "Ts", "Tt", "Tbt", "TtW", "TbtW" ], 
    "TTV": [ "TTWl", "TTZlM10", "TTZlM1to10", "TTHB", "TTHnoB" ],
    "TTXY": [ "TTHH", "TTTJ", "TTTW", "TTWH", "TTWW", "TTWZ", "TTZH", "TTZZ" ],
    "qcd": [ "QCDht200", "QCDht300", "QCDht500", "QCDht700", "QCDht1000", "QCDht1500", "QCDht2000" ],
    "tt1b": [ tt + "TT1b" for tt in tt_list ],
    "tt2b": [ tt + "TT2b" for tt in tt_list ],
    "ttbb": [ tt + "TTbb" for tt in tt_list ],
    "ttcc": [ tt + "TTcc" for tt in tt_list ],
    "ttjj": [ tt + "TTjj" for tt in tt_list if tt != "TTJetsSemiLepNjet0" ]
  }
  bkg[ "PROCESS" ][ "WJets" ] += [ "WJetsMG1200" + str(i) for i in [1,2,3] ] if args.year == "2017" else [ "WJetsMG1200" ]
  bkg[ "PROCESS" ][ "WJets" ] += [ "WJetsMG2500" + str(i) for i in [2,3,4] ] if args.year == "2017" else [ "WJetsMG2500" ]
  if args.year == "2017": bkg[ "PROCESS" ][ "T" ] += [ "Tbs" ]

# specify the grouped processes
with bkg[ "PROCESS" ] as process:
  # corresponds to bkgGrupList
  bkg[ "GROUP" ] = {
    "ttnobb": process[ "ttjj" ] + process[ "ttcc" ] + process[ "tt1b" ] + process[ "tt2b" ],
    "ttbb": process[ "ttbb" ],
    "top": process[ "T" ] + process[ "TTV" ] + process[ "TTXY" ],
    "ewk": process[ "WJets" ] + process[ "ZJets" ] + process[ "VV" ],
    "qcd": process[ "qcd" ]
  }
  # corresponds to ttbarGruplist
  bkg[ "TTBAR_GROUPS" ] = { tt: bkg[ "GROUP" ][ tt ] for tt in [ "ttnobb", "ttbb" ] }
  # corresponds to ttbarProcList
  bkg[ "TTBAR_PROCESS" ] = { tt: process[ tt ] for tt in [ "ttjj", "ttcc", "ttbb", "tt1b", "tt2b" ] }
  
# specify the systematics
bkg[ "SYSTEMATICS" ] = {}
with { "hd": "HDAMP", "ue": "UE" } as syst_key: 
  for syst in [ "hd", "ue" ]:
    for dir in [ "up", "dn" ]:
      for flavor in [ "jj", "cc", "bb", "1b", "2b" ]:
        bkg[ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ] = [
          "TTJetsHad{}{}TT{}".format( syst_key[ syst ], dir, flavor ),
          "TTJets2L2nu{}{}TT{}".format( syst_key[ syst ], dir, flavor ),
          "TTJetsSemiLep{}{}TT{}".format( syst_key[ syst ], dir, flavor )
        ]
      bkg[ "SYSTEMATICS" ][ "ttbj_" + syst + dir ] = []
      bkg[ "SYSTEMATICS" ][ "ttnobb_" + syst + dir ] = []
      for flavor in [ "1b", "2b" ]:
        bkg[ "SYSTEMATICS" ][ "ttbj_" + syst + dir ] += bkg[ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ]
      for flavor in [ "jj", "cc", "1b", "2b" ]:
        bkg[ "SYSTEMATICS" ][ "ttnobb_" + syst + dir ] += bkg[ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ] 

# specify the ht processes
bkg[ "HT" ] = { # corresponds to htProcs
  "ewk": bkg[ "GROUP" ][ "ewk" ],
  "WJets": bkg[ "PROCESS" ][ "WJets" ],
  "qcd": bkg[ "GROUP" ][ "qcd" ]
}

# specify the toppt processes
bkg[ "TOPPT" ] = { # corresponds to topptProcs
  "ttbj": bkg[ "PROCESS" ][ "tt1b" ] + bkg[ "PROCESS" ][ "tt2b" ],
  "ttnobb": bkg[ "GROUP" ][ "ttnobb" ],
  tt: bkg[ "PROCESS" ][ tt ] for tt in [ "ttjj", "ttcc", "ttbb", "tt1b", "tt2b", "ttbj", "ttnobb" ]
}

sig[ "PROCESS" ] = [ "tttt" ]

data[ "PROCESS" ] = [ "DataE", "DataM" ]

def init_hists( variable, hists, dataHists, sigHists, bkgHists, data, sig, bkg, category, tagBR ):
# this is used in make_category_templates to initialize the histograms 
# hists from hists.py are stored with the keys "[variable]_[lumiStr]_[category]_[sample]"
# for the systematics: "[variable][sys][dir]_[lumiStr]_[catStr]_[sample]"
# for the pdf: "[variable]pdf[i]_[lumiStr]_[catStr]_[sample]"

  if args.verbose: print("Processing category: {}".format(category))
  histKey = "{}_{}_{}".format( variable, lumiStr, category )
  tagBRpCat = tagBR + category
 
  if len(data) > 0: 
    hists[ "data" + tagBRpCat ] = dataHists[ histKey + "_" + data[0] ].Clone( histKey + "__DATA" )
    for sample in data:
      if sample != data[0]: hists[ "data" + tagBRpCat ].Add( data[ histKey + "_" + sample ] )
          
# process refers to a collection of samples
  for process in bkg:
    hists[ process + tagBRpCat ] = bkgHists[ histKey + "_" + bkg[ process ][0] ].Clone( histKey + "__" + process )
    for sample in bkg[ process ]:
      if sample != bkg[ process ][0]: hists[ process + tagBRpCat ].Add( bkg[ histKey + "_" + sample ] )
             
  for sample in sig:
    hists[ sample + tagBRpCat ] = sigHists[ histKey + "_" + sample ].Clone( histKey + "__sig" )
          
  if args.sys:
    for sys in systList:
      for dir in [ "Up", "Down" ]:
        for process in bkg:
          if sys == "toppt" and process not in topptProcs: continue
          if sys == "ht" and process not in htProcs: continue
          hists[ process + tagBRpCat + sys + dir ] = bkgHists[ histKey.replace( variable, variable + sys + dir ) + "_" + bkg[ process ][0] ].Clone(
            histKey + "__" + process + "__" + sys + "__" + dir.replace("Up","plus").replace("Down","minus")
          )
          for sample in bkg[ process ]:
            if sample != bkg[ process ][0]: hists[ process + tagBRpCat + sys + dir ].Add(
              bkgHists[ histKey.replace( variable, variable + sys + dir ) + "_" + sample ]
            )
        if sys == "toppt" or sys == "ht": continue
        for sample in sig:
          hists[ sample + tagBRpCat + sys + dir ] = sigHists[ histKey.replace( variable, variable + sys + dir ) + "_" + sample ].Clone(
            histKey + "__sig__" + sys + "__" + dir.replace("Up","plus").replace("Down","minus")
          )
    for process in hdamp:
    # HDAMP systematics
      hists[ process + tagBRpCat ] = bkgHists[ histKey + "_" + hdamp[ process ][0] ].Clone(
        histKey + "__" + process.replace( "hd", "_hdamp" ).replace( "up", "__plus" ).replace( "dn", "__minus" ) )
      for sample in hdamp[ process ]:
        if sample != hdamp[ process ][0]: hists[ process + tagBRpCat ].Add( bkg[ histKey + "_" + sample ] )
    
    for process in ue:             
    # UE systematics
      hists[ process + tagBRpCat ] = bkgHists[ histKey + "_" + ue[ process ][0] ].Clone(
        histKey + "__" + process.replace( "ue", "_ue" ).replace( "up", "__plus" ).replace( "dn", "__minus" ) )
      for sample in ue[ process ]:
        if sample != ue[ process ][0]: hists[ process + tagBRpCat ].Add(
          bkgHists[ histKey + "_" + sample ] )
                     
  if args.pdf:
    for j in range(100):
      for process in bkg:
        hists[ process + tagBRpCat + "pdf" + str(j) ] = bkgHists[ histKey.replace( variable, variable + "pdf" + str(j) ) + "_" + bkg[ process ][0] ].Clone(
          histKey + "__" + process + "__pdf" + str(j) )
        for sample in bkg[ process ]:
          if sample != bkg[ process ][0]: hists[ process + tagBRpCat + "pdf" + str(j) ].Add(
            bkgHists[ histKey.replace( variable, variable + "pdf" + str(j) ) + "_" + sample ]
            )
      for sample in sig:
        hists[ sample + tagBRpCat + "pdf" + str(j) ] = sig[ histKey.replace( variable, variable + "pdf" + str(j) ) + "_" + sample ].Clone(
          histKey + "__" + sample + "__pdf" + str(j)
          )
          
  return hists

def scale_ttbb( hists, sig, bkg, hdamp, ue, variable, category, tagBR ):
  histKey = "{}_{}_{}".format( variable, lumiStr, category )
  tagBRpCat = tagBR + category
  
  samples = [ 
    "ttnobb", "ttbb",
    "ttjj", "ttcc", "ttbb", "tt1b", "tt2b"
  ]
  
  N_ttbb = hists[ "ttbb" + tagBRpCat ].Integral()
  N_ttnobb = 0.
  for sample in samples:
    if sample.lower() != "ttbb": N_ttnobb += hists[ sample + tagBRpCat ].Integral()

  ttHFsf = 4.7/3.9 # from TOP-18-002 (v34) Table 4, set it to 1 if no ttHFsf is desired
  # no need to scale if the scale factor is equal to 1
  if ttHFsf == 1.:
    return hists

  else:
    if args.verbose: print( "Scaling ttbb by: {}".format( ttHFsf ) )
    ttLFsf = 1. + ( 1. - ttHFsf ) * ( N_ttbb / N_ttnobb )

    hists[ "ttbb" + tagBRpCat ].Scale( ttHFsf )
    for sample in samples:
      if sample.lower() != "ttbb": hists[ sample + tagBRpCat ].Scale( ttLFsf )
  
    if args.sys:
      for sys in systList:
        for dir in [ "Up", "Down" ]:
          hists[ "ttbb" + tagBRpCat + sys + dir ].Scale( ttHFsf )
          for sample in samples:
            if sample.lower() != "ttbb":
              hists[ sample + tagBRpCat + sys + dir ].Scale( ttLFsf )
            
  # HDAMP systematics
      for process in hdamp:
        if "ttbb" in process.lower(): # scale up ttbb
          hists[ process + tagBRpCat ].Scale( ttHFsf )
        else: # scale down tt non-bb
          hists[ process + tagBRpCat ].Scale( ttLFsf )
        
    # UE systematics
      for process in ue:
        if "ttbb" in process.lower():
          hists[ process + tagBRpCat ].Scale( ttHFsf )
        else:
          hists[ process + tagBRpCat ].Scale( ttLFsf )
        
  # PDF      
    if args.pdf:
      for j in range(100):
        for process in samples:
          if "ttbb" in process.lower():
            hists[ process + tagBRpCat + "pdf" + str(j) ].Scale( ttHFsf )
          else:
            hists[ process + tagBRpCat + "pdf" + str(j) ].Scale( ttLFsf )
          
  return hists

def systematic_yield( hists, yields, variable, sig, bkg, hdamp, ue, hotPt, ht, category, tagBR ):
# this is used in make_category_templates and obtains the yields for the +/- systematic variations
  if args.verbose: print( "Applying one sigma variations of the shape systematics" )
    
  histKey = "{}_{}_{}".format( variable, lumiStr, category )
  tagBRpCat = tagBR + category
    
  for sys in systList:
    for dir in ["Up","Down"]:
      for sample in sig + bkg:
        if sys == "toppt" and sample not in topPt: continue # mod topptProcs
        if sys == "ht" and sample not in ht: continue # mod htProcs
        yields[ histKey + sys + dir ][ sample ] = hists[ sample + tagBRpCat + sys + dir ].Integral()
  for sample in hdamp:
    yields[ sample + tagBRpCat ] = hists[ sample + tagBRpCat ].Integral()
  for sample in ue:
    yields[ sample + tagBRpCat ] = hists[ sample + tagBRpCat ].Integral()
    
  return yields
        
def nominal_yield( hists, yields, errors, sig, bkg, variable, category, tagBR ):
    if args.verbose: print("Preparing yield tables and MC yield error tables")
    
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    tagBRpCat = tagBR + category
    
    samples = list(bkg.keys()) + sig + ["data"]
    bkgGrupList = [
      "ttnobb", "ttbb",
      "top", "ewk", "qcd"
    ]
    bkgGrupList = []
    
    for sample in samples:
      yields[ histKey ][ sample ] = hists[ sample + tagBRpCat ].Integral()
      errors[ histKey ][ sample ] = 0.
        
    yields[ histKey ][ "totBkg" ]      = sum( [ hists[ sample + tagBRpCat ].Integral() for sample in bkgGrupList ] )
    yields[ histKey ][ "dataOverBkg" ] = ( yields[ histKey ][ "data" ] ) / ( yields[ histKey ][ "totBkg" ] + zero )
    errors[ histKey ][ "totBkg" ] = 0.
    errors[ histKey ][ "dataOverBkg" ] = 0.
    
    for j in range( 1, hists[ bkgGrupList[0] + tagBRpCat ].GetXaxis().GetNbins() + 1 ):
      for sample in samples:
        errors[ histKey ][ sample ] += hists[ sample + tagBRpCat ].GetBinError( j )**2
      errors[ histKey ][ "totBkg" ] += sum( [ hists[ sample + tagBRpCat ].GetBinError( j )**2 for sample in bkgGrupList ] )
    for error_key in errors[ histKey ].keys(): 
        errors[ histKey ][ error_key ] = math.sqrt( yields[ histKey ][ error_key ] )
    
    return yields, errors
        
def scale_xsec( hists, variable, sig, allSamples, categories, tagBR ):
# used in make_category_templates
  if args.verbose: print("Scaling cross sections to 1 pb")
  
  histKey = "{}_{}_{}".format( variable, lumiStr, category )
  tagBRpCat = tagBR + category
  
  for sample in sig:
    hists[ sample + tagBRpCat ].Scale( 1. / allSamples[ sample ][2] )
    if args.sys:
      for sys in systList:
        for dir in [ "Up", "Down" ]:
          if sys == "toppt" or syst == "ht": continue
          hists[ sample + tagBRpCat + sys + dir ].Scale( 1. / allSamples[ sample ][2] )
          if args.normalize and ( sys.startswith("mu") or sys == "pdf" ):
            hists[ sample + tagBRpCat + sys + dir ].Scale( hists[ sample + tagBRpCat ].Integral() / hists[ sample + tagBRpCat + sys + dir ].Integral() )
    if args.pdf:
      for j in range(100):
        hists[ sample + tagBRpCat + "pdf" + str(j) ].Scale( 1. / allSamples[ sample ][2] )
  return hists
    
def theta_template( hists, variable, sig, topPt, ht, categories, tagBR ):
# used in make_category_templates
  if args.sys: print("Writing theta templates")
   
  bkgGrupList = [
    "ttnobb", "ttbb",
    "top", "ewk", "qcd"
  ]
    
  for sampleSig in sig:
    thetaFileName = "{}/templates_{}/theta_{}_{}{}_{}.root".format(
      dataset,
      dateTag,
      variable,
      sampleSig,
      tagBR,
      lumiStr
      )
    thetaFile = TFile( thetaFileName, "RECREATE" )
    for category in categories:
      histKey = "{}_{}_{}".format( variable, lumiStr, category )
      tagBRpCat = tagBR + category
            
      nTotBkg = sum( [ hists[ sampleBkg + tagBRpCat ].Integral() for sampleBkg in bkgGrupList ] )
      
      if len(data) > 0: hists[ "data" + tagBRpCat ].Write()
      
      for sample in bkgGrupList + sig:
        if sample in bkgGrupList and ( hists[ sample + tagBRpCat ].Integral() / nTotBkg ) <= int(args.threshold):
          if args.verbose:
            print("{} is empty or beneath threshold. Skipping".format( sample + tagBRpCat ))
            continue
        hists[ sample + tagBRpCat ].Write()
        if args.sys:
          for sys in systList:
            for dir in [ "Up", "Down" ]:
              if sys == "toppt" and sample not in topPt: continue
              if sys == "ht" and sample not in ht: continue
              if hists[ sample + tagBRpCat + sys + dir ].Integral() == 0:
                hists[ sample + tagBRpCat + sys + dir ].SetBinContent(1,zero)
              hists[ sample + tagBRpCat + sys + dir ].Write()
      
      if args.pdf:
        for j in range(100): hists[ sample + tagBRpCat + "pdf" + str(j) ].Write()
      
      if args.sys:
        for sample in hdamp: 
          hists[ sample + tagBRpCat ].Write()
     
      if args.sys:
        for sample in ue:
          hists[ sample + tagBRpCat ].Write()
      
    thetaFile.Close()
        
def combine_template( hists, sig, hdamp, ue, topPt, ht, variable, categories, tagBR ):
# used in make_category templates
  if args.sys: print("Writing combine templates")
  
  bkgGrupList = [
    "ttnobb", "ttbb",
    "top", "ewk", "qcd"
  ]
  
  combineFileName = "{}/templates_{}/combine_{}{}_{}.root".format(
    dataset,
    dateTag,
    variable,
    tagBR,
    lumiStr
  )
  combineFile = TFile( combineFileName, "RECREATE" )
  for category in categories:
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    tagBRpCat = tagBR + category
    
    for sample in sig:
      hists[ sample + tagBRpCat ].SetName( hists[ sample + tagBRpCat ].GetName().replace( "__sig", "__" + sample ) )
      hists[ sample + tagBRpCat ].Write()
      
      if args.sys:
        for sys in systList:
          if sys == "toppt" or sys == "ht": continue
          hists[ sample + tagBRpCat + sys + "Up" ].SetName(
            hists[ sample + tagBRpCat + sys + "Up" ].GetName().replace( "__sig", "__" + sample ).replace( "__plus", "Up" ) )
          hists[ sample + tagBRpCat + sys + "Down" ].SetName(
            hists[ sample + tagBRpCat + sys + "Down" ].GetName().replace( "__sig", "__" + sample ).replace( "__minus", "Down" ) )
          hists[ sample + tagBRpCat + sys + "Up" ].Write()
          hists[ sample + tagBRpCat + sys + "Down" ].Write()
          
      if args.pdf:
        for j in range(100):
          hists[ sample + tagBRpCat + "pdf" + str(j) ].SetName( 
            hists[ sample + tagBRpCat + "pdf" + str(j) ].GetName().replace( "__sig", "__" + sample ) )
          hists[ sample + tagBRpCat + "pdf" + str(j) ].Write()
    
    nTotBkg = sum( [ hists[ sample + tagBRpCat ].Integral() for sample in bkgGrupList ] )
    
    for process in bkgGrupList:
      if ( hists[ process + tagBRpCat ].Integral() / nTotBkg ) <= int(args.threshold):
        if args.verbose: 
          print("{} is empty or beneath threshold. Skipping...".format( process + tagBRpCat ))
        continue
      
      hists[ process + tagBRpCat ].SetName( hists[ process + tagBRpCat ].GetName() ) # this seems redundant?
      
      if hists[ process + tagBRpCat ].Integral() == 0: hists[ process + tagBRpCat ].SetBinContent( 1, zero )
      hists[ process + tagBRpCat ].Write()
      
      if args.sys:
        for sys in systList:
          for dir in [ "Up", "Down" ]:
            if sys == "toppt" and process not in topPt: continue
            if sys == "ht" and process not in ht: continue
            hists[ process + tagBRpCat + sys + dir ].SetName( 
              hists[ process + tagBRpCat + sys + dir ].GetName().replace( "__plus", "Up" ).replace( "__minus", "Down" ) )
            hists[ process + tagBRpCat + sys + dir ].Write()
      if args.pdf:
        for j in range(100):
          hists[ process + tagBRpCat + "pdf" + str(j) ].SetName( hists[ process + tagBRpCat + "pdf" + str(j) ].GetName() )
          hists[ process + tagBRpCat + "pdf" + str(j) ].Write()
    if args.sys: # HDAMP
      for sample in hdamp:
        hists[ sample + tagBRpCat ].SetName( hists[ sample + tagBRpCat ].GetName().replace( "__plus", "Up" ).replace( "__minus", "Down" ) )
        hists[ sample + tagBRpCat ].Write()
    if args.sys: # UE
      for sample in ue:
        hists[ sample + tagBRpCat ].SetName( hists[ sample + tagBRpCat ].GetName().replace( "__plus", "Up" ).replace( "__minus", "Down" ) )
        hists[ sample + tagBRpCat ].Write()
    
    if len(data) > 0:    
      hists[ "data" + tagBRpCat ].SetName( hists[ "data" + tagBRpCat ].GetName().replace( "DATA", "data_obs" ) )
      hists[ "data" + tagBRpCat ].Write()
    
  combineFile.Close()
    
def format_summary_yields( yieldHists, yields, errors, category, variable, sample, topPt, ht, binNum ):
# ued in summary_template()
  histKey = "{}_{}_{}".format( variable, lumiStr, category )
  label = ""

  nHOT = category.split("_")[-5][4:]
  nT   = category.split("_")[-4][2:]
  nW   = category.split("_")[-3][2:]
  nB   = category.split("_")[-2][2:]
  nJ   = category.split("_")[-1][2:]
  
  if nHOT != "0p":
    if "p" in nHOT: label += "#geq{}res-t/".format( nHOT[:-1] )
    else: label += "{}res-t/".format( nHOT )
  if nT != "0p":
    if "p" in nT: label += "#geq{}t/".format( nT[:-1] )
    else: label += "{}t/".format( nT )
  if nW != "0p":
    if "p" in nW: label += "#geq{}W/".format( nW[:-1] )
    else: label += "{}W/".format( nW )
  if nB != "0p":
    if "p" in nB: label += "#geq{}b/".format( nB[:-1] )
    else: label += "{}b/".format( nB )
  if nJ != "0p":
    if "p" in nJ: label += "#geq{}j".format( nJ[:-1] )
    else: label += "{}j".format( nJ )
  if label.endswith( "/" ): label = label[:-1]
  
  yieldHists[ lep + sample ].SetBinContent( binNum, yields[ histKey ][ sample ] )
  yieldHists[ lep + sample ].SetBinError( binNum, errors[ histKey ][ sample ] )
  yieldHists[ lep + sample ].GetXaxis().SetBinLabel( binNum, label )
  
  # might need to modify the systematic sample calls
  if args.sys and sample != "data":
    for sys in systList:
      for dir in [ "Up", "Down" ]:
        if sys == "toppt" and sample not in topPt: continue
        if sys == "ht" and sample not in ht: continue
        yieldHists[ lep + sample + sys + dir ].SetBinContent( binNum, yields[ histKey + sys + dir ][ sample ] )
        yieldHists[ lep + sample + sys + dir ].GetXaxis().SetBinLabel( binNum, label )
  if args.sys and sample in hdamp:
    yieldHists[ lep + sample ].SetBinContent( binNum, yields[ histKey ][ sample ] )
    yieldHists[ lep + sample ].GetXaxis().SetBinLabel( binNum, label )
  if args.sys and sample in ue:
    yieldHists[ lep + sample ].SetBinContent( binNum, yields[ histKey + "ueUp" ][ sample ] )
    yieldHists[ lep + sample ].GetXaxis().SetBinLabel( binNum, label )
    
  return yieldHists
        
def summary_template( yields, errors, data, sig, bkg, hdamp, ue, topPt, ht, categories, variable, tagBR ):
  if args.sys: print("Writing summary templates")
  
  for sampleSig in sig:
    summaryFileName = "{}/templates_{}/summary_{}{}_{}.root".format(
      dataset,
      dateTag,
      sampleSig,
      tagBR,
      lumiStr
    )
    
    summaryFile = TFile( summaryFileName, "RECREATE" )
      
    samples = {
      "ttnobb", "ttbb",
      "top", "ewk", "qcd",
      "data",
      sampleSig
    }
      
    for lep in [ "E", "M" ]:
      for sample in samples:
        yieldHists = {}
        yieldHists[ lep + sample ] = TH1F(
          "yield_{}_is{}_nHOT0p_nT0p_nW0p_nB0p_nJ0p__{}".format(
          lumiStr, lep, sample.replace( sampleSig ).replace( "data", "DATA" ) ), 
          "", 
          len( tagList ), 0, len( tagList ) 
          )
        if args.sys and sample != "data":
          for sys in systList:
            for dir in [ "Up", "Down" ]:
              if sys == "toppt" and sample not in topPt: continue
              if sys == "ht" and sample not in ht: continue
              yieldHists[ lep + sample + sys + dir ] = TH1F(
                "yield_{}_is{}_nHOT0p_nT0p_nW0p_nB0p_nJ0p__{}__{}__{}".format(
                  lumiStr, lep, sample.replace( sampleSig, "sig" ),
                  dir.replace( "Up", "plus" ).replace( "Down", "minus" ) ),
                "",
                len( tagList ), 0, len( tagList ) )
                
        for j, category in enumerate( categories ):
          yieldHists = format_summary_yields( yieldHists, yields, errors, category, variable, sample, topPt, ht, j )
          yieldHists[ lep + sample ].Write()
              
          if args.sys and sample != "data":
            for sys in systList:
              for dir in [ "Up", "Down" ]:
                if sys == "toppt" and sample not in topPt: continue
                if sys == "ht" and sample not in ht: continue
                yields[ lep + sample + sys + dir ].Write()
                  
              if args.sys and sample + "_hdup" in samplesBkg.keys():
                yields[ lep + sample + "hdUp" ].Write()
                yields[ lep + sample + "hdDown" ].Write()
              if args.sys and sample + "_ueup" in samplesBkg.keys():
                yields[ lep + sample + "ueUp" ].Write()
                yields[ lep + sample + "ueDown" ].Write()
                  
      if args.sys:
        for sample in hdamp:
          yields[ lep + sample ] = TH1F(
            "yield_{}_is{}_nHOT0p_nT0p_nW0p_nB0p_nJ0p__{}".format(
              lumiStr, lep,
              sample.replace( "hdup", "__hdamp__plus" ).replace( "hddn", "__hdamp__minus" ) ),
            "",
            len( tagList ), 0, len( tagList ) )
            
          for j, category in enumerate( categories ):
            yields = format_summary_yields( yields, errors, category, variable, sample, topPt, ht, j )
            yields[ lep + sample ].Write()
              
          for sys in systList:
            for dir in [ "Up", "Down" ]:
              yields[ lep + sample + sys + dir ].Write()
            
      if args.sys:
        for sample in ue:
          yields[ lep + sample ] = TH1F(
            "yield_{}_is{}_nHOT0p_nT0p_nW0p_nB0p_nJ0p__{}".format(
              lumiStr, lep, sample.replace( "ueup", "__ue__plus" ).replace( "uedn", "__ue__down" ) ),
            "",
            len( tagList ), 0, len( tagList ) )
        
          for j, category in enumerate( categories ):
            yields = format_summary_yields( yields, errors, category, variable, sample, topPt, ht, j )
            yields[ lep + sample ].Write()
            
          for sys in systList:
            for dir in [ "Up", "Down" ]:
              yields[ lep + sample + sys + dir ].Write()
          
      summaryFile.Close()
  return yields
   
def table_systematics( table, yields, data, sig, bkg, topPt, ht, categories ):
  if args.verbose: print( "Adding systematics to table..." )
  
  bkgGrupList = [
    "ttnobb", "ttbb",
    "top", "ewk", "qcd"
  ]

  table.append( [ "break" ] )
  table.append( [ "", "Systematics" ] )
  table.append( [ "break" ] )
  for sample in bkgGrupList + sig:
    table.append( [ sample ] + [ category for category in categories ] + [ "\\\\" ] )
    for sys in sorted( systList + [ "hd", "ue" ] ):
      for dir in [ "Up", "Down" ]:
        row = [ sys + dir ]
        for category in categories:
        
          histKey = "{}_{}_{}".format( variable, lumiStr, category )
          
          try: row.append( " & " + str( round( yields[ histKey + sys + dir ][ sample ] / ( yields[ histKey ][ sample ] + zero ), 2 ) ) )
          except:
            if not ( ( sys == "toppt" and sample not in topPt ) or  
                     ( sys == "ht" and sample not in ht ) or
                     ( sys == "hd" and ( sample + "_hdup" not in hdamp or not args.sys ) ) or
                     ( sys == "ue" and ( sample + "_ueup" not in ue or not args.sys ) ) ):
              print( "Missing {} for channel {} and systematic {}".format( sample, category, sys ) )
            pass
        row.append( "\\\\" )
        table.append( row )
    table.append( [ "break" ] )
    
  return table
   
def yield_tables( yields, erorrs, categories, variable, data, sig, bkg, tagBR ):
# this is used in make_category_templates
# i'll probably need to clena this up more, a lot of the calls in this method are all over the place
  if args.verbose: print( "Producing yield tables" )
  
  bkgProcList = [
    "ttjj", "ttcc", "ttbb", "tt1b", "tt2b",
    "T", "TTV", "TTXY", "WJets", "ZJets", "VV", "qcd"
  ]
  
  bkgGrupList = [
    "ttnobb", "ttbb",
    "top", "ewk", "qcd"
  ]
  
  modelingSys = {}
  
  for category in categories:
    tagMod = tag[ category.find( "nT" ):category.find( "nJ" ) - 3 ]
    modelingSys[ "data_" + tagMod ] = 0.
    modelingSys[ "qcd_" + tagMod ] = 0.
    if not args.CRsys:
      for sample in bkg.keys():
        modelingSys[ sample + "_" + tagMod ] = 0.

  table = []
  
  table.append([ "CUTS:", cutString ])
  table.append([ "break" ])
  table.append([ "break" ])
  
  if args.verbose: print( "Producing yield tables without background grouping..." )
  table.append( ["YIELDS"] + [ process for process in bkgProcList + [ "data" ] ] )
  for category in categories:
    row = [ category ]
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    
    for sample in bkgProcList + [ "data" ]:
      row.append( str( yields[ histKey ][ sample ] ) + " $\pm$ " + str( errors[ histKey ][ sample ] ) )
    table.append( row )
  table.append([ "break" ])
  table.append([ "break" ])
  
  if args.verbose: print( "Producing yield tables with background (top, EWK, QCD) grouping..." )
  table.append( [ "YIELDS" ] + [ sample for sample in bkgGrupList + [ "data" ] ] )
  for category in categories:
    row = [ category ]
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    
    for sample in bkgGrupList + [ "data" ]:
      row.append( str( yields[ histKey ][ sample ] ) + " $\pm$ " + str( errors[ histKey ][ sample ] ) )
    table.append( row )
  table.append( [ "break" ] )
  table.append( [ "break" ] )
  
  if args.verbose: print( "Producing yield tables for signals..." )
  table.append( [ "YIELDS" ] + [ sample for sample in sig ] )
  for category in categories:
    row = [ cateogry ]
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    for sample in sig:
      row.append( str( yields[ histKey ][ sample ] ) + " $\pm$ " + str( errors[ histKey ][ sample ] ) )
    table.append( row )
  
  if args.verbose: print( "Producing yields for AN tables (e/m channels)..." )
  for lep in [ "E", "M" ]:
    if lep == "E": corrdSys = eSysTot
    if lep == "M": corrdSys = mSysTot
    for HOT in nHOTs:
      table.append( [ "break" ] )
      table.append( [ "", "is{}_{}_yields".format( lep, HOT ) ] )
      table.append( [ "break" ] )
      table.append( [ "YIELDS"] + [ category for category in categories if "is" + lep in category and HOT in category ] + ["\\\\"] )
      for sample in bkgGrupList + [ "totBkg", "data", "dataOverBkg" ] + sig:
        row = [ sample ] 
        for category in categories:
          if not ( "is" + lep in category and HOT in category ): continue
          tagMod = category[ category.find( "nT" ):category.find( "nJ" ) - 3 ]
          histKey = "{}_{}_{}".format( variable, lumiStr, category )
          yieldTemp = 0.
          errorTemp = 0.
          if sample == "totBkg" or sample == "dataOverBkg":
            for sampleBkg in bkgGrupList:
              try:
                yieldTemp += yields[ histKey ][ sampleBkg ] + zero
                errorTemp += errors[ histKey ][ sampleBkg ]**2
                errorTemp += ( modelingSys[ sampleBkg + "_" + tagMod ]*yields[ histKey ][ sampleBkg ] )**2
              except:
                print( "Missing {} for channel {}".format( sampleBkg, category ) )
                pass
            errorTemp += ( corrdSys * yieldTemp )**2
            if sample == "dataOverBkg":
              dataTemp = yields[ histKey ][ "data" ] + zero
              dataErrTemp = errors[ histKey ][ "data" ]**2
              errorTemp = ( ( dataTemp / yieldTemp )**2 )*( dataErrTemp / dataTemp**2 + errorTemp / yieldTemp**2 )
              yieldTemp = dataTemp / yieldTemp
          else:
            try:
              yieldTemp += yields[ histKey ][ sample ]
              errorTemp += errors[ histKey ][ sample ]**2
            except:
              print( "Missing {} for channel {}".format( sample, category ) )
              pass
            if sample not in sigList: errorTemp += ( modelingSys[ sample + "_" + tagMod ]*yieldTemp )**2
            errorTemp += ( corrdSys * yieldTemp )**2
          errorTemp = math.sqrt( errorTemp )
          if sample == "data": row.append( " & " + str( int( yields[ histKey ][ sample ] ) ) )
          else: row.append( " & " + str( np.around( yieldTemp, 5 ) ) + " $\pm$ " + str( np.around( yieldErrTemp, 2 ) ) )
        row.append( "\\\\" )
        table.append( row )
        
  if args.verbose: print( "Producing yields for PAS tables (e/m channels combined)..." )
  for HOT in nhottlist:
    table.append( [ "break" ] )
    table.append( [ "", "isL_{}_yields".format( HOT ) ] )
    table.append( [ "break" ] )
    table.append( [ "YIELDS" ] + [ category.replace( "isE", "isL" ) for category in categories if "isE" in cateogry and HOT in category ] + [ "\\\\" ] )
    for sample in bkgGrupList + [ "totBkg", "data", "dataOverBkg" ] + sig:
      row = [ sample ]
      for category in categories: 
        if not ( "isE" in category and HOT in category ): continue
        tagMod = category[ category.find( "nT" ):category.find( "nJ" )-3 ]
        histKey = "{}_{}_{}".format( variable, lumiStr, category )
        histKeyE = histKey 
        histKeyM = histKey.replace( "isE", "isM" )
        yieldTemp = 0.
        yieldTempE = 0.
        yieldTempM = 0.
        errorTemp = 0.
        if sample == "totBkg" or sample == "dataOverBkg":
          for sampleBkg in bkgGrupList:
            try:
              yieldTempE += yields[ histKeyE ][ sampleBkg ]
              yieldTempM += yields[ histkeyM ][ sampleBkg ]
              yieldTemp += yields[ histKeyE ][ sampleBkg ] + yields[ histKeyM ][ sampleBkg ] + zero
              errorTemp += errors[ histKeyE ][ sampleBkg ]**2 + errors[ histKeyM ][ sampleBkg ]**2
              errorTemp += ( modelingSys[ sampleBkg + "_" + tagMod ]*( yields[ histKeyE ][ sampleBkg ] + yields[ histKeyM ][ sampleBkg ] ) )**2
            except:
              print( "Missing {} for channel {}".format( sampleBkg, category ) )
              pass
          errorTemp += ( eSysTot * yieldTempE )**2 + ( mSysTot * yieldTempM )**2
          if sample == "dataOverBkg":
            dataTemp = yields[ histKeyE ][ "data" ] + yields[ histKeyM ][ "data" ] + zero
            dataErrTemp = errors[ histKeyE ][ "data" ]**2 + yields[ histKeyM ][ "data" ]**2
            errorTemp = ( ( dataTemp / yieldTemp )**2 )*( dataErrTemp / dataTemp**2 + errorTemp / yieldTemp**2 )
            yieldTemp = dataTemp / yieldTemp 
        else:
          try:
            yieldTempE += yields[ histKeyE ][ sample ]
            yieldTempM += yields[ histkeyM ][ sample ]
            yieldTemp += yields[ histKeyE ][ sample ] + yields[ histKeyM ][ sample ]
            errorTemp += errors[ histKeyE ][ sample ]**2 + errors[ histKeyM ][ sample ]**2
          except:
            print( "Missing {} for channel {}".format( sample, category ) )
            pass
          if sample not in sig: errorTemp += ( modelingSys[ sample + "_" + tagMod ] * yieldTemp )**2
          errorTemp += ( eSysTot*yieldTempE )**2 + ( mSysTot*yieldTempM)**2 
        errorTemp = math.sqrt( errorTemp )
        if sample == "data": row.append( " & " + str( int( yields[ histKeyE ][ sample ] + yields[ histKeyM ][ sample ] ) ) )
        else: row.append( " & " + str( np.around( yieldTemp, 5 ) ) + "$\pm$" + str( np.around( errorTemp, 2 ) ) )
      row.append( "\\\\" )
      table.append( row )
      
  if args.sys:
    table = systematics( table, yields, sig, bkg, hdamp, ue, hotPt, ht, categories )
  
  if args.CRsys: outFile = open( "{}/templates_{}/yields_CR_{}{}_{}.txt".format( dataset, dateTag, variable, tagBR, lumiStr ), "w" )
  else: outFile = open( "{}/templates_{}/yields_{}{}_{}.txt".format( dataset, dateTag, variable, tagBR, lumiStr ), "W" )
  print_table( table, outFile )
  outFile.close()
    
def modify_hists( dataHists, sigHists, bkgHists, lumiScale, rebin ):
  if args.verbose: print( "Modifying histograms by scaling, rebinning, and adjusting overflow/underflow bins" )
  if lumiScale != 1.:
    if args.verbose: print( "Scaling luminosity by a factor of {}".format( lumiScale ) )
    for key in bkgHists: bkgHists[key].Scale( lumiScale )
    for key in sigHists: sigHists[key].Scale( lumiScale )
    
  if rebin > 0:
    if args.verbose: print( "Rebinning histograms: merging {} bins...".format( rebin ) )
    for key in dataHists: dataHists[key] = dataHists[key].Rebin( rebin )
    for key in bkgHists:  bkgHists[key]  = bkgHists[key].Rebin(  rebin )
    for key in sigHists:  sigHists[key]  = sigHists[key].Rebin(  rebin )
    
  if args.verbose: print( "Correcting negative bins..." )
  for j, key in enumerate( list( bkgHists.keys() ) ):
    negative_bin_correction( bkgHists[ key ] )
  for j, key in enumerate( list( sigHists.keys() ) ):
    negative_bin_correction( sigHists[ key ] )
  
  if args.verbose: print( "Correcting overflow/underflow bins..." )
  for j, key in enumerate( list( dataHists.keys() ) ):
    overflow_bin_correction( dataHists[key] )
    underflow_bin_correction( dataHists[key] )
  for j, key in enumerate( list( bkgHists.keys() ) ):
    overflow_bin_correction( bkgHists[key] )
    underflow_bin_correction( dataHists[key] )
  for j, key in enumerate( list( sigHists.keys() ) ):
    overflow_bin_correction( sigHists[key] )
    underflow_bin_correction( sigHists[key] )
  
  return dataHists, sigHists, bkgHists  
  
def make_category_templates( dataHists, sigHists, bkgHists, data, sig, bkg, hdamp, ue, variable, categories ):
# this is called in main() 
  yields = {}
  errors = {}
  hists = {}
  
  for category in categories:
    histKey = "{}_{}_{}".format( variable, lumiStr, category )
    yields[ histKey ] = {}
    errors[ histKey ] = {}
    if args.sys:
      for sys in systList:
        for dir in [ "Up", "Down" ]:
          yields[ histKey + sys + dir ] = {}
      yields[ histKey + "hdUp" ] = {}
      yields[ histKey + "hdDown" ] = {}
      yields[ histKey + "ueUp" ] = {}
      yields[ histKey + "ueDown" ] = {}
  
  for i in range( len( varsList.branchRatio["BW"] ) ):
    tagBR = ""
    if args.BRscan: tagBR = "_bW{}_tZ{}_tH{}".format(
      str(varsList.branchRatio["BW"][i]).replace(".","p"),
      str(varsList.branchRatio["TZ"][i]).replace(".","p"),
      str(varsList.branchRatio["TH"][i]).replace(".","p")
    )
    for category in categories:
      hists = init_hists( variable, hists, dataHists, sigHists, bkgHists, data, sig, bkg, ue, hdamp, category, tagBR )
      
      for hist in hists: hists[hist].SetDirectory(0)
    
      #hists = scale_ttbb( hist, sig, bkg, hdamp, ue, variable, category, tagBR )
        
      if args.sys:
        yields = systematic_yield( hists, yields, variable, sig, bkg, hdamp, ue, hotPt, ht, category, tagBR )
      
      yields, errors = nominal_yield( hists, yields, errors, sig, bkg, variable, category, tagBR )
    
    hists = scale_xsec( hists, variable, sig, categories, tagBR )
    
    theta_template( hists, variable, allSamples, categories, tagBR )
    combine_template( hists, variable, allSamples, categories, tagBR )
    
    if args.summary: 
      yields = summary_template( yields, errors, categories, variable, tagBR )
    
    yield_tables( yields, errors, categories, variable, data, sig, bkg, tagBR )
      
    for key in hists.keys(): del hists[key]
    for key in data.keys(): del data[key]
    for key in sig.keys(): del sig[key]
    for key in bkg.keys(): del bkg[key]
      
def main( data, sig, bkg, hdamp, ue, ht, topPt, categories, variable ):
# hists from hists.py are stored with the keys "[variable]_[lumiStr]_[category]_[process][flv]"
# for the systematics: "[variable][sys][dir]_[lumiStr]_[catStr]_[process][flv]"
# for the pdf: "[variable]pdf[i]_[lumiStr]_[catStr]_[process][flv]"
  dataHists = {}
  bkgHists = {}
  sigHists = {}

  if args.variable != "":
    if args.verbose: print( "Making template for 1 variable: {}".format( args.variable ) )
    for category in categories:
      if os.path.exists( "{}/{}/data_{}.p".format( dataset, category, args.variable ) ):
        dataHists.update( pickle.load( open( "{}/{}/data_{}.p".format( dataset, category, args.variable ) ) ) )
      else:
        if args.verbose: print( "{}/{}/data_{}.p doesn't exist, skipping...".format( dataset, category, args.variable ) )
      if os.path.exists( "{}/{}/bkg_{}.p".format( dataset, category, args.variable ) ):
        bkgHists.update( pickle.load( open( "{}/{}/bkg_{}.p".format( dataset, category, args.variable ) ) ) )
      else:
        if args.verbose: print( "{}/{}/bkg_{}.p doesn't exist, skipping...".format( dataset, category, args.variable ) )
      if os.path.exists( "{}/{}/sig_{}.p".format( dataset, category, args.variable ) ):
        sigHists.update( pickle.load( open( "{}/{}/sig_{}.p".format( dataset, category, args.variable ) ) ) )
      else: 
        if args.verbose: print( "{}/{}/sig_{}.p doesn't exist, skipping...".format( dataset, category, args.variable ) )    

    dataHists, sigHists, bkgHists = modify_hists( dataHists, sigHists, bkgHists, float(args.lumiscale), int(args.rebin) )
    
    make_category_templates( dataHists, sigHists, bkgHists, data, sig, bkg, hdamp, ue, args.variable, categories )
  
  else:
    varList = [ x.replace( "bkg_hists_", "" )[:-2] for x in os.listdir( "{}/{}/".format( dataset, categories[0] ) ) if "bkg_hists_" in x and ".p" in x ]
    if args.verbose: print( "Making templates for {} variables".format( len(varList) ) )
    for variable in varList:
      for category in categories:
        if os.path.exists( "{}/{}/data_{}.p".format( dataset, category, args.variable ) ):
          dataHists.update( pickle.load( open( "{}/{}/data_{}.p".format( dataset, category, variable ) ) ) )
        if os.path.exists( "{}/{}/bkg_{}.p".format( dataset, category, args.variable ) ):
          bkgHists.update( pickle.load( open( "{}/{}/bkg_{}.p".format( dataset, category, variable ) ) ) )
        if os.path.exists( "{}/{}/sig_{}.p".format( dataset, category, args.variable ) ):
          sigHists.update( pickle.load( open( "{}/{}/sig_{}.p".format( dataset, category, variable ) ) ) )
    
      dataHists, sigHists, bkgHists = modify_hists( dataHists, sigHists, bkgHists, float(args.lumiscale), int(args.rebin) )
      
      make_category_templates( dataHists, sigHists, bkgHists, data, sig, bkg, hdamp, ue, args.variable, categories )
  
  if args.verbose: print( "Finished creating templates in {:.2f} minutes".format( ( tStart - time.time() ) / 60. ) )
  
main( data, sig, bkg, categories, variables )


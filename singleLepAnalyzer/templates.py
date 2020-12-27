#!/usr/bin/python

import os, sys, json, time, math, datetime, pickle, itertools
from argparse import ArgumentParser
from ROOT import gROOT, TFile, TH1F
import numpy as np
from array import array
import varsList

gROOT.SetBatch(1)

parser = ArgumentParser()
parser.add_argument( "-y", "--year",   required = True )
parser.add_argument( "-j", "--config", required = True )
args = parser.parse_args()

with open( args.config, "r" ) as file:
  jsonFile = json.load( file )
  
all_samples = varsList.all_samples[ args.year ]
weights = varsList.weights [ args.year ]

configuration = jsonFile[ "CONFIGURATION" ]
step2_configuration = jsonFile[ "STEP 2" ][ "CONFIGURATION" ]

do_systematics = configuration[ "USE_SYSTEMATICS" ]
systematics_list = configuration[ "SYSTEMATICS" ]
do_test = configuration[ "UNIT_TEST" ]
do_pdf = configuration[ "USE_PDF" ]

do_summary = step2_configuration[ "SUMMARY" ]                 # bool
do_scale_to_1_pb = step2_configuration[ "SCALE_TO_1_PB" ]     # not implemented
do_cr_systematic = step2_configuration[ "CR_SYS" ]            # not implemented
do_normalize_pdf = step2_configuration[ "NORMALIZE_PDF" ]     # bool
do_an = step2_configuration[ "AN" ]                           # bool
do_pas = step2_configuration[ "PAS" ]                         # bool
do_br_scan = step2_configuration[ "BR_SCAN" ]                 # not implemented
rebin = step2_configuration[ "REBIN" ]                        # int
lumiscale = step2_configuration[ "LUMISCALE" ]                # float

zero = step2_configuration[ "ZERO" ]                          # float
remove_threshold = step2_configuration[ "REMOVE_THRESHOLD" ]  # float
ttHFsf = step2_configuration[ "ttHFsf" ]                      # float
ttLFsf = step2_configuration[ "ttLFsf" ]                      # float

categories = jsonFile[ "CATEGORIES" ][ "FULL" ] if not do_test else jsonFile[ "CATEGORIES" ][ "TEST" ]
category_list = [
  "is{}_nhot{}_nt{}_nw{}_nb{}_nj{}".format( cat[0], cat[1], cat[2], cat[3], cat[4], cat[5] ) for cat in list( itertools.product(
    categories[ "LEP" ], categories[ "NHOT" ], categories[ "NTOP" ], categories[ "NW" ], categories[ "NBOT" ], categories[ "NJET" ] ) )  
]

variables = configuration[ args.year ][ "INPUTS" ]

lumiStr = str( varsList.targetLumi / 1000. ).replace( ".", "p" ) + "fb" 
uncertainties = varsList.uncertainties

def group_process(): # done
# each ROOT sample can be categorized into a collective group of samples based on shared features
# the groups are evaluated separately 
  groups = { "BKG": {}, "SIG": {}, "DAT": {} }
  
  # specify the individual data process(es)
  groups[ "DAT" ][ "PROCESS" ] = [ "DataE", "DataM" ]
  
  # specify the individual signal process(es)
  groups[ "SIG" ][ "PROCESS" ] = [ "tttt" ]
  
  # specify the individual background processes
  with [ "TTJetsHad", "TTJets2L2nu", "TTJetsSemiLepNjet9bin", "TTJetsSemiLepNjet0", "TTJetsSemiLepNjet9" ] as tt_list:
    # corresponds to bkgProcList
    groups[ "BKG" ][ "PROCESS" ] = { 
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
    groups[ "BKG" ][ "PROCESS" ][ "WJets" ] += [ "WJetsMG1200" + str(i) for i in [1,2,3] ] if args.year == "2017" else [ "WJetsMG1200" ]
    groups[ "BKG" ][ "PROCESS" ][ "WJets" ] += [ "WJetsMG2500" + str(i) for i in [2,3,4] ] if args.year == "2017" else [ "WJetsMG2500" ]
    if args.year == "2017": groups[ "BKG" ][ "PROCESS" ][ "T" ] += [ "Tbs" ]
    
  # specify the grouped background processes
  with groups[ "BKG" ][ "PROCESS" ] as process:
    # corresponds to bkgGrupList
    groups[ "BKG" ][ "GROUP" ] = {
      "ttnobb": process[ "ttjj" ] + process[ "ttcc" ] + process[ "tt1b" ] + process[ "tt2b" ],
      "ttbb": process[ "ttbb" ],
      "top": process[ "T" ] + process[ "TTV" ] + process[ "TTXY" ],
      "ewk": process[ "WJets" ] + process[ "ZJets" ] + process[ "VV" ],
      "qcd": process[ "qcd" ]
    }
    # corresponds to ttbarGruplist
    groups[ "BKG" ][ "TTBAR_GROUPS" ] = { tt: groups[ "BKG" ][ "GROUP" ][ tt ] for tt in [ "ttnobb", "ttbb" ] }
    # corresponds to ttbarProcList
    groups[ "BKG" ][ "TTBAR_PROCESS" ] = { tt: process[ tt ] for tt in [ "ttjj", "ttcc", "ttbb", "tt1b", "tt2b" ] }
    
  # specify the systematics
  groups[ "BKG" ][ "SYSTEMATICS" ] = {}
  with { "hd": "HDAMP", "ue": "UE" } as syst_key: 
    for syst in [ "hd", "ue" ]:
      for dir in [ "up", "dn" ]:
        for flavor in [ "jj", "cc", "bb", "1b", "2b" ]:
          groups[ "BKG" ][ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ] = [
            "TTJetsHad{}{}TT{}".format( syst_key[ syst ], dir, flavor ),
            "TTJets2L2nu{}{}TT{}".format( syst_key[ syst ], dir, flavor ),
            "TTJetsSemiLep{}{}TT{}".format( syst_key[ syst ], dir, flavor )
          ]
        groups[ "BKG" ][ "SYSTEMATICS" ][ "ttbj_" + syst + dir ] = []
        groups[ "BKG" ][ "SYSTEMATICS" ][ "ttnobb_" + syst + dir ] = []
        for flavor in [ "1b", "2b" ]:
          groups[ "BKG" ][ "SYSTEMATICS" ][ "ttbj_" + syst + dir ] += groups[ "BKG" ][ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ]
        for flavor in [ "jj", "cc", "1b", "2b" ]:
          groups[ "BKG" ][ "SYSTEMATICS" ][ "ttnobb_" + syst + dir ] += groups[ "BKG" ][ "SYSTEMATICS" ][ "tt{}_{}{}".format( flavor, syst, dir ) ] 

  # specify the ht processes
  groups[ "BKG" ][ "HT" ] = { # corresponds to htProcs
    "ewk": groups[ "BKG" ][ "GROUP" ][ "ewk" ],
    "WJets": groups[ "BKG" ][ "PROCESS" ][ "WJets" ],
    "qcd": groups[ "BKG" ][ "GROUP" ][ "qcd" ]
  }

  # specify the toppt processes
  groups[ "BKG" ][ "TOPPT" ] = { # corresponds to topptProcs
    "ttbj": groups[ "BKG" ][ "PROCESS" ][ "tt1b" ] + groups[ "BKG" ][ "PROCESS" ][ "tt2b" ],
    "ttnobb": groups[ "BKG" ][ "GROUP" ][ "ttnobb" ],
    tt: groups[ "BKG" ][ "PROCESS" ][ tt ] for tt in [ "ttjj", "ttcc", "ttbb", "tt1b", "tt2b", "ttbj", "ttnobb" ]
  }
  
  return groups

def load_histograms( variable ): # done
  hists = {
    "DAT": {},
    "BKG": {},
    "SIG": {},
    "CMB": {}
  }
  
  for category in category_list:
    with os.path.join( varsList.step3DirEOS[ args.year ], configuration[ "STEP 1" ][ "EOSFOLDER" ], category ) as path:
      hists[ "DAT" ].update( pickle.load( open( os.path.join( path, "data_{}.pkl".format( variable ) ), "rb" ) ) )
      hists[ "BKG" ].update( pickle.load( open( os.path.join( path, "bkg_{}.pkl".format( variable ) ),  "rb" ) ) )
      hists[ "SIG" ].update( pickle.load( open( os.path.join( path, "sig_{}.pkl".format( variable ) ),  "rb" ) ) )

  return hists
  
def correct_histograms( hists ): # done
  def scale_luminosity( hists ):
    print( ">> Re-scaling the luminosity by a factor {}".format( lumiscale ) )
    for key in hists[ "BKG" ].keys(): hists[ "BKG" ][ key ].Scale( lumiscale )
    for key in hists[ "SIG" ].keys(): hists[ "SIG" ][ key ].Scale( lumiscale )
    return hists
    
  def rebinning( hists ):
    print( ">> Re-binning the histograms by {} bins".format( rebin ) )
    for key in hists[ "DATA" ].keys(): hists[ "DATA" ][ key ].Rebin( rebin )
    for key in hists[ "BKG" ].keys(): hists[ "BKG" ][ key ].Rebin( rebin )
    for key in hists[ "SIG" ].keys(): hists[ "SIG" ][ key ].Rebin( rebin )
    return hists
    
  def negative_correction( hists ):
    def function( hist ):
      norm = hist.Integral()
      for i in range( hist.GetNbinsX() + 2 ):
        if hist.GetBinContent( i ) < 0:
          hist.SetBinContent( i, 0 )
          hist.SetBinError( i, 0 )
      if hist.Integral() != 0 and norm > 0: hist.Scale( norm / hist.Integral() )
      return hist
      
    print( ">> Correcting negative bins" )
    for key in hists[ "BKG" ].keys(): hists[ "BKG" ][ key ] = function( hists[ "BKG" ][ key ] )
    for key in hists[ "SIG" ].keys(): hists[ "SIG" ][ key ] = function( hists[ "SIG" ][ key ] )
    return hists
    
  def bin_correction( hists ):
    def function( hist ):
      # overflow
      with hist.GetXaxis().GetNbins() as n:
        content = hist.GetBinContent( n ) + hist.GetBinContent( n + 1 )
        error = math.sqrt( hist.GetBinError( n )**2 + hist.GetBinError( n + 1 )**2 )
        hist.SetBinContent( n, content )
        hist.SetBinError( n, error )
        hist.SetBinContent( n + 1, 0 )
        hist.SetBinError( n + 1, 0 )
      # underflow
      content = hist.GetBinContent( 1 ) + hist.GetBinContent( 0 )
      error = math.sqrt( hist.GetBinError( 1 )**2 + hist.GetBinError( 0 )**2 )
      hist.SetBinContent( 1, content )
      hist.SetBinError( 1, error )
      hist.SetBinContent( 0, 0 )
      hist.SetBinError( 0, 0 )
      return hist
    
    print( ">> Correcting over/under-flow bins" )
    for key in hists[ "DATA" ].keys(): hists[ "DATA" ][ key ] = function( hists[ "DATA" ][ key ] )
    for key in hists[ "BKG" ].keys():  hists[ "BKG" ][ key ]  = function( hists[ "BKG" ][ key ] )
    for key in hists[ "SIG" ].keys():  hists[ "SIG" ][ key ]  = function( hists[ "SIG" ][ key ] )
    return hists
    
  if lumiscale != 1.: hists = scale_luminosity( hists )
  if rebin > 0:       hists = rebinning( hists )
  hists = negative_correction( hists )
  hists = bin_correction( hists )

  return data_hists, bkg_hists, sig_hist
  
def consolidate_histograms( hists, variable ): # done
  def scale_ttbb( hists ):
    print( ">> Scaling tt+bb by a factor of {}".format( ttHFsf ) )
    for category in category_list:
      N = { 
        "ttbb": hists[ "CMB" ][ "ttbb" + category ].Integral(),
        "ttnobb": hists[ "CMB" ][ "ttnobb" + category ].Integral()
      }
      
      if ttLFsf == -1:
        try:
          ttLFsf = 1. + ( 1. - ttHFsf ) * ( N[ "ttbb" ] / N[ "ttnobb" ] )
        except ZeroDivisionError:
          ttLFsf = 1.
          
      hists[ "CMB" ][ "ttbb" + category ].Scale( ttHFsf )
      hists[ "CMB" ][ "ttnobb" + category ].Scale( ttLFsf )
      
      if do_systematics:
        for syst in systematics_list + [ "hd", "ue" ]:
          for dir in [ "Up", "Down" ]:
            hists[ "CMB" ][ "ttbb" + category + syst + dir ].Scale( ttHFsf )
            hists[ "CMB" ][ "ttnobb" + category + syst + dir ].Scale( ttLFsf )
            
      if do_pdf:
        for i in range(100):
          hists[ "CMB" ][ "ttbb" + category + "pdf{}".format( i ) ].Scale( ttHFsf )
          hists[ "CMB" ][ "ttnobb" + category + "pdf{}".format( i ) ].Scale( ttLFsf )
    
    return hists

  def set_zero( hists ):
    print( ">> Adjusting 0 values to be non-trivial ({}) in histograms".format( remove_threshold ) )
    for category in category_list:
      background_total = sum( [ hists[ "CMB" ][ group + category ].Integral() for group in groups[ "BKG" ][ "GROUP" ] ] )
      for process in list( groups[ "BKG" ][ "GROUP" ].keys() ) + groups[ "SIG" ][ "PROCESS" ]:
        if do_systematics:
          for syst in systematics_list:
            for dir in [ "Up", "Down" ]:
              if hists[ process + category + syst + dir ].Integral() == 0: hists[ process + category + syst + dir ].SetBinContent( 1, zero )
        
    return hists
  
  # might add scale signal to 1 pb at some point
  
  for category in category_list:
    with "{}_{}_{}_".format( variable, lumiStr, category ) as key:
      # group the data processes
      hists[ "CMB" ][ "DATA" + category ] = hists[ "DAT" ][ key + groups[ "DAT" ][ "PROCESS" ][0] ].Clone( key + "_DATA" )
      for process in groups[ "DAT" ][ "PROCESS" ][1:]: hists[ "CMB" ][ "DATA" + category ].Add( hists[ "DAT" ][ key + process ] )
      
      # group the signal processes
      hists[ "CMB" ][ "tttt" + category ] = hists[ "SIG" ][ key + groups[ "SIG" ][ "PROCESS" ][0] ].Clone( key + "_sig" )
      
      # group the background processes
      for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ):
        hists[ "CMB" ][ process + category ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "PROCESS" ][ process ][0] ].Clone( key + "_" + process )
        for sample in groups[ "BKG" ][ "PROCESS" ][ process ][1:]: hists[ "CMB" ][ process + category ].Add( hists[ "BKG" ][ key + sample ] )
        
      for group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
        hists[ "CMB" ][ group + category ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "GROUP" ][ group ][0] ].Clone( key + "_" + group )
        for sample in groups[ "BKG" ][ "GROUP" ][ group ][1:]: hists[ "CMB" ][ group + category ]
        
    if do_systematics:
      dir_key = { "Up": "plus", "Down": "minus" }
      for syst in systematics_list:
        for dir in [ "Up", "Down" ]:
          with "{}_{}_{}_".format( variable + syst + dir, lumiStr, category ) as key:
            hists[ "CMB" ][ "SIGNAL" + category + syst + dir ] = hists[ "SIG" ][ key + groups[ "SIG" ][ "PROCESS" ][0] ].Clone( "{}_sig__{}__{}".format( key, syst, dir_key[dir] ) )
            
            for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ):
              hists[ "CMB" ][ process + category + syst + dir ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "PROCESS" ][ process ][0] ].Clone( "{}_{}__{}__{}".format( key, process, syst, dir_key[dir] ) )
              for sample in hists[ "BKG" ][ "PROCESS" ][ process ][1:]: hists[ "CMB" ][ process + category + syst + dir ].Add( hists[ "BKG" ][ key + sample ] )
            
            for group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
              hists[ "CMB" ][ group + category + syst + dir ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "GROUP" ][ group ][0] ].Clone( "{}_{}__{}__{}".format( key, group, syst, dir_key[dir] ) )
              
      syst_key = { "hdup": "__hdamp__plus", "hddn": "__hdamp__minus", "ueup": "__ue__plus", "uedn": "__ue__minus" }
      for process in list( groups[ "BKG" ][ "SYSTEMATICS" ].keys() ):
        syst = process.split( "_" )[-1]
        hists[ "CMB" ][ process + category ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "SYSTEMATICS" ][ process ][0] ].Clone( "{}_{}".format( key, process, syst_key[syst] ) )
        for sample in groups[ "BKG" ][ "SYSTEMATICS" ][ process ][1:]: hists[ "CMB" ][ process + category ].Add( hists[ "BKG" ][ key + sample ] )

    if do_pdf:
      for i in range(100):
        with "{}pdf{}_{}_{}".format( variable, i, lumiStr, category ) as key:
          for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ):
            hists[ "CMB" ][ process + category + "pdf{}".format( i ) ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "PROCESS" ][ process ][0] ].Clone( "{}_{}__pdf{}".format( key, process, i ) )
            for sample in groups[ "BKG" ][ "PROCESS" ][ process ][1:]: hists[ "CMB" ][ process + category + "pdf{}".format( i ) ].Add( hists[ "BKG" ][ key + sample ] )
          
          for group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
            hists[ "CMB" ][ group + category + "pdf{}".format( i ) ] = hists[ "BKG" ][ key + groups[ "BKG" ][ "GROUP" ][ group ][0] ].Clone( "{}_{}__pdf{}".format( key, group, i ) )
            for sample in groups[ "BKG" ][ "GROUP" ][ group ][1:]: hists[ "CMB" ][ group + category + "pdf{}".format( i ) ].Add( hists[ "BKG" ][ key + sample ] )
            
          hists[ "CMB" ][ "SIGNAL" + category + "pdf{}".format( i ) ] = hists[ "SIG" ][ key + groups[ "SIG" ][ "PROCESS" ][0] ].Clone( "{}_{}__pdf{}".format( key, process, i ) )
    
  for key in hists[ "CMB" ].keys(): hists[ "CMB" ][ key ].SetDirectory(0)  
  
  if ttHFsf != 1 and "ttbb" in list( groups[ "BKG" ][ "TTBAR_GROUPS" ].keys() ): hists = scale_ttbb( hists )
  hists = set_zero( hists )

  return hists
  
def make_tables( hists, variable ): # done
  def initialize():
    print( ">> Initializing yield and statistical error tables" )
    tables = { "YIELD": {}, "ERROR": {} }
    for category in category_list:
      with "{}_{}_{}".format( variable, lumiStr, category ) as key:
        tables[ "YIELD" ][ key ] = {}
        tables[ "ERROR" ][ key ] = {}
        if do_systematics:
          for syst in systematics_list:
            for dir in [ "Up", "Down" ]:
              tables[ "YIELD" ][ key + syst + dir ] = {}
          for syst in [ "hd", "ue" ]:
            for dir in [ "Up", "Down" ]:
              tables[ "YIELD" ][ key + syst + dir ] = {}
           
        tables[ "ERROR" ][ key ][ "tttt" ] = 0.
        tables[ "ERROR" ][ key ][ "DATA" ] = 0.
        for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ): tables[ "ERROR" ][ key ][ process ] = 0.
        for group in list( groups[ "BKG" ][ "GROUP" ].keys() ): tables[ "ERROR" ][ key ][ group ] = 0.
        tables[ "ERROR" ][ key ][ "TOTBKG" ] = 0.
        tables[ "ERROR" ][ key ][ "DATAOVERBKG" ] = 0.
              
    return tables

  def table_systematics( tables, category ):
    print( ">> Scaling shape systematics by one sigma" )
    with "{}_{}_{}".format( variable, lumiStr, cateogry ) as key:
      for syst in systematics_list + [ "ue", "hd" ]:
        for dir in [ "Up", "Down" ]:
          for process in groups[ "SIG" ][ "PROCESS" ]:
            tables[ "YIELD" ][ key + syst + dir ][ process ] = hists[ "CMB" ][ process + category + syst + dir ].Integral()
          for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ):
            tables[ "YIELD" ][ key + syst + dir ][ process ] = hists[ "CMB" ][ process + category + syst + dir ].Integral()
          for group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
            tables[ "YIELD" ][ key + syst + dir ][ group ] = hists[ "CMB" ][ group + category + syst + dir ].Integral()
            
    return tables
  
  tables = initialize()
  
  for category in category_list:
    with "{}_{}_{}".format( variable, lumiStr, category ) as key:
      for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ): tables[ "YIELD" ][ key ][ process ] = hists[ "CMB" ][ process + category ].Integral()
      for group in list( groups[ "BKG" ][ "GROUP" ].keys() ): tables[ "YIELD" ][ key ][ group ] = hists[ "CMB" ][ group + category ].Integral()
      tables[ "YIELD" ][ key ][ "DATA" ] = hists[ "CMB" ][ "DATA" + category ].Integral()
      tables[ "YIELD" ][ key ][ "tttt" ] = hists[ "CMB" ][ "tttt" + category ].Integral()
      
      tables[ "YIELD" ][ key ][ "TOTBKG" ] = sum( [ hists[ "CMB" ][ group + category ].Integral() for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) ] )
      tables[ "YIELD" ][ key ][ "DATAOVERBKG" ] = tables[ "YIELD" ][ key ][ "DATA" ] / ( tables[ "YIELD" ][ key ][ "TOTBKG" ] + zero )
      
      for i in range( 1, hists[ "CMB" ][ groups[ "BKG" ][ "GROUP" ][0] + category ].GetXaxis().GetNbins() + 1 ):
        for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ): tables[ "ERROR" ][ key ][ process ] += hists[ process + category ].GetBinError( i )**2
        for group in list( groups[ "BKG" ][ "GROUP" ].keys() ): tables[ "ERROR" ][ key ][ group ] += hists[ group + category ].GetBinError( i )**2
        tables[ "ERROR" ][ key ][ "tttt" ] += hists[ "tttt" + category ].GetBinError( i )**2
        tables[ "ERROR" ][ key ][ "DATA" ] += hists[ "DATA" + category ].GetBinError( i )**2
        tables[ "ERROR" ][ key ][ "TOTBKG" ] += sum( [ hists[ process + category ].GetBinError( i )**2 for process in list( groups[ "BKG" ][ "GROUP" ].keys() ) ] )
      
      for hist_key in tables[ "ERROR" ][ key ].keys(): tables[ "ERROR" ][ key ][ hist_key ] = math.sqrt( tables[ "ERROR" ][ key ][ hist_key ] )
    if do_systematics: tables = table_systematics( tables, category )
    
  return tables
  
def theta_templates( hists ): # done
  print( ">> Writing Theta templates" )
  theta_name = "theta_{}_{}_{}.root".format( variable, groups[ "SIG" ][ "PROCESS" ][0], lumiStr )
  theta_file = TFile( theta_name, "RECREATE" )
  for category in category_list:
    hists[ "DATA" + category ].Write()
    with sum( [ hists[ "CMB" ][ group + category ].Integral() for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) as total:
      for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "tttt" ]:
        if hists[ "CMB" ][ group + category ].Integral() / total <= remove_threshold:
          print( ">> Process {} in category {} beneath threshold ({:.3f}), skipping".format( hists[ "CMB" ][ group + category ].Integral() / total ) )
          continue
        hists[ "CMB" ][ group + category ].Write()
        
        if do_systematics:
          for syst in systematics_list + [ "hd", "ue" ]:
            for dir in [ "Up", "Down" ]:
              if hists[ "CMB" ][ group + category + syst + dir ].Write()
              
        if do_pdf:
          for i in range(100): hists[ "CMB" ][ group + category + "pdf{}".format( i ) ].Write()
  theta_file.Close()
  print( "[OK ] Finished writing Theta template" )

def combine_templates( hists ): # done
  print( ">> Writing Combine templates" )
  combine_name = "combine_{}_{}.root".format( variable, lumiStr )
  combine_file = TFile( combine_name, "RECREATE" )
  for category in category_list:
    hists[ "CMB" ][ "DATA" + category ].SetName( hists[ "CMB" ][ "DATA" + category ].GetName().replace( "DATA", "data_obs" ) )
    hists[ "CMB" ][ "DATA" + category ].Write()
  
    with groups[ "SIG" ][ "PROCESS" ][0] as signal:
      hists[ "CMB" ][ signal + category ].SetName( hists[ "CMB" ][ signal + category ].GetName().replace( "SIG", signal )
      hists[ "CMB" ][ signal + category ].Clone()
      
      if do_systematics:
        dir_key = [ "Up": "__plus", "Down": "__minus" ]
        for syst in systematics_list:
          for dir in [ "Up", "Down" ]:
            hists[ "CMB" ][ signal + category + syst + dir ].SetName( hists[ "CMB" ][ signal + category + syst + dir ].GetName().replace( "SIG", signal ).replace( dir_key[ dir ], dir ) )
            hists[ "CMB" ][ signal + category + syst + dir ].Write()
      if do_pdf:
        for i in range(100):
          hists[ "CMB" ][ signal + category + syst + dir ].SetName( hists[ "CMB" ][ signal + category + syst + dir ].GetName().replace( "SIG", signal ).replace( "SIG", signal ) )
          hists[ "CMB" ][ signal + category + syst + dir ].Write()
    
    with sum( [ hists[ "CMB" ][ group + category ].Integral() for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) as total:
      for group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
        if hists[ "CMB" ][ group + category ].Integral() / total <= remove_threshold:
          print( ">> Process {} in category {} beneath threshold ({:.3f}), skipping".format( hists[ "CMB" ][ group + category ].Integral() / total )
          continue
        hists[ "CMB" ][ group + category ].SetName( hists[ "CMB" ][ group + category ].GetName() )
        hists[ "CMB" ][ group + category ].Write()
        
        if do_systematics:
          dir_key = [ "Up": "__plus", "Down": "__minus" ]
          for syst in systematics_list + [ "hd", "ue" ]:
            for dir in [ "Up", "Down" ]:
              hists[ "CMB" ][ group + category + syst + dir ].SetName( hists[ "CMB" ][ group + category + syst + dir ].GetName().replace( dir_key[ dir ], dir ) )
              hists[ "CMB" ][ group + category + syst + dir ].Write()
        
        if do_pdf:
          for i in range(100):
            hists[ "CMB" ][ group + category + "pdf{}".format( i ) ].SetName( hists[ "CMB" ][ group + category + "pdf{}".format( i ) ].GetName() )
            hists[ "CMB" ][ group + category + "pdf{}".format( i ) ].Write()
        
  combine_file.Close()
  print( "[OK ] Finished writing Combine template" )
  
def summary_templates( hists ): # done
  print( ">> Writing summary templates" )
  yield_name = "yield_{}_{}_{}".format( variable, groups[ "SIG" ][ "PROCESS" ][0], lumiStr )
  yield_file = TFile( yield_name, "RECREATE" )
  for lep in [ "E", "M" ]:
    for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "DATA", groups[ "SIG" ][ "PROCESS" ][0] ]:
      with len( category_list ) / 2 as tag_length:
        hists[ "YIELD" ] = {}
        hists[ "YIELD" ][ lep + group ] = TH1F( "yield_{}_is{}_{}".format( lumiStr, lep, process ), "", tag_length, 0, tag_length )
        if do_systematics and group not "DATA":
          for syst in systematics_list + [ "hd", "ue" ]:
            for dir in [ "Up", "Down" ]:
              hists[ "YIELD" ][ lep + group + syst + dir ] = TH1F( "yield_{}_is{}_{}_{}{}".format( lumiStr, lep, process, syst, dir ), "", tag_length, 0, tag_length )
  
      for i, category in enumerate( category_list ):
        if lep not in category: continue
        tag_splits = category.split( "_" )
        nhot = tag_splits[1][4:]
        nt = tag_splits[2][2:]
        nw = tag_splits[3][2:]
        nb = tag_splits[4][2:]
        nj = tag_splits[5][2:]
        bin_label = ""
        if nhot != "0p":
          if "p" in nhot: bin_label += "#geq{}res-t/".format( nhot[:-1] )
          else: bin_label += "{}res-t/".format( nhot )
        if nt != "0p":
          if "p" in nt: bin_label += "#geq{}t/".format( nt[:-1] )
          else: bin_label += "{}t/".format( nt )
        if nw != "0p":
          if "p" in nw: bin_label += "#geq{}W/".format( nw[:-1] )
          else: bin_label += "{}W/".format( nw )
        if nb != "0p":
          if "p" in nb: bin_label += "#geq{}b/".format( nb[:-1] )
          else: bin_label += "{}b/".format( nb )
        if nj != "0p":
          if "p" in nj: bin_label += "#geq{}j/".format( nj[:-1] )
          else: bin_label += "{}j/".format( nj )
        if bin_label.endswith( "/" ): bin_label = bin_label[:-1]
        with "{}_{}_{}".format( variable, lumiStr, category ) as key:
          hists[ "YIELD" ][ lep + group ].SetBinContent( i + 1, tables[ "YIELD" ][ key ][ group ] )
          hists[ "YIELD" ][ lep + group ].SetBinError( i + 1, tables[ "ERROR" ][ key ][ group ] )
          hists[ "YIELD" ][ lep + group ].GetXaxis().SetBinLabel( i + 1, bin_label )
          if do_systematics and group not "DATA":
            for syst in systematics_list + [ "hd", "ue" ]:
              for dir in [ "Up", "Down" ]:
                hists[ "YIELD" ][ lep + group + syst + dir ].SetBinContent( i + 1, tables[ "YIELD" ][ key + syst + dir ][ group ] )
                hists[ "YIELD" ][ lep + group + syst + dir ].GetXaxis().SetBinLabel( i + 1, bin_label )
        
      hists[ "YIELD" ][ lep + group ].Write()
      if do_systematics and group not "data":
        for syst in systematics_list + [ "hd", "ue" ]:
          for dir in [ "Up", "Down" ]:
            hists[ "YIELD" ][ lep + group + syst + dir ].Write()
      
  yield_file.Close()  
  
def print_tables( tables, variable ):
  def nominal_table( tables ):
    print( ">> Adding yields without background grouping" )
    tables[ "PRINT" ].append( [ "YIELDS" ] + [ process for process in list( groups[ "BKG" ][ "PROCESS"].keys() ) + [ "DATA" ] ] )
    for category in category_list:
      this_entry = [ category ]
      with "{}_{}_{}".format( variable, lumiStr, category ) as key:
        for process in list( groups[ "BKG" ][ "PROCESS" ].keys() ) + [ "DATA" ]:
          this_entry.append( str( tables[ "YIELD" ][ key ][ process ] ) + " $\pm$" + str( tables[ "ERROR" ][ key ][ process ] ) )
      tables[ "PRINT" ].append( this_entry )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    
    print( ">> Adding yields with top, ewk, qcd grouping" )
    tables[ "PRINT" ].append( [ "YIELDS" ] + [ group for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "DATA" ] ] )
    for category in category_list:
      this_entry = [ category ]
      with "{}_{}_{}".format( variable, lumiStr, category ) as key:
        for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "DATA" ]:
          this_entry.append( str( tables[ "YIELD" ][ key ][ group ] ) + " $\pm$" + str( tables[ "ERROR" ][ key ][ group ] ) )
      tables[ "PRINT" ].append( this_entry )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    
    print( ">> Adding yields for signals" )
    tables[ "PRINT" ].append( [ "YIELDS" ] + [ process for process in groups[ "SIG" ][ "PROCESS" ] ] )
    for category in category_list:
      this_entry = [ category ]
      with "{}_{}_{}".format( variable, lumiStr, category ) as key:
        for process in groups[ "SIG" ][ "PROCESS" ]:
          this_entry.append( str( tables[ "YIELD" ][ key ][ process ] ) + " $\pm$" + str( tables[ "ERROR" ][ key ][ group ] ) )
      tables[ "PRINT" ].append( this_entry )
    
    return tables
    
  def an_table( tables ):
    print( ">> Adding yields in electron/muon channels" )
    lep_key = { "E": "ELECTRON", "M": "MUON" }
    for lep in [ "E", "M" ]:
      uncertainties[ lep_key[ lep ] ][ "TOTAL" ][ args.year ]
      for nhot in categories[ "NHOT" ]:
        tables[ "PRINT" ].append( [ "BREAK" ] )
        tables[ "PRINT" ].append( [ "","is{}_{}_yields".format( lep, nhot ) ] )
        tables[ "PRINT" ].append( [ "BREAK" ] )
        tables[ "PRINT" ].append( [ "YIELDS" ] + [ category in category_list if "is{}".format( lep ) in category and "nhot{}".format( nhot ) in category ] )
        for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "DATA", "TOTBKG", "DATAOVERBKG" ] + groups[ "SIG" ][ "PROCESS" ]:
          this_entry = [ group ]
          for category in category_list:
            if not ( "is{}".format( lep ) in category and "nhot{}".format( nhot ) in category ): continue
            sub_category = category[ category.find( "nt" ): category.find( "nj" ) - 3 ]
            with "{}_{}_{}".format( variable, lumiStr, category ) as key:
              this_yield = { "BKG": 0., "DATA": 0., "RATIO": 0., "TOT": 0. }
              this_error = { "BKG": 0., "DATA": 0., "RATIO": 0., "TOT": 0. }
              if group == "TOTBKG" or group == "DATAOVERBKG":
                for sub_group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
                  try:
                    this_yield[ "BKG" ] += tables[ "YIELD" ][ key ][ sub_group ] + zero
                    this_error[ "BKG" ] += tables[ "YIELD" ][ key ][ sub_group ]**2
                  except:
                    print( "[WARN] missing {} for category {}".format( sub_group, category ) )
                    pass
                
                  if group == "DATAOVERBKG":
                    this_yield[ "DATA" ] = tables[ "YIELD" ][ key ][ "DATA" ] + zero
                    this_error[ "DATA" ] = tables[ "ERROR" ][ key ][ "DATA" ]**2
                    this_yield[ "RATIO" ] = this_yield[ "DATA" ] / this_yield[ "BKG" ]
                    this_error[ "RATIO" ] = ( this_yield[ "RATIO" ]**2 ) * ( ( this_error[ "DATA" ] / this_yield[ "DATA" ]**2 ) + ( this_error[ "BKG" ] / this_yield[ "BKG" ]**2 ) )
              else:
                try:
                  this_yield[ "TOTAL" ] += tables[ "YIELD" ][ key ][ group ]
                  this_error[ "TOTAL" ] += tables[ "ERROR" ][ key ][ group ]**2
                except:
                  print( "[WARN] missing {} for channel {}".format( sub_group, category ) )
                  pass
                
                this_error[ "TOTAL" ] += ( uncertainties[ lep_key[ lep ] ][ "TOTAL" ][ args.year ] * this_yield[ "TOTAL" ] )**2
              
            for key in this_error.keys(): this_error[ key ] = math.sqrt( this_error[ key ] )
            
            if group == "DATA":
              this_entry.append( " & " + str( int( tables[ "YIELD" ][ key ][ group ] ) ) )
            else:
              if group == "DATAOVERBKG":
                this_entry.append( " & " + str( round_sig( this_yield[ "RATIO" ], 5 ) ) + " $\pm$ " + str( round_sig( this_error[ "RATIO" ], 2 ) ) )
              else:
                this_entry.append( " & " + str( round_sig( this_yield[ "TOTAL" ], 5 ) ) + " $\pm$ " + str( round_sig( this_error[ "TOTAL" ], 2 ) ) )
            
          this_entry.append( "\\\\" )
          tables[ "PRINT" ].append( this_entry )
    
    return tables
    
  def pas_table( tables ):
    print( ">> Adding yields in electron/muon channels combined" )
    for nhot in categories[ "NHOT" ]:
      tables[ "PRINT" ].append( [ "BREAK" ] )
      tables[ "PRINT" ].append( [ "", "isL_nhot{}_yields".format( nhot ) ] )
      tables[ "PRINT" ].append( [ "BREAK" ] )
      tables[ "PRINT" ].append( [ "YIELDS" ] + [ category.replace( "isE", "isL" ) for category in category_list if "isE" in category and "nhot{}".format( nhot ) in category ] + [ "\\\\" ] )
      for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + [ "DATA", "TOTBKG", "DATAOVERBKG" ] + groups[ "SIG" ][ "PROCESS" ]:
        this_entry = [ group ]
        for category in category_list:
          if not ( "isE" in category and "nhot{}".format( nhot ) in category ): continue
          sub_category = category[ category.find( "nt" ): category.find( "nj" ) - 3 ]
          with "{}_{}_{}".format( variable, lumiStr, category ) as key_e:
            key_m = key_e.replace( "isE", "isM" )
            this_yield = { "COMBINED": 0., "ELECTRON": 0., "MUON": 0., "DATA": 0., "RATIO": 0. }
            this_error = { "COMBINED": 0., "ELECTRON": 0., "MUON": 0., "DATA": 0., "RATIO": 0. }
            if group == "TOTBKG" or group == "DATAOVERBKG":
              for sub_group in list( groups[ "BKG" ][ "GROUP" ].keys() ):
                try:
                  this_yield[ "ELECTRON" ] += tables[ "YIELD" ][ key_e ][ sub_group ] 
                  this_yield[ "MUON" ] += tables[ "YIELD" ][ key_m ][ sub_group ]
                  this_yield[ "COMBINED" ] += tables[ "YIELD" ][ key_e ][ sub_group ] + tables[ "YIELD" ][ key_m ][ sub_group ] + zero
                  this_error[ "COMBINED" ] += tables[ "ERROR" ][ key_e ][ sub_group ]**2 + tables[ "ERROR" ][ key_m ][ sub_group ]**2
                except:
                  print( "[WARN] Missing {} for channel {}".format( sub_group, category ) )
                  pass
                  
              this_error[ "COMBINED" ] += ( uncertainties[ "ELECTRON" ][ "TOTAL" ][ args.year ] * this_yield[ "ELECTRON" ] )**2 + ( uncertainties[ "MUON" ][ "TOTAL" ][ args.year ] * this_yield[ "MUON" ] )**2
              
              if group == "DATAOVERBKG":
                this_yield[ "DATA" ] = tables[ "YIELD" ][ key_e ][ "DATA" ] + tables[ "YIELD" ][ key_m ][ "DATA" ] + zero
                this_error[ "DATA" ] = tables[ "ERROR" ][ key_e ][ "DATA" ]**2 + tables[ "ERROR" ][ key_m ][ "DATA" ]**2
                this_yield[ "RATIO" ] = this_yield[ "DATA" ] / this_yield[ "COMBINED" ]
                this_error[ "RATIO" ] = ( ( this_yield[ "RATIO" ] )**2 ) * ( ( this_error[ "DATA" ] / this_yield[ "DATA" ]**2 ) + ( this_error[ "COMBINED" ] / this_yield[ "COMBINED" ]**2 ) )
            else: 
              try:
                this_yield[ "ELECTRON" ] += tables[ "YIELD" ][ key_e ][ group ]
                this_yield[ "MUON" ] += tables[ "YIELD" ][ key_m ][ group ]
                this_yield[ "COMBINED" ] += tables[ "YIELD" ][ key_e ][ group ] + tables[ "YIELD" ][ key_m ][ group ]
                this_error[ "COMBINED" ] += tables[ "ERROR" ][ key_e ][ group ]**2 + tables[ "ERROR" ][ key_m ][ group ]**2
              except:
                print( "[WARN] Missing {} for channel {}".format( sub_group, category ) )
                pass
              
              this_error[ "COMBINED" ] += ( uncertainties[ "ELECTRON" ][ "TOTAL" ][ args.year ] * this_yield[ "ELECTRON" ] )**2 + ( uncertainties[ "MUON" ][ "TOTAL" ][ args.year ] * this_yield[ "MUON" ] )**2
              
          for key in this_error.keys(): this_error[ key ] = math.sqrt( this_error[ key ] )
          
          if group == "DATA": 
            this_entry.append( " & " + str( int( tables[ "YIELD" ][ key_e ][ group ] + tables[ "YIELD" ][ key_m ][ group ] ) ) )
          else:
            this_entry.append( " & " + str( round_sig( this_yield[ "COMBINED" ], 5 ) ) + " $\pm$ " + str( round_sig( this_error[ "COMBINED" ], 2 ) ) )
        
        this_entry.append( "\\\\" )
        tables[ "PRINT" ].append( this_entry )
        
    return tables
    
  def systematic_table( tables ):
    print( ">> Adding systematics" )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    tables[ "PRINT" ].append( [ "", "SYSTEMATICS" ] )
    tables[ "PRINT" ].append( [ "BREAK" ] )
    for group in list( groups[ "BKG" ][ "GROUP" ].keys() ) + groups[ "SIG" ][ "PROCESS" ]:
      tables[ "PRINT" ].append( [ group ] + [ category for category in category_list ] + [ "\\\\" ] )
      for syst in systematics_list + [ "hd", "ue" ]:
        for dir in [ "Up", "Down" ]:
          this_entry = [ syst + dir ]
          for category in category_list:
            with "{}_{}_{}".format( variable, lumiStr, category ) as key:
              syst_key = key + syst + dir
              try:
                this_entry.append( " & " + str( round( tables[ "YIELD" ][ syst_key ][ group ] / ( tables[ "YIELD" ][ key ][ group ] + zero ), 2 ) ) )
              except:
                print( "[WARN] Missing {} for channel {} with systematics {}{}".format( group, category, syst, dir ) )
                pass
          this_entry.append( "\\\\" )
          tables[ "PRINT" ].append( this_entry )
      tables[ "PRINT" ].append( [ "BREAK" ] )
          
    return tables
    
  def print_table( table ):
    def get_max_width( table, index )
      max = 0
      for row in table:
        try:
          n = len( str( row[ index ] ) )
          if n > max: max = nb
        except: pass
      return max
    
    print( ">> Printing out table, padded for alignment" )
    
    paddings = []
    out_file = open( "yields_{}_{}.txt".format( variable, lumiStr ), "w" )
    max_columns = 0
    
    for row in table:
      if len( row ) > max_columns: max_columns = len( row )
      
    for i in range( max_columns ):
      paddings.append( get_max_width( table, i ) )
      
    for row in table:
      if row[0] == "BREAK": row[0] = "-" * ( sum( paddings ) + ( 2 * len( paddings ) ) )
      print >> out_file, str( row[0] ).ljust( paddings[0] + 1 ),
      for i in range( 1, len( row ) ):
        column = str( row[i] ).ljust( paddings[i] + 2 )
        print >> out_file, column,
      print >> out_file
      
    out_file.close()
    
  print( ">> Producing yield tables" )
  
  tables[ "PRINT" ] = []
  
  tables = nominal_tables( tables )
  if do_an: tables = an_table( tables )
  if do_pas: tables = pas_table( tables )
  if do_systematics: tables = systematic_table( tables )
  
  print_table( tables[ "PRINT" ] )

def main():
  groups = group_process()
  for variable in variables:
    hists = load_histograms( variable )
    hists = correct_histograms( hists )
    hists = consolidate_histograms( hists )
    tables = make_tables( hists )
    theta_templates( hists )
    combine_templates( hists )
    summary_templates( hists )
    print_tables( tables, variable )
    del hists
    del tables
  
  
  
  

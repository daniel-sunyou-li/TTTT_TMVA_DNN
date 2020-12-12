#!/usr/bin/python
# this is the equivalent script to singleLepAnalyzer/makeTemplates/doHists.py
# this is run on a Condor node from step1.sh

import os, sys, json, time, math, getpass, datetime, pickle, itertools, getopt
from argparse import ArgumentParser
from ROOT import TH1D, gROOT, TFile, TTree
import numpy as np

sys.path.insert(0,"../TTTT_TMVA_DNN")

import varsList
from analyze import analyze
import utils

parser = ArgumentParser()
parser.add_argument( "-y", "--year",     required = True,       help = "Sample year" )
parser.add_argument( "-v", "--variable", required = True,       help = "Variable to produce a histogram for" )
parser.add_argument( "-c", "--category", required = True )
args = parser.parse_args()

gROOT.SetBatch(1)

# load in settings from the config file
with open( args.config, "r" ) as file:
  jsonFile = json.load( file )
  
configuration = jsonFile[ "CONFIGURATION" ]
test = jsonFile[ "CONFIGURATION" ][ "UNIT_TEST" ].lower()
systematics = configuration[ "USE_SYSTEMATICS" ].lower()
pdf = configuration[ "USE_PDF" ].lower()

print( ">> Running hists.py for:" )
print( ">> Variable: {}".format( args.variable ) )
print( ">> Category: {}".format( args.category ) )
print( ">> Year: {}".format( args.year ) )
print( ">> Test: {}".format( test ) )
print( ">> Systematics: {}".format( systematics ) )
print( ">> PDFs: {}".format( pdf ) )

allSamples = varsList.all_samples[ str(args.year) ]
inputDir = varsList.step3DirEOS[ str(args.year) ]

print( ">> Reading in step3 files from: {}".format( inputDir ) )
print( ">> Saving histograms at: {}".format( outputDir ) )

varList = varsList.varList[ "Step3" ]
varIndx = np.argwhere( np.asarray(varList)[:,0] == args.variable )

sig = []
bkg = []
data = []
hdamp = []
ue = []

for key in allSamples.keys():
  if "tttt" in str(key).lower():
    sig.append(key)
  elif "data" in str(key).lower():
    data.append(key)
  elif "hdamp" in str(key).lower():
    hdamp.append(key)
  elif "ue" in str(key).lower():
    ue.append(key)
  else:
    bkg.append(key)

if args.verbose:
  print( "{} signal samples found".format( len(sig) ) )
  print( "{} data samples found".format( len( data ) ) )
  print( "{} hdamp samples found".format( len( hdamp ) ) )
  print( "{} ue samples found".format( len( ue ) ) )
  print( "{} background samples found".format( len( bkg ) ) )

def read_tree( file ):
  if not os.path.exists(file):
    print("[ERR] {} does not exist.  Exiting program...".format(file))
    sys.exit(1)
  rootFile = TFile( file, "READ" )
  rootTree = rootFile.Get( "ljmet" )
  return rootFile, rootTree

def run_data( category, label, data, minBin, maxBin, nBin ):
  treeData = {}
  fileData = {}
  dataHists = {}
  for sample in data:
    fileData[ sample ], treeData[ sample ] = read_tree( os.path.join( inputDir, "nominal/", allSamples[ sample ][ 0 ] ) )
    dataHists.update( analyze(
      treeData, sample, "", False, pdf, args.variable,
      [ args.variable, np.linspace(minBin,maxBin,nBin).tolist(), label ],
      category, args.year, True ) )
    del treeData[cat]
    del fileData[cat]
  pickle.dump( dataHists, open( "data_{}.pkl".format( args.variable ), "wb" ) )

def run_signal( category, label, sig, minBin, maxBin, nBin ):
  treeSig = {}
  fileSig = {}
  sigHists = {}
  for sample in sig:
    fileSig[ sample ], treeSig[ sample ] = read_tree( os.path.join( inputDir, "nominal/", allSamples[sample][0] ) )
    if systematics:
      for sys in [ "jec", "jer" ]:
        for dir in [ "Up", "Down" ]:
          fileSig[ sample + sys + dir ], treeSig[ sample + sys + dir ] = read_tree(
            os.path.join( inputDir, sys.Upper() + dir.lower(), + allSamples[ sample ][ 0 ] )
    sigHists.update( analyze(
      treeSig, sample, "", systematics, pdf, args.variable, 
      ( args.variable, np.linspace( minBin, maxBin, nBin ).tolist(), label ),
      category, args.year, True ) )
    del treeSig[ sample ]
    del fileSig[ sample ]
    if systematics:
      for sys in [ "jec", "jer" ]:
        for dir in [ "Up", "Down" ]:
          del treeSig[ sample + sys + dir ]
          del fileSig[ sample + sys + dir ]
  pickle.dump( sigHists, open( "sig_{}.pkl".format( args.variable ), "wb" ) )

def run_background( category, label, bkg, hdamp, ue, minBin, maxBin, nBin ):
  treeBkg = {}
  fileBkg = {}
  bkgHists = {}
  for sample in bkg:
    fileBkg[ sample ], treeBkg[ sample ] = read_tree( os.path.join( inputDir, "nominal/", allSamples[ sample ][ 0 ] ) )
    if systematics:
      for sys in [ "jec" , "jer" ]:
        for dir in [ "Up" , "Down" ]:
          fileBkg[ sample + sys + dir ] = read_tree(
            os.path.join( inputDir, sys.Upper() + dir.lower(), allSamples[ sample ][ 0 ] )
    bkgHists.update( analyze(
      treeBkg, sample, "", systematics, pdf, args.variable,
      [ args.variable, np.linspace( minBin, maxBin, nBin ).tolist(), label ],
      category, args.year, True ) )
    for sys in [ "jec" , "jer" ]:
      for dir in [ "Up" , "Down" ]:
        del treeBkg[ sample + sys + dir ]
        del fileBkg[ sample + sys + dir ]
  if systematics:
    for sample in hdamp:
      fileBkg[ sample ], treeBkg[ sample ] = read_tree( os.path.join( inputDir, "nominal/", allSamples[ sample ][ 0 ] ) )
      bkgHists.update( analyze(
        treeBkg, sample, "", False, pdf, args.variable,
        [ args.variable, np.linspace( minBin, maxBin, nBin ).tolist(), varList[ varIndx, 1 ] ],
        category, args.year, args.verbose ) )
      del fileBkg[ sample ]
      del treeBkg[ sample ]
    for sample in ue:
      fileBkg[ sample ], treeBkg[ sample ] = read_tree( os.path.join( inputDir, "nominal/", allSamples[ sample ][ 0 ] ) )
      bkgHists.update( analyze(
        treeBkg, sample, "", False, pdf, args.variable,
        [ args.variable, np.linspace( minBin, maxBin, nBin).tolist(), label ],
        category, args.year, args.verbose ) )
      del fileBkg[sample]
      del treeBkg[sample]
  pickle.dump( bkgHists, open( "bkg_{}.pkl".format( args.variable ), "wb" ) )

def pickle_step3( label, minBin, maxBin, nBin, category, sample_type ):
  print(">> Storing {} as {}".format( args.variable, label ) )
  print(">> Using binning: ({},{},{})".format(minBin,maxBin,nBin))
  startTime = time.time()
  if sample_type.lower() == "sig":
    print( ">> Pickling signal samples..." )
    run_signal( category, label, sig, minBin, maxBin, nBin )
    print( "[OK ] Finished pickling signal samples in {:.2f} minutes.".format( ( time.time()-startTime ) / 60. ) )
  elif sample_type.lower() == "bkg":
    print( ">> Plotting background samples..." )
    run_background( category, label, bkg, hdamp, ue, minBin, maxBin, nBin)
    print( "[OK ] Finished pickling background samples in {:.2f} minutes.".format( ( time.time()-startTime ) / 60. ) )
  elif sample_type.lower() == "data":
    print( ">> Plotting data samples..." )
    run_data( category, label, data, minBin, maxBin, nBin)
    print( "[OK ] Finished pickling data samples stored in {:.2f} minutes.".format( ( time.time()-startTime ) / 60. ) )

varTuple = varList[ varIndx[0][0] ]
if ( len(bkg) > 0 or len(hdamp) > 0 or len(ue) > 0 ): 
  pickle_step3( varTuple[1], varTuple[2], varTuple[3], varTuple[4], args.category, "bkg" )
if len(sig) > 0: 
  pickle_step3( varTuple[1], varTuple[2], varTuple[3], varTuple[4], args.category, "sig" )
if len(data) > 0: 
  pickle_step3( varTuple[1], varTuple[2], varTuple[3], varTuple[4], args.category, "data" )

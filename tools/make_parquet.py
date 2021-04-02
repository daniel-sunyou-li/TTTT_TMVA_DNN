import os, sys, time
from ROOT import TMVA, TCut, TFile
#import pyarrow.parquet as pq
import pandas as pd
import pyarrow as pa
import numpy as np
from argparse import ArgumentParser
sys.path.insert( 0, "../TTTT_TMVA_DNN" )
import varsList

parser = ArgumentParser()
parser.add_argument( "-y",  "--year",   required = True )
parser.add_argument( "-nj", "--njets",  default = 4, required = False )
parser.add_argument( "-nb", "--nbjets", default = 2, required = False )
parser.add_argument( "-t",  "--test",   action = "store_true" )
args = parser.parse_args()

if args.year not in [ "2017", "2018" ]: 
  print( "[ERR] Invalid year option: {}, choose either 2017 or 2018".format( args.year ) )
  quit()

samples = varsList.sig_training[ args.year ] + varsList.bkg_training[ args.year ]

variables = [ variable[0] for variable in varsList.varList["DNN"] ] + \
	[ "isElectron", "isMuon", "DataPastTriggerX", "MCPastTriggerX" ]

variables = np.asarray( variables )

index = {
  "lepPt": np.argwhere( variables == "leptonPt_MultiLepCalc" ),
  "met": np.argwhere( variables == "corr_met_MultiLepCalc" ),
  "isE": np.argwhere( variables == "isElectron" ),
  "isM": np.argwhere( variables == "isMuon" ),
  "MT": np.argwhere( variables == "MT_lepMet" ),
  "minDRlj": np.argwhere( variables == "minDR_lepJet" ),
  "HT": np.argwhere( variables == "AK4HT" ),
  "Data": np.argwhere( variables == "DataPastTriggerX" ),
  "MC": np.argwhere( variables == "MCPastTriggerX" ),
  "nB": np.argwhere( variables == "NJetsCSV_MultiLepCalc" ),
  "nJ": np.argwhere( variables == "NJets_JetSubCalc" )
}

cut = {
  "lepPt": 20,
  "met": 20,
  "MT": 60,
  "minDRlj": 0.4,
  "HT": 500
}

out_folder = "parquet_{}".format( varsList.date )
if not os.path.isdir( out_folder ):
  print( ">> Creating output folder for .parquet files" )
  os.mkdir( out_folder )
out_file = "TTTT_DNN_nJ{}_nB{}_{}.parquet".format( args.njets, args.nbjets, args.year ) if not args.test else "test.parquet"


py_events = {}


for sample in samples:
  if args.test: 
    if "tttt" not in sample.lower(): continue
  root_file   = TFile.Open( os.path.join( varsList.step2Sample[ args.year ], "nominal", sample ) )
  tree_events = root_file.Get( "ljmet" )
  start_time = time.time()
  py_events[ sample ] = tree_events.AsMatrix( variables )
  print( ">> Finished processing {} in {:.2f} minutes".format( sample, ( time.time() - start_time ) / 60. ) )

sig_events = np.concatenate( [ py_events[ sample ] for sample in samples if "tttt" in sample.lower() ] )
if not args.test: bkg_events = np.concatenate( [ py_events[ sample ] for sample in samples if "tttt" not in sample.lower() ] )

sig_cut_mask = []
bkg_cut_mask = []

for i in range( np.shape( sig_events )[0] ):
  if( sig_events[i,index["lepPt"]] > cut["lepPt"] and ( sig_events[i,index["isE"]] == 1 or sig_events[i,index["isM"]] == 1 ) ):
    if( sig_events[i,index["met"]] > cut["met"] and sig_events[i,index["MT"]] > cut["MT"] and sig_events[i,index["HT"]] > cut["HT"] and sig_events[i,index["minDRlj"]] > cut["minDRlj"] ):
      if( sig_events[i,index["Data"]] == 1 and sig_events[i,index["MC"]] == 1 ):
        if( sig_events[i,index["nJ"]] >= int(args.njets) and sig_events[i,index["nB"]] >= int(args.nbjets) ):
          sig_cut_mask.append( i )     

if not args.test:
  for i in range( np.shape( bkg_events )[0] ):
    if( bkg_events[i,index["lepPt"]] > cut["lepPt"] and ( bkg_events[i,index["isE"]] == 1 or bkg_events[i,index["isM"]] == 1 ) ):
      if( bkg_events[i,index["met"]] > cut["met"] and bkg_events[i,index["MT"]] > cut["MT"] and bkg_events[i,index["HT"]] > cut["HT"] and bkg_events[i,index["minDRlj"]] > cut["minDRlj"] ):
        if( bkg_events[i,index["Data"]] == 1 and bkg_events[i,index["MC"]] ):
          if( bkg_events[i,index["nJ"]] >= int(args.njets) and bkg_events[i,index["nB"]] >= int(args.nbjets) ):
            bkg_cut_mask.append( i )

# filter the events that pass the selection
sig_cut_events = sig_events[ sig_cut_mask ]
if not args.test: bkg_cut_events = bkg_events[ bkg_cut_mask ]

sig_cut_inputs = []
bkg_cut_inputs = []

for i in range( np.shape( sig_cut_events )[0] ):
  sig_cut_inputs.append( np.append( sig_cut_events[i][:-4], 1 ) )

if not args.test:
  for i in range( np.shape( bkg_cut_events )[0] ):
    bkg_cut_inputs.append( np.append( bkg_cut_events[i][:-4], 0 ) )

all_cut_inputs = np.concatenate( [ sig_cut_inputs ] if args.test else [ sig_cut_inputs, bkg_cut_inputs ] )

all_cut_df = pd.DataFrame( all_cut_inputs, columns = [ variable for variable in variables[:-4] ] + [ "type" ] )

print( ">> Writing {}...".format( out_file ) )
all_cut_df.to_parquet( os.path.join( out_folder, out_file ) )










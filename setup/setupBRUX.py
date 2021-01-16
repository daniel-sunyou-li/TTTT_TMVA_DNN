#!/usr/bin/env python

import os, sys, getpass, pexpect, argparse
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

parser = ArgumentParser()
parser.add_argument( "-y", "--year", required = True )
parser.add_argument( "-t", "--tag", default = "" )
args = parser.parse_args()

samples = varsList.all_samples[ args.year ]

if not os.path.exists( varsList.step3Sample[ args.year ] + args.tag ):
  os.system( "mkdir ./{}".format( varsList.step3Sample[ args.year ] + args.tag ) )
  os.system( "mkdir ./{}/nominal/".format( varsList.step3Sample[ args.year ] + args.tag ) )
  for syst in [ "JEC", "JER" ]:
    for dir in [ "up", "down" ]:
      os.system( "mkdir ./{}/{}".format( varsList.step3Sample[ args.year ] + args.tag, syst + dir ) )
            
            
for sample in samples:
  os.system(  "xrdcp  root://cmseos.fnal.gov///store/user/{}/{}nominal/{} ./nominal/".format( varsList.eosUserName, varsList.step3Sample[ args.year ] + args.tag, sample )
  for syst in [ "JEC", "JER" ]:
    for dir in [ "up", "down" ]:
      if "up" in sample.lower() or "down" in sample.lower(): continue
      if "muon" in sample.lower() or "electron" in sample.lower() or "egamma" in sample.lower() or "jetht" in sample.lower(): continue
      os.system( xrdcp root://cmseos.fnal.gov///store/user/{}/{}{}/{} .{}/".format( varsList.eosUserName, varsList.step3Sample[ args.year } + args.tag, syst + dir, sample, syst + dir )
  

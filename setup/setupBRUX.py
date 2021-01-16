#!/usr/bin/env python

import os, sys, getpass, pexpect, argparse
sys.path.insert(0, "../TTTT_TMVA_DNN")
import varsList

parser = ArgumentParser()
parser.add_argument( "-y", "--year", required = True )
parser.add_argument( "-t", "--tag", default = "" )
args = parser.parse_args()

all_samples = varsList.all_samples[ args.year ]
samples = [ all_samples[ sample_key ][0] for sample_key in all_samples.key() ]

out_folder = varsList.step3Sample[ args.year ] + args.tag 
done_samples = {
  "nominal": os.listdir( out_folder + "/nominal/" ),
}
for syst in [ "JEC", "JER" ]:
  for dir in [ "up", "down" ]:
    done_samples[ syst + dir ] = os.listdir( out_folder + "/{}".format( syst + dir ) )
  


if not os.path.exists( out_folder ):
  os.system( "mkdir ./{}".format( out_folder ) )
  os.system( "mkdir ./{}/nominal/".format( out_folder ) )
  for syst in [ "JEC", "JER" ]:
    for dir in [ "up", "down" ]:
      os.system( "mkdir ./{}/{}".format( out_folder, syst + dir ) )
            
            
for sample in samples:
  if sample not in done_samples[ "nominal" ]: 
    print( "Adding {}".format( sample ) )
    os.system(  "xrdcp  root://cmseos.fnal.gov///store/user/{}/{}nominal/{} ./nominal/".format( varsList.eosUserName, out_folder, sample )
  for syst in [ "JEC", "JER" ]:
    for dir in [ "up", "down" ]:
      if "up" in sample.lower() or "down" in sample.lower(): continue
      if "muon" in sample.lower() or "electron" in sample.lower() or "egamma" in sample.lower() or "jetht" in sample.lower(): continue
      if sample not in done_samples[ syst + dir ]:
        os.system( xrdcp root://cmseos.fnal.gov///store/user/{}/{}{}/{} .{}/".format( varsList.eosUserName, out_folder, syst + dir, sample, syst + dir )
  

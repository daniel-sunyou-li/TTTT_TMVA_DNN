#!/usr/bin/env python

import os, sys, getpass, pexpect, subprocess
from subprocess import check_output
from subprocess import call as sys_call
from argparse import ArgumentParser

sys.path.insert(0,"../TTTT_TMVA_DNN")

import varsList

# set-up the working area
home = os.path.expanduser( "~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/" )
brux_pwd = None

parser = ArgumentParser()
parser.add_argument( "-y",   "--year",        default = "2017",      help = "Which production year samples to transfer" )
parser.add_argument( "-sys", "--systematics", action = "store_true", help = "Include the systematic samples" )
parser.add_argument( "-r",   "--remove",      action = "store_true", help = "Remove non-training samples on LPC after transferring" )
parser.add_argument( "-n",   "--split",       default = "-1",        help = "Split the step2 sample into n parts" )
parser.add_argument( "-t",   "--tar",         action = "store_true", help = "Tar the CMSSW directory and transfer to EOS" )
parser.add_argument( "-v",   "--verbose",     action = "store_true", help = "Turn verbosity on" )
parser.add_argument( "-lpc", "--lpcOnly",     action = "store_true", help = "Only transfer training samples" )
parser.add_argument( "-eos", "--eos",         action = "store_true", help = "Transfer from BRUX to EOS" )
args = parser.parse_args()

all_samples      = varsList.all_samples[ "2017" ]  if args.year == "2017" else varsList.all_samples[ "2018" ]
sig_training     = varsList.sig_training[ "2017" ] if args.year == "2017" else varsList.sig_training[ "2018" ]
bkg_training     = varsList.bkg_training[ "2017" ] if args.year == "2017" else varsList.bkg_training[ "2018" ]
training_samples = sig_training + bkg_training
step2Sample      = varsList.step2Sample[ "2017" ]  if args.year == "2017" else varsList.step2Sample[ "2018" ]
step2DirBRUX     = varsList.step2DirBRUX[ "2017" ] if args.year == "2017" else varsList.step2DirBRUX[ "2018" ]
step2DirLPC      = varsList.step2DirLPC[ "2017" ]  if args.year == "2017" else varsList.step2DirLPC[ "2018" ]
step2DirEOS      = varsList.step2DirEOS[ "2017" ]  if args.year == "2017" else varsList.step2DirEOS[ "2018" ]

samples = [ all_samples[ sample_key ][0].replace("split0_step3","hadd") for sample_key in all_samples.keys() ]

def print_options():
  sys_opt     = "[ON ]" if args.systematics else "[OFF]"
  remove_opt  = "[ON ]" if args.remove else "[OFF]"
  split_opt   = "[ON ]" if int(args.split) > 0 else "[OFF]"
  verbose_opt = "[ON ]" if args.verbose else "[OFF]"
  lpc_opt     = "[ON ]" if args.lpcOnly else "[OFF]"
  
  print( ">> OPTIONS:" )
  print( "{} Include systematic samples".format( "[ON ]" if args.systematics else "[OFF]" ) )
  print( "{} Remove samples from LPC".format( "[ON ]" if args.remove else "[OFF]" ) )
  print( "{} Splitting samples".format( "[ON ]" if int(args.split) > 0 else "[OFF]" ) )
  print( "{} CMSSW Tar".format( "[ON ]" if args.tar else "[OFF]" ) )
  print( "{} Transfer to LPC only".format( "[ON ]" if args.lpcOnly else "[OFF]" ) )
  print( "{} Verbosity".format( "[ON ]" if args.verbose else "[OFF]" ) )

def check_voms(): # used in voms_init
  print( ">> Checking grid certificate validation (VOMS)..." )
  try:
    output = check_output("voms-proxy-info", shell = True)
    print( output.rfind("timeleft") )
    print( output[ output.rfind(": ") + 2: ] )
    if output.rfind( "timeleft" ) > -1:
      if int( output[ output.rfind( ": " ) + 2: ].replace(":","") ) > 0:
        print( "[OK ] VOMS found" )
        return True
    return False
  except:
    return False
    
def voms_init(): # run independently
  if not check_voms():
    print( ">> Initializing grid certificate..." )
    output = check_output( "voms-proxy-init --rfc --voms cms", shell = True )
    if "failure" in output:
      print( ">> Incorrect password entered, try again." )
      voms_init()
    print( "[OK ] Grid certificate initialized" )

def brux_auth():
  global brux_pwd
  print( ">> Password for {}@brux.hep.brown.edu".format( varsList.bruxUserName ) )
  if brux_pwd == None:
    brux_pwd = getpass.getpass( ">> Password: " )
    
def compile_splitter():
  if "splitROOT.out" in os.listdir( os.getcwd() + "/setup/" ):
    sys_call( "rm {}/setup/splitROOT.out".format( os.getcwd() ), shell = True )
  print( ">> Compiling splitROOT.cpp..." )
  if sys_call( "g++ `root-config --cflags` `root-config --libs` -o ./setup/splitROOT.out ./setup/splitROOT.cpp", shell = True ) == 0:
    print( "[OK ] Compiled splitROOT.cpp" )
  else:
    print( "[ERR] Compiling splitROOT.cpp failed!" )
    sys.exit(1)
    
def split_root( sample, directory, splits ):
  print( "[   ] Splitting {}...".format( sample ) )
  if sys_call( "./setup/splitROOT.out {} {} {} {}".format(
    directory,
    directory,
    sample,
    splits
    ), shell = True ) == 1:
    print( "[ERR] Splitting {} failed".format( sample ) )
  print( "[OK ] Finished splitting {}, now transferring to EOS".format( sample ) )

def brux_to_lpc( directoryBRUX, sample, step2Dir ):
  child = pexpect.spawn( "scp -r {}@brux.hep.brown.edu:{}{} ./{}".format(
    varsList.bruxUserName,
    directoryBRUX,
    sample,
    step2Dir
    ))
    
  opt = 1
  while opt == 1:
    opt = child.expect( [ varsList.bruxUserName + "@brux.hep.brown.edu's password: ",
      "Are you sure you want to continue connecting (yes/no)? " ] )
    if opt == 1:
      child.sendline( "yes" )
  child.sendline( brux_pwd )
  child.interact()

def brux_to_eos( year, systematics, samples, split ):
  include_systematics = "" if not systematics else ", including systematics"
  print( ">> Transferring samples from BRUX to LPC for {} samples{}".format( year, include_systematics ) )
  if args.remove: print( ">> Removing non-training samples on LPC after transferring to EOS..." )  
  split_tag = "hadd"
  if split > -1:
    print(">> Splitting samples in {}".format(split))
    split_tag = "split0"

# create the necessary directories
# create directories in lpc
  if step2Sample not in os.listdir( home ):
    print( ">> Creating LPC directory for Step2 samples" )
    sys_call( "mkdir {}{}".format( home, step2Sample ), shell = True )
  if "nominal" not in os.listdir( home + step2Sample ):
    print( ">> Creating LPC directory for nominal samples" )
    os.system( "mkdir {}{}/nominal".format( home, step2Sample ) )
  if args.systematics:
    for syst in [ "JEC", "JER" ]:
      for dir in [ "up", "down" ]:
        if syst + dir not in os.listdir( home + step2Sample ):
          print( ">> Creating LPC directory for systematic: {}{}".format( syst, dir ) )
          print( home + step2Sample + "/" + syst + dir )
          os.system( "mkdir {}{}/{}{}".format( home, step2Sample, syst, dir ) )
  
# create directories in EOS
  eosContent = subprocess.check_output( "eos root://cmseos.fnal.gov ls /store/user/{}/".format( varsList.eosUserName ), shell=True )
  if step2Sample not in eosContent:
    print(">> Creating EOS directory for nominal samples")
    sys_call( "eos root://cmseos.fnal.gov mkdir /store/user/{}/{}".format( varsList.eosUserName, step2Sample ), shell = True )
  if "nominal" not in subprocess.check_output( "eos root://cmseos.fnal.gov ls /store/user/{}/{}".format ( varsList.eosUserName, step2Sample ), shell = True ):
    sys_call( "eos root://cmseos.fnal.gov mkdir /store/user/{}/{}/nominal".format( varsList.eosUserName, step2Sample ), shell = True )
  if args.systematics:
    for syst in [ "JEC", "JER" ]:
      for dir in [ "up", "down" ]:
        if syst + dir not in subprocess.check_output( "eos root://cmseos.fnal.gov ls /store/user/{}/{}".format( varsList.eosUserName, step2Sample ), shell = True ):
          print( ">> Creating EOS directory for systematic: {}{}".format( syst, dir ) )
          sys_call( "eos root://cmseos.fnal.gov mkdir /store/user/{}/{}/{}{}".format( varsList.eosUserName, step2Sample, syst, dir ), shell = True )


  eos_samples = {
    "nominal": check_output( "eos root://cmseos.fnal.gov ls /store/user/{}/{}/nominal/".format( varsList.eosUserName, step2Sample ), shell = True )
  }

  if args.systematics:
    for syst in [ "JEC", "JER" ]:
      for dir in [ "up", "down" ]:
        eos_samples[ syst + dir ] = check_output( "eos root://cmseos.fnal.gov ls /store/user/{}/{}/{}{}/".format( varsList.eosUserName, step2Sample, syst, dir ), shell = True )

# transfer samples from BRUX to EOS 
  for sample in samples:
    if sample.replace( "hadd", split_tag ) not in eos_samples[ "nominal" ]:
      if sample.replace( "hadd", split_tag ) not in os.listdir( "{}{}/nominal/".format( home, step2Sample ) ):
        print( ">> Transferring {} to {}/nominal/".format( sample, step2Sample ) )
        brux_to_lpc(
          step2DirBRUX + "/nominal/",
          sample,
          step2Sample + "/nominal/"
        ) 
        if split > -1:
          print( ">> Splitting {} into {} parts.".format( sample, splits ) )
          split_root( sample, step2DirLPC + "nominal/", str(splits) )
        print( ">> Removing {} from LPC".format( sample ) )

      print( ">> Transferring {} to /nominal/ EOS".format( sample.replace( "hadd", split_tag ) ) )
      sys_call( "xrdcp {}{} {}nominal/".format(
        step2DirLPC + "nominal/",
        sample.replace( "hadd", split_tag ),
        varsList.eosUserName,
        step2DirEOS
      ), shell = True )
      if args.remove and sample not in training_samples:
        print( ">> Removing all {} files from /nominal/ LPC".format( sample ) )
        if split > -1:
          os.system( "rm {}nominal/{}".format( step2DirLPC, sample.replace( "hadd.root", "split*" ) ) )
        else:
          os.system( "rm {}nominal/{}".format( step2DirLPC, sample ) )
    else: print( "[OK ] {} exists in /nominal/ on EOS, skipping...".format( sample.replace( "hadd", split_tag ) ) ) 

    if args.systematics:
      for syst in [ "JEC", "JER" ]:
        for dir in [ "up", "down" ]:
          if "up" in sample.lower() or "down" in sample.lower(): continue
          if "muon" in sample.lower() or "electron" in sample.lower() or "egamma" in sample.lower() or "jetht" in sample.lower(): continue
          if sample.replace( "hadd", split_tag ) not in eos_samples[ syst + dir ]:
            if sample.replace( "hadd", split_tag ) not in os.listdir( "{}{}/{}{}/".format( home, step2Sample, syst, dir ) ):
              print( ">> Transferring {} to {}/{}{}/".format( sample, step2Sample, syst, dir ) )
              brux_to_lpc(
                step2DirBRUX + syst + dir + "/",
                sample,
                step2Sample + "/" + syst + dir + "/"
              ) 
              if split > -1:
                print( ">> Splitting {} into {} parts.".format( sample, splits ) )
                split_root( sample, step2DirLPC + syst + dir + "/", str(splits) )
              print( ">> Removing {} from /{}{}/ on LPC".format( sample, syst, dir ) )
            print( ">> Transferring {} to /{}{}/ on EOS".format( sample.replace( "hadd", split_tag ), syst, dir ) )
            sys_call( "xrdcp {}{} {}/".format(
              step2DirLPC + syst + dir + "/",
              sample.replace( "hadd", split_tag ),
              varsList.eosUserName,
              step2DirEOS + syst + dir 
            ), shell = True )
            if args.remove:
              print( ">> Removing all {} files from /{}{}/ LPC".format( sample, syst, dir ) )
              if split > -1:
                os.system( "rm {}{}{}/{}".format( step2DirLPC, syst, dir, sample.replace( "hadd.root", "split*" ) ) )
              else:
                os.system( "rm {}{}{}/{}".format( step2DirLPC, syst, dir, sample ) ) 
          else: print( "[OK ] {} exists in /{}{}/ on EOS, skipping...".format( sample.replace( "hadd", split_tag ), syst, dir ) )
    print( "[OK ] Transfer of {} from BRUX to EOS complete.  Proceeding to next sample.\n".format( sample ) ) 
     
  print( "[OK ] All samples transferred..." )

def lpc_only( year, systematics, samples, split ):
  print( ">> Transferring training samples from BRUX to LPC for {} samples".format( year ) )
  split_tag = "hadd"
  if split > -1:
    print( ">> Splitting samples in {}".format( split ) )
    split_tag = "split0"

  if step2Sample not in os.listdir( home ):
    print( ">> Creating LPC directory for step2 samples" )
    os.system( "mkdir {}{}/nominal".format( home, step2DirLPC ) )
  
  lpc_samples = check_output( "ls {}nominal/".format( step2DirLPC ), shell = True )
  for sample in samples:
    if sample.replace( "hadd", split_tag ) not in lpc_samples:
      print( ">> Transferring {} to {}/nominal/".format( sample, step2Sample ) )
      brux_to_lpc(
        step2DirBRUX + "nominal/",
        sample,
        step2Sample + "/nominal/"
      )
      if split > -1:
        print( ">> Splitting {} into {} parts.".format( sample, split ) )
        split_root( sample, step2DirLPC + "nominal/", str( split ) )
  print( "[OK ] Done transferring step2 files from BRUX to LPC" )

def create_tar():
  # tar the CMSSW repo
  tarDir = "CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/"
  if "CMSSW.tgz" in os.listdir( home ):
    print( ">> Deleting existing CMSSW946.tgz" ) 
    os.system( "rm {}{}".format( home, "CMSSW946.tgz" ) )
  print( ">> Creating new tar file for CMSSW946.tgz" )
  os.system( "tar -C ~/nobackup/ -zcvf CMSSW946.tgz --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\"  --exclude=\"{}\" --exclude=\"{}\" --exclude=\"{}\" {}".format(
    tarDir + "FWLJMET*",
    tarDir + "condor_log*",
    tarDir + "dataset*",
    tarDir + "application_log*",
    tarDir + "notebooks/*",
    tarDir + "parquet*",
    tarDir + "etc/*",
    tarDir + "cut_events*",
    tarDir + "CMSSW946.tgz",
    tarDir + ".git/*",
    "CMSSW_9_4_6_patch1/" 
  ) )
  print( ">> Transferring CMSSW946.tgz to EOS" )
  os.system( "xrdcp -f CMSSW946.tgz root://cmseos.fnal.gov//store/user/{}".format( varsList.eosUserName ) )
  print( "[OK ] Transfer complete!" )
 
def main():
  partial = print_options()
  voms_init()
  if int( args.split ) > -1: compile_splitter()
  if args.lpcOnly or args.eos: brux_auth()
  if args.lpcOnly: lpc_only( args.year, args.systematics, training_samples, int(args.split) )
  else:
    if args.eos: brux_to_eos( args.year, args.systematics, samples, int(args.split) )
  if args.tar: create_tar()  

main()

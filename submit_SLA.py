#!/usr/bin/python

import os, sys, json, datetime, itertools
import utils, varsList
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument( "-s", "--step",   required = True,       help = "Single Lep Analyzer step to submit" )
parser.add_argument( "-c", "--config", required = True,       help = ".json configuration file to use" )
args = parser.parse_args()

it args.step not in [ "1", "2", "3", "4", "5" ]: 
  print( "[ERR] Invalid step option used.  Please use either 1, 2, 3, 4 or 5.  Exiting program." )

try:
  with open( args.config, "r" ) as file:
    jsonFile = json.load( file )
except:
  print( "Config file: {}, was not found. Exiting program".format( args.config ) )

# setup configuration file parameters
  
date_tag = datetime.datetime.now().strftime( "%d.%b.%Y" )
configuration = jsonFile[ "CONFIGURATION" ]
test = configuration[ "UNIT_TEST" ][ "UNIT_TEST" ]
inputs = configuration[ "INPUTS" ]
categories = jsonFile[ "CATEGORIES" ][ "FULL" ] if test.lower() == "false" else jsonFile[ "CATEGORIES" ][ "TEST" ]
category_list = [
  "is{}_nhot{}_nt{}_nw{}_nb{}_nj{}".format( cat[0], cat[1], cat[2], cat[3], cat[4], cat[5] ) for cat in list( itertools.product(
    categories[ "LEP" ], categories[ "NHOT" ], categories[ "NTOP" ], categories[ "NW" ], categories[ "NBOT" ], categories[ "NJET" ] ) )
]

def print_options( configuration, categories, category_list ):
  print( ">> Running Step {} Using the configuration:".format( args.step ) )
  print( ">> Years: {}".format( configuration[ "YEAR" ] ) )
  print( ">> Inputs ({}):".format( len( configuration[ "INPUTS" ] ) ) )
  for input in configuration[ "INPUTS" ]:
    print( ">>   {}".format( input ) )
  print( ">> Categories ({}):".format( len( category_list ) ) )
  for category in categories.keys():
    print( ">>   {}: {}".format( category, categories[ category ] ) )
  print( ">> UNIT TEST: {}".format( configuration[ "UNIT_TEST" ] ) )
  print( ">> SYSTEMATICS: {}".format( configuration[ "USE_SYSTEMATICS" ] ) )
  print( ">> PDF: {}".format( configuration[ "USE_PDF" ] ) )
  if configuration[ "USE_SYSTEMATICS" ].lower() == "true":
    print( ">> Using the systematics ({}):".format( len( configuration[ "SYSTEMATICS" ] ) ) )
    for sytematic in configuration[ "SYSTEMATICS" ]:
      print( ">>   {}".format( systematic ) )

def check_step( jsonFile, step ):
  def check_step_one():
    finished = False
    # add code for checking step1 progress
    if finished: 
      print( "[OK ] Step One finished processing" )
      jsonFile[ "STEP 1" ][ "DONE" ] = "True"
    else: 
      print( "[WARN] Step One is not finished processing. Exiting program." )
      sys.exit(0)
      
  def check_step_two():
    finished = False
    # add code for checking step2 progress
    if finished:
      print( "[OK ] Step Two finished processing" )
      jsonFile[ "STEP 2" ][ "DONE" ] = "True"
    else:
      print( "[WARN] Step Two is not finished processing. Exiting program." )
      sys.exit(0)
      
  def check_step_three():
    finished = False
    # add code for checking step3 progress
    if finished:
      print( "[OK ] Step Three finished processing" )
      jsonFile[ "STEP 3" ][ "DONE" ] = "True"
    else:
      print( "[WARN] Step Three is not finished processing. Exiting program." )
      sys.exit(0)
      
  def check_step_four():
    # add code for checking step 4
    
  def check_step_five():
    # add code for checking step 5
      
  for i in range( step ):
    step_key = "STEP {}".format( i + 1 )
    if i + 1 < step:
      if jsonFile[ step_key ][ "SUBMIT" ].lower() == "false":
        print( "[ERR] Missing submission for step {}.  Exiting program.".format( step ) )
        sys.exit(0)
      if json[ step_key ][ "DONE" ].lower() == "false":
        if step_key   == "STEP 1": check_step_one()
        elif step_key == "STEP 2": check_step_two()
        elif step_key == "STEP 3": check_step_three()
        elif step_key == "STEP 4": check_step_four()
        elif step_key == "STEP 5": check_step_five()
  
  return jsonFile

def step_one( jsonFile, date_tag, years, category_list, variables ):
  jsonFile[ "STEP 1" ][ "SUBMIT" ] = "True"
  jsonFile[ "STEP 1" ][ "LOGFOLDER" ] = "log_step1_{}".format( date_tag )
  
  with os.path.join( "/singleLepAnalyzer", jsonFile[ "STEP 1" ][ "LOGFOLDER" ] ) as path:
    if not os.path.exists( path ):
      print( ">> Creating Step 1 log directory: {}".format( path ) )
      os.system( "mkdir -p {}".format( path ) )
  
  for year in years:
    with os.path.join ( "/store/user/", varsList.eosUserName, varsList.step3Sample[ year ] ) as path:
    if jsonFile[ "STEP 1" ][ "EOSFOLDER" ] not in subprocess.check_output( "eos root://cmseos.fnal.gov ls {}".format( path ), shell = True ):
      print( ">> Creating EOS directory for singleLepAnalyzer ({}): {}".format( year, os.path.join( path, jsonFile[ "STEP 1" ][ "EOSFOLDER" ] ) ) )
      sys_call( "eos root://cmseos.fnal.gov mkdir {}".format( os.path.join( path, jsonFile[ "STEP 1" ][ "EOSFOLDER" ] ) ), shell = True )
      
    for category in category_list:
      with os.path.join( "/store/user/{}/".format( varsList.eosUserName ), varsList.step3Sample[ year ], jsonFile[ "STEP 1" ][ "EOSFOLDER" ] ) as path:
        if category not in subprocess.check_output( "eos root://cmseos.fnal.gov ls {}".format( path ), shell = True ):
          print( ">> Creating EOS directory for histogram category ({}): {}".format( year, os.path.join( path, category ) ) )
          sys_call( "eos root://cmseos.fnal.gov mkdir {}".format( os.path.join( path, category ) ), shell = True )
      if category not in subprocess.check_output( "ls {}".format( jsonFile[ "STEP 1" ][ "LOGFOLDER" ] ), shell = True ):
        os.system( "mkdir -p {}".format( os.path.join( jsonFile[ "STEP 1" ][ "LOGFOLDER" ], category ) ) )
            
      for variable in variables:
        with os.path.join( jsonFile[ "STEP 1" ][ "LOGFOLDER" ], category ) as path:
          jdf_name = "{}_{}".format( variable, year )
          jdf_dict = {
            "LOGPATH": os.path.join( path, jdf_name + ".log" ), 
            "OUTPATH": os.path.join( path, jdf_name + ".out" ), 
            "ERRPATH": os.path.join( path, jdf_name + ".err" ),
            "YEAR": year, "CATEGORY": cateogry, "VARIABLE": variable, "JSON": args.config,
            "EOSDIR": os.path.join( varsList.step3Sample[ year ], jsonFile[ "STEP 1" ][ "EOSFOLDER" ], category ), 
            "EOS_USERNAME": varsList.eosUserName
          }
          jdf = open( os.path.join( path, jdf_name + ".job" ), "w" )
          jdf.write(
"""universe = vanilla
Executable = singleLepAnalyzer/step1_SLA.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 1024
Output = %(OUTPATH)s
Error = %(ERRPATH)s
Log = %(LOGPATH)s
Notification = Never
Arguments = %(YEAR)s %(CATEGORY)s %(VARIABLE)s %(JSON)s %(EOSDIR)s %(EOS_USERNAME)s
Queue 1"""%jdf_dict )
          jdf.close()        
          os.system( "condor_submit {}.job".format( os.path.join( path, jdf_name ) ) )
          
  return jsonFile
          
def step_two( jsonFile, years ):
  #check_step( jsonFile, 2 )
  jsonFile[ "STEP 2" ][ "SUBMIT" ] = "True"
  jsonFile[ "STEP 2" ][ "LOGFOLDER" ] = "log_step2_{}".format( date_tag )
  
  for year in years:
    with os.path.join( jsonFile[ "STEP 2" ][ "LOGFOLDER" ] ) as path:
      jdf_name = "{}".format( year )
      jdf_dict = {
        "LOGPATH": os.path.join( path, jdf_name + ".log" ), 
        "OUTPATH": os.path.join( path, jdf_name + ".out" ), 
        "ERRPATH": os.path.join( path, jdf_name + ".err" ),
        "YEAR": year, "JSON": args.config,
        "EOSDIR": os.path.join( varsList.step3Sample[ year ], jsonFile[ "STEP 1" ][ "EOSFOLDER" ], category ), 
        "EOS_USERNAME": varsList.eosUserName
      }
      jdf = open( os.path.join( path, jdf_name + ".job" ), "w" )
      jdf.write(
"""universe = vanilla
Executable = singleLepAnalyzer/step2_SLA.sh
Should_Transfer_Files = YES
WhentoTransferOutput = ON_EXIT
request_memory = 3072
Output = %(OUTPATH)s
Error = %(ERRPATH)s
Log = %(LOGPATH)s
Notification = Never
Arguments = %(YEAR)s %(JSON)s %(EOSDIR)s %(EOS_USERNAME)s
Queue 1"""%jdf_dict )
      jdf.close()
      os.system( "condor_submit {}.job".format( os.path.join( path, jdf_name ) ) ) 
    
  return jsonFile

def step_three():
  #check_step( jsonFile, 3 )
  return

def step_four( jsonFile ):
  #check_step( jsonFile, 4 )
  return

def step_five( jsonFile ):
  #check_step( jsonFile, 5 )
  return

def main( jsonFile, step, configuration, variables, categories, category_list, date_tag ):
  print_options( configuration, categories, category_list )
  if args.step   == "1": jsonFile = step_one( jsonFile, date_tag, years, category_list, variables )
  elif args.step == "2": jsonFile = step_two( jsonFile )
  elif args.step == "3": jsonFile = step_three( jsonFile )
  elif args.step == "4": jsonFile = step_four( jsonFile )
  elif args.step == "5": jsonFile = step_five( jsonFile )
  
  with open( args.config, "w" ) as file:
    json.dump( jsonFile, file, indent = 2, sort_keys = False )

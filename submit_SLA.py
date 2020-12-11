#!/usr/bin/python

import os, sys, json, datetime, itertools
import utils, varsList
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument( "-s", "--step",   required = True,       help = "Single Lep Analyzer step to submit" )
parser.add_argument( "-c", "--config", required = True,       help = ".json configuration file to use" )
parser.add_argument( "-t", "--test",   action = "store_true", help = "Run a unit test on a single category" )
args = parser.parse_args()

it args.step not in [ "1", "2", "3", "4", "5" ]: 
  print( "[ERR] Invalid step option used.  Please use either 1, 2, 3, 4 or 5.  Exiting program." )

with open( args.config, "r" ) as file:
  jsonFile = json.load( file )

date_tag = datetime.datetime.now().strftime( "%d.%b.%Y" )
configuration = jsonFile[ "CONFIGURATION" ]

def print_options( configuration ):
  print( ">> Using the configuration:" )
  print( ">> " )

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

def step_one( jsonFile ):
  # submission code here
  jsonFile[ "STEP 1" ][ "SUBMIT" ] = "True"
  
  for year in years:
    for variable in variables:
      os.system( "condor_submit log_step1_{}/{}_{}.job".format( date_tag, variable, year ) )

def step_two( jsonFile ):
  check_step( jsonFile, 2 )
  return jsonFile

def step_three():
  check_step( jsonFile, 3 )
  return

def step_four( jsonFile ):
  check_step( jsonFile, 4 )
  return

def step_five( jsonFile ):
  check_step( jsonFile, 5 )
  return

def main( jsonFile, step ):
  if args.step   == "1": jsonFile = step_one( jsonFile )
  elif args.step == "2": jsonFile = step_two( jsonFile )
  elif args.step == "3": jsonFile = step_three( jsonFile )
  elif args.step == "4": jsonFile = step_four( jsonFile )
  elif args.step == "5": jsonFile = step_five( jsonFile )
  
  with open( args.config, "w" ) as file:
    json.dump( jsonFile, file )
  
  
                

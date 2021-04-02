# import libraries and other scripts
import glob, os, sys, subprocess
import varsList
import numpy as np
from datetime import datetime
from argparse import ArgumentParser
from json import loads as load_json
from json import dump as dump_json

# read in arguments
parser = ArgumentParser()
parser.add_argument("-y","--year",required=True,help="The sample year (2017 or 2018)")
parser.add_argument("folders", nargs="+", help="Folders where model/weights, results are stored")
parser.add_argument("-l","--log",default="application_log_" + datetime.now().strftime("%d.%b.%Y"),help="Condor job log folder")
parser.add_argument("-v","--verbose", action="store_true", help="Verbosity option")
parser.add_argument("-t","--test", action="store_true", help="If true, produce step3 file for only one sample")
parser.add_argument("-sys","--systematics", action="store_true", help="Include systematic samples")
parser.add_argument("-s","--split",action="store_true",help="Split step2 files into # parts")
parser.add_argument("-r","--resubmit",default=None,help="Identify failed jobs from Condor logs within the input directory")

args = parser.parse_args()

# start message
if args.verbose:
    print(">> Running step 3 application for the .h5 DNN, producing new step3 ROOT files...")

# set some paths
condorDir   = varsList.step2DirEOS[ args.year ] # location where samples stored on EOS
step2Sample = varsList.step2Sample[ args.year ] 
step3Sample = varsList.step3Sample[ args.year ] 
files_step2 = {}
files_step3 = {}

# test on one signal and one background sample
if args.test:
  files_step2[ "nominal" ] = [ varsList.all_samples[ args.year ]["TTTT"][0] ]
  files_step2[ "nominal" ] = [ varsList.all_samples[ args.year ][ "TTJetsSemiLepNJet9TTjj" ][0] ]
else:
  files_step2[ "nominal" ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/nominal/".format( varsList.eosUserName, step2Sample ),shell=True).split("\n")[:-1]
  if args.resubmit != None: files_step3[ "nominal" ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/nominal/".format( varsList.eosUserName, step3Sample ),shell=True).split("\n")[:-1]
  if args.systematics:
    for syst in [ "JEC", "JER" ]:
      for dir in [ "up", "down" ]:
        files_step2[ syst+dir ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/{}{}/".format( varsList.eosUserName, step2Sample, syst, dir ), shell=True).split("\n")[:-1]
        if args.resubmit != None: files_step3[ syst+dir ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/{}{}/".format( varsList.eosUserName, step3Sample, syst, dir ), shell=True).split("\n")[:-1]

submit_files = {}
if args.verbose: print( ">> Converting the following samples to step3:" )
if args.resubmit != None:
  print( "[OPT] Running resubmission" )
  resubmit_count = 0
  out_files = [ file for file in os.listdir( args.resubmit ) if ".out" in file ]
  log_files = [ file for file in os.listdir( args.resubmit ) if ".log" in file ]

  # check for failed jobs based on .out file -- ran, but failed during filling tree in step3.py
  for out_file in out_files:
    lines = open( os.path.join( args.resubmit, out_file ) ).readlines()
    if "[OK ]" not in lines[-1]:
      sample_name = out_file.split( "hadd" )[0] + "hadd.root" 
      sample_tag = out_file.split( "hadd_" )[1].split( "." )[0] 
      if sample_tag not in submit_files.keys(): submit_files[ sample_tag ] = [ sample_name ]
      else: submit_files[ sample_tag ].append( sample_name )
      resubmit_count += 1
      if args.verbose: print( ">> Resubmitting failed job: {}".format( sample_name ) )
  # check for failed jobs based on .log and .out file -- job was held due to insufficient memory requested, resubmit with more memory
  for log_file in log_files:
    if log_file.split( "." )[0] + ".out" not in out_files:
      sample_name = log_file.split( "hadd" )[0] + "hadd.root"
      sample_tag = log_file.split( "hadd_" )[1].split( "." )[0]
      if sample_tag not in submit_files.keys():
        submit_files[ sample_tag ] = [ sample_name ]
      else: submit_files[ sample_tag ].append( sample_name )
      resubmit_count += 1
      if args.verbose: print( ">> Resubmitting suspended job: {}".format( sample_name ) )
  # check for failed jobs based on step3 in eos -- compare the step2 files with the produced step3 and see if any step3 are missing
  for key in files_step2:
    submit_files[key] = []
    for i, file in enumerate( files_step2[key] ):
      if file not in files_step3[key]:
        submit_files[key].append(file)
        resubmit_count += 1
        if args.verbose: print( ">> Resubmitting missing step3 job: {}".format( sample_name ) )
  print( ">> {} samples to resubmit".format( resubmit_count ) )
  if resubmit_count == 0: 
    print( "[OK ] No samples found to resubmit, exiting program" )    
    sys.exit()   

else:
    for key in files_step2:
        submit_files[key] = []
        print(">> {} samples to submit:".format( key ))
        for i, file in enumerate( files_step2[key] ):
            print("   {:<4} {}".format( str(i+1) + ".", file )) 
            submit_files[key].append(file)

resultDir    = args.folders                      # location where model/weights stored and where new files are output
logDir       = args.log                          # location where condor job outputs are stored
sampleDir    = varsList.step2Sample[ args.year ] # sample directory name
    
# check for parameters from json file
jsonFiles = []
jsonNames = [] 
for folder in resultDir:
  jsonCheck = glob.glob( "{}/config*.json".format(folder) )
  if len(jsonCheck) > 0:
    if args.verbose: print( ">> Using parameters file: {}".format( jsonCheck[0] ) )
    jsonNames.append(jsonCheck[0])
    jsonFiles.append(load_json(open(jsonCheck[0]).read()))
  else:
    print( "[ERR] No config .json file was found in {}, exiting program...".format( folder ) )
    sys.exit()

jsonNames_arg = ""
for jsonName in jsonNames:
  jsonNames_arg += jsonName + ", "

# check for .h5 model
models = []
for folder in resultDir:
  modelCheck = glob.glob("{}/*.h5".format(folder))
  opt_model = None
  for modelName in modelCheck:
    if "final" in modelName.lower(): opt_model = modelName
  if len(modelCheck) > 0:
    if args.verbose: print( ">> Using model: {}".format(opt_model))
    models.append(opt_model)
  else:
    print( "[ERR] No model found in {}, exiting program...".format(folder) )
    sys.exit() 

models_arg = ""
for model in models:
  models_arg += model + ", "

# define variables and containers
varList      = np.asarray( varsList.varList["DNN"] )[:,0]
variables    = [ list( jsonFile["variables"] ) for jsonFile in jsonFiles ]
   
def check_voms():
  print( ">> Checking VOMS" )
  try:
    output = subprocess.check_output( "voms-proxy-info", shell = True )
    if output.rfind( "timeleft" ) > - 1:
      if int( output[ output.rfind(": ")+2: ].replace( ":", "" ) ) > 0:
        print( "[OK ] VOMS found" )
        return True
      return False
  except: return False

def voms_init():
  if not check_voms():
    print( ">> Initializing VOMS" )
    output = subprocess.check_output( "voms-proxy-init --voms cms", shell = True )
    if "failure" in output:
      print( "[WARN] Incorrect password entered. Try again." )
      voms_init()
    print( "[OK ] VOMS initialized" )
 
def condor_job( fileName, condorDir, outputDir, logDir, tag ):
  request_memory = "10240" 
  if "tttosemilepton" in fileName.lower() and "ttjj_hadd" in fileName.lower(): request_memory = "12288" 
  if args.resubmit != None: request_memory = "12288"
  dict = {
    "MODEL"     : models_arg,          # stays the same across all samples
    "PARAMFILE" : jsonNames_arg,       # stays the same across all samples
    "FILENAME"  : fileName,            # changes with sample
    "CONDORDIR" : condorDir,           # changes with sample
    "OUTPUTDIR" : outputDir,           # stays the same across all samples
    "LOGDIR"    : logDir,              # stays the same across all samples
    "TAG"       : tag,                 # changes with sample 
    "EOSNAME"   : varsList.eosUserName,
    "MEMORY"    : request_memory
  }
  jdfName = "{}/{}_{}.job".format(logDir,fileName,tag)
  jdf = open(jdfName, "w")
  jdf.write(
"""universe = vanilla
Executable = application.sh
Should_Transfer_Files = Yes
WhenToTransferOutput = ON_EXIT
request_memory = %(MEMORY)s
Transfer_Input_Files = %(MODEL)s %(PARAMFILE)s
Output = %(LOGDIR)s/%(FILENAME)s_%(TAG)s.out
Error = %(LOGDIR)s/%(FILENAME)s_%(TAG)s.err
Log = %(LOGDIR)s/%(FILENAME)s_%(TAG)s.log
Notification = Never
Arguments = %(CONDORDIR)s %(FILENAME)s %(OUTPUTDIR)s %(EOSNAME)s %(TAG)s
Queue 1"""%dict
  )
  jdf.close()
  os.system( "condor_submit {}".format( jdfName ) )
    
def submit_jobs( files, key, condorDir, logrDir, sampleDir ):
  os.system( "mkdir -p " + logrDir )
  outputDir = sampleDir.replace("step2","step3") + "/" + key
  if args.verbose: print( ">> Making new EOS directory: store/user/{}/{}/".format( varsList.eosUserName, outputDir ) )
  os.system( "eos root://cmseos.fnal.gov mkdir store/user/{}/{}/".format( varsList.eosUserName, sampleDir.replace( "step2","step3" ) ) )
  os.system( "eos root://cmseos.fnal.gov mkdir store/user/{}/{}/".format( varsList.eosUserName, outputDir ) ) 
  jobCount = 0
  for file in files[key]:
    if args.verbose: print( ">> Submitting Condor job for {}/{}".format( key, file ) )
    condor_job( file.split(".")[0], condorDir, outputDir, logDir, key )
    jobCount += 1
  print( ">> {} jobs submitted for {}/...".format( jobCount, key ) )
  return jobCount

def main( files, variables, models ):    
# display variables being used
  if args.verbose:
    for i in range(len(variables)):
      print(">> Using {} variables in {}:".format(len(variables[i]),models[i]))

# run the submission
  count = 0
  for key in files_step2:
    count += submit_jobs(files,key,condorDir,logDir,sampleDir)
  print("\n>> {} total jobs submitted...".format(count))
  if args.verbose: print( "[OK ] Application Condor job logs stored in {}".format( logDir ) )

voms_init()
main(submit_files,variables,models)

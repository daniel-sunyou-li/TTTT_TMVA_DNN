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
parser.add_argument("-r","--resubmit",action="store_true",help="Resubmit failed jobs with more memory")

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

if args.test:
    files_step2[ "nominal" ] = [ varsList.all_samples[ args.year ]["TTTT"][0] ]
else:
    files_step2[ "nominal" ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/nominal/".format( varsList.eosUserName, step2Sample ),shell=True).split("\n")[:-1]
    if args.resubmit: files_step3[ "nominal" ] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/nominal/".format( varsList.eosUserName, step3Sample ),shell=True).split("\n")[:-1]
    if args.systematics:
        for syst in [ "JEC", "JER" ]:
            for dir in [ "up", "down" ]:
                files_step2[syst+dir] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/{}{}/".format( varsList.eosUserName, step2Sample, syst, dir ), shell=True).split("\n")[:-1]
                if args.resubmit: files_step3[syst+dir] = subprocess.check_output("eos root://cmseos.fnal.gov ls /store/user/{}/{}/{}{}/".format( varsList.eosUserName, step3Sample, syst, dir ), shell=True).split("\n")[:-1]

submit_files = {}
if args.verbose: print(">> Converting the following samples to step3:")
if args.resubmit:
    print("[OPT] Running resubmission")
    for key in files_step2:
        submit_files[key] = []
        print(">> {} samples to resubmit ( {} / {} ):".format( key, len( files_step2[key] ) - len( files_step3[key] ), len( files_step2[key] ) ) )
        for i, file in enumerate( files_step2[key] ):
            if file not in files_step3[key]:
                print("    {:<4} {}".format( str(i+1) + ".", file ))
                submit_files[key].append(file)

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
    jsonCheck = glob.glob("{}/parameters*.json".format(folder))
    if len(jsonCheck) > 0:
        if args.verbose:
            print(">> Using parameters file: {}".format(jsonCheck[0]))
        jsonNames.append(jsonCheck[0])
        jsonFiles.append(load_json(open(jsonCheck[0]).read()))
    else:
        print("[ERR] No parameters .json file was found in {}, exiting program...".format(folder))
        sys.exit()

jsonNames_arg = ""
for jsonName in jsonNames:
    jsonNames_arg += jsonName + ", "

# check for .h5 model
models = []
for folder in resultDir:
    modelCheck = glob.glob("{}/*.h5".format(folder))
    if len(modelCheck) > 0:
        if args.verbose:
            print(">> Using model: {}".format(modelCheck[0]))
        models.append(modelCheck[0])
    else:
        print("[ERR] No model found in {}, exiting program...".format(folder))
        sys.exit() 

models_arg = ""
for model in models:
    models_arg += model + ", "

# define variables and containers
varList = np.asarray(varsList.varList["DNN"])[:,0]
variables    = [ list(jsonFile["variables"]) for jsonFile in jsonFiles ]
    
def condor_job(fileName,condorDir,outputDir,logDir,tag):
    request_memory = "3072" 
    if "tttosemilepton" in fileName.lower() and "ttjj" in fileName.lower(): request_memory = "6144" 
    if args.resubmit: request_memory = "7168"
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
    os.system("condor_submit {}".format(jdfName))
    
def submit_jobs(files,key,condorDir,logrDir,sampleDir):
    os.system("mkdir -p " + logrDir)
    outputDir = sampleDir.replace("step2","step3") + "/" + key
    if args.verbose: print(">> Making new EOS directory: store/user/{}/{}/".format(varsList.eosUserName,outputDir))
    os.system("eos root://cmseos.fnal.gov mkdir store/user/{}/{}/".format(varsList.eosUserName,sampleDir.replace("step2","step3")))
    os.system("eos root://cmseos.fnal.gov mkdir store/user/{}/{}/".format(varsList.eosUserName,outputDir)) 
    jobCount = 0
    for file in files[key]:
        if args.verbose: print(">> Submitting Condor job for {}/{}".format(key,file))
        condor_job(file.split(".")[0],condorDir,outputDir,logDir,key)
        jobCount += 1
    print(">> {} jobs submitted for {}/...".format(jobCount,key))
    return jobCount

def main(files,variables,models):    
# display variables being used
    if args.verbose:
        for i in range(len(variables)):
            print(">> Using {} variables in {}:".format(len(variables[i]),models[i]))
#            for i, variable in enumerate(variables[i]): print("   {:<4} {}".format(str(i)+".",variable))

# run the submission
    count = 0
    for key in files_step2:
        count += submit_jobs(files,key,condorDir,logDir,sampleDir)
    print("\n>> {} total jobs submitted...".format(count))
    if args.verbose: print(">> Application Condor job logs stored in {}".format(logDir))

main(submit_files,variables,models)

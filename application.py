# import libraries and other scripts
import glob, os, sys
import varsList
from datetime import datetime
from argparse import ArgumentParser
from json import loads as load_json
from json import dump as dump_json

# read in arguments
parser = ArgumentParser()
parser.add_argument("-y","--year",required=True,help="The sample year (2017 or 2018)")
parser.add_argument("-f","--folder",required=True,help="Folder where model/weights, results are stored")
parser.add_argument("-l","--log",default="application_log_" + datetime.now().strftime("%d.%b.%Y"),help="Condor job log folder")

args = parser.parse_args()

# load-in parameters from json file
jsonFile = None
jsonCheck = glob.glob("{}/parameters*.json".format(args.folder))
if len(jsonCheck) > 0:
    jsonFile = open(jsonCheck[0])
    jsonFile = load_json(jsonFile.read())
else:
    print("No parameters .json file was found, exiting program...")
    sys.exit()
weightFile = None
weightCheck = glob.glob("{}/*.xml".format(args.folder))
if len(weightCheck) > 0:
    weightFile = open(weightCheck[0])
    weightFile = load_json(weightFile.read())
else:
    print("No trained weights .xml file was found, exiting program...")
    sys.exit() 

# define variables and containers
varList = np.asarray(varsList.varList["DNN"])[:,0]
# need to check with Adam how the order of the variables is sorted in mltools.py since it's not obvious to memoryview
# need to make sure that the variable ordering in application.C matches the expected input for the trained model/weights
variables    = jsonFile[list(jsonFile.keys())[0]]["parameters"]["variables"]
inputDir     = varsList.condorDirLPC2018 if year == "2018" else varsList.condorDirLPC2017 # location where samples stored on EOS
files        = [file.split(".")[0] for file in list(glob.glob("inputDir/*.root"))] # all ROOT sample file names
resultDir    = args.folder # location where model/weights stored and where new files are output
condorDir    = args.log    # location where condor job outputs are stored
sampleDir    = varsList.step2Sample2018 if year == "2018" else varsList.step2Sample2017 # sample directory name

def condor_job(fileName,resultDir,inputDir,condorDir):
# I think this is adapted for BRUX currently, so need to adapt it to LPC
# main concern is the file referencing, which can be handled by cmseos
    dict = {
        "WGTFILE"  : weightCheck[0],
        "PARAMFILE": jsonCheck[0],
        "FILENAME" : fileName,
        "RESULTDIR": resultDir,
        "INPUTDIR" : inputDir,
        "CONDORDIR": condorDir
    }
    jdfName = "{}/{}.job".format(condorDir,fileName)
    jdf = open(jdfName, "w")
    jdf.write(
"""universe = vanilla
Executable = application.sh
Should_Transfer_Files = Yes
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Transfer_Input_Files = step3.py, varsList.py, $(WGTFILE)s, $(PARAMFILE)s
Output = %(CONDORDIR)s/%(FILENAME)s.out
Error = %(CONDORDIR)s/%(FILENAME)s.err
Log = %(CONDORDIR)s/%(FILENAME)s.log
Notification = Never
Arguments = %(INPUTDIR)s %(RESULTDIR)s %(FILENAME)s.root $(CONDORDIR)s
Queue 1"""%dict
    )
    jdf.close()
    os.system("%(CONDORDIR)s/condor_submit %(FILENAME)s.job"%dict)
    
def submit_jobs(templateFile,variables,files,inputDir,resultDir,condorDir,sampleDir):
    os.system("mkdir -p " + condorDir)
    os.system("eos root://cmseos.fnal.gov mkdir store/user/{}/{}/step3/".format(varsList.eosUserName,sampleDir)) 
    make_application_config(templateFile,resultDir,variables)
    jobCount = 0
    for file in files:
        print("Submitting Condor job for {}".format(file))
        condor_job(file,folder,inputDir,resultDir,condorDir)
        jobCount += 1
    print("{} jobs submitted...".format(jobCount))
    print("Application Condor job logs stored in {}".format(condorDir))
    
# run the submission
submit_jobs(templateFile,variables,files,inputDir,resultDir,condorDir,sampleDir)

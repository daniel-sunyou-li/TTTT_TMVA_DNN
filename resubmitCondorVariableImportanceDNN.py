#/usr/bin/env python
import glob, os, sys 
import getopt
import math
import varsList

def condorJob(SeedN="",SubSeedN="",count=0,options=['','','']): # submits a single condor job
    runDir = options[0]
    condorDir = options[1]
    numVars = options[2]
    SubmitSeedN = ""
    if SubSeedN == "": 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN)
        SubmitSeedN = SeedN
    else: 
        fileName = "Keras_" + str(numVars) + "vars_Seed_" + str(SeedN) + "_Subseed_" + str(SubSeedN)
        SubmitSeedN = SubSeedN
    dict = {
        "RUNDIR": runDir,           # run directory
        "METHOD": "Keras",          # tmva method, should be "Keras"
        "SubmitSeedN": SubmitSeedN,
        "TAG": str(count),
        "FILENAME": fileName
    }
    jdfName = condorDir + "%(FILENAME)s.job"%dict
    jdf = open(jdfName, "w")
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 4025
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(TAG)s %(SubmitSeedN)s
Queue 1"""%dict)
    jdf.close()
    os.chdir("%s/"%(condorDir))
    os.system("condor_submit %(FILENAME)s.job"%dict)
    os.system("sleep 0.5")
    os.chdir("%s"%(runDir))
    count += 1
    return count
    
options = [
    os.getcwd(),
    os.getcwd() + "/condor_log/",
    len(varsList.varList["BigComb"])
]

RESUBMIT = True

finished_count = 0
count = 0

seedList = []           # holds all seed keys
seedDict = {}           # seeds are the key and subseeds are the entries

seedStrDir = os.listdir(options[1])

for seedStr in seedStrDir:
    if "Subseed_" not in seedStr and ".out" in seedStr:
        seed = seedStr.split("_Seed_")[1].split(".out")[0]
        seedList.append(seed)
        
for seed in seedList:
    subSeedArr = glob.glob(options[1] + "Keras_" + str(options[2]) + "vars_Seed_" + seed + "_Subseed_*.out")
    seedDict[seed] = subSeedArr

maxSeed = str(int("1"*options[2],2))
formSize = max(len(maxSeed) + 1, 8)
seedDictNum = sum([len(x) for x in seedDict.values()])
print("Total seeds: {}, Total subseeds: {}".format(len(seedList),seedDictNum))
print("{:{}}{:{}}{:10}".format("Seed",formSize,"Subseed",formSize,".out Size (b)"))
# resubmit the seed jobs that failed
for seed in seedDict:
    fileName = "Keras_" + str(options[2]) + "vars_Seed_" + seed
    check_one = True        # checks if "ROC-integral" is in .out file
    check_two = False       # checks if file is done running
    
    # perform first check on [fileName].out
    for line in open(options[1] + fileName + ".out").readlines():
        # don't want to resubmit if "ROC-integral" is already calculated
        if "ROC-integral" in line: 
            check_one = False
            finished_count += 1
    if check_one:
        for line in open(options[1] + fileName + ".log").readlines():
            # if 005 is the last condor status, then do resubmit
            if "005 (" in line: check_two = True
            # if 000 or 006, then the job is either in queue or running
            elif "006 (" in line: check_two = False
            elif "000 (" in line: check_two = False
            elif "001 (" in line: check_two = False
    if check_one and check_two:
        fileSize = os.stat(options[1] + fileName + ".out").st_size
        print("{:<{}}{:<{}}{:<10}".format(seed,formSize,"",formSize,fileSize))
        if RESUBMIT:
          count = condorJob(SeedN=seed,count=count,options=options)
          print("would resubmit")
    for subseedStr in seedDict[seed]:
        subseed = subseedStr.split("_Subseed_")[1].split(".out")[0]
        fileNameSS = fileName + "_Subseed_" + subseed
        check_one = True
        check_two = False
        for line in open(options[1] + fileNameSS + ".out").readlines():
            if "ROC-integral" in line:
                check_one = False
                finished_count += 1
        if check_one:
            for line in open(options[1] + fileNameSS + ".log").readlines():
                if "005 (" in line: check_two = True
                elif "006 (" in line: check_two = False
                elif "000 (" in line: check_two = False
                elif "001 (" in line: check_two = False
        if check_one and check_two:
            fileSize = os.stat(options[1] + fileNameSS + ".out").st_size
            print("{:<{}}{:<{}}{:<5}".format(seed,formSize,subseed,formSize,fileSize))
            if RESUBMIT:
              count = condorJob(seed,subseed,count,options)

total_seeds = len(seedList) + seedDictNum
percent_done = ( float(finished_count) / float(total_seeds) ) * 100
print("___________________")
print("{} out of {} ({:.2f}%) Jobs Done".format(finished_count,total_seeds,percent_done))
print("{} Jobs Resubmitted.".format(count))

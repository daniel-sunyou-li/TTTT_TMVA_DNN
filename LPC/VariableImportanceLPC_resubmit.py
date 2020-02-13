#/usr/bin/env python
import glob, os, sys 
import getopt
import math

sys.path.insert(0, "../TTTT_TMVA_DNN")
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
        "SubmitSeedN": SubmitSeedN,
        "FILENAME": fileName
    }
    jdfName = condorDir + "%(FILENAME)s.job"%dict
    jdf = open(jdfName, "w")
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/LPC/VariableImportanceLPC_step2.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 4.2 GB
request_cpus = 4
request_disk = 40 GB
image_size = 4 GB
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
    print("{} jobs submitted.".format(count))
    return count
    
options = [
    os.getcwd(),
    os.getcwd() + "/condor_log/",
    len(varsList.varList["BigComb"])
]

# checks if job was removed by scheduler (false)
def check_one(seedOut,seedOutDirectory):
    if seedOut in seedOutDirectory: return True
    else: return False

# checks if condor job is done running (true)
def check_two(condorPath,seedLog):
    condorJobDone = False
    for line in open(condorPath + seedLog).readlines():
        if "005 (" or "009 (" in line: 
            condorJobDone = True
        elif "006 (" or "000 (" or "001 (" in line:
            condorJobDone = False
        else: condorJobDone = True
    return condorJobDone

# check if ROC-integral is in .out file
def check_three(condorPath,seedOut):
    isROC = False
    for line in open(condorPath + seedOut).readlines():
        if "ROC-Integral" in line: isROC = True
    return isROC

finished_count = 0
count = 0

seedList = []           # holds all seed keys
seedDict = {}           # seeds are the key and subseeds are the entries

seedDirectory = os.listdir(options[1])
seedOutDirectory = [seedStr for seedStr in seedDirectory if ".out" in seedStr]
seedJobDirectory = [seedStr for seedStr in seedDirectory if ".job" in seedStr]
seedLogDirectory = [seedStr for seedStr in seedDirectory if ".log" in seedStr]

for seedStr in seedStrDir:
    if "Subseed_" not in seedStr and ".job" in seedStr:
        seed = seedStr.split("_Seed_")[1].split(".out")[0]
        seedList.append(seed)
        
for seed in seedList:
    subSeedArr = glob.glob(options[1] + "Keras_" + str(options[2]) + "vars_Seed_" + seed + "_Subseed_*.out")
    seedDict[seed] = subSeedArr

maxSeed = str(int("1"*options[2],2))
formSize = max(len(maxSeed) + 1, 8)     # print formatting setting
seedDictNum = sum([len(x) for x in seedDict.values()])
print("Total seeds: {}, Total subseeds: {}".format(len(seedList),seedDictNum))
print("{:{}}{:{}}{:10}".format("Seed",formSize,"Subseed",formSize,".out Size (b)"))
# resubmit the seed jobs that failed
for seed in seedDict:
    fileName = "Keras_" + str(options[2]) + "vars_Seed_" + seed
    seedOut = fileName + ".out"
    seedLog = fileName + ".log"
    seedJob = fileName + ".job"
    
    if check_three(options[1],seedOut) == False:    # checks if ROC-integral is present
        if check_two(options[1],seedLog) == True:   # checks if job finished running
            if check_one(seedOut,seedOutDirectory): # checks if the .out file was produced
                fileSize = os.stat(options[1] + fileName + ".out").st_size
                print("{:<{}}{:<{}}{:<10}".format(seed,formSize,"",formSize,fileSize))
                count = condorJob(SeedN=seed,count=count,options=options)
                
    for subSeed in seedDict[seed]:
        fileName = "Keras_" + str(options[2]) + "vars_Seed_" + seed + "_Subseed_" + subSeed
        subSeedOutDirectory = []
        subSeedOut = fileName + ".out"
        subSeedLog = fileName + ".log"
        subSeedJob = fileName + ".job"
        
        if check_three(options[1],subSeedOut) == False:
            if check_two(options[1],subSeedLog) == True:
                if check_one(subSeedOut,seedDict[seed]):
                    fileSize = os.stat(options[1] + fileName + ".out").st_size
                    print("{:<{}}{:<{}}{:<10}".format(seed,formSize,subSeed,formSize,fileSize))
                    count = condorJob(SeedN=subSeed,count=count,options=options)
        

total_seeds = len(seedList) + seedDictNum
percent_done = ( float(finished_count) / float(total_seeds) ) * 100
print("___________________")
print("{} out of {} ({:.2f}%) Jobs Done".format(finished_count,total_seeds,percent_done))
print("{} Jobs Resubmitted.".format(count))

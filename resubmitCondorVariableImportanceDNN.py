#/usr/bin/env python
import glob, os, sys 
import math
import varsList

outPath.os.getcwd()
outFile = os.listdir(outpath + '/condor_log/')

numVars = 11
nTrees = "100"
method = "Keras"
mDepth = "2"
runDir = os.getcwd()
condorDir = runDir + "/condor_log/"
os.system("mkdir -p " + condorDir)

varListKeys = ["BigComb"]
varList = varsList.varList["BigComb"]

seedList = []

for Files in outFile:
  if "Subseed_" not in Files and ".out" in Files:
    seedList.append(Files.split("_Seed_")[1].split(".out")[0])
    
os.chdir(outPath+'/condor_log')

seedDict = {}         # seeds are keys and subseeds are entries
seedResubmit = []     # seeds to resubmit
subseedResubmit = {}  # subseeds to resubmit

for index, seed in enumerate(seedList):
  if index > 100: break
  seedDict[seed] = glob.glob("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seed + "_Subseed_*.out")
  
for seed in seedDict:
  write_bool = True
  for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seed + ".out").readlines():
    if "ROC-integral" in line: write_bool = False
  if write_bool == True:
    seedResubmit.append(seed)
  for subseedout in seedDict[seed]:
    subseed = subseedout.split("_Subseed_")[1].split(".out")[0]
    write_bool = True
    for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seed + "_Subseed_" + subseed + ".out").readlines():
      if "ROC-integral" in line: write_bool = False
    if write_bool == True:
      if seed in subseedResubmit.keys():
        subseedResubmit[seed].append(subseed)
      else:
        subseedResubmit[seed] = [subseed]
      
# Submit the condor jobs

for seed in seedResubmit:
  outf_key = "Seed_" + str(seed)
  fileName = method + "_" + "BigComb" + "_" + str(len(varList)) + "vars_mDepth" + mDepth + "_" + outf_key
  dict = {
    "RUNDIR":runDir,
    "METHOD":method,
    "vListKey":"BigComb",
    "nTrees":nTrees,
    "mDepth":mDepth,
    "SeedN":seed,
    "FILENAME":fileName
  }
  jdfName = condorDir + "%(FILENAME)s.job"%dict
  print(jdfName)
  print("Resubmitting seed: {}".format(seed))
  jdf = open(jdfName, "w")
  jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportance.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SeedN)s %(nTrees)s %(mDepth)s
Queue 1"""%dict
  )
  jdf.close()
  os.chdir("%s/"%(condorDir))
  os.system("condor_submit %(FILENAME)s.job"%dict)
  os.system("sleep 0.5")
  os.chdir("%s"%(runDir))

for seed in subseedResubmit:
  for subseed in subseedResubmit[seed]:
    outf_key = "Seed_" + str(seed) + "_Subsed_" + str(subseed)
    fileName = method + "_" + "BigComb" + "_" + str(len(varList)) + "vars_mDepth" + mDepth + "_" + outf_key
    dict_sub = {
      "RUNDIR":runDir,
      "METHOD":method,
      "vListKey":"BigComb",
      "nTrees":nTrees,
      "mDepth":mDepth,
      "SeedN":seed,
      "SubSeedN":subseed,
      "FILENAME":fileName
    }
    jdfName = condorDir + "%(FILENAME)s.job"%dict_sub
    print(jdfName)
    print("Resubmitting seed, subseed: {}, {}".format(seed,subseed))
    jdf = open(jdfName,"w")
    jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportance.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SubSeedN)s %(nTrees)s %(mDepth)s
Queue 1"""%dict_sub
    )
    jdf.close()
    os.chdir("%s/"%(condorDir))
    os.system("condor_submit %(FILENAME)s.job"%dict_sub)
    os.system("sleep 0.5")
    os.chdir("%s"%(runDir))
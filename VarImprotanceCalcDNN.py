#!/usr/bin/env python
import glob, os, math
import varsList

outPath = os.getcwd()
outFile = os.listdir(outpath+'/condor_log/')

numVars = 6

seedList = []
for Files in outFile:
  if "Subseed_" not in Files and ".out" in Files:
    seedList.append(Files.split("_Seed_")[1].split(".out")[0])

os.chdir(outPath+'/condor_log')

seedDict = {}
for index, seed in enumerate(seedList):
  if index > 100: break
  seedDict[seed] = glob.glob("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seed + "_Subseed_*.out")
 
importances = {}
for index in range(0,numVars):
  importances[index] = 0
  
for seeds in seedDict:
  l_seed = long(seeds)
  print("Seed:",seeds)
  for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seeds + ".out").readlines():
    if "ROC-integral" in line:
      SROC = float(line[:-1].split(' ')[-1])
  for subseedout in seedDict[seeds]:
    subseed = subseedout.split("_Subseed_")[1].split(".out")[0]
    l_subseed = long(subseed)
    varIndx = math.log(l_seed - l_subseed)/0.693147
    for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seeds + "_Subseed_" + subseeds + ".out").readlines():
      if "ROC-integral" in line:
        SSROC = float(line[:-1].split(" ")[-1])
        importances[int(varIndx)] += SROC - SSROC
        
normalization = 0;
for index in range(0,numVars):
  normalization += importances[index]
  
for index in range(0,numVars):
  print("Importance:",100*importances[index]/normalization,"\t\tvariable:",varsList.varList["BigComb"][index][0])
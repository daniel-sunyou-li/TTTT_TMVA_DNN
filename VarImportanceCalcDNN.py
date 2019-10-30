#!/usr/bin/env python
import glob, os, math
import varsList
import datetime

outPath = os.getcwd()
outFile = os.listdir(outPath+'/condor_log/')

numVars = 11
bit_str = "00000000010"

varImportance_file = open(outPath+'/dataset/'+bit_str+'/VarImportanceCalculation.txt','w')

varImportance_file.write("Bit string: {}, Date: {}".format(bit_str,datetime.datetime.today().strftime('%Y-%m-%d')))

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
  varImportance_file.write("\nSeed: {}, Subseeds: ".format(seeds))
  for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seeds + ".out").readlines():
    if "ROC-integral" in line:
      SROC = float(line[:-1].split(' ')[-1][:-1])
  for subseedout in seedDict[seeds]:
    subseed = subseedout.split("_Subseed_")[1].split(".out")[0]
    l_subseed = long(subseed)
    varImportance_file.write("{} ".format(subseed))
    varIndx = math.log(l_seed - l_subseed)/0.693147
    for line in open("Keras_BigComb_" + str(numVars) + "vars_mDepth2_Seed_" + seeds + "_Subseed_" + subseed + ".out").readlines():
      if "ROC-integral" in line:
        SSROC = float(line[:-1].split(" ")[-1][:-1])
        importances[int(varIndx)] += SROC - SSROC
        
normalization = 0;
for index in range(0,numVars):
  normalization += importances[index]
  
varImportance_file.write("\nImportance calculation:")
varImportance_file.write("\nNormalization: {}".format(normalization))
varImportance_file.write("\nVariable,Importance:")

for index in range(0,numVars):
  varImportance_file.write("\n{},{}".format(varsList.varList["BigComb"][index][0],100*importances[index]/normalization))

print("Finished variable importance calculation for {}".format(bit_str))

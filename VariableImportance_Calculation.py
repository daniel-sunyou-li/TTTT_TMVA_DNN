#!/usr/bin/env python
import glob, os, math
import varsList
import datetime
import numpy as np

def get_seeds(filePath):
  seedList  = []
  seedDict = {}
  fileDirectory = os.listdir(filePath)
  outFileDirectory = [seedStr for seedStr in fileDirectory if ".out" in seedStr]
  numVars = int(outFileDirectory[0].split("vars_")[0].split("Keras_")[1])
  for outFile in outFileDirectory:
    if "Subseed_" not in outFile and ".out" in outFile:
      seedList.append(outFile.split("_Seed_")[1].split(".out")[0])
  for indx, seed in enumerate(seedList):
    seedDict[seed] = glob.glob(filePath + "Keras_" + str(numVars) + "vars_Seed_" + seed + "_Subseed_*.out")
  return seedDict, numVars

def variable_occurence(count_arr,seed):
  seed_str = "{:0{}b}".format(seed,len(count_arr))
  for count, variable in enumerate(seed_str):
    if variable == "1": count_arr[count] += 1
  return count_arr

def variable_importance(filePath="",outPath="",seedDict={},numVars=0,option=0):
  importances = {}
  count_arr = np.zeros(numVars)
  numVars = numVars
  if option == 1:
    varImportanceFile = open(outPath + "/dataset/VariableImportanceResults_" + str(numVars) + "vars_opt1.txt","w")
  else:
    varImportanceFile = open(outPath + "/dataset/VariableImportanceResults_" + str(numVars) + "vars_opt0.txt","w")
  varImportanceFile.write("Number of Variables: {}, Date: {}".format(
    numVars,
    datetime.datetime.today().strftime("%Y-%m-%d")
  ))
  if option == 1:
    for indx in np.arange(numVars): importances[indx] = []
  else:
    for indx in np.arange(numVars): importances[indx] = 0
  print("Calculating variable importance...")
  varImportanceFile.write("\n{:<3}: {:<25} {:<12}".format("#","Seed","# Vars"))
  for indx,seed in enumerate(seedDict):
    seed_long = long(seed)
    seed_str = "{:0{}b}".format(int(seed),int(numVars))
    count_arr = variable_occurence(count_arr,int(seed))
    varImportanceFile.write("\n{:<3}: {:<25} {:<12}".format(indx+1,seed,seed_str.count("1")))
    for line in open(filePath + "Keras_" + str(numVars) + "vars_Seed_" + seed + ".out").readlines():
      if "ROC-integral" in line: SROC = float(line[:-1].split(" ")[-1][:-1])
    for subseedOut in seedDict[seed]:
      subseed = subseedOut.split("_Subseed_")[1].split(".out")[0]
      subseed_long = long(subseed)
      varIndx = numVars -  int( math.log( seed_long - subseed_long ) / 0.693147 ) - 1
      for line in open(filePath + "Keras_" + str(numVars) + "vars_Seed_" + seed + "_Subseed_" + subseed + ".out").readlines():
        if "ROC-integral" in line:
          SSROC = float(line[:-1].split(" ")[-1][:-1])
          if option == 1:
            importances[varIndx].append( SROC - SSROC )
          else:
            importances[varIndx] += SROC - SSROC

  importance_stats = {}
  normalization = 0
  if option == 1:
    for varIndx in importances:
      if not importances[varIndx]: importances[varIndx] = [0]
      importance_stats[varIndx] = np.array( [np.mean(importances[varIndx]),np.std(importances[varIndx])] )
      normalization += abs(importance_stats[varIndx][0])
    for varIndx in importances:
      importance_stats[varIndx] = ( 100. / normalization ) * importance_stats[varIndx]
    varImportanceFile.write("\nImportance calculation:")
    varImportanceFile.write("\nNormalization: {}".format(normalization))
    varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<7} / {:<7}".format("Index","Variable Name","Freq.","Mean","RMS"))
    for varIndx in importance_stats:
      varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<7.4f} / {:<7.4f}".format(
        str(varIndx+1)+".",
        varsList.varList["BigComb"][varIndx][0],
        count_arr[varIndx],
        importance_stats[varIndx][0],
        importance_stats[varIndx][1]
      ))
  else:
    for indx in np.arange(numVars): normalization += importances[indx]
    varImportanceFile.write("\nImportance calculation:")
    varImportanceFile.write("\nNormalization: {}".format(normalization))
    varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<8}:".format("Index","Variable Name","Freq","Importance"))
    for indx in np.arange(numVars):
      varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<8.4f}".format(
        str(indx+1)+".",
        varsList.varList["BigComb"][indx][0],
        count_arr[indx],
        100.*importances[indx] / normalization
      ))
  varImportanceFile.close()

filePath = os.getcwd() + "/condor_log/"
outPath = os.getcwd()

seedDict, numVars = get_seeds(filePath)

variable_importance(filePath,outPath,seedDict,numVars,0)
print("Saving results to {}".format(outPath + "/dataset/"))


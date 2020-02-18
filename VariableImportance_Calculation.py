#!/usr/bin/env python
import glob, os, sys, math
import varsList
import datetime
import numpy as np

condor_dirs = [ # if combining multiple results, add to this array, must have same variables (in order)
    "condor_log" 
]

def get_seeds(condor_dirs):
    seedListDict = {}
    seedDict = {}
    fileDirectories = {}
    outFileDirectories = {}
    numVarsDir = {}
    numVars = 0
    for condor_dir in condor_dirs:
        fileDirectories[condor_dir] = os.listdir(os.getcwd() + "/" + condor_dir)
        outFileDirectories[condor_dir] = [seedStr for seedStr in fileDirectory[condor_dir] if ".out" in seedStr]
        numVarsDir[condor_dir] = int(outFileDirectories[condor_dir][0].split("vars_")[0].split("Keras_")[1])
    if len(set(numVarsDir.values())) > 1:
        print("Condor jobs used different number of input variables, cannot combine variable importance calculation.")
        sys.exit(0)
    else:
        numVars = set(numVarsDir.values())
    for key in outFileDirectories:
        seedListDict[key] = []
        seedDict[key] = {}
        for outFile in outFileDirectories[key]:
            if "Subseed_" not in outFile and ".out" in outFile:
                seedListDict[key].append(outFile.split("_Seed_")[1].split(".out")[0])
        for indx, seed in enumerate(seedListDict[key]):
            seedDict[key][seed] = glob.glob(os.getcwd() + "/" + key + "/Keras_" + str(numVars) + "vars_Seed_" + seed + "_Subseed_*.out")
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
    for key in seedDict:
        for indx,seed in enumerate(seedDict[key]):
            seed_long = long(seed)
            seed_str = "{:0{}b}".format(int(seed),int(numVars))
            count_arr = variable_occurence(count_arr,int(seed))
            varImportanceFile.write("\n{:<3}: {:<25} {:<12}".format(indx+1,seed,seed_str.count("1")))
            for line in open(filePath + "Keras_" + str(numVars) + "vars_Seed_" + seed + ".out").readlines():
                if "ROC-integral" in line: SROC = float(line[:-1].split(" ")[-1][:-1])
            for subseedOut in seedDict[key][seed]:
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
            importance_stats[varIndx] = importance_stats[varIndx] / normalization
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
                importances[indx] / normalization
            ))
    varImportanceFile.close()
  
    if option == 1:
        np.save("ROC_hists_" + str(numVars) + "vars_opt1",importance_stats)
    else:
        np.save("ROC_hists_" + str(numVars) + "vars_opt0",importances)
  

# Run the program  

seedDict, numVars = get_seeds(condor_dirs)

variable_importance(filePath,outPath,seedDict,numVars,0)
print("Saving results to {}".format(os.getcwd() + "/dataset/"))

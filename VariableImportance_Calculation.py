#!/usr/bin/env python
import glob, os, sys, math
import varsList
import datetime
import argparse
import numpy as np

# Parse directories to work with
condorDirs = []

parser = argparse.ArgumentParser()
parser.add_argument("folders", nargs="*", default=[], help="condor_log folders to use, default is all condor_log*")
args = parser.parse_args()

for d in args.folders:
    if os.path.exists(os.path.join(os.getcwd(), d)):
        condorDirs.append(os.path.join(os.getcwd(), d))
    elif os.path.exists(d):
        condorDirs.append(d)

if condorDirs == []:
    condorDirs = [os.path.join(os.getcwd(), d) for d in os.listdir(os.getcwd()) if d.startswith("condor_log")]

print "Variable Importance Calculator"
print "Folders: \n - " + "\n - ".join(condorDirs)

def get_seeds(condor_dirs):
    seedListDict = {}
    seedDict = {}
    fileDirectories = {}
    outFileDirectories = {}
    numVars = -1
    for condor_dir in condor_dirs:
        fileDirectories[condor_dir] = os.listdir(condor_dir)
        outFileDirectories[condor_dir] = [seedStr for seedStr in fileDirectories[condor_dir] if ".out" in seedStr]
        if numVars == -1:
            numVars = int(outFileDirectories[condor_dir][0].split("vars_")[0].split("Keras_")[1])
            print("Set numVars to {}.".format(numVars))
        elif int(outFileDirectories[condor_dir][0].split("vars_")[0].split("Keras_")[1]) != numVars:
            print "Condor jobs used different number of input variables, cannot combine variable importance calculation."
            sys.exit(1)
    for key in outFileDirectories:
        print "Scanning " + key
        seedListDict[key] = []
        seedDict[key] = {}
        for outFile in outFileDirectories[key]:
            if "Subseed_" not in outFile:
                seedListDict[key].append(outFile.split("_Seed_")[1].split(".out")[0])
        for indx, seed in enumerate(seedListDict[key]):
            seedDict[key][seed] = glob.glob(key + "/Keras_" + str(numVars) + "vars_Seed_" + seed + "_Subseed_*.out")
    return seedDict, numVars

def variable_occurence(count_arr, seed):
    seed_str = "{:0{}b}".format(seed, len(count_arr))
    for count, variable in enumerate(seed_str):
        if variable == "1": count_arr[count] += 1
    return count_arr

def variable_importance(seedDict={}, numVars=0):
    importances = {}
    count_arr = np.zeros(numVars)
    varImportanceFile = open("./dataset/VariableImportanceResults_" + str(numVars) + "vars.txt", "w")
    varImportanceFile.write("Weight: {}\n".format(varsList.weightStr))
    varImportanceFile.write("Cut: {}\n".format(varsList.cutStr))
    varImportanceFile.write("Folders: \n - " + "\n - ".join(condorDirs) + "\n")
    varImportanceFile.write("Number of Variables: {}, Date: {}\n".format(
        numVars,
        datetime.datetime.today().strftime("%Y-%m-%d")
    ))
    for indx in range(numVars):
        importances[indx] = []
    print("Calculating variable importance...")
    #varImportanceFile.write("{:<3}: {:<{}} {:<10}".format("#", "Seed", numVars+2, "# Vars"))
    for key in seedDict:
        print("Processing {}".format(key))
        for indx, seed in enumerate(seedDict[key]):
            seed_long = long(seed)
            seed_str = "{:0{}b}".format(int(seed), int(numVars))
            count_arr = variable_occurence(count_arr, int(seed))
            #varImportanceFile.write("\n{:<3}: {:<{}} {:<12}".format(indx+1, seed_str, numVars+2, seed_str.count("1")))
            SROC = 0
            with open(key + "/Keras_" + str(numVars) + "vars_Seed_" + seed + ".out") as f:
                for line in f.readlines():
                    if "ROC-integral" in line:
                        SROC = float(line[:-1].split(" ")[-1][:-1])
            print("Seed {} of {}: {}\r".format(indx, len(seedDict[key]), seed_str)),
            for subseedOut in seedDict[key][seed]:
                subseed = subseedOut.split("_Subseed_")[1].split(".out")[0]
                subseed_long = long(subseed)
                varIndx = numVars -  int( math.log( seed_long - subseed_long ) / 0.693147 ) - 1
                with open(key + "/Keras_" + str(numVars) + "vars_Seed_" + seed + "_Subseed_" + subseed + ".out") as f:
                    for line in f.readlines():
                        if "ROC-integral" in line:
                            SSROC = float(line[:-1].split(" ")[-1][:-1])
                            importances[varIndx].append( SROC - SSROC )
        print
    importance_stats = {}
    normalization = 0
    for indx in range(numVars):
        normalization += sum(importances[indx])
    for varIndx in importances:
        if not importances[varIndx]:
            importances[varIndx] = [0]
        importance_stats[varIndx] = np.array( [np.mean(importances[varIndx]),
                                               np.std(importances[varIndx]),
                                               np.mean(importances[varIndx]) / np.std(importances[varIndx])
                                              ] )
    varImportanceFile.write("\nImportance calculation:")
    varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<7} / {:<7} / {:<11}".format(
        "Index",
        "Variable Name",
        "Freq.",
        "Sum",
        "Mean",
        "RMS",
        "Importance"
    ))
    for varIndx in importance_stats:
        varImportanceFile.write("\n{:<6} {:<34} / {:<6} / {:<8.4f} / {:<7.4f} / {:<7.4f} / {:<11.3f}".format(
            str(varIndx+1)+".",
            varsList.varList["DNN"][varIndx][0],
            count_arr[varIndx],
            sum(importances[varIndx]) / abs(normalization),
            importance_stats[varIndx][0],
            importance_stats[varIndx][1],
            importance_stats[varIndx][2]
    ))
    varImportanceFile.close()
  
    importances_name = {}
    for key in importances:
        importances_name[varsList.varList["DNN"][key][0]] = importances[key]
    np.save("./dataset/ROC_hists_" + str(numVars) + "vars", importances_name)


#Ensure dataset forlder exists
if not os.path.exists("dataset"):
    os.mkdir("dataset")

seedDict, numVars = get_seeds(condorDirs)
variable_importance(seedDict, numVars)
print("Saving results to {}".format(os.getcwd() + "/dataset/"))

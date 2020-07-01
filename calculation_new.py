import jobtracker as jt
import numpy as np

from argparse import ArgumentParser
from datetime import datetime

import os
import varsList

condor_folders = []

# Read command line args
parser = ArgumentParser()
parser.add_argument("folders", nargs="*", default=[], help="condor_log folders to use, default is all condor_log*")
parser.add_argument("-f", "--output-folder", default="auto", help="The folder to output calculations to.")
parser.add_argument("-v", "--verbose", action="store_true", help="Display output from job tracker system.")
parser.add_argument("-o", "--sort-order", default="importance",
                    help="Which attribute to sort variables by in resulting files. Choose from (importance, freq, sum, mean, rms).")
args = parser.parse_args()

# Interpret folder paths
for d in args.folders:
    if os.path.exists(os.path.join(os.getcwd(), d)):
        condor_folders.append(os.path.join(os.getcwd(), d))
    elif os.path.exists(d):
        condor_folders.append(d)

# Substitute default value if no folders specified
if condor_folders == []:
    condor_folders = [os.path.join(os.getcwd(), d) for d in os.listdir(os.getcwd()) if d.startswith("condor_log")]

# Ensure dataset folder exists
ds_folder = args.output_folder
if ds_folder == "auto":
    ds_folder = "dataset_" + datetime.now().strftime("%d.%b.%Y")
if not os.path.exists(ds_folder):
    os.mkdir(ds_folder)
    print("Output directory {} created.".format(ds_folder))
else:
    print("Output to {}.".format(ds_folder))

# Set verbosity
jt.LOG = args.verbose

# Interpret sort order
sort_order = "importance"
if args.sort_order.lower() not in ["importance", "freq", "sum", "mean", "rms"]:
    print("Invalid sort option: {}. Using \"importance\".".format(args.sort_order.lower()))
else:
    sort_order = args.sort_order.lower()

print "Variable Importance Calculator"
print "Using Folders: \n - " + "\n - ".join(condor_folders)
print

print "Loading job data..."
job_folders = []
for folder in condor_folders:
    jf = jt.JobFolder(folder)
    if jf.jobs == None:
        # Folder needs to be imported
        print("The folder {} has not been loaded by the job tracker.".format(folder))
        choice = raw_input ("Import with default variables? (Y/n)")
        if "n" in choice.lower():
            print "Folder skipped."
            continue
        print "Importing data from folder."
        jf.import_folder([v[0] for v in varsList.varList["DNN"]])
    job_folders.append(jf)
    print("Loaded {}".format(folder))
print "All data loaded."

print "Computing Importances..."

# Compute importances, stats, and normalization
importances = {}
importance_stats = {}
normalization = 0

# Find ROC-integral values for all seeds
seed_rocs = {}
for jf in job_folders:
    for seed_j in jf.seed_jobs:
        if seed_j.has_result:
            seed_rocs[seed_j.seed] = (seed_j.roc_integral, jf)
            for var, included in seed_j.seed.states.iteritems():
                if included:
                    if var in importance_stats:
                        importance_stats[var]["freq"] += 1
                    else:
                        importance_stats[var] = { "freq": 1 }

print "Found " + str(len(seed_rocs.keys())) + " seed ROC-integrals."

n = 1
for seed, seed_roc in seed_rocs.iteritems():
    print("Processing seed {}.\r".format(n)),
    n += 1
    for subseed_j in seed_roc[1].subseed_jobs(seed):
        if subseed_j.has_result:
            for var, included in subseed_j.subseed.states.iteritems():
                if not included and seed.states[var]:
                    if var in importances:
                        importances[var].append(seed_roc[0] - subseed_j.roc_integral)
                    else:
                        importances[var] = [seed_roc[0] - subseed_j.roc_integral]
print
    
print "Computing stats."
for var, importance in importances.iteritems():
    normalization += sum(importance)

    # Compute stats
    mean = np.mean(importance)
    std = np.std(importance)

    importance_stats[var]["mean"] = mean
    importance_stats[var]["rms"] = std
    importance_stats[var]["importance"] = mean / std
    importance_stats[var]["sum"] = sum(importance)

print "Importances computed."

print "Writing to output files."

num_vars = len(importances.keys())

# Variable Importance File
with open(os.path.join(ds_folder, "VariableImportanceResults_" + str(num_vars) + "vars.txt"), "w") as f:
    f.write("Weight: {}\n".format(varsList.weightStr))
    f.write("Cut: {}\n".format(varsList.cutStr))
    f.write("Folders: \n - " + "\n - ".join(condor_folders) + "\n")
    f.write("Number of Variables: {}\n".format(num_vars))
    f.write("Date: {}\n".format(datetime.today().strftime("%Y-%m-%d")))
    f.write("\nImportance Calculation:")
    f.write("\nNormalization: {}".format(normalization))
    f.write("\n{:<6} / {:<34} / {:<6} / {:<7} / {:<7} / {:<11} / {:<11}".format(
        "Index",
        "Variable Name",
        "Freq.",
        "Sum",
        "Mean",
        "RMS",
        "Importance"
    ))

    for i, var in enumerate(reversed(sorted(importances.keys(), key=lambda k: importance_stats[k][sort_order]))):
        f.write("\n{:<6} / {:<34} / {:<6} / {:<8.4f} / {:<7.4f} / {:<7.4f} / {:<11.3f}".format(
            str(i + 1) + ".",
            var,
            importance_stats[var]["freq"],
            importance_stats[var]["sum"],
            importance_stats[var]["mean"],
            importance_stats[var]["rms"],
            importance_stats[var]["importance"]
        ))
print "Wrote VariableImportanceResults_" + str(num_vars) + "vars.txt"

# ROC Hists File
np.save(os.path.join(ds_folder, "ROC_hists_" + str(num_vars) + "vars"), importances)
print "Wrote ROC_hists_" + str(num_vars) + "vars"

# Importance Order File
with open(os.path.join(ds_folder, "VariableImportanceOrder_" + str(num_vars) + "vars.txt"), "w") as f:
    for var in reversed(sorted(importances.keys(), key=lambda k: importance_stats[k][sort_order])):
        f.write(var + "\n")
print "Wrote " + "VariableImportanceOrder_" + str(num_vars) + "vars.txt"

print "Done."
    

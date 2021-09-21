import jobtracker as jt
import numpy as np

from argparse import ArgumentParser
from datetime import datetime

import os
import config

condor_folders = []

# Read command line args
parser = ArgumentParser()
parser.add_argument("folders", nargs="*", default=[], help="condor_log folders to use, default is all condor_log*")
parser.add_argument("-f", "--output-folder", default="auto", help="The folder to output calculations to.")
parser.add_argument("-v", "--verbose", action="store_true", help="Display output from job tracker system.")
parser.add_argument("-o", "--sort-order", default="significance", help="Which attribute to sort variables by in resulting files. Choose from (importance, freq, sum, mean, rms).")
parser.add_argument("--sort-increasing", action="store_true", help="Sort in increasing instead of decreasing order")
args = parser.parse_args()

print(" >> Running variable importance calculation")

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
  print(">> Output directory {} created.".format(ds_folder))
else:
  print(">> Output variable importance results to {}.".format(ds_folder))

# Set verbosity
jt.LOG = args.verbose

# Interpret sort order
sort_order = "significance"
if args.sort_order.lower() not in ["significance", "freq", "sum", "mean", "rms"]:
  print(">> Invalid sort option: {}. Using \"importance\".".format(args.sort_order.lower()))
else:
  sort_order = args.sort_order.lower()
sort_increasing = args.sort_increasing

print( ">> Using Folders: \n - " + "\n - ".join(condor_folders) )

print( ">> Loading job data" )
job_folders = []
bkg_samples = []
cut_variables = [ "NJETS", "NBJETS" ]
cuts = { variable: [] for variable in cut_variables }
years = []
for folder in condor_folders:
  jf = jt.JobFolder(folder)
  for variable in cut_variables:
    cuts[ variable ].append( jf.pickle[ "CUTS" ][ variable ] )
  years.append( jf.pickle[ "YEAR" ] )
  bkg_samples.append( jf.pickle[ "BACKGROUND" ] )
  if jf.pickle[ "JOBS" ] == None:
    # Folder needs to be imported
    print( "[WARN] The folder {} has not been loaded by the job tracker.".format(folder) )
    choice = raw_input ("Import with default variables? (Y/n)")
    if "n" in choice.lower():
      print( ">> Folder skipped." )
      continue
    print( ">> Importing data from folder." )
    jf.import_folder([v[0] for v in config.varList["DNN"]])
  job_folders.append(jf)
  print(">> Loaded {}".format(folder))
print( "[OK ] All data loaded." )


print( ">> Checking year consistency between folders..." )

if len( set( years ) ) > 1:
  print( "[ERR] Exiting calculate.py, compacted folders have multiple years..." )
  quit()

print( ">> Checking background sample consistency between folders..." )

quit_ = False
for i, bkg_sample in enumerate( bkg_samples ):
  if set( bkg_sample ) != set( bkg_samples[0] ):
    print( "[WARN] Different collection of background samples in {}: {}...".format( condor_folders[i], set( bkg_samples[0] ).difference( bkg_sample ) ) )

print( ">> Checking cut consistency between folders..." )

quit_ = False
for variable in cut_variables:
  if len( set( cuts[ variable ] ) ) > 1:
    print( "[WARN] Inconsistent cut settings for {}: {}...".format( variable, set( cuts[ variable ] ) ) )
    quit_ = True
if quit_ is True:
  print( "[ERR] Exiting calculate.py, cut conditions are not consistent..." )
  quit()

print( ">> Computing Importances..." )

# Compute importances, stats, and normalization
significances = {}
significances_stats = {}
normalization = 0

# Find ROC-integral values for all seeds
seed_rocs = {}
for jf in job_folders:
  for seed_j in jf.seed_jobs:
    if seed_j.has_result:
      seed_rocs[seed_j.seed] = (seed_j.roc_integral, jf)
      for var, included in seed_j.seed.states.iteritems():
        if included:
          if var in significances_stats:
            significances_stats[var]["freq"] += 1
          else:
            significances_stats[var] = { "freq": 1 }

print( "Found " + str(len(seed_rocs.keys())) + " seed ROC-integrals." )

n = 1
for seed, seed_roc in seed_rocs.iteritems():
  print("Processing seed {}.\r".format(n)),
  n += 1
  for subseed_j in seed_roc[1].subseed_jobs(seed):
    if subseed_j.subseed == seed:
      continue
    if subseed_j.has_result:
      for var, included in subseed_j.subseed.states.iteritems():
        if not included and seed.states[var]:
          if var in significances:
            significances[var].append(seed_roc[0] - subseed_j.roc_integral)
          else:
            significances[var] = [seed_roc[0] - subseed_j.roc_integral]
    
print( "\n>> Computing stats." )
for var, significance in significances.iteritems():
  normalization += sum(significance)

  # Compute stats
  mean = np.mean(significance)
  std = np.std(significance)

  significances_stats[var]["mean"] = mean
  significances_stats[var]["rms"] = std
  significances_stats[var]["significance"] = mean / std
  significances_stats[var]["sum"] = sum(significance)

print( "[OK ] Importances computed." )

print( ">> Writing to output files." )

num_vars = len(significances.keys())
sorted_vars = list(sorted(significances.keys(), key=lambda k: significances_stats[k][sort_order]))
if not sort_increasing:
  sorted_vars = list(reversed(sorted_vars))

# Variable Importance File
with open(os.path.join(ds_folder, "VariableImportanceResults_" + str(num_vars) + "vars.txt"), "w") as f:
  f.write("Year:{}\n".format(years[0]))
  f.write("Weight: {}\n".format(config.weightStr))
  for variable in cut_variables: f.write( "{}:{}\n".format( variable, cuts[ variable ][0] ) )
  f.write("Folders: \n - " + "\n - ".join(condor_folders) + "\n")
  f.write("Number of Variables: {}\n".format(num_vars))
  f.write("Date: {}\n".format(datetime.today().strftime("%Y-%m-%d")))
  f.write("\nImportance Calculation:")
  f.write("\nNormalization: {}".format(normalization))
  f.write("\n{:<6} / {:<34} / {:<6} / {:<8} / {:<7} / {:<7} / {:<11}".format(
    "Index",
    "Variable Name",
    "Freq.",
    "Sum",
    "Mean",
    "RMS",
    "Significance"
  ))
    
  for i, var in enumerate(sorted_vars):
    f.write("\n{:<6} / {:<34} / {:<6} / {:<8.4f} / {:<7.4f} / {:<7.4f} / {:<11.3f}".format(
      str(i + 1) + ".",
      var,
      significances_stats[var]["freq"],
      significances_stats[var]["sum"],
      significances_stats[var]["mean"],
      significances_stats[var]["rms"],
      significances_stats[var]["significance"]
    ))
print( "[OK ] Wrote VariableImportanceResults_" + str(num_vars) + "vars.txt" )

# ROC Hists File
np.save(os.path.join(ds_folder, "ROC_hists_" + str(num_vars) + "vars"), significances)
print( "Wrote ROC_hists_" + str(num_vars) + "vars" )

# Importance Order File
with open(os.path.join(ds_folder, "VariableImportanceOrder_" + str(num_vars) + "vars.txt"), "w") as f:
  for var in sorted_vars:
    f.write(var + "\n")

print( "[OK ] Wrote " + "VariableImportanceOrder_" + str(num_vars) + "vars.txt" )

print( "[OK ] Finished obtaining all variable importance results." )
    

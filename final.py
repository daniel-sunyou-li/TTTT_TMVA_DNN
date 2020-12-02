import os
from argparse import ArgumentParser
from json import loads as load_json
from json import dump as dump_json
from datetime import datetime
from shutil import rmtree, copy
import numpy as np

import varsList
import mltools

parser = ArgumentParser()
parser.add_argument( "-y", "--year", required=True, help="The dataset to use when training. Specify 2017 or 2018")
parser.add_argument( "datasets", nargs="*", default=[], help="The dataset folders to search for HPO information")
parser.add_argument( "-f", "--folder", default="auto", help="The name of the output folder.")
parser.add_argument( "-k", "--num-folds", default="5", help="The number of cross-validation iterations to perform for each configuration")
parser.add_argument( "--no-cut-save", action="store_true", help="Do not attempt to load or create saved cut event files.")
args = parser.parse_args()

print( ">> Final Model Training: k-fold Cross Validation" )

# Parse year
if args.year != "2017" and args.year != "2018":
  raise ValueError( "[ERR] Invaid year selected: {}. Year must be 2017 or 2018.".format( args.year ) )

# Gather list of signal and background folders
tree_folder = varsList.step2DirLPC[ args.year ] + "nominal"
signal_files = [ os.path.join( tree_folder, sig ) for sig in varsList.sig_training[ args.year ] ]
background_files = [ os.path.join( tree_folder, bkg ) for bkg in varsList.bkg_training[ args.year ] ]

# Look for HPO data files
hpo_data = {}
datasets = args.datasets
if args.datasets == []:
  datasets = [ d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and d.startswith("dataset") ]
print(">> Using Datasets:\n - {}".format("\n - ".join(datasets)))
for dataset in datasets:
  if os.path.exists(dataset):
    if os.path.isdir(dataset):
      for dfile in os.listdir(dataset):
        if dfile.startswith("optimized_parameters") and dfile.endswith(".json"):
          try:
            with open( os.path.join( dataset, dfile ), "r") as f:
              hpo_data[os.path.join(dataset, dfile)] = load_json(f.read())
          except:
            print("[WARN] Unable to read JSON from {}.".format(os.path.join(dataset, dfile)))
    else:
      try:
        with open(dataset, "r") as f:
          hpo_data[dataset] = load_json(f.read())
      except:
        print("[WARN] Unable to read JSON from {}.".format(dataset))

# Create output folder
folder = args.folder
if folder == "auto":
  folder = "final_" + datetime.now().strftime("%d.%b.%Y")
if not os.path.exists(folder):
  os.mkdir(folder)

# Assign configuration order
config_order = list(sorted(hpo_data.keys(), key=lambda p: os.path.getmtime(p)))

# Open output file
summary_f = open(os.path.join(folder, "summary.txt"), "w")
summary_f.write("Final Training Summary: {}\n\n".format(datetime.now().strftime("%d.%b.%Y")))
summary_f.write("Index , Parameters , Model , AUC , Accuracy , Loss \n")

data = {}

# Go through all configurations
for config_num, config_path in enumerate(config_order):
  print(">> Now processing configuration #{} from {}.".format(config_num + 1, config_path))

  cv_folder = os.path.join(folder, "cross_validation")
  if not os.path.exists(cv_folder):
    os.mkdir(cv_folder)
        
  model_path = os.path.join(folder, config_path[config_path.rfind("/") + 1:].rstrip(".json") + ".h5")

  # Load JSON data
  parameters = None
  with open(config_path, "r") as f:
    parameters = load_json(f.read())

  # Load variables list
  with open(config_path.replace("optimized_parameters", "parameters"), "r") as f:
    full_params = load_json(f.read())
    parameters["variables"] = full_params["variables"]
    parameters["patience"] = full_params["patience"][-1] if type(full_params["patience"]) == list else full_params["patience"]
    parameters["epochs"] = full_params["epochs"][-1] if type(full_params["epochs"]) == list else full_params["epochs"]
  print( ">> Using njets >= {} and nbjets >= {}".format( full_params[ "njets" ], full_params[ "nbjets" ] ) )

  model = mltools.CrossValidationModel(
    parameters,
    signal_files, background_files, 
    cv_folder, 
    full_params["njets"], full_params["nbjets"], int(args.num_folds ) )
  if not args.no_cut_save:
    if not os.path.exists(mltools.CUT_SAVE_FILE):
      print( ">> Generating saved cut event files." )
      model.load_trees()
      model.apply_cut()
      model.save_cut_events(mltools.CUT_SAVE_FILE)
    else:
      print( ">> Loading saved cut event files." )
      model.load_cut_events(mltools.CUT_SAVE_FILE)
  else:
    model.load_trees()
    model.apply_cut()

  print( ">> Starting cross-validation." )
    
  model.train_model()

  print( ">> Collecting results." )

  for k in range(model.num_folds):
    print(">> Configuration {}.{} finished with ROC-Integral value: {}{}.".format(
      config_num, k, model.auc_test[k], " (best)" if k == model.best_fold else "" ) )
    summary_f.write(" , ".join([str(x) for x in [str(config_num) + "." + str(k), config_path, model_path if k == model.best_fold else "unsaved", model.auc_test[k], model.accuracy[k], model.loss[k]]]) + "\n" )
  print( ">> AUC (test)  = {:.4f} +- {:.4f}".format( np.mean( model.auc_test ), np.std( model.auc_test ) ) )
  print( ">> AUC (train) = {:.4f} +- {:.4f}".format( np.mean( model.auc_train ), np.std( model.auc_train ) ) )
  data[config_path] = {
    "config_id": config_num,
    "config_path": config_path,
    "model_path": model_path,
    "parameters": parameters,        
    "best_model": model.best_fold,
    "auc_test": model.auc_test,
    "auc_train": model.auc_train,
    "auc_test_k": [ np.mean(model.auc_test), np.std(model.auc_test) ],
    "auc_train_k": [ np.mean(model.auc_train), np.std(model.auc_train) ],
    "loss": model.loss,
    "accuracy": model.accuracy,
    "fpr_train": [",".join([str(x) for x in fpr]) for fpr in model.fpr_train],
    "tpr_train": [",".join([str(x) for x in tpr]) for tpr in model.tpr_train],
    "fpr_test": [",".join([str(x) for x in fpr]) for fpr in model.fpr_test],
    "tpr_test": [",".join([str(x) for x in tpr]) for tpr in model.tpr_test]
  }

  print( ">> Preserving best model file as {}".format( model_path ) )
  copy( model.model_paths[ model.best_fold ], model_path )
  rmtree(cv_folder)

summary_f.close()

print( ">> Writing final data file to {}".format( os.path.join( folder, "data.json" ) ) )
with open( os.path.join( folder, "data.json" ), "w" ) as f:
  dump_json(data, f, indent=2)

print( "[OK ] Done." )

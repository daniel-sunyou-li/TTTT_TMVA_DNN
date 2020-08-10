import os
from argparse import ArgumentParser
from json import loads as load_json
from datetime import datetime

os.environ["KERAS_BACKEND"] = "tensorflow"

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras import backend

import varsList
import mltools

parser = ArgumentParser()
parser.add_argument("-y", "--year", required=True, help="The dataset to use when training. Specify 2017 or 2018")
parser.add_argument("datasets", nargs="*", default=[], help="The dataset folders to search for HPO information")
parser.add_argument("-f", "--folder", default="auto", help="The name of the output folder.")
parser.add_argument("--no-cut-save", action="store_true", help="Do not attempt to load or create saved cut event files.")
args = parser.parse_args()

print "Final Model Training"

# Parse year
year = args.year
if year != "2017" and year != "2018":
    raise ValueError("Invaid year selected: {}. Year must be 2017 or 2018.".format(year))

# Gather list of signal and background folders
tree_folder = None
if year == "2017":
    tree_folder = varsList.inputDirLPC2017
elif year == "2018":
    tree_folder = varsList.inputDirLPC2018
signal_files = [os.path.join(tree_folder, sig) for sig in (varsList.sig2017_1 if year == "2017" else varsList.sig2018_1)]
background_files = [os.path.join(tree_folder, bkg) for bkg in (varsList.bkg2017_1 if year == "2017" else varsList.bkg2018_1)]

# Look for HPO data files
hpo_data = {}
datasets = args.datasets
if args.datasets == []:
    datasets = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and d.startswith("dataset")]
print("Using Datasets:\n - {}".format("\n - ".join(datasets)))
for dataset in datasets:
    if os.path.exists(dataset):
        if os.path.isdir(dataset):
            for dfile in os.listdir(dataset):
                if dfile.startswith("optimized_parameters") and dfile.endswith(".json"):
                    try:
                        with open(os.path.join(dataset, dfile), "r") as f:
                            hpo_data[os.path.join(dataset, dfile)] = load_json(f.read())
                    except:
                        print("WARN: Unable to read JSON from {}.".format(os.path.join(dataset, dfile)))
        else:
            try:
                with open(dataset, "r") as f:
                    hpo_data[dataset] = load_json(f.read())
            except:
                print("WARN: Unable to read JSON from {}.".format(dataset))

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

# Go through all configurations
for config_num, config_path in enumerate(config_order):
    print("Now processing configuration #{} from {}.".format(config_num + 1, config_path))
    
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

    model = mltools.HyperParameterModel(parameters, signal_files, background_files, model_path)
    if not args.no_cut_save:
        if not (os.path.exists(mltools.CUT_SAVE_SIGNAL) and os.path.exists(mltools.CUT_SAVE_BACKGROUND)):
            print "Generating saved cut event files."
            model.load_trees()
            model.apply_cut()
            model.save_cut_events(mltools.CUT_SAVE_SIGNAL, mltools.CUT_SAVE_BACKGROUND)
        else:
            print "Loading saved cut event files."
            model.load_cut_events(mltools.CUT_SAVE_SIGNAL, mltools.CUT_SAVE_BACKGROUND)
    else:
        model.load_trees()
        model.apply_cut()
    
    model.build_model()

    model.train_model()

    print("Configuration #{} finished with AUC {:.3f}, accuracy {:.3f} and loss {:.3f}".format(config_num, model.roc_integral, model.accuracy, model.loss))

    print("->  Model saved to: {}".format(model_path))

    summary_f.write(" , ".join([str(x) for x in [config_num, config_path, model_path, model.roc_integral, model.accuracy, model.loss]]) + "\n")

f.close()

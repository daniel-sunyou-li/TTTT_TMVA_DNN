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

parser = ArgumentParser()
parser.add_argument("-y", "--year", required=True, help="The dataset to use when training. Specify 2017 or 2018")
parser.add_argument("datasets", nargs="*", default=[], help="The dataset folders to search for HPO information")
parser.add_argument("-f", "--folder", default="auto", help="The name of the output folder.")
args = parser.parse_args()

print "Final Model Training"

# Parse year
year = args.year
if year != "2017" and year != "2018":
    raise ValueError("Invaid year selected: {}. Year must be 2017 or 2018.".format(year))
if year == "2017":
    tree_folder = varsList.inputDirLPC2017
elif year == "2018":
    tree_folder = varsList.inputDirLPC2018

# Look for HPO data files
hpo_data = {}
datasets = args.datasets
if args.datasets == []:
    datasets = [d for d in os.listdir() if os.path.isdir(d) and d.startswith("dataset")]
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


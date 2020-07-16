import os
from datetime import datetime
from argparse import ArgumentParser
from json import loads as load_json
from json import dumps as write_json
from math import log

os.environ["KERAS_BACKEND"] = "tensorflow"

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras import backend

from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
from skopt import gp_minimize

from ROOT import TMVA, TFile, TCut

import varsList

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
(TMVA.gConfig().GetIONames()).fWeightFileDir = "/weights"

parser = ArgumentParser()
#parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed logs.")
parser.add_argument("dataset", help="The dataset folder to use variable importance results from.")
parser.add_argument("-o", "--sort-order", default="importance",
                    help="Which attribute to sort variables by. Choose from (importance, freq, sum, mean, rms, or specify a filepath).")
parser.add_argument("--sort-increasing", action="store_true", help="Sort in increasing instead of decreasing order")
parser.add_argument("-n", "--num-vars", default="all", help="How many variables, from the top of the sorted order, to use.")
parser.add_argument("-y", "--year", required=True, help="The dataset to use when training. Specify 2017 or 2018")
parser.add_argument("-p", "--parameters", default=None, help="Specify a JSON folder with static and hyper parameters.")
args = parser.parse_args()

# Parse year
year = args.year
if year != "2017" and year != "2018":
    raise ValueError("Invaid year selected: {}. Year must be 2017 or 2018.".format(year))
if year == "2017":
    tree_folder = varsList.inputDirLPC2017
elif year == "2018":
    tree_folder = varsList.inputDirLPC2018

# Load dataset
datafile_path = None
if os.path.exists(args.dataset):
    for f in os.listdir(args.dataset):
        if f.startswith("VariableImportanceResults"):
            datafile_path = os.path.join(args.dataset, f)
            break
        
if datafile_path == None:
    raise IOError("{} is not a valid dataset!".format(args.dataset))

print("Loading variable importance data from {}.".format(datafile_path))
# Read the data file
var_data = {}
with open(datafile_path, "r") as f:
    # Scroll to variable entries
    line = f.readline()
    while not "Normalization" in line:
        line = f.readline()
        if line == "":
            raise IOError("End of File Reached, no data found.")
    # Data reached.
    # Read headers
    headers = [h.strip().rstrip().lower().replace(".", "") for h in f.readline().rstrip().split("/")]
    print("    Found data columns: {}".format(", ".join(headers)))
    for h in headers:
        var_data[h] = []
    # Read data
    line = f.readline().rstrip()
    while line != "":
        content = [c.strip().rstrip() for c in line.split("/")]
        content[0] = content[0].rstrip(".")
        for i, h in enumerate(headers):
            if i == 1:
                var_data[h].append(content[i])
            elif "inf" in content[i]:
                print("    Warning: Replaced infinite value with 0!")
                var_data[h].append(0)
            else:
                var_data[h].append(float(content[i]) if "." in content[i] else int(content[i]))
        line = f.readline().rstrip()

# Determine variable sort order
var_order = []
if os.path.exists(args.sort_order):
    print("Reading variable sort order from {}.".format(args.sort_order))
    with open(args.sort_order, "r") as f:
        for line in f.readlines():
            if line != "":
                var_name = line.rstrip().strip()
                if not var_name in var_data["variable name"]:
                    print("    Data for variable {} not found in dataset. Skipping.".format(var_name))
                else:
                    var_order.append(var_name)
    print("Found {} variables.".format(len(var_order)))
else:
    sort_order = args.sort_order.lower()
    if sort_order not in var_data:
        print("Invalid sort option: {}. Using \"importance\".".format(sort_order))
        sort_order = "importance"
    else:
        print("Sorting {} variables by {}.".format(len(var_data["variable name"]), sort_order))
    sorted_vars = sorted([(n, i) for i, n in enumerate(var_data["variable name"])],
                       key=lambda p: var_data[sort_order][p[1]])
    if not args.sort_increasing:
        sorted_vars = reversed(sorted_vars)
    var_order = [v[0] for v in sorted_vars]

# Determine the variables to use
variables = None
if args.num_vars == "all":
    variables = var_order
else:
    variables = var_order[:int(args.num_vars)]
print("Variables used in optimization:\n - {}".format("\n - ".join(variables)))

# Determine static and hyper parameter
timestamp = datetime.now()
PARAMETERS = {
    "static": [
        "static",
        "epochs",
        "patience",
        "model_name",
        "tag_num",
        "tag",
        "log_file",
        "n_calls",
        "n_starts"
        ],

    "epochs": 15,
    "patience": 5,
    "model_name": "dummy_opt_model.h5",
    "tag_num": str(timestamp.hour),
    "tag": timestamp.strftime("%m-%d_%H"),
    "log_file": os.path.join(args.dataset, "optimize_log_" + timestamp.strftime("%m-%d_%H") + ".txt"),

    "hidden_layers": [1, 3],
    "initial_nodes": [len(var_order), len(var_order) * 10],
    "node_pattern": ["static", "dynamic"],
    "batch_power": [8, 11],
    "learning_rate": [1e-5, 1e-2],
    "regulator": ["none", "dropout", "normalization", "both"],
    "activation_function": ["relu", "softplus", "elu"],

    "n_calls": 50,
    "n_starts": 30
}
# Update parameters given file
if args.parameters != None and os.path.exists(args.parameters):
    print("Loading updated parameters from {}.".format(args.parameters))
    with open(args.parameters, "r") as f:
        u_params = load_json(f.read())
        PARAMETERS.update(u_params)

# Save used parameters to file
parameter_file = os.path.join(args.dataset, "optimize_parameters" + timestamp.strftime("%m-%d_%H") + ".json")
with open(parameter_file, "w") as f:
    f.write(write_json(PARAMETERS, indent=2))
print("Parameters saved to dataset folder.")

# Start the logfile
logfile = open(PARAMETERS["log_file"], "w")
logfile.write("{:7}, {:7}, {:7}, {:7}, {:9}, {:14}, {:10}, {:7}\n".format(
      "Hidden",
      "Nodes",
      "Rate",
      "Batch",
      "Pattern",
      "Regulator",
      "Activation",
      "ROC"
    )
  )

# Determine optimization space
opt_space = []
opt_order = {}
i = 0
for param, value in PARAMETERS.iteritems():
    if param not in PARAMETERS["static"]:
        if type(value[0]) == str:
            opt_space.append(
                Categorical(value, name=param)
                )
        elif param == "learning_rate":
            opt_space.append(
                Real(value[0], value[1], "log-uniform", name=param)
                )
        else:
            opt_space.append(
                Integer(*value, name=param)
                )
        opt_order[param] = i
        i += 1

# Training Instance
class TrainingInstance(object):
    def __init__(self, X):
        self.X = X
        self._build_model()
        self.loader = TMVA.DataLoader("tmva_data")
        self._add_variables()        
        self._add_trees()
        self.loader.SetSignalWeightExpression(varsList.weightStr)
        self.loader.SetBackgroundWeightExpression(varsList.weightStr)
        self.cut = TCut(varsList.cutStr)

        loader.PrepareTrainingAndTestTree( 
            self.cut, self.cut, 
            "SplitMode=Random:NormMode=NumEvents:!V"
        )

        self.factory = TMVA.Factory(
            "Optimization",
            "!V:!ROC:!Silent:Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification"
            )

        self.factory.BookMethod(
            self.loader,
            TMVA.Types.kPyKeras,
            "PyKeras",
            "!H:!V:VarTransform=G:FilenameModel=" + X["model_name"] + \
            ":SaveBestOnly=true" + \
            ":NumEpochs=" + str(X["epochs"]) + \
            ":BatchSize=" + str(2**X["batch_power"]) +\
            ":TriesEarlyStopping=" + str(X["patience"])
            )

    def get_result(self):
        self.factory.TrainAllMethods()
        self.factory.TestAllMethods()
        self.factory.EvaluateAllMethods()

        ROC = self.factory.getROCIntegral(self.loader, "PyKeras")

        self.factory.DeleteAllMethods()
        self.factory.fMethodsMap.clear()

        return ROC


    def _add_variables(self):
        for var in variables:
            var_data = varsList.varList["DNN"][[v[0] for v in varsList.varList["DNN"]].index(var)]
            self.loader.AddVariable(var_data[0], var_data[1], var_data[2], "F")

    def _add_trees(self):
        self.signals = []
        self.signal_trees = []
        self.backgrounds = []
        self.background_trees = []
        
        for sig in varsList.sig2017_1 if year == "2017" else varsList.sig2018_1:
            self.signals.append(TFile.Open(os.path.join(tree_folder, sig)))
            self.signal_trees.append(self.signals[-1].Get("ljmet"))
            self.signal_trees[-1].GetEntry(0)
            self.loader.AddSignalTree(self.signal_trees[-1], 1)

        for bkg in varsList.bkg2017_1 if year == "2017" else varsList.bkg2018_1:
            self.backgrounds.append(TFile.Open(os.path.join(tree_folder, bkg)))
            self.background_trees.append(self.backgrounds[-1].Get("ljmet"))
            self.background_trees[-1].GetEntry(0)
            if self.background_trees[-1].GetEntries() != 0:
                self.loader.AddBackgroundTree(self.background_trees[-1], 1)


    def _build_model(self):
        self.model = Sequential()
        self.model.add(Dense(
          self.X["initial_nodes"],
          input_dim=len(variables),
          kernel_initializer="glorot_normal",
          activation=self.X["activation_function"]
          )
        )
        partition = int(self.X["initial_nodes"] / self.X["hidden_layers"])
        for i in range(hidden):
            if self.X["regulator"] in ["normalization", "both"]:
                self.model.add(BatchNormalization())
            if regulator in ["dropout", "both"]:
                self.model.add(Dropout(0.5))
            if self.X["node_pattern"] == "dynamic":
                self.model.add(Dense(
                    self.X["initial_nodes"] - (partition * i),
                    kernel_initializer="glorot_normal",
                    activation=self.X["activation_function"]
                    )
                )
            elif self.X["node_pattern"] == "static":
                self.model.add(Dense(
                    self.X["initial_nodes"],
                    kernel_initializer="glorot_normal",
                    activation=self.X["activation_function"]
                    )
                )
        # Final classification node
        self.model.add(Dense(
            2,
            activation="sigmoid"
            )
        )
        self.model.compile(
            optimizer=Adam(lr=self.X["learning_rate"]),
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )
            
# Objective function
@use_named_args(opt_space)
def objective(**X):
    print("Configuration:\n{}\n".format(X))
    instance = TrainingInstance(X)
    result = instance.get_result()
    print("Obtained ROC-Integral value: {}".format(result))
    opt_metric = log(1 - result)
    print("    Metric: {}".format(round(opt_metric, 2)))
    return opt_metric


# Perform the optimization
start_time = datetime.now()

res_gp = gp_minimize(
            func = objective,
            dimensions = opt_space,
            n_calls = PARAMETERS["n_calls"],
            n_random_starts = PARAMETERS["n_starts"],
            verbose = True
            )

logfile.close()

# Report results
print("Writing optimized parameter log to: optimized_params_" + PARAMETERS["tag"] + ".txt")
with open(os.path.join(args.dataset, "optimized_params_" + PARAMETERS["tag"] + ".txt"), "w") as f:
    f.write("TTTT TMVA DNN Hyper Parameter Optimization Parameters \n")
    f.write("Static and Parameter Space stored in: {}\n".format(parameter_file))
    f.write("Optimized Parameters:\n")
    f.write(" Hidden Layers: {}\n".format(res_gp.x[opt_order["hidden_layers"]]))
    f.write(" Initial Nodes: {}\n".format(res_gp.x[opt_order["initial_nodes"]]))
    f.write(" Batch Power: {}\n".format(res_gp.x[opt_order["batch_power"]]))
    f.write(" Learning Rate: {}\n".format(res_gp.x[opt_order["learning_rate"]]))
    f.write(" Node Pattern: {}\n".format(res_gp.x[opt_order["node_pattern"]]))
    f.write(" Regulator: {}\n".format(res_gp.x[opt_order["regulator"]]))
    f.write(" Activation Function: {}\n".format(res_gp.x[opt_order["activation_function"]]))
print("Finished optimization in: {} s".format(datetime.now() - start_time))

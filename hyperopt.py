import os
from datetime import datetime
from argparse import ArgumentParser
from json import loads as load_json
from json import dumps as write_json

from skopt.space import Real, Integer, Categorical

parser = ArgumentParser()
#parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed logs.")
parser.add_argument("dataset", help="The dataset folder to use variable importance results from.")
parser.add_argument("-o", "--sort-order", default="importance",
                    help="Which attribute to sort variables by. Choose from (importance, freq, sum, mean, rms, or specify a filepath).")
parser.add_argument("--sort-increasing", action="store_true", help="Sort in increasing instead of decreasing order")
parser.add_argument("-n", "--num-vars", default="all", help="How many variables, from the top of the sorted order, to use.")
parser.add_argument("-p", "--parameters", default=None, help="Specify a JSON folder with static and hyper parameters.")
args = parser.parse_args()

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
with open(os.path.join(args.dataset, "optimize_parameters" + timestamp.strftime("%m-%d_%H") + ".json"), "w") as f:
    f.write(write_json(PARAMETERS))
print("Parameters saved to dataset folder.")

# Determine optimization space
opt_space = []
for param, value in PARAMETERS.iteritems():
    if param not in PARAMETERS["static"]:
        if type(value[0]) == str:
            opt_space.append(
                Categorical(value, name=param)
                )
        elif param == "learning_rate":
            opt_space.append(
                Real(*value, "log-uniform", name=param)
                )
        else:
            opt_space.append(
                Integer(*value, name=param)
                )
            

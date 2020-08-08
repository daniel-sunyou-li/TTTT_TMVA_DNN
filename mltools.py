import os
from pickle import load as pickle_load
from pickle import dump as pickle_dump

os.environ["KERAS_BACKEND"] = "tensorflow"

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras import backend

from ROOT import TFile

import numpy as np

import varsList

# The parameters to apply to the cut.
CUT_VARIABLES = ["leptonPt_MultiLepCalc", "isElectron", "isMuon",
                 "corr_met_MultiLepCalc", "MT_lepMet", "minDR_lepJet",
                 "AK4HT", "DataPastTriggerX", "MCPastTriggerX",
                 "NJetsCSVwithSF_MultiLepCalc", "NJets_JetSubCalc"]
CUT_STRING = "((%(leptonPt_MultiLepCalc)s > 50 and %(isElectron)s == 1) or " + \
             "(%(leptonPt_MultiLepCalc)s > 50 and %(isMuon)s == 1)) and " + \
             "(%(corr_met_MultiLepCalc)s > 60 and %(MT_lepMet)s > 60 and " + \
             "%(minDR_lepJet)s > 0.4 and %(AK4HT)s > 510) and " + \
             "(%(DataPastTriggerX)s == 1 and %(MCPastTriggerX)s == 1) and " + \
             "(%(NJetsCSVwithSF_MultiLepCalc)s >= 2 and %(NJets_JetSubCalc)s >=6)"
test_cut = lambda d: eval(CUT_STRING % d)

ML_VARIABLES = [x[0] for x in varsList.varList["DNN"]]
VARIABLES = list(sorted(list(set(ML_VARIABLES).union(set(CUT_VARIABLES)))))
CUT_VARIABLES = [(v, VARIABLES.index(v)) for v in CUT_VARIABLES]

# Standard saved event locations
CUT_SAVE_SIGNAL = os.path.join(os.getcwd(), "cut_signal.evts")
CUT_SAVE_BACKGROUND = os.path.join(os.getcwd(), "cut_background.evts")

print("mltools using {} variables.".format(len(VARIABLES)))

class MLTrainingInstance(object):
    def __init__(self, signal_paths, background_paths):
        self.signal_paths = signal_paths
        self.background_paths = background_paths

    def load_cut_events(self, sig_path, bg_path):
        if os.path.exists(sig_path) and os.path.exists(bg_path):
            with open(sig_path, "rb") as f:
                self.signal_events = pickle_load(f)
            with open(bg_path, "rb") as f:
                self.background_events = pickle_load(f)

    def save_cut_events(self, sig_path, bg_path):
        with open(sig_path, "wb") as f:
            pickle_dump(self.signal_events, f)
        with open(bg_path, "wb") as f:
            pickle_dump(self.background_events, f)

    def load_trees(self):
        # Load signal files
        self.signal_files = {}
        self.signal_trees = {}
        for path in self.signal_paths:
            self.signal_files[path] = TFile.Open(path)
            self.signal_trees[path] = self.signal_files[path].Get("ljmet")
        # Load background files
        self.background_files = {}
        self.background_trees = {}
        for path in self.background_paths:
            self.background_files[path] = TFile.Open(path)
            self.background_trees[path] = self.background_files[path].Get("ljmet")
    
    def apply_cut(self):
        # Apply cut parameters to the loaded signals and backgrounds
        # Load in events
        all_signals = None
        for signal_tree in self.signal_trees.values():
            sig_list = np.asarray(signal_tree.AsMatrix(VARIABLES))
            if type(all_signals) == type(None):
                all_signals = sig_list
            else:
                all_signals = np.concatenate((all_signals, sig_list))
        all_backgrounds = None
        for background_tree in self.background_trees.values():
            bkg_list = np.asarray(background_tree.AsMatrix(VARIABLES))
            if type(all_backgrounds) == type(None):
                all_backgrounds = bkg_list
            else:
                all_backgrounds = np.concatenate((all_backgrounds, bkg_list))
        # Apply cuts
        self.signal_events = []
        for event in all_signals:
            if test_cut({var: event[i] for var, i in CUT_VARIABLES}):
                self.signal_events.append(event)
        self.background_events = []
        for event in all_backgrounds:
            if test_cut({var: event[i] for var, i in CUT_VARIABLES}):
                self.background_events.append(event)
        print("{}/{} signal and {}/{} background events passed cut.".format(len(self.signal_events),
                                                                            len(all_signals),
                                                                            len(self.background_events),
                                                                            len(all_backgrounds)))

    def build_model(self):
        # Override with the code that builds the Keras model.
        pass

class HyperParameterModel(MLTrainingInstance):
    def __init__(self, parameters, signal_paths, background_paths, model_name=None):
        MLTrainingInstance.__init__(self, signal_paths, background_paths)
        self.parameters = parameters
        self.model_name = model_name

    def build_model(self):
        self.model = Sequential()
        self.model.add(Dense(
            self.parameters["initial_nodes"],
            input_dim=len(self.parameters["variables"]),
            kernel_initializer="glorot_normal",
            activation=self.parameters["activation_function"]
            )
        )
        partition = int(self.parameters["initial_nodes"] / self.parameters["hidden_layers"])
        for i in range(self.parameters["hidden_layers"]):
            if self.parameters["regulator"] in ["normalization", "both"]:
                self.model.add(BatchNormalization())
            if self.parameters["regulator"] in ["dropout", "both"]:
                self.model.add(Dropout(0.5))
            if self.parameters["node_pattern"] == "dynamic":
                self.model.add(Dense(
                    self.parameters["initial_nodes"] - (partition * i),
                    kernel_initializer="glorot_normal",
                    activation=self.parameters["activation_function"]
                    )
                )
            elif self.parameters["node_pattern"] == "static":
                self.model.add(Dense(
                    self.parameters["initial_nodes"],
                    kernel_initializer="glorot_normal",
                    activation=self.parameters["activation_function"]
                    )
                )
        # Final classification node
        self.model.add(Dense(
            2,
            activation="sigmoid"
            )
        )
        self.model.compile(
            optimizer=Adam(lr=self.parameters["learning_rate"]),
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )

        if self.model_name != None:
            self.model.save(self.model_name)
        self.model.summary()

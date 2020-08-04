import os

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
CUT_PARAMETERS = {
    "leptonPt_MultiLepCalc":       (">", 50),
    "isElectron":                  ("==", 1),
    "isMuon":                      ("==", 1),
    "corr_met_MultiLepCalc":       (">", 60),
    "MT_lepMet":                   (">", 60),
    "minDR_lepJet":                (">", 0.4),
    "AK4HT":                       (">", 510),
    "DataPastTriggerX":            ("==", 1),
    "MCPastTriggerX":              ("==", 1),
    "NJetsCSVwithSF_MultiLepCalc": (">=", 2),
    "NJets_JetSubCalc":            (">=", 6)
}

VARIABLES = [x[0] for x in varsList.varList["DNN"]]

class MLTrainingInstance(object):
    def __init__(self, signal_paths, background_paths):
        self.signal_paths = signal_paths
        self.background_paths = background_paths

        self.load_trees()

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
        self.signal_events = np.array([])
        for signal_tree in self.signal_trees.values():
            sig_list = np.asarray(signal_tree.AsMatrix(VARIABLES))
            self.signal_events = np.concatenate(self.signal_events, sig_list)
        self.background_events = np.array([])
        for background_tree in self.background_trees.values():
            bkg_list = np.asarray(background_tree.AsMatrix(VARIABLES))
            self.background_events = np.concatenate(self.background_events, bkg_list)
        print signal_events[0]

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

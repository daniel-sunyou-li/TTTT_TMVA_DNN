import os
from pickle import load as pickle_load
from pickle import dump as pickle_dump

os.environ["KERAS_BACKEND"] = "tensorflow"

from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint

from ROOT import TFile

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve, auc

import numpy as np

import varsList

# The parameters to apply to the cut.
CUT_VARIABLES = ["leptonPt_MultiLepCalc", "isElectron", "isMuon",
                 "corr_met_MultiLepCalc", "MT_lepMet", "minDR_lepJet",
                 "AK4HT", "DataPastTriggerX", "MCPastTriggerX",
                 "NJetsCSVwithSF_MultiLepCalc", "NJets_JetSubCalc"]

# TODO: maybe move to varslist?
CUT_STRING = "((%(leptonPt_MultiLepCalc)s > 50 and %(isElectron)s == 1) or " + \
             "(%(leptonPt_MultiLepCalc)s > 50 and %(isMuon)s == 1)) and " + \
             "(%(corr_met_MultiLepCalc)s > 60 and %(MT_lepMet)s > 60 and " + \
             "%(minDR_lepJet)s > 0.4 and %(AK4HT)s > 510) and " + \
             "(%(DataPastTriggerX)s == 1 and %(MCPastTriggerX)s == 1) and " + \
             "(%(NJetsCSVwithSF_MultiLepCalc)s >= 2 and %(NJets_JetSubCalc)s >= 6)"
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
        # Save the cut signal and background events to pickled files
        # TODO: Track cut string in pickle file
        if os.path.exists(sig_path) and os.path.exists(bg_path):
            with open(sig_path, "rb") as f:
                self.signal_events = pickle_load(f)
            with open(bg_path, "rb") as f:
                self.background_events = pickle_load(f)

    def save_cut_events(self, sig_path, bg_path):
        # Load pickled events files
        with open(sig_path, "wb") as f:
            pickle_dump(self.signal_events, f)
        with open(bg_path, "wb") as f:
            pickle_dump(self.background_events, f)

    def select_ml_variables(self, varlist):
        # Select which variables from ML_VARIABLES to use in training
        events = []
        positions = {v: VARIABLES.index(v) for v in varlist}
        for e in self.signal_events:
            events.append([e[positions[v]] for v in varlist])
        for e in self.background_events:
            events.append([e[positions[v]] for v in varlist])
        return events

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

    def train_model(self):
        # Train the model on the singal and background data
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
            1,
            activation="sigmoid"
            )
        )
        self.model.compile(
            optimizer=Adam(lr=self.parameters["learning_rate"]),
            loss="binary_crossentropy",
            metrics=["accuracy"]
        )

        if self.model_name != None:
            self.model.save(self.model_name)
        self.model.summary()

    def train_model(self):
        signal_labels = np.full(len(self.signal_events), [1]).astype("bool")
        background_labels = np.full(len(self.background_events), [0]).astype("bool")

        all_x = np.array(self.select_ml_variables(self.parameters["variables"]))
        all_y = np.concatenate((signal_labels, background_labels))

        print "Splitting data."
        train_x, test_x, train_y, test_y = train_test_split(
            all_x, all_y,
            test_size=0.3
        )

        model_checkpoint = ModelCheckpoint(
            self.model_name,
            verbose=0,
            save_best_only=True,
            save_weights_only=False,
            mode="auto",
            period=1
        )

        early_stopping = EarlyStopping(
            monitor="val_loss",
            patience=self.parameters["patience"]
        )

        # Train
        print "Training."
        history = self.model.fit(
            np.array(train_x), np.array(train_y),
            epochs=self.parameters["epochs"],
            batch_size=2**self.parameters["batch_power"],
            shuffle=True,
            verbose=1,
            callbacks = [early_stopping, model_checkpoint],
            validation_split=0.25
        )

        # Test
        print "Testing."
        model_ckp = load_model(self.model_name)
        self.loss, self.accuracy = model_ckp.evaluate(test_x, test_y, verbose=1)

        self.fpr, self.tpr, _ = roc_curve(test_y.astype(int),
                                          model_ckp.predict(test_x)[:,0])

        self.roc_integral = auc(self.fpr, self.tpr)
        

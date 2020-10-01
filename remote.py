import sys
import os
from base64 import b64decode

os.environ['KERAS_BACKEND'] = 'tensorflow'

from ROOT import TMVA, TCut, TFile

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam

import jobtracker as jt
import varsList

# Parse the arguments
year = int(sys.argv[1])
seed_vars = set(b64decode(sys.argv[2]).split(","))

print("TTTT Condor Job using {} data.".format(year))

# Initialize TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

inputDir = varsList.inputDirCondor2017 if year == 2017 else varsList.inputDirCondor2018
loader = TMVA.DataLoader("tmva_data")
factory = TMVA.Factory("VariableImportance",
                       "!V:!ROC:Silent:!Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification")

# Add variables from seed to loader
num_vars = 0
for var_data in varsList.varList["DNN"]:
    if var_data[0] in seed_vars:
        num_vars += 1
        loader.AddVariable(var_data[0], var_data[1], var_data[2], "F")

# Add signal and background trees to loader
signals = []
signal_trees = []
backgrounds = []
background_trees = []  
for sig in varsList.sig2017_0 if year == 2017 else varsList.sig2018_0:
    signals.append(TFile.Open(inputDir + sig))
    signal_trees.append(signals[-1].Get("ljmet"))
    signal_trees[-1].GetEntry(0)
    loader.AddSignalTree(signal_trees[-1], 1)

for bkg in varsList.bkg2017_0 if year == 2017 else varsList.bkg2018_0:
    backgrounds.append(TFile.Open(inputDir + bkg))
    background_trees.append(backgrounds[-1].Get("ljmet"))
    background_trees[-1].GetEntry(0)
    if background_trees[-1].GetEntries() != 0:
        loader.AddBackgroundTree(background_trees[-1], 1)

# Set weights and cuts
loader.SetSignalWeightExpression(varsList.weightStr)
loader.SetBackgroundWeightExpression(varsList.weightStr)

cut = TCut(varsList.cutStr)

# Prepare tree
loader.PrepareTrainingAndTestTree( 
    cut, cut, 
    "SplitMode=Random:NormMode=NumEvents:!V"
)

# Build model
model_name = "TTTT_TMVA_model.h5"
model = Sequential()
model.add(Dense(100,
                input_dim=num_vars,
                kernel_initializer="glorot_normal", 
                activation="relu")
          )
for _ in range(2):
    model.add(BatchNormalization())
    model.add(Dense(100,
                    kernel_initializer="glorot_normal",
                    activation="relu")
              )
model.add(Dense(2, activation="sigmoid"))

model.compile(
    loss="categorical_crossentropy",
    optimizer=Adam(),
    metrics=["accuracy"]
)

model.save(model_name)
model.summary()

factory.BookMethod(
    loader,
    TMVA.Types.kPyKeras,
    "PyKeras",
    "!H:!V:VarTransform=G:FilenameModel=" + model_name + ":NumEpochs=15:BatchSize=512"
)

(TMVA.gConfig().GetIONames()).fWeightFileDir = "weights"

# Train
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

# Get Results
ROC = factory.GetROCIntegral(loader, "PyKeras")
print("ROC-integral: {}".format(ROC))

factory.DeleteAllMethods()
factory.fMethodsMap.clear()


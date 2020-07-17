import sys
import os.path

from ROOT import TMVA, TCut, TFile

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam

import jobtracker as jt
import varsList

# Parse the arguments
year = int(sys.argv[1])
seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), sys.argv[2])

print("TTTT Condor Job using {} data and seed from {}.".format(year, seed_path))

# Load the seed
seed = jt.Seed.load_from(seed_path)

# Initialize TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

loader = TMVA.DataLoader("tmva_data")
factory = TMVA.Factory("VariableImportance",
                       "!V:!ROC:Silent:!Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification")

# Add variables from seed to loader
num_vars = 0
for var, included in seed.states.iteritems():
    if included:
        num_vars += 1
        var_data = varsList.varList["DNN"][[v[0] for v in varsList.varList["DNN"]].index(var)]
        loader.AddVariable(var_data[0], var_data[1], var_data[2], "F")

# Add signal and background trees to loader
signals = []
signal_trees = []
backgrounds = []
background_trees = []  
for sig in varsList.sig2017_1 if year == 2017 else varsList.sig2018_1:
    signals.append(TFile.Open(os.path.join(varsList.inputDirCondor, sig)))
    signal_trees.append(signals[-1].Get("ljmet"))
    signal_trees[-1].GetEntry(0)
    loader.AddSignalTree(signal_trees[-1], 1)

for bkg in varsList.bkg2017_1 if year == 2017 else varsList.bkg2018_1:
    backgrounds.append(TFile.Open(os.path.join(varsList.inputDirCondor, bkg)))
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


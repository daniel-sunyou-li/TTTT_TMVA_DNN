import sys
import os
from base64 import b64decode

os.environ['KERAS_BACKEND'] = 'tensorflow'

from ROOT import TMVA, TCut, TFile

from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from argparse import ArgumentParser

import jobtracker as jt
import varsList

# Parse the arguments
parser = ArgumentParser()
parser.add_argument( "-y",  "--year", required = True, help = "Sample year" )
parser.add_argument( "-s",  "--seedvars", required = True, help = "Seed value" )
parser.add_argument( "-nj", "--njets", required = True, help = "Number of jets to cut on" )
parser.add_argument( "-nb", "--nbjets", required = True, help = "Number of b jets to cut on" )
args = parser.parse_args()

year = int(args.year)
seed_vars = set(b64decode(args.seedvars).split(","))

print(">> TTTT Condor Job using data from: {}".format( varsList.step2Sample[ args.year ] ) )

# Initialize TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

inputDir = varsList.step2DirEOS[ args.year ] + "nominal/"
loader = TMVA.DataLoader( "tmva_data" )
factory = TMVA.Factory("VariableImportance",
                       "!V:!ROC:Silent:!Color:!DrawProgressBar:Transformations=I;:AnalysisType=Classification")

# Add variables from seed to loader
num_vars = 0
print( ">> Using the following variables: " )
for var_data in varsList.varList["DNN"]:
  if var_data[0] in seed_vars:
    num_vars += 1
    print( "    {:<4} {}".format( str(num_vars) + ".", var_data[0] ) )
    loader.AddVariable( var_data[0], var_data[1], "", "F")

# Add signal and background trees to loader
signals = []
signal_trees = []
backgrounds = []
background_trees = []  
for sig in varsList.sig_training[ args.year ]:
  signals.append( TFile.Open( inputDir + sig ) )
  signal_trees.append( signals[-1].Get("ljmet") )
  signal_trees[-1].GetEntry(0)
  loader.AddSignalTree( signal_trees[-1], 1 )

for bkg in varsList.bkg_training[ args.year ]:
  backgrounds.append( TFile.Open( inputDir + bkg ) )
  background_trees.append( backgrounds[-1].Get( "ljmet" ) )
  background_trees[-1].GetEntry(0)
  if background_trees[-1].GetEntries() != 0:
    loader.AddBackgroundTree( background_trees[-1], 1 )

# Set weights and cuts
cutStr = varsList.cutStr
cutStr += " && ( NJetsCSVwithSF_MultiLepCalc >= {} )".format( args.nbjets ) 
cutStr += " && ( NJets_JetSubCalc >= {} )".format( args.njets ) 
cutStr += " && ( ( isTraining == 1 ) || ( isTraining == 2 ) )"

loader.SetSignalWeightExpression( varsList.weightStr )
loader.SetBackgroundWeightExpression( varsList.weightStr )

cut = TCut( cutStr )

# Prepare tree
loader.PrepareTrainingAndTestTree( 
    cut, cut, 
    "SplitMode=Alternate:MixMode=Alternate:NormMode=NumEvents:!V"
)

# Build model
model_name = "TTTT_TMVA_model.h5"
model = Sequential()
model.add( Dense( num_vars,
                input_dim = num_vars,
                activation = "relu") )
for _ in range( 3 ):
    model.add( BatchNormalization() )
    model.add( Dropout( 0.5 ) )
    model.add( Dense( 50, activation = "relu" ) )
model.add( Dense( 2, activation="sigmoid" ) )

model.compile(
    loss = "categorical_crossentropy",
    optimizer = Adam(),
    metrics = [ "accuracy" ]
)

model.save( model_name )
model.summary()

factory.BookMethod(
    loader,
    TMVA.Types.kPyKeras,
    "PyKeras",
    "!H:!V:VarTransform=G:FilenameModel=" + model_name + ":NumEpochs=30:BatchSize=512:SaveBestOnly=true"
)

(TMVA.gConfig().GetIONames()).fWeightFileDir = "weights"

# Train
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

# Get Results
ROC = factory.GetROCIntegral( loader, "PyKeras")
print( "ROC-integral: {}".format( ROC ) )

factory.DeleteAllMethods()
factory.fMethodsMap.clear()

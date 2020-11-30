import os, sys
from pickle import load as pickle_load
from pickle import dump as pickle_dump

os.environ["KERAS_BACKEND"] = "tensorflow"

from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout
from keras.layers import BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.backend import clear_session

from ROOT import TFile

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.model_selection import ShuffleSplit
from sklearn.utils import shuffle as shuffle_data

import numpy as np

import varsList

# The parameters to apply to the cut.
CUT_VARIABLES = ["leptonPt_MultiLepCalc", "isElectron", "isMuon",
                 "corr_met_MultiLepCalc", "MT_lepMet", "minDR_lepJet",
                 "AK4HT", "DataPastTriggerX", "MCPastTriggerX", "isTraining",
                 "NJetsCSVwithSF_MultiLepCalc", "NJets_JetSubCalc"]

# TODO: maybe move to varslist?
base_cut = "((%(leptonPt_MultiLepCalc)s > 50 and %(isElectron)s == 1) or " + \
            "(%(leptonPt_MultiLepCalc)s > 50 and %(isMuon)s == 1)) and " + \
            "%(corr_met_MultiLepCalc)s > 60 and %(MT_lepMet)s > 60 and " + \
            "%(minDR_lepJet)s > 0.4 and %(AK4HT)s > 510 and " + \
            "( %(DataPastTriggerX)s == 1 and %(MCPastTriggerX)s == 1 ) and " + \
            "( %(isTraining)s == 1 or %(isTraining)s == 2 )"

ML_VARIABLES = [ x[0] for x in varsList.varList[ "DNN" ] ]
VARIABLES = list( sorted( list( set( ML_VARIABLES ).union( set( CUT_VARIABLES ) ) ) ) )
CUT_VARIABLES = [ ( v, VARIABLES.index(v) ) for v in CUT_VARIABLES ]

# Standard saved event locations
CUT_SAVE_FILE = os.path.join( os.getcwd(), "cut_events.pkl" )

SAVE_FPR_TPR_POINTS = 20

print(">> mltools.py using {} variables.".format(len(VARIABLES)))

class MLTrainingInstance(object):
  def __init__(self, signal_paths, background_paths, njets, nbjets):
    self.signal_paths = signal_paths
    self.background_paths = background_paths
    self.cut = base_cut + \
               " and ( %(NJetsCSVwithSF_MultiLepCalc)s >= {} ) ".format( nbjets ) + \
               " and ( %(NJets_JetSubCalc)s >= {} )".format( njets)

  def load_cut_events(self, path):
    # Save the cut signal and background events to pickled files 
    if os.path.exists( path ):
      with open( path, "rb" ) as f:
        cut_events = pickle_load( f )
        if cut_events["condition"] != self.cut:
          print( "[WARN] Cut condition in file {} is different from cut condition in program.".format( path ) )
          print( ">> File will be regenerated." )
          self.load_trees()
          self.apply_cut()
          self.save_cut_events( path )
          print( "[OK] Cut condition file saved." )
          return
        self.cut_events = cut_events

  def save_cut_events( self, path ):
    # Load pickled events files
    with open( path, "wb" ) as f:
      pickle_dump( self.cut_events, f )

  def load_trees( self ):
    # Load signal files
    self.signal_files = {}
    self.signal_trees = {}
    for path in self.signal_paths:
      self.signal_files[ path ] = TFile.Open( path )
      self.signal_trees[ path ] = self.signal_files[path].Get( "ljmet" )
    # Load background files
    self.background_files = {}
    self.background_trees = {}
    for path in self.background_paths:
      self.background_files[ path ] = TFile.Open( path )
      self.background_trees[ path ] = self.background_files[ path ].Get( "ljmet" )
    
  def apply_cut( self ):
    # Apply cut parameters to the loaded signals and backgrounds
    # Load in events
    test_cut = lambda d: eval( self.cut % d )
    all_signals = {}
    for path, signal_tree in self.signal_trees.iteritems():
      sig_list = np.asarray( signal_tree.AsMatrix( VARIABLES ) )
      if path in all_signals:
        all_signals[path] = np.concatenate( ( all_signals[path], sig_list ) )
      else:
        all_signals[path] = sig_list
    all_backgrounds = {}
    for path, background_tree in self.background_trees.iteritems():
      bkg_list = np.asarray( background_tree.AsMatrix( VARIABLES ) )
      if path in all_backgrounds:
        all_backgrounds[ path ] = np.concatenate( ( all_backgrounds[path], bkg_list ) )
      else:
        all_backgrounds[ path ] = bkg_list
    # Apply cuts
    self.cut_events = {
      "condition": self.cut,
      "signal": {},
      "background": {}
    }
    n_s = 0
    c_s = 0
    for path, events in all_signals.iteritems():
      self.cut_events[ "signal" ][ path ] = []
      n_s += len( events )
      for event in events:
        if test_cut( { var: event[i] for var, i in CUT_VARIABLES } ):
          self.cut_events[ "signal" ][ path ].append( event )
          c_s += 1
    n_b = 0
    c_b = 0
    for path, events in all_backgrounds.iteritems():
      self.cut_events[ "background" ][ path ] = []
      n_b += len( events )
      for event in events:
        if test_cut( { var: event[i] for var, i in CUT_VARIABLES } ):
          self.cut_events[ "background" ][ path ].append( event )
          c_b += 1

    print(">> Signal {}/{}, Background {}/{}".format(c_s, n_s, c_b, n_b))
                
  def build_model(self):
    # Override with the code that builds the Keras model.
    pass

  def train_model(self):
    # Train the model on the singal and background data
    pass        

class HyperParameterModel(MLTrainingInstance):
  def __init__(self, parameters, signal_paths, background_paths, njets, nbjets, model_name=None):
    MLTrainingInstance.__init__(self, signal_paths, background_paths, njets, nbjets)
    self.parameters = parameters
    self.model_name = model_name

  def select_ml_variables(self, sig_events, bkg_events, varlist):
    # Select which variables from ML_VARIABLES to use in training
    events = []
    positions = {v: VARIABLES.index(v) for v in varlist}
    for e in sig_events:
      events.append([e[positions[v]] for v in varlist])
    for e in bkg_events:
      events.append([e[positions[v]] for v in varlist])
    return events

  def build_model(self, input_size="auto"):
    self.model = Sequential()
    self.model.add( Dense(
      self.parameters[ "initial_nodes" ],
      input_dim=len(self.parameters["variables"]) if input_size == "auto" else input_size,
      kernel_initializer="glorot_normal",
      activation=self.parameters[ "activation_function" ]
    ) )
    partition = int( self.parameters[ "initial_nodes" ] / self.parameters[ "hidden_layers" ] )
    for i in range( self.parameters[ "hidden_layers" ] ):
      self.model.add( BatchNormalization() )
      if self.parameters[ "regulator" ] in [ "dropout", "both" ]:
        self.model.add( Dropout( 0.5 ) )
      if self.parameters[ "node_pattern" ] == "dynamic":
        self.model.add( Dense(
          self.parameters[ "initial_nodes" ] - ( partition * i ),
          kernel_initializer = "glorot_normal",
          activation=self.parameters[ "activation_function" ]
        ) )
      elif self.parameters[ "node_pattern" ] == "static":
	self.model.add( Dense(
          self.parameters[ "initial_nodes" ],
          kernel_initializer = "glorot_normal",
          activation=self.parameters[ "activation_function" ]
        ) )
      # Final classification node
    self.model.add(Dense(
      1,
      activation = "sigmoid"
    ) )
    self.model.compile(
      optimizer = Adam( lr = self.parameters["learning_rate"] ),
      loss = "binary_crossentropy",
      metrics=[ "accuracy" ]
    )

    if self.model_name != None:
      self.model.save( self.model_name )

    self.model.summary()

  def train_model( self ):
    # Join all signals and backgrounds
    signal_events = []
    for events in self.cut_events[ "signal" ].values():
      for event in events:
        signal_events.append( event )
    background_events = []
    for events in self.cut_events[ "background" ].values():
      for event in events:
        background_events.append( event )
        
    signal_labels = np.full( len( signal_events ), [1] ).astype( "bool" )
    background_labels = np.full( len( background_events ), [0] ).astype( "bool" )

    all_x = np.array( self.select_ml_variables( signal_events, background_events, self.parameters[ "variables" ] ) )
    all_y = np.concatenate( ( signal_labels, background_labels ) )

    print( ">> Splitting data." )
    train_x, test_x, train_y, test_y = train_test_split(
      all_x, all_y,
      test_size = 0.2
    )

    model_checkpoint = ModelCheckpoint(
      self.model_name,
      verbose = 0,
      save_best_only = True,
      save_weights_only = False,
      mode = "auto",
      period = 1
    )

    early_stopping = EarlyStopping(
      monitor = "val_loss",
      patience=self.parameters[ "patience" ]
    )

    # Train
    print( ">> Training." )
    history = self.model.fit(
      np.array( train_x ), np.array( train_y ),
      epochs = self.parameters[ "epochs" ],
      batch_size = 2**self.parameters[ "batch_power" ],
      shuffle = True,
      verbose = 1,
      callbacks = [ early_stopping, model_checkpoint ],
      validation_split = 0.25
    )

    # Test
    print( ">> Testing." )
    model_ckp = load_model( self.model_name )
    self.loss, self.accuracy = model_ckp.evaluate( test_x, test_y, verbose = 1 )
      
    self.fpr_train, self.tpr_train, _ = roc_curve( train_y.astype(int), model_ckp.predict( train_x )[:,0] )
    self.fpr_test,  self.tpr_test,  _ = roc_curve( test_y.astype(int),  model_ckp.predict( test_x )[:,0] )

    self.auc_train = auc( self.fpr_train, self.tpr_train )
    self.auc_test  = auc( self.fpr_test,  self.tpr_test )

class CrossValidationModel( HyperParameterModel ):
  def __init__( self, parameters, signal_paths, background_paths, model_folder, njets, nbjets, num_folds = 5 ):
    HyperParameterModel.__init__( self, parameters, signal_paths, background_paths, njets, nbjets, None )
        
    self.model_folder = model_folder
    self.num_folds = num_folds

    if not os.path.exists( self.model_folder ):
      os.mkdir( self.model_folder )

  def train_model( self ):
    shuffle = ShuffleSplit( n_splits = self.num_folds, test_size = float( 1.0 / self.num_folds ), random_state = 0 )

    # Set up and store k-way cross validation events
    # Event inclusion masks
    print( ">> Splitting events into {} sets for cross-validation.".format( self.num_folds ) )
    fold_mask = {
      "signal": {},
      "background": {}
    }

    for path, events in self.cut_events[ "signal" ].iteritems():
      self.cut_events[ "signal" ][path] = np.array(events)

    for path, events in self.cut_events["background"].iteritems():
      self.cut_events["background"][path] = np.array(events)
        
    for path, events in self.cut_events["signal"].iteritems():
      k = 0
      fold_mask["signal"][path] = {}
      for train, test in shuffle.split(events):
        fold_mask["signal"][path][k] = {
          "train": train,
          "test": test
         }
        k += 1

    for path, events in self.cut_events["background"].iteritems():
      k = 0
      fold_mask["background"][path] = {}
      for train, test in shuffle.split(events):
        fold_mask["background"][path][k] = {
          "train": train,
          "test": test
        }
        k += 1

    # Event lists
    fold_data = []
    for k in range(self.num_folds):
      sig_train_k = np.concatenate([
        self.cut_events["signal"][path][fold_mask["signal"][path][k]["train"]] for path in self.cut_events["signal"]
      ])
      sig_test_k = np.concatenate([
        self.cut_events["signal"][path][fold_mask["signal"][path][k]["test"]] for path in self.cut_events["signal"]
      ])
      bkg_train_k = np.concatenate([
        self.cut_events["background"][path][fold_mask["background"][path][k]["train"]] for path in self.cut_events["background"]
      ])
      bkg_test_k = np.concatenate([
        self.cut_events["background"][path][fold_mask["background"][path][k]["test"]] for path in self.cut_events["background"]
      ])
            
      fold_data.append( {
        "train_x": np.array( self.select_ml_variables(
          sig_train_k, bkg_train_k, self.parameters[ "variables" ] ) ),
        "test_x": np.array( self.select_ml_variables(
          sig_test_k, bkg_test_k, self.parameters[ "variables" ] ) ),

        "train_y": np.concatenate( (
          np.full( np.shape( sig_train_k )[0], 1 ).astype( "bool" ),
          np.full( np.shape( bkg_train_k )[0], 0 ).astype( "bool" ) ) ),
        "test_y": np.concatenate( (
          np.full( np.shape( sig_test_k )[0], 1 ).astype( "bool" ),
          np.full( np.shape( bkg_test_k )[0], 0 ).astype( "bool" ) ) ) 
      } )

    # Train each fold
    print( ">> Beginning Training and Evaluation." )
    self.model_paths = []
    self.loss = []
    self.accuracy = []
    self.fpr_train = []
    self.fpr_test = []
    self.tpr_train = []
    self.tpr_test = []
    self.auc_train = []
    self.auc_test = []
    self.best_fold = -1

    for k, events in enumerate(fold_data):
      print("CV Iteration {} of {}".format(k + 1, self.num_folds))  
      clear_session()

      model_name = os.path.join(self.model_folder, "fold_{}.h5".format(k))

      self.build_model(events["train_x"].shape[1])

      model_checkpoint = ModelCheckpoint(
        model_name,
        verbose=0,
        save_best_only=True,
        save_weights_only=False,
        mode="auto",
        period=1
      )

      early_stopping = EarlyStopping(
        monitor = "val_loss",
        patience=self.parameters[ "patience" ]
      )

      shuffled_x, shuffled_y = shuffle_data( events[ "train_x" ], events[ "train_y" ], random_state=0 )
      shuffled_test_x, shuffled_test_y = shuffle_data( events[ "test_x" ], events[ "test_y" ], random_state=0 )

      history = self.model.fit(
        shuffled_x, shuffled_y,
        epochs = self.parameters[ "epochs" ],
        batch_size = 2**self.parameters[ "batch_power" ],
        shuffle = True,
        verbose = 1,
        callbacks = [ early_stopping, model_checkpoint ],
        validation_split = 0.25
      )

      model_ckp = load_model(model_name)
      loss, accuracy = model_ckp.evaluate(shuffled_test_x, shuffled_test_y, verbose=1)
         
      fpr_train, tpr_train, _ = roc_curve( shuffled_y.astype(int), model_ckp.predict(shuffled_x)[:,0] )
      fpr_test, tpr_test, _ = roc_curve( shuffled_test_y.astype(int), model_ckp.predict(shuffled_test_x)[:,0] )

      auc_train = auc( fpr_train, tpr_train )
      auc_test  = auc( fpr_test, tpr_test )

      if self.best_fold == -1 or auc_test > max(self.auc_test):
        self.best_fold = k

      self.model_paths.append( model_name )
      self.loss.append( loss )
      self.accuracy.append( accuracy )
      self.fpr_train.append( fpr_train[ 0::int( len(fpr_train) / SAVE_FPR_TPR_POINTS ) ] )
      self.tpr_train.append( tpr_train[ 0::int( len(tpr_train) / SAVE_FPR_TPR_POINTS ) ] )
      self.fpr_test.append( fpr_test[ 0::int( len(fpr_test) / SAVE_FPR_TPR_POINTS ) ] )
      self.tpr_test.append( tpr_test[ 0::int( len(tpr_test) / SAVE_FPR_TPR_POINTS ) ] )
      self.auc_train.append( auc_train )
      self.auc_test.append( auc_test )

    print( "[OK ] Finished." )
        

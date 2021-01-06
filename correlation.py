from ROOT import TMVA, TFile, TCut
from random import randint
import numpy as np
import os
from jobtracker import Seed
import varsList

# Initialize TMVA library
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

def get_correlation_matrix(year, variables, njets, nbjets):
  # Returns the correlation matrix of the given variables
  # Get signal and background paths
  signal_path = os.path.join(os.getcwd(),
                             varsList.step2Sample[ str(year) ] + "/nominal/",
                             varsList.sig_training[ str(year) ][0] )
  bkgrnd_path = os.path.join(os.getcwd(),
                             varsList.step2Sample[ str(year) ] + "/nominal/",
                             varsList.bkg_training[ str(year) ][0] )

  # Create TMVA object
  loader = TMVA.DataLoader("tmva_data")

  # Load used variables
  for var in variables:
    try:
      var_data = varsList.varList["DNN"][ [ v[0] for v in varsList.varList["DNN"] ].index(var) ]
      loader.AddVariable( var_data[0], var_data[1], "", "F" )
    except ValueError:
      print( "[WARN] The variable {} was not found. Omitting.".format(var) )

  # Open ROOT files
  signal_f = TFile.Open( signal_path )
  signal = signal_f.Get( "ljmet" )
  bkgrnd_f = TFile.Open( bkgrnd_path )
  bkgrnd = bkgrnd_f.Get( "ljmet" )

  # Load signal and background
  loader.AddSignalTree(signal)
  loader.fTreeS = signal
  loader.AddBackgroundTree(bkgrnd)
  loader.fTreeB = bkgrnd

  # Set weights
  weight_string = varsList.weightStr
  loader.SetSignalWeightExpression( weight_string )
  loader.SetBackgroundWeightExpression( weight_string )

  # Set cuts
  cutStr = varsList.cutStr
  cutStr += " && ( NJetsCSVwithSF_MultiLepCalc >= {} )".format( nbjets ) 
  cutStr += " && ( NJets_JetSubCalc >= {} )".format( njets )
  cutStr += " && ( ( isTraining == 1 ) || ( isTraining == 2 ) )"
  cut_string = TCut( cutStr )
  loader.PrepareTrainingAndTestTree(
    cut_string, cut_string,
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V:VerboseLevel=Info"
  )
    
  # Set the pointer to the right histogram
  loader.GetDefaultDataSetInfo().GetDataSet().GetEventCollection()
    
  # Retrieve the signal correlation matrix
  sig_th2 = loader.GetCorrelationMatrix( "Signal" )

  n_bins = sig_th2.GetNbinsX()
  sig_corr = np.zeros( ( n_bins, n_bins ) )
    
  for x in range(n_bins):
    for y in range(n_bins):
      sig_corr[x, y] = sig_th2.GetBinContent(x + 1, y + 1)
    
  return sig_corr

def reweight_importances( year, variables, importances, njets, nbjets ):
  # Re-weight the variable importances
  corr_mat = abs( get_correlation_matrix( int(year), variables, njets, nbjets ) / 100.0 )
  mod_corr_mat = np.zeros( ( len( corr_mat ), len( corr_mat ) ) )
  for i in range(len(corr_mat)):
    for j in range(len(corr_mat)):
      if i == j:
     	mod_corr_mat[i,j] = corr_mat[i,j]
      elif j > i:
        mod_corr_mat[i,j] = corr_mat[i,j]
        for k in range(j):
          if k > i:
            mod_corr_mat[i,j] *= 1.0 - corr_mat[k,j]
    
  wgt_sig_mat = np.array([ np.multiply(importances,mod_corr_mat[i]) for i in range(len(corr_mat)) ])
  weightLSig = np.zeros(len(corr_mat))
  weightQSig = np.zeros(len(corr_mat))
  for i in range(len(corr_mat)):
    for j in range(len(corr_mat)):
      if i == j:
        weightLSig[i] = wgt_sig_mat[i,j]
        weightQSig[i] = wgt_sig_mat[i,j]**2
      if j > i:
        weightLSig[i] -= wgt_sig_mat[i,j]
        weightQSig[i] -= wgt_sig_mat[i,j]**2
    
  print("Weighted Quadratic Sum: {}".format(np.sum(np.sqrt(weightQSig))))
  print("Weighted Linear Sum: {}".format(np.sum(weightLSig)))
  return weightLSig, np.sqrt(weightQSig)

def get_correlated_groups(corr_mat, variables, cutoff):
  # Returns the groups of variables which are <cutoff> or more correlated
  shape = np.shape(corr_mat)

  # Find pairs of correlated variables
  pairs = []
  for i in range(shape[0]):
    for j in range(i+1, shape[1]):
      if abs(corr_mat[i,j]) >= float( cutoff ):
        pairs.append([variables[i],variables[j]])

  # Find correlated groups
  groups = []
  grouped = []
  for i, pair_i in enumerate( pairs ):
    if i in grouped: continue
    else:
      this_group = pair_i[:]
      for j, pair_j in enumerate( pairs[i:] ):
        if i + j in grouped: continue
        else:
          if len( set( this_group ) & set( pair_j ) ) > 0:
            this_group = list( set( this_group + pair_j ) )
            grouped.append( i + j )
      groups.append( sorted( this_group ) )
    grouped.append( i )
				
  return groups, pairs
                    
def generate_uncorrelated_seeds(count, variables, cutoff, year, njets, nbjets):
  # Generates <count> uncorrelated Seed objects using the specified variables
  # Get correlated pairs of variables
  groups, _ = get_correlated_groups(
    get_correlation_matrix(year, variables, njets, nbjets),
    variables,
    cutoff
  )

  # Generate some random seeds
  seeds = [Seed.random(variables) for _ in range( int(count) ) ]

  # Find seeds that violate correlated pairs and modify them

  for seed in seeds:
    for group in groups:
      # group = {X, Y, Z} are highly correlated
      group_vars = [v for v in group if seed.includes(v)]
      # group_vars = {X, Z} -> variables from <group> which are ON in seed (seed.includes(Y) == False)
      if len(group_vars) > 1:
        # This seed needs to be modified.
        keep = randint(0, len(group_vars))
        # Pick a random variable from {X, Z} to keep: for example Z (1).
        for i, gv in enumerate(group_vars):
          if i != keep:
            # for i == 0 (X) -> exclude X from seed
            seed.exclude(gv)

  return seeds

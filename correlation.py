from ROOT import TMVA, TFile, TCut
from random import randint
import numpy as np
import os
from jobtracker import Seed
import varsList

# Initialize TMVA library
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# Load parameters
weight_string = varsList.weightStr
cut_string = TCut(varsList.cutStr)

def get_correlation_matrix(year, variables):
    # Returns the correlation matrix of the given variables
    # Get signal and background paths
    signal_path = os.path.join(os.getcwd(),
                               varsList.step2Sample2017 if year == 2017 else varsList.step2Sample2018,
                               varsList.sig2017_0[0] if year == 2017 else varsList.sig2018_0[0])
    bkgrnd_path = os.path.join(os.getcwd(),
                               varsList.step2Sample2017 if year == 2017 else varsList.step2Sample2018,
                               varsList.bkg2017_0[0] if year == 2017 else varsList.bkg2018_0[0])

    # Create TMVA object
    loader = TMVA.DataLoader("tmva_data")

    # Load used variables
    for var in variables:
        try:
            var_data = varsList.varList["DNN"][[v[0] for v in varsList.varList["DNN"]].index(var)]
            loader.AddVariable(var_data[0], var_data[1], var_data[2], "F")
        except ValueError:
            print("[WARN] The variable {} was not found. Omitting.".format(var))

    # Open ROOT files
    signal_f = TFile.Open(signal_path)
    signal = signal_f.Get("ljmet")
    bkgrnd_f = TFile.Open(bkgrnd_path)
    bkgrnd = bkgrnd_f.Get("ljmet")

    # Load signal and background
    loader.AddSignalTree(signal)
    loader.fTreeS = signal
    loader.AddBackgroundTree(bkgrnd)
    loader.fTreeB = bkgrnd

    # Set weights
    loader.SetSignalWeightExpression(weight_string)
    loader.SetBackgroundWeightExpression(weight_string)

    # Set cuts
    loader.PrepareTrainingAndTestTree(
        cut_string, cut_string,
        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V:VerboseLevel=Info"
    )
    
    # Set the pointer to the right histogram
    loader.GetDefaultDataSetInfo().GetDataSet().GetEventCollection()
    
    # Retrieve the signal correlation matrix
    sig_th2 = loader.GetCorrelationMatrix("Signal")

    n_bins = sig_th2.GetNbinsX()
    sig_corr = np.zeros((n_bins, n_bins))
    
    for x in range(n_bins):
        for y in range(n_bins):
            sig_corr[x, y] = sig_th2.GetBinContent(x + 1, y + 1)
    
    return sig_corr

def reweight_importances(year, variables, importances):
    # Re-weight the variable importances
    corr_mat = get_correlation_matrix(int(year), variables)
    row_sum_inv_sq = (corr_mat.sum(axis=1))**(-2)
    weight_mat = np.array([
        np.multiply(row_sum_inv_sq[i], corr_mat[i]) for i in range(len(corr_mat))
    ])
    weighted_sig = np.dot(weight_mat, importances)
    return weighted_sig


def get_correlated_groups(corr_mat, variables, cutoff):
    # Returns the groups of variables which are <cutoff> or more correlated
    shape = np.shape(corr_mat)

    # Find pairs of correlated variables
    pairs = []
    in_pairs = lambda p: len([x for x in pairs if x[0] == p]) != 0
    for i in range(shape[0]):
        for j in range(i + 1, shape[1]):
            if corr_mat[i,j] >= cutoff:
                pair = set([variables[i], variables[j]])
                if not in_pairs(pair):
                    pairs.append((pair, corr_mat[i, j]))

    print("Found {} correlated pairs.".format(len(pairs)))

    # Find correlated groups
    correlated = []
    for var in variables:
        var_pairs = [p[0] for p in pairs if var in p[0]]
        if len(var_pairs) > 1:
            c_grp = set()
            for v_pair in var_pairs:
                c_grp.update(v_pair)
            if not c_grp in correlated:
                print("Found group {}".format(c_grp))
                correlated.append(c_grp)
        elif len(var_pairs) == 1:
            print("Listing correlated pair {}".format(var_pairs[0]))
            correlated.append(var_pairs[0])
            
    return correlated, pairs
                    
def generate_uncorrelated_seeds(count, variables, cutoff, year):
    # Generates <count> uncorrelated Seed objects using the specified variables
    # Get correlated pairs of variables
    groups, _ = get_correlated_groups(
        get_correlation_matrix(year, variables),
        variables,
        cutoff)

    # Generate some random seeds
    seeds = [Seed.random(variables) for _ in range(count)]

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

    
        

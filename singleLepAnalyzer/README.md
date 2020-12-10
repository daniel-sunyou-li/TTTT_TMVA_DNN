# Single Lep Analyzer (DNN) -- Quick Start Instructions

The singleLepAnalyzer framework is split into 6 overall steps, beginning with step3 `.root` files produced by `application.py` and ending with the calculation of the yield limits.  The process occurs over the course of five steps:

1. 
2.
3.
4.
5.

Each step can be run using the `submit_SLA.py -s [#] -c [config file]` script using the input command `-s` to indicate a step from `1` to `5` and `-c` indicates which configuration file to use. A unit test submission can be made using the tag `--test`. The configuration file template with default values is provided as `config_SLA.ini` and __should be edited__ to the user's discretion.

## Detailed Description

### Step 1: Make Single Lep Analyzer Templates 
In this step, a Condor job is submitted to consolidate the background, signal, and/or data samples into a pickled file (histogram) containing information for the [variables of interest](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/varsList.py#L572-L573) specified in the config `.ini` file. Each of the background, signal and data file has its own histogram, with each histogram containing information on the same specified variables. The histograms are further categorized based on lepton flavor (electron or muon) and various (flavored) jet cuts.  Each category will have its own set of background, signal and data histograms.  The total number of histograms produced in "Step 1" is:

  Number of Histograms = ( 3 [BKG/SIG/DAT] ) x ( 2 [E/M] ) x ( # HOT-jets ) x ( # t-jets ) x ( # b-jets ) x ( # W-jets ) x ( # jets )
  
fds

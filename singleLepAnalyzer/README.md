# Single Lep Analyzer (DNN)

## Quick Start Instructions

The singleLepAnalyzer framework is split into 5 overall steps, beginning with step3 `.root` files produced by `application.py` and ending with the calculation of the yield limits:

__1.  Produce signal/background/data histograms for each variable__
__2.  Produce the combine templates and compute all systematics, re-bin the histograms for combine, and visualize the distributions__
3. 
4.
5.

Each step can be run using the `submit_SLA.py -s [#] -c [config file]` script using the input command `-s` to indicate a step from `1` to `5` and `-c` indicates which configuration file to use. A unit test submission can be made using the tag `--test`. The configuration file template with default values is provided as [`config_SLA.json`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/config_SLA.json) and __should be edited__ to the user's discretion.

## Detailed Description
The results of the Single Lep Analyzer will all be stored in a subdirectory: `/TTTT_TMVA_DNN/singleLepAnalyzer/templates_[year]/`. The Condor `.job` scripts and the `.log`, `.out` and `.err` files are stored in `/TTTT_TMVA_DNN/singleLepAnalyzer/log_step[#]_[date]/`.

### Step 1: Make Histograms 
In this step, a Condor job is submitted to consolidate the background, signal, and/or data samples into a pickled file (histogram) containing information for the [variables of interest](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/varsList.py#L572-L573) specified in the config `.json` file. Additionally, the EOS folders to store the histograms are created in the submission script.  Each of the background, signal and data file has its own histogram, with each histogram containing information on one of the specified variables. The histograms are further categorized based on lepton flavor (electron or muon) and various (flavored) jet cuts.  Each category will have its own set of background, signal and data histograms.  The total number of histograms produced in "Step 1" is:

  Number of Histograms = ( 3 [BKG/SIG/DAT] ) x ( 2 [E/M] ) ( # Variables ) x ( # HOT-jets ) x ( # t-jets ) x ( # b-jets ) x ( # W-jets ) x ( # jets )
  
The resulting histograms are stored in the EOS path(s): `root://cmseos.fnal.gov:///store/user/[EOS username]/FWLJMET102X_1lep[year]_Oct2019_4t_[sample date]_step3/templates/[category]/[bkg/sig/data]_[variable].pkl`. For running multiple iterations of the workflow, edit the configuration parameter `config_SLA[ "STEP 1" ][ "EOSFOLDER" ]`.  The number of Condor jobs produced is equivalent to `( # variables ) x ( # years ) x ( # categories )`.  For each Condor job, the script `hists.py`--which references `analyze.py` and `utils.py`--is run once and stores the resultant three histograms on EOS at the specified path.

### Step 2: Consolidate Histograms and Format for Combine, Also Visualize

### Step 3: Produce the Configuration Files for Higgs Combine

### Step 4: Run Higgs Combine on Either 2017 or 2018

### Step 5: Combine Results from 2017 and 2018




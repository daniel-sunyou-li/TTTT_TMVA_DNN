# Single Lep Analyzer (DNN)

## Quick Start Instructions

The singleLepAnalyzer framework is split into 5 overall steps, beginning with step3 `.root` files produced by `application.py` and ending with the calculation of the yield limits:  

> __1.  Produce signal/background/data histograms for each variable__  
> __2.  Produce the combine templates and compute all systematics__  
> 3.  Re-bin the histograms for combine and plot the templates (WIP)  
> 4.  
> 5.  

Each step can be run using the `submit_SLA.py -s [#] -c [config file]` script using the input command `-s` to indicate a step from `1` to `5` and `-c` indicates which configuration file to use. A unit test submission can be made using the tag `--test`. The configuration file template with default values is provided as [`config_SLA.json`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/config_SLA.json) and __should be edited__ to the user's discretion.

## Detailed Description
The results of the Single Lep Analyzer will all be stored in a subdirectory: `/TTTT_TMVA_DNN/singleLepAnalyzer/templates_[year]/`. The Condor `.job` scripts and the `.log`, `.out` and `.err` files are stored in `/TTTT_TMVA_DNN/singleLepAnalyzer/log_step[#]_[date]/`.

### Step 1: Make Histograms 
___Relevant Scripts:___
* `submit_SLA.py`
* `step1.sh`
* `hists.py`
* `analyze.py`
* `utils.py`

In this step, a Condor job is submitted to consolidate the background, signal, and/or data samples into a pickled file (histogram) containing information for the [variables of interest](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/varsList.py#L572-L573) specified in the config `.json` file. Additionally, the EOS folders to store the histograms are created in the submission script.  Each of the background, signal and data file has its own histogram, with each histogram containing information on one of the specified variables. The histograms are further categorized based on lepton flavor (electron or muon) and various (flavored) jet cuts.  Each category will have its own set of background, signal and data histograms.  The total number of histograms produced in "Step 1" is:

  Number of Histograms = ( 3 [BKG/SIG/DAT] ) x ( 2 [E/M] ) ( # Variables ) x ( # HOT-jets ) x ( # t-jets ) x ( # b-jets ) x ( # W-jets ) x ( # jets )
  
The resulting histograms are stored in the EOS path(s): `root://cmseos.fnal.gov:///store/user/[EOS username]/FWLJMET102X_1lep[year]_Oct2019_4t_[sample date]_step3/templates/[category]/[bkg/sig/data]_[variable].pkl`. For running multiple iterations of the workflow, edit the configuration parameter `config_SLA[ "STEP 1" ][ "EOSFOLDER" ]`.  The number of Condor jobs produced is equivalent to `( # variables ) x ( # years ) x ( # categories )`.  For each Condor job, the script `hists.py`--which references `analyze.py` and `utils.py`--is run once and stores the resultant three histograms on EOS at the specified path.

The histograms are specifically created in [`analyze.py`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/analyze.py#L145-L477) and returned in the `hists.py` script.  The `analyze.py` script is run for each [combination of sample, variable, category and year]( https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/hists.py#L89-L92 ).  The `hists.py` script collects a group of histograms based on the sample classification (background, signal, data) and dumps the histograms into a pickled file.  

__[ADD FURTHER EXPLANATION OF ANALYZE.PY]__

### Step 2: Consolidate Histograms and Compute Systematics into ROOT Files for Higgs Combine
___Relevant Scripts:___
* `submit_SLA.py`
* `step2_SLA.sh`
* `templates.py`

In this step, a Condor job is submitted to consolidate all the background, signal and data histograms from each category into a single `ROOT` file.  A single job is submitted per year. The Condor job runs the script [`templates.py`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/templates.py).  The `templates.py` script performs several tasks:  
* __Write Theta templates:__ produces a `ROOT` file for each variable and year (I can probably phase this out for now since it seems as if only Combine is being used)
* __Write Combine templates:__ produces a `ROOT` file for each variable and year
* __Write Summary templates:__ produces a `ROOT` file for each year
* __Write yield tables:__ produces a `.txt` file for each variable and year  
The templates are later used in Higgs Combine to compute the limits.

__[ADD FURTHER EXPLANATION OF TEMPLATES.PY]__
* need to distinguish between the different templates and what exactly goes into a template
* what is the "interesting" information in the yield tables

### Step 3: Re-bin the Histograms and Plot the Templates
___Relevant Scripts:___
* `submit_SLA.py`
* `step3_SLA.sh`
* `modify_binning.py`
* `plot_templates.py`

In this step, a Condor job is submitted that first re-bins the histograms for the Higgs Combine templates and then produces `.png` plots from the templates.  A single job is submitted per combination of variable and year. The result of the `modify_binning.py` script is to produce a new `ROOT` file for the previously produced Combine template with a modification to the naming by including the tag 'rebin'. Additionally, new yield tables are produced based on the modified binning. The result of the `plot_templates.py` script is the production of a plot for each combination of variable, category and year.  The `plot_templates.py` script can opt to either use the `original` or `modified` binning, this parameter "PLOT" is set in the `.json` [configuration file](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/singleLepAnalyzer/config_SLA.json#L18).

__[ADD FURTHER EXPLANATION ABOUT HOW THE BINNING IS MODIFIED]__
__[ADD FURTHER EXPLANATION ABOUT WHAT IS BEING PLOTTED]__

### Step 4: Run Higgs Combine on Either 2017 or 2018

### Step 5: Combine Results from 2017 and 2018




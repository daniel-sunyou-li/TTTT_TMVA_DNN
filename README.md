# TTTT Single-Lepton Final State DNN -- Quick Start Instructions #
This repository contains code for producing step3 `.root` files used in calculating the limits for the single-lepton final state in four top quark events. The code is partitioned into four steps:

1. [__Variable Importance Calculation__](#Submit-Variable-Importance-Condor-Jobs)
2. [__Hyper Parameter Optimization__](#Run-the-Hyper-Parameter-Optimization)
3. [__k-Fold Cross Validation Training__](#Run-the-k-fold-Cross-Validation)
4. [__step3 `.root` File Production__](#Submit-Step3-Condor-Jobs)

The step3 files are to be used by the [singleLepAnalyzer](https://github.com/BrownCMS/singleLepAnalyzer) to produce the limits. The TTTT DNN code is intended to be run on the LPC while the singleLepAnalyzer is intended to be run on the Brown Linux server (BRUX).  To run all the code successfully, you will need to have accounts on BRUX, FNAL LPC and CERN LXPLUS.  You will also need storage requested on [CMSEOS](https://uscms.org/uscms_at_work/computing/LPC/usingEOSAtLPC.shtml#createEOSArea) and have a working [CERN grid certificate](https://uscms.org/uscms_at_work/computing/getstarted/get_grid_cert.shtml). The general-use instructions are as follows:

## Setup on LPC
Sign-in to the LPC using your FNAL [username]

    kinit -f [username]@FNAL.GOV
    ssh -xy [username]@cmslpc-sl7.fnal.gov

Retrieve the CMSSW environment (BASH #TCSH)

    cd nobackup/
    
    export SCRAM_ARCH=slc7_amd64_gcc630
    # setenv SCRAM_ARCH slc7_amd64_gcc630
    source /cvmfs/cms.cern.ch/cmsset_default.sh
    # source /cvmfs/cms.cern.ch/cmsset_default.csh
    
Clone the repository

    cd CMSSW_9_4_6_patch1/src/
    cmsenv
    git clone https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN.git
    cd ./TTTT_TMVA_DNN/
    chmod u+rwx *
    
Edit the `varsList.py` file to set your usernames and the sample date:
* `bruxUserName`
* `lpcUserName`
* `eosUserName`
* `date` 
    
Setup the repository.  This will take some time. There are two possible choices for the year: 2017 or 2018.  The settings used below are for general-use, refer to [`description.md`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/blob/test/description.md) for a detailed explanation of all the options.

    pip install --user scikit-optimize
    python ./setup/setup.py -y 2017 -sys -r -t -eos -v
    
## Submit Variable Importance Condor Jobs
Setup the environment for submitting the Condor jobs

    source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
    # source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.csh
    source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh
    # source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh
    
Note that after running these source commands, you will not be able to upload files to CMSEOS.  You will need to restart the console and follow the previous steps. Submit _n_ seed Condor jobs.  The `.job`, `.log`, `.out` and `.err` files are stored in the directory `condor_log_[day].[month].[year]`. The following options should be modified depending on your situation:
* `year (-y)` = `2017` or `2018`  
* `njets (-nj)` = `2` or `4`  
* `correlation (-c)` = `50` to `100`, `60` (recommended)  
* `seeds (-n)` = `500` (recommnded)  

Submit the jobs using:

    python submit.py -y 2017 -nj 4 -c 60 -n 500

While the jobs run, check on the progress using:
 
    python folders.py condor_log_[day].[month].[year]
    
if there are any failed jobs, resubmit with:

    python submit.py -y 2017 --unstarted -r condor_log_[day].[month].[year]

## Run the Variable Importance Calculation
After all your jobs have finished, calculate the variable importance.  First, compact all of the Condor results to a `.jtd` file with:

    python folders.py -c condor_log_[day].[month].[year]
    
At this point, it's recommended to move all the `.jtd` files for a given set of {`year`, `njets`} into one directory:

    mkdir condor_log_4j_2017
    mv *.jtd condor_log_4j_2017/
    
Run the calculation script and save the results to a similarly named directory

    mkdir dataset_4j_2017
    python calculate.py -f dataset_4j_2017 condor_log_4j_2017/*
    
The results produced are used automatically in the following steps. They can also be visualized using the python notebooks located in the [/notebooks/](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/tree/test/notebooks) repository.
    
## Run the Hyper Parameter Optimization
Hyper parameter optimization is used to optimize the performance of a neural network by tuning the network architecture for a given number of input variables using the `scikit-optimize` library.  The input variables are grouped based on their ranking, determined in the previous step.  For this step, it is important _not_ to run the previous `source` command and `cmsenv`. The main option to set for this step is `numvars (-n)` = `1` to `76`, the recommended number is to include all variables that have a non-zero, positive importance value:

    source /cvmfs/cms.cern.ch/cmsset_default.sh
    # source /cvmfs/cms.cern.ch/cmsset_default.csh
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-centos7-gcc8-opt/setup.sh
    # source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-centos7-gcc8-opt/setup.csh
    python hyperopt.py -y 2017 -n 50 -nj 4 dataset_4j_2017/
    
## Run the k-fold Cross Validation
After determining the an optimal set of hyper parameters, with the results stored in a directory of the form `/dataset_4j_2017/1to50/`, run the `k`-fold cross validation to obtain statistics on the model performance.  The command is:

    source /cvmfs/cms.cern.ch/cmsset_default.sh
    # source /cvmfs/cms.cern.ch/cmsset_default.csh
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-centos7-gcc8-opt/setup.sh
    # source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-centos7-gcc8-opt/setup.csh
    python final.py -y 2017 -k 10 -f dataset_4j_2017/1to50/ dataset_4j_2017/1to50/
    
After this step finishes, the model with the best performance out of the `k` folds is saved in `/dataset_4j_2017/1to50/` and will be applied to the produce the step3 files on Condor. 

## Submit Step3 Condor Jobs
The step3 files will be stored on CMSEOS. The step3 script can take multiple models so the step3 file can hold multiple discriminators for different sets of jet cuts and number of input variables. The command is:

    source /cvmfs/cms.cern.ch/cmsset_default.sh
    # source /cvmfs/cms.cern.ch/cmsset_default.csh
    cmsenv
    python application.py -y 2017 -l application_log_2017 -sys -v dataset_4j_2017/1to40/ dataset_4j_2017/1to50/
    
The Condor jobs can be checked directly by checking the Condor job outputs:

    ls application_log_2017/*.out | wc # the number of finished jobs
    ls application_log_2017/*.log | wc # the total number of jobs
    
For any jobs that failed, resubmit using:

    python application.py -y 2017 -l application_log_resubmit -v -r application_log_2017 dataset_4j_2017/1to40/ dataset_4j_2017/1to50/
    
Once jobs are finished, you will find the step3 files stored on CMSEOS at:

    eosls /store/user/[EOS Username]/FWLJMET102X_1lep2017_Oct2019_4t_10072020_step2/[tag]/
    
where `tag` can be `nominal`, `JECup`, `JECdown`, `JERup`, or `JERdown`.  After finishing producing the step3 files, refer to the [`singleLepAnalyzer`](https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN/tree/test/singleLepAnalyzer) subdirectory for instructions for running on BRUX.
    

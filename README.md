# TTTT 2017 DNN Classifier using ROOT.TMVA #
__Train a dense neural network to classify .ROOT samples as being either signal (TTTT) or background events.__\
__***Needs updating***__

There are three general steps for this analysis:
  1.  _Input variable importance calculation_
  2.  _Dense neural network hyper parameter optimization_
  3.  _Evaluate a fully trained optimized dense neural network classifier_

### Set-up Instructions for BRUX
    # sign-in to BRUX
    ssh -XY [username]@brux.hep.brown.edu
    
    # retrieve the CMSSW environment
    source /cvmfs/cms.cern.ch/cmsset_default.sh
    export SCRAM_ARCH=slc7_amd64_gcc630
    cmsrel CMSSW_9_4_6_patch1
    cd CMSSW_9_4_6_patch1/src/
    cmsenv
    
    # clone the repository
    git clone https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN.git
    cd ./TTTT_TMVA_DNN/
    mkdir dataset
    pip install --user scikit-optimize # this should be stored in .local/lib/python2.7/site-packages
    
### Set-up Instructions for LPC
    # sign-in to LPC
    kinit -f [username]@FNAL.GOV
    ssh -XY [username]@cmslpc-sl7.fnal.gov
    
    cd nobackup/
    
    # retrieve the CMSSW environment
    source /cvmfs/cms.cern.ch/cmsset_default.csh
    export SCRAM_ARCH=slc7_amd64_gcc530
    cmsrel CMSSW_9_4_6_patch1
    cd CMSSW_9_4_6_patch1/src/
    cmsenv
    
    # clone the repository
    git clone https://github.com/daniel-sunyou-li/TTTT_TMVA_DNN.git
    cd ./TTTT_TMVA_DNN/
    chmod u+rwx *
    mkdir dataset
    
    # recommended to only use LPC for variable importance, so don't need scikit-optimize

    
Some of the scripts have the line `os.system('bash')` which is required for setting up the environment but requires `exit` in the command line after running the script to view the outputs.
      
### Datasets ###
We are using 2017 Step 2 LJMET samples that are stored in: `/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_12122019_step2/nominal/`
* The directory is also listed in `varsList.py` as `inputDir`

There is one signal sample: `TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root`
* You can select backgrounds--the essential ones are `TTToSemiLeptonic`

### Importing Datasets to LPC ###
When running variable importance on the LPC, we need to import the signal and background samples onto both the LPC storage and the EOS storage. Run the commands:

`python ~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/setupLPC.py`

In case there are issues with the tar file, then make adjustments to `TTTT_TMVA_DNN` and run the commands,

    tar -zcvf CMSSW946.tgz ~/nobackup/CMSSW_9_4_6_patch1/
    xrdcp CMSSW946.tgz root://cmseos.fnal.gov//store/user/<EOS Username>

Make sure that the background samples specified (uncommented) in `varsList.py` are reflected in `LPC/VariableImportanceLPC_step2.sh`.

## 1. Input Variable Importance Calculation ###
__Calculate the relative importance of a Step 2 input variable in training a dense neural network classifier.  Then, the "unimportant" variables can be excluded from subsequent training to save time.__
### 1.1 (Optional) Edit `varsList.py` ###
`varsList.py` contains a python `dict` named `varList["BigComb"]` containing lists of: the input variable name, expression and units.  Comment out (or uncomment) the variables being included in the variable importance calculation.
* As of the 2017 Step 2 samples, there are an additional 11 HOT Tagger variables
### 1.2 (Optional) Edit the network architecture ###
If you would like to change the generic unoptimized network architecture being trained, then you can edit `TMVAClassification_VariableImportance.py`.  
### 1.3.1 Run the variable importance calculation script ###
The variable importance analysis is run by the command:

    mkdir condor_log
    voms-proxy-init --valid 192:00 -voms cms
    ./submit_VariableImportance.sh LPC # or BRUX

which submits Condor jobs, each representing a different input subset to be trained.  The results and logs are stored in `condor_log` where the desired result is the ROC value, which is contained in the `.out` file.

If submitting on the LPC, be sure to edit the username parameters in:
1. `setupLPC.py`
2. `VariableImportanceLPC_step2.sh`

### 1.3.2 Resubmit failed Condor jobs ###
To check the status of the Condor job, use the command: `condor_q`
* Using the option `-better-analyze` provides a summary of available nodes

You can identify a failed job by noting a small `.out` file size and checking the `.err` log. In the case of failed jobs, run the script:

`python resubmit_VariableImportance.sh BRUX # or LPC`

which iterates through the `.out` files identifying if the ROC value is present.  Keep running the script so long as there are failed Condor jobs. 

On the LPC, if a job uses more memory than specified in the Condor job submission file, then the scheduler will remove the job. To adjust the memory usage, edit `/LPC/VariableImportanceLPC_step1.py` and adjust the variable `request_memory`.
* Advised to ([read the description of the LPC condor cluster machines](https://uscms.org/uscms_at_work/computing/setup/batch_systems_advanced.shtml)) before adjusting parameters

### 1.4.1 Calculate the variable importance ###
After ensuring that all jobs are finished running--or finding out by the calculation script failing--run the script:

`python VariableImportance_Calculation.py`

which iterates through all the `.out` files determining the relative importance of the variables and storing the results in `TTTT_TMVA_DNN/dataset/VariableImportanceResults_vars[#].txt`.

### 1.4.2 Plot the variable importance ###
Because BRUX cannot display graphics, to visualize the variable importance, we need to move `VariableImportanceResults_vars[#].txt` to a different system.  Using a Jupyter python notebook ([Google Colab](https://colab.research.google.com/notebooks/welcome.ipynb) or [CERN SWAN](swan.cern.ch)):
1. From a local repository (or from the terminal in SWAN) use: `scp [brux_username]@brux.hep.brown.edu:/path/to/file.txt/ ./` or `scp [lpc_username]@cmslpc-sl7.fnal.gov:/path/to/file/`
2. Run `VariableImportance_Plot.ipynb` which should generate a bar graph of the variable importance.
* For Google Colab, be sure to use the code:

      from google.colab import drive
      drive.mount('/content/drive',force_remount = True)
      %cd /content/drive/My Drive/
    
## 2 Hyper Parameter Optimization ##
__Determine the optimal dense neural network hyper parameters for a given input using `scikit-optimize`.__
### 2.1 (Optional) Edit `varsList.py` ###
Comment out the variables in `varsList.varList` that do not contribute to the classifier performance.
### 2.2 (Optional) Edit the hyper parameter survey space in `TMVAClassificationPyKeras_OptimizationWrapper.py` ###
To make best use of this step, select a reduced input variable set.  By default, there are seven hyper parameters being optimized:
* `HIDDEN (Integer)`: the number of hidden layers in the dense network
* `NODES (Integer)`: the number of initial input nodes
* `PATTERN (Categorical)`: choosing between a static number or reducing number of nodes per hidden layer
* `BATCH_POW (Integer)`: the power determining the batch size where `BATCH_SIZE = 2**{BATCH_POW}`
* `LRATE (Real)`: the starting learning rate for the model optimizer (`Adam`)
* `REGULATOR (Categorical)`: choosing the combination of training regulators (i.e. Dropout, Batch normalization)
* `ACTIVATION (Categorical)`: the activation function that transforms the node output (i.e. ReLU, Softplus)

For each of these hyper parameters, the survey space can be edited before running the analysis.  Also, there are static parameters that can be edited:
* `EPOCHS`: the number of training iterations for a model
* `PATIENCE`: the number of epochs before implementing early stopping
* `NCALLS`: the total number of hyper parameter iterations (the number of inferred samples is `NCALLS - NSTARTS`)
* `NSTARTS`: the number of randomly sampled hyper parameter iterations

If editing the static parameters, necessary to edit `EPOCHS` and `PATIENCE` in `TMVAOptimization.py` as well.

__(Important!!!)__ Need to edit the line `sys.path.insert(0, "/home/dli50/.local/lib/python2.7/site-packages")` to point to your own directory where `scikit-optimize` is stored.
* Install `scikit-optimize` using: `pip install --user scikit-optimize`
### 2.2 Run the hyper parameter optimization ###
Run the script `submit_Optimization.sh`.  This will begin the hyper parameter process that selects a hyper parameter set and then trains that architecture with the defined (reduced) input variable set.  The parameters and result (ROC integral) of each trained model are written to `TTTT_TMVA_DNN/dataset/optimization_[#]vars/optimizationLog_[date and tag].txt`.  The model with the best result (largest ROC integral) is written to `optimizationParams_[date and tag].txt`.

__Note:__ The hyper parameter optimization uses fewer number of training/testing events and fewer epochs to give preliminary results to a full training cycle.  Under the assumption that there is more than one signal sample and many background samples, the abridged dataset greatly reduces computation time.
## 3. Run a full training cycle ##
__Using the "important" variables and optimized model architecture, run a full training set to get final results.__

### 3.1 Edit `TMVAClassification_Training.py` ###
1. Referencing the optimized hyper parameter set defined in `TTTT_TMVA_DNN/dataset/weights/params_[date and tag].txt` edit the default model defined in `TMVAClassification_Training.py`.  It would also be good to check that `varsList.py` has the desired set of input variables at this time.
2. (Optional) Edit the static parameters (i.e. epochs, patience, etc.) for the full training cycle.

### 3.2 Run the final full training cycle ###
Run the final full training cycle using: `./submit_Training.sh`
* To see the final ROC integral value, type in the commandline `exit`
* The fully trained model will be stored in `TTTT_TMVA_DNN/dataset/weights/training_[#]vars/TrainedModel_PyKeras.h5`.  

Now, you should have a fully trained model (`TrainedModel_PyKeras.h5`) that can be used on any dataset with the same Step 2 inputs! 
* It would be a good idea to change the name of this model and store it somewhere safe


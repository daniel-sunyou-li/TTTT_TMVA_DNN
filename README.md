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
    pip install --user scikit-optimize
    python ./Tools/setupLPC.py

Some of the scripts have the line `os.system('bash')` which is required for setting up the environment but requires `exit` in the command line after running the script to view the outputs.
      
### Datasets ###
We are using 2017 Step 2 LJMET samples that are stored in: `/mnt/hadoop/store/group/bruxljm/FWLJMET102X_1lep2017_Oct2019_4t_03202020_step2/nominal/`
* The directory is also listed in `varsList.py` as `inputDirBRUX`

There is one signal sample: `TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root`
There are fifteen background samples.  All the sample names can be found in `varsList.py`.

### Importing Datasets to LPC ###
When running variable importance on the LPC, we need to import the signal and background samples onto both the LPC storage and the EOS storage. Run the commands:

`python ~/nobackup/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/setupLPC.py`

In case there are issues with the tar file, then make adjustments to `TTTT_TMVA_DNN` and run the commands,

    tar -zcvf CMSSW946.tgz ~/nobackup/CMSSW_9_4_6_patch1/
    xrdcp CMSSW946.tgz root://cmseos.fnal.gov//store/user/<EOS Username>

## 1. Input Variable Importance Calculation ###
__Calculate the relative importance of a Step 2 input variable in training a dense neural network classifier.  Then, the "unimportant" variables can be excluded from subsequent training to save time.__
### 1.1 (Optional) Edit `varsList.py` ###
`varsList.py` contains a python `dict` named `varList["DNN"]` containing lists of: the input variable name, expression and units.  Comment out (or uncomment) the variables being included in the variable importance calculation.
### 1.2 (Optional) Edit the network architecture ###
If you would like to change the generic unoptimized network architecture being trained, then you can edit `TMVAClassification_VariableImportance.py`.  
### 1.3.1 Run the variable importance calculation script ###
The variable importance analysis is run by the command:

    mkdir condor_log
    voms-proxy-init --valid 192:00 -voms cms
    ./submit_VariableImportance.sh LPC 100 80 

which submits Condor jobs for training the networks, each representing a different input subset to be trained.  The first argument is to specify which server the script is being run out of; the second argument specifies the number of "seeds" being generated; and the third argument specifies the correlation coefficient cut.  
* A seed is a binary string with a character length equal to the number of input variables considered.  A value of `1` indicates that the variable should be included as an input to the network and a `0` is to exclude the variable. The total number of Condor jobs relates to the number of seeds by roughly: `# Jobs ~ # Seeds + 0.5 * # Seeds * # Variables`.

The results and logs are stored in `condor_log` where the desired result is the ROC value, which is contained in the `.out` file. 

If submitting on the LPC, be sure to edit the username parameters in `varsList.py`.

### 1.3.2 Resubmit failed Condor jobs ###
To check the status of the Condor job, use the command: `condor_q`
* Using the option `-better-analyze` provides a summary of available nodes
* Using the option `-batch -run` provides a summary of all running jobs

You can identify a failed job by noting a small `.out` file size and checking the `.err` log. In the case of failed jobs, run the script:

`python resubmit_VariableImportance.sh BRUX # or LPC`

which iterates through the `.out` files identifying if the ROC value is present.  Keep running the script so long as there are failed Condor jobs. 

On the LPC, if a job uses more memory than specified in the Condor job submission file, then the scheduler will remove the job. To adjust the memory usage, edit `/LPC/VariableImportanceLPC_step1.py` and adjust the variable `request_memory`.
* Advised to ([read the description of the LPC condor cluster machines](https://uscms.org/uscms_at_work/computing/setup/batch_systems_advanced.shtml)) before adjusting parameters

### 1.4.1 Calculate the variable importance ###
After ensuring that all jobs are finished running--or finding out by the calculation script failing--run the script:

`python VariableImportance_Calculation.py 1`

which iterates through all the `.out` files determining the relative importance of the variables and storing the results in `TTTT_TMVA_DNN/dataset/VariableImportanceResults_vars[#].txt` as well as `ROC_hists_[#]vars.npy` which contains a NumPy array of the distributions which can be plotted.
* There are two options for running variable importance: the traditional variable importance (`0`) or the variable importance significance (`1`).  The traditional variable importance sums over all the values in the ROC differential distributions for a given variable and normalizes the value. The variable importance significance takes the ratio of the distributions mean to RMS.

### 1.4.2 Plot the variable importance ###
Because BRUX cannot display graphics, to visualize the variable importance, we need to move `VariableImportanceResults_vars[#].txt` to a different system.  Using a Jupyter python notebook ([Google Colab](https://colab.research.google.com/notebooks/welcome.ipynb) or [CERN SWAN](swan.cern.ch)):
1. From a local repository (or from the terminal in SWAN) use: `scp [brux_username]@brux.hep.brown.edu:/path/to/file.txt/ ./` or `scp [lpc_username]@cmslpc-sl7.fnal.gov:/path/to/file/`
* An easy way to extract the Variable Importance results is to use the following commands:
  * `scp '[lpc_username]@cmslpc-sl7.fnal.gov:/uscms_data/d3/[lpc_username]/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset/VariableImportance*' ./`
  * `scp '[lpc_username]@cmslpc-sl7.fnal.gov:/uscms_data/d3/[lpc_username]/CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/dataset/ROC*' ./`
2. Run `VariableImportance_Plot.ipynb` which should generate a bar graph of the variable importance.
* The notebook is configured to run on Google Colab and connect to Google's 'My Drive' so editing will need to be done if being run on SWAN.
    
## 2 Hyper Parameter Optimization ##
__Determine the optimal dense neural network hyper parameters for a given input using `scikit-optimize`.__
### 2.1 (Optional) Edit the hyper parameter survey space in `TMVAClassificationPyKeras_OptimizationWrapper.py` ###
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
### 2.2 Run the hyper parameter optimization ###
Run the script:

`./submit_Optimization.sh LPC 10 1`  

The first argument is the server the script is being run out of (LPC or BRUX). The second argument is for the number of ranked variables to be included in the hyper parameter optimization training (e.g. include the top 10 ranked variables). The third argument specifies how the variables should be ranked with `0` corresponding to the traditional variable importance and `1` corresponding to the variable importance significance.

This will begin the hyper parameter process that selects a hyper parameter set and then trains that architecture with the defined (reduced) input variable set.  The parameters and result (ROC integral) of each trained model are written to `TTTT_TMVA_DNN/dataset/optimize_Keras_[#]vars/optimize_log_[date and tag].txt`.  The model with the best result (largest ROC integral) is written to `params_[date and tag].txt`.  An additional text file `varsListHPO.txt` will be written specifying the sum of the variable importance metric used in ranking along with the inputs included (in order of increasing importance). 

__Note:__ The hyper parameter optimization uses fewer number of training/testing events and fewer epochs to give preliminary results to a full training cycle.  Under the assumption that there is more than one signal sample and many background samples, the abridged dataset greatly reduces computation time.
## 3. Run a full training cycle ##
__Using the "important" variables and optimized model architecture, run a full training set to get final results.__

### 3.1 Run the final full training cycle with `TMVAClassification_Training.py` ###
Run the final full training cycle using: 

`./submit_Training.sh LPC 1 ./dataset/optimize_Keras_[#]vars/`

The first argument is the server the script is being run out of (LPC or BRUX). The second argument is to specify if a static model is used (`0`) or a hyper parameter optimized model will be used (`1`). The third argument accompanies the second argument where if a hyper parameter optimized model is used, then the results directory from the hyper parameter optimization should be specified. 

After the training completes, the ROC integral value will be displayed in the commandline but also appended to `varsListHPO.txt` at the end of the file. The fully trained model will be stored in `TTTT_TMVA_DNN/dataset/weights/Keras_[#]vars/TrainedModel_PyKeras.h5`.  

Now, you should have a fully trained model (`TrainedModel_PyKeras.h5`) that can be used on any dataset with the same Step 2 inputs! 
* It would be a good idea to change the name of this model and store it somewhere safe


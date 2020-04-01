# Tools Used to Prepare the Analysis Process
Running the script `setupLPC.py` using:

    python setupLPC.py
    
should prepare the workspace by:
* Copying files from BRUX to LPC
* Splitting ntuples on LPC for independent training processes
* Copying files from LPC to EOS
* Creating all the relevant directories for holding analysis results

After running the `setupLPC.py` script, the analysis can be run by submitting `submit_VariableImportance.sh` in the home directory.  Follow instructions in the home directory README.

## Description of each script
* __`countCondorJobs.py`__: counts the number of condor jobs running and checks for failed jobs.  Also reports seed statistics.
* __`getVariables.py`__: produces a `.txt` file containing a list of branches in a ROOT tree. Edit for file names.
* __`setupLPC.py`__: setup the CMSSW workspace to run variable importance, hyper parameter optimization and model training.
* __`splitROOT.cpp`__: splits ROOT ntuples into equally defined parts.
* __`trimROOT.py`__: trims a ROOT file to have a specified number of events.

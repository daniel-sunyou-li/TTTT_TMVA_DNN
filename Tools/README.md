# Tools Used to Prepare the Analysis Process

## `setupLPC.py`

The LPC Setup script prepares the working environment on LPC (Fermilab) servers before analysis can take place.

**Before Running**

Ensure you have entered the proper working environment (necessary each time you are working within this project) by calling

- `source /cvmfs/cms.cern.ch/cmsset_default.sh` (or .csh for CShell)
- `cmsenv` 

In addition, ensure that your EOS, FNAL, and BRUX usernames are set in `varsList.py`.



**Running the Setup Script**

Run the script with default settings using `python Tools/setupLPC.py`.

In automatic/default mode, the script does the following in order:
*Each action can also be toggled independently using the listed flag.*

1. Check for a VOMS proxy using `voms-proxy-info` and initialize one if not found.
2. (*-c*) Compile the splitRoot binary from `Tools/splitRoot.cpp`.
3. (*-d*) Download the generated sample files from BRUX to LPC. You will be asked for your BRUX password.
4. (*-s*) Split the downloaded ROOT files into training, testing, and validation files.
5. (*-e*) Upload the training files to EOS.
6. (*-t*) Create a TAR file of the project code and resources and upload to EOS.

The sample set(s) to be used can also be specified by year: choose from 2017 or 2018. The default is both.

Information about the available flags and syntax can be obtained by running `python Tools/setupLPC.py -h`.

<u>Example Usage</u>
To compile the splitRoot binary, create split files for the 2017 dataset, and upload them to EOS, the syntax would be:
`python Tools/setupLPC.py -c -s -e 2017`

Note that the full script may take hours to finish running.



## Description of each script
* __`countCondorJobs.py`__: counts the number of condor jobs running and checks for failed jobs.  Also reports seed statistics.
* __`getVariables.py`__: produces a `.txt` file containing a list of branches in a ROOT tree. Edit for file names.
* __`setupLPC.py`__: setup the CMSSW workspace to run variable importance, hyper parameter optimization and model training.
* __`splitROOT.cpp`__: splits ROOT ntuples into equally defined parts.
* __`trimROOT.py`__: trims a ROOT file to have a specified number of events.

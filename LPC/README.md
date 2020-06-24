# Variable Importance on LPC Servers

This document discusses the Variable Importance scripts designed to run on LPC (Fermilab) servers. It assumes you have set up an environment as detailed in the documentation for `Tools/setupLPC.py`, and that you have a working LPC account able to submit Condor jobs.

All commands are run from the `TTTT_TMVA_DNN` folder.

### Submitting Jobs

The `submit_VariableImportance.sh` script is the starting point for submitting variable importance calculation jobs.

Run the script with default setting (in bash) using `./submit_VariableImportance.sh`.

With automatic/default arguments, the script submits 500 seeds to LPC servers using the 2017 dataset and a correlation cutoff of 80%, to be saved into an automatically named condor log folder.

*You will be asked to confirm your submission by the script.*

The optional arguments are:

- -h [host name]: the server to run the submissions on, from LPC or BRUX. Default LPC.
- -y [year]: the dataset to work with, from 2017 or 2018. Default 2017.
- -s [num. seeds]: the number of seeds to submit (not subseeds!). Default 500.
- -c [correlation cutoff]: the percentage correlation for two variables to be considered highly correlated. Default 80.
- -f [condor log path]: the folder to store the resulting Condor logfiles in. Will be created if it does not exist.
  - The default is a folder labeled by date `condor_log_[day].[Month].[year]`
- -t: toggle test mode, only one (or very few) jobs will be submitted. Default: off/not included.

<u>Example Usage</u>
To submit 100 jobs using 2018 data to LPC servers with a 90% correlation cutoff to be saved to `new_logs`, the syntax is:
`./submit_VariableImportance.sh -h LPC -y 2018 -s 1000 -c 90 -f new_logs`

Note that the submission script takes a minimum of 0.25s/job, so submitting 1000 jobs will take at least four hours.

### Checking the Progress of Jobs

To view information about the status of running or submitted jobs whose logs are stored in a given folder, the `Tools/countCondorJobs.py` script can be used.

See the documentation in the Tools README.

### Resubmitting Failed Jobs

Jobs that did not complete successfully can be automatically resubmitted using the `resubmit_VariableImportance.sh` script.

With automatic/default arguments, the script resubmits failed jobs from the `condor_log` folder to LPC servers using 2017 data.

*You will be asked to confirm resubmission by the script.*

The optional arguments are:

- -h [host name]: the server to run the submissions on, from LPC or BRUX. Default LPC.
- -y [year]: the dataset to work with, from 2017 or 2018. Default 2017.
- -f [condor log path]: the folder from which to resubmit failed jobs. Default `condor_log`.

<u>Example Usage</u>
To resubmit failed jobs from the `condor_log_15.June.2020` folder using 2018 data to LPC servers, the syntax is:
`./resubmit_VariableImportance.sh -h LPC -y 2018 -f condor_log_15.June.2020`

Like the submission script, this process takes at least 0.25s/job.


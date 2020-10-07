### TTTT Machine Learning Classification and Importance Calculation *Quick Start Guide*

Hello! This text assumes that you've just cloned the TTTT_TMVA_DNN repository to your Fermilab workspace, and that you can navigate to its "src" folder. It is intended as a walkthrough to using all of the various components of the script.

You should be able to type `ls` and see a list of the files as they appear on the GitHub.

**Step 1**: Editing the Variable List

The `varsList.py` file contains data entries that are used by the other scripts in the software suite. Some of them can be customized.

Open `varsList.py` for editing using `nano varsList.py`. Then, navigate to the `bruxUserName`, `lpcUserName`, and `eosUserName` and update them to your personal login info.

*TLDR*: `nano varsList.py` and change the usernames.



**Step 2**: Starting the Environment

The various Python scripts require the proper environment to run. This  includes entering the CMS environment, and selecting the proper ROOT  version. The `start.sh` script contains all of the necessary steps, and *must* be run before any of the Python scripts can work properly.

To start the environment, type `. start.sh` (note, the leading `.` is important! It lets the script modify the working environment). This must be done *every time* you restart the Fermilab workspace.

*TLDR*: `. start.sh` every time you log in.



**Step 3**: Running the Setup Script

The setup script takes care of the comprehensive workspace setup. It will generate and upload the necessary files for the analysis. It may take minutes or hours to run.

Run the script using `python setup/setupLPC.py`.

If you only need to run a specific part of setup, run the script with the `-h` flag (`python setup/setupLPC.py -h`) to see the relevant flags for each of the setup script steps.

*TLDR*: `python setup/setupLPC.py`



**Step 4**: Submit Jobs

To submit your first batch of jobs, you will use the `submit.py` script. The precise arguments to the script will depend on your experimental parameters.

For example, to submit 500 seeds at 80% correlation from the 2018 dataset, you would run `python submit.py -n 500 -c 80 -y 2018`.

You may want to test to make sure the submission process is working. In that case, run the previous command with `--test` appended. Only one job will be created.

The script may take minutes or hours to finish. To increase speed, change the number of processes using the `-p` flag. A value between 4 and 8 works well.

The running of the script creates a folder called `condor_log_[day].[Month].[year]`.

*TLDR*: `python submit.py -n 500 -c 80 -y 2018`.



**Step 5**: Check on Job Progress

To see how submitted jobs are doing, use the `folders.py` script. To see which folders contain logs, type `ls | grep condor_log`.

See information using `python folders.py condor_log_[day].[Month].[year]` 

*TLDR*: `python folders.py condor_log_[day].[Month].[year]` .



**Step 6**: Resubmit Failed Jobs

Sometimes, jobs will fail to complete. The submit script can automatically resubmit them. In resubmit mode, you only need to specify the dataset year as a parameter.

Run `python submit.py -r -y 2018 condor_log_[day].[Month].[year]` to resubmit failed jobs in the specified folder using 2018 data.

*TLDR*: `python submit.py -r -y 2018 condor_log_[day].[Month].[year]` .



**Step 7**: Run Calculations on Finished Folders

Once all of the jobs in a folder are finished (see Step 5), you will use the calculation script to analyze the results.

Run the script using `python calculate.py condor_log_[day].[Month].[year]`. This may take minutes, and generates a folder named `dataset_[day].[Month].[year]` with a date matching *today*, not necessarily the Condor log folder.

*TLDR*: `python calculate.py condor_log_[day].[Month].[year]`.



**Step 8**: Repeat

Generate more datasets by repeating Steps 4 through 7.



**Step 9**: Hyper-Parameter Optimization

Tune the parameters of your machine learning model using the HPO script.

Run the script using `python hyperopt.py -n 5 -y 2018 dataset_[day].[Month].[year]` to generate the best model using the 5 most important variables based on the 2018 dataset.


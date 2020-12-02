# Four Top Machine Learning Classification and Importance Calculation

### Introduction

<u>Jump to a Section</u>

- [Setup](#setup)
- [Starting the Environment](#starting-the-environment)
- [Managing Jobs](#managing-jobs)
  - [`jobtracker.py`: The Backend](#jobtrackerpy-the-backend)
  - [`folders.py`: Folder Management Utilities](#folderspy-folder-management-utilities)
  - [`submit.py`: Job Submission and Resubmission](#submitpy-job-submission-and-resubmission)
  - [`calculate.py`: Variable Importance Calculation](#calculatepy-variable-importance-calculation)
- [Condor Job Scripts](#condor-job-scripts)
- [Hyper Parameter Optimization](#hyper-parameter-optimization)

## Setup

Setup



[Return to Index](#introduction)



## Starting the Environment

The various Python scripts require the proper environment to run. This includes entering the CMS environment, and selecting the proper ROOT version. The `start.sh` script contains all of the necessary steps, and *must* be run before any of the Python scripts can work properly.

<u>To Run the Start Script</u>
From bash, enter the `src` directory and type `. start.sh`. The leading `.` allows the shell script to modify the current working environment, which is the desired effect.

The script must be run by the user. It cannot be started from within the Python script.

[Return to Index](#introduction)



## Managing Jobs

The bulk of the data generated in this project is stored in individual jobs. Each job corresponds to one instance of training a neural network, testing it, and computing a ROC-Integral value. These jobs are defined by `.job` files, which are submitted to Condor. As the network is trained, a `.out`, `.err`, and `.log` file is also generated for each job, containing its output and information about its status.

The cycle of creating, submitting, checking the status of, and gathering results from jobs is handled by different Python scripts within the software package.

[Return to Index](#introduction)



### `jobtracker.py`: The Backend

To simplify job management, the software package is built around `jobtracker.py`, a job management library. It tracks the status of jobs and provides convenient information about them.

*Note*: In order for spec files to be read properly, <u>never</u> import the library using `from jobtracker import *`. You <u>must</u> import the library using a module name, such as `import jobtracker as jt`. Otherwise you will encounter errors when loading spec files.

`LOG = True`: Turns on output from the library. Set at the module level.



```python
class Job(folder: str, name: str, seed: Seed, subseed: None or Seed)
```

The `Job` object represents a single Condor job stored within a given folder.
An instance has the following method:

- `check_finished()`
  Reads the `.out` file of the job if it exists, and updates its `finished` and `roc_integral` properties accordingly.

An instance has the following properties:

- `folder`
  The full path to the folder in which the job is stored, or `None` if the job is stored in a compacted state.
- `name`
  The name of the job, corresponding to filenames. <u>Example</u>: `Keras_76vars_Seed_<#>_Subseed_<#>`.
- `path`
  The full filepath of the `.job` file, or `None` if the job is stored in a compacted state.
- `seed`
  A `Seed` object corresponding to the job's seed.
- `subseed`
  A `Seed` object corresponding to the job's subseed, or `None` if the job does not have a subseed.
- `finished`
  `True` if the job has finished processing, whether a result was achieved or not. `False` otherwise. Updated by the `check_finished` method.
- `roc_integral`
  Stores the value of the ROC-Integral computed by the job, or `-1` if the value has not been computed yet. Updated by the `check_finished` method.
- `has_result`
  `True` if the job has finished and obtained a ROC-Integral value, `False` otherwise.
- `has_outfile`
  `True` if the job has an `.out` file in the job folder, or if the job is in a compacted folder.



```python
class JobFolder(path: str)
```

The `JobFolder` object encapsulates a folder where job files are stored and its related **spec file**. See the section on spec files for more details.

An instance has the following properties:

- `path`
  The full path to the folder containing jobs, or to the spec file if the folder is compacted.
- `jobs`
  A list of `Job` objects in the folder, or `None` if the folder has not been initialized.
- `compacted`
  `True` if the folder has been compacted using the `compact_folder` method, `False` otherwise.
- `seed_jobs`
  A list of `Job` objects which have no subseed.
- `variables`
  A list of variable names. A variable name will appear if it is used in at least one `Job` in the folder.
- `result_jobs`
  A list of `Job` objects which have finished, obtaining a ROC-Integral value.
- `unstarted_jobs`
  A list of `Job` objects which have not started yet, and therefore do not have a `.out` file.

An instance has the following methods:

- `check(subset: list)`
  Calls the `check_finished` method of each `Job` object in the `subset`, or on all jobs in the folder if no subset is specified.
- `get_variable_counts()`
  Returns a dictionary whose keys are the union of all the variables used across all jobs in the folder, and whose values are the number of times the given variable is included in a job which has no `subseed`. 
- `get_resubmit_list()`
  Returns a list of `Job` objects which have finished without computing a ROC-Integral value, and thus need to be resubmitted to Condor.
- `variable_jobs(var: str)`
  Returns a list of `Job` objects whose `seed` contains the given variable name `var`. Note that the variable does not have to be included, just contained.
- `subseed_jobs(seed: Seed)`
  Returns a list of `Job` objects whose `seed` properties match the given seed value and have a `subseed` value not equal to `None`.
- `get_stats()`
  Returns a dictionary with information about the folder and job progress. The dictionary contains the following entries:
  - `jobs`: The number of jobs in the folder. Equivalent to `len(job_folder)`.
  - `finished_jobs`: The number of jobs that have finished (regardless of success). Equivalent to `len(job_folder.result_jobs)`.
  - `failed_jobs`: The number of jobs that finished without computing a ROC-Integral value. Equivalent to `len(job_folder.get_resubmit_list())`.
  - `unstarted_jobs`: The number of jobs which do not have a `.out` file. Equivalent to `len(job_folder.unstarted_jobs)`.
  - `seeds`: The number of seeds in the folder. Equivalent to `len(job_folder.seed_jobs)`.
  - `variable_counts`: Equivalent to `job_folder.get_variable_counts()`.
- `import_folder(variables: list)`
  Scans the folder on the disk, reading information from the `.job` files and creating `Job` objects to store in a spec file. The variable list is necessary to interpret the seed and subseed values in the file names. After the jobs have been created, their status is checked and the spec file is saved.
  *Note*: This may take several minutes depending on how many job files are in the folder.
- `compact_folder( [ dest: str = "default" ] )`
  Deletes the folder and contained `.job` files, leaving only a spec file named identically to the folder, or at path `dest` if the default value is overridden. The compaction process can only take place if all jobs in the folder have finished. The process is irreversible.

The class has the following static method:

- `JobFolder.create( [ name: str = "default" ] )`
  Creates a new `JobFolder` object corresponding to a blank folder. The folder will be named `condor_log_[day].[Month].[year]` and placed in the working directory if the default name is used. The `JobFolder` object is returned.



```python
class Seed(variables: list)
```

The `Seed` class corresponds to a binary seed which indicates which variables are tested in each job.

An instance has the following properties:

- `variables`
  The list of variable names, in order, that are used in generating this seed.
- `states`
  A dictionary where the keys are variable names, and the values are `True` if the given variable is included in the seed (corresponding to a `1` in the binary string), or `False` otherwise (`0`).
- `binary`
  A binary string representation of the seed. The leftmost character corresponds to the first variable in the list.

An instance has the following methods:

- `include(var)`
  If the variable `var` is used in this seed, set its entry in `states` to `True`.
- `exclude(var)`
  If the variable `var` is used in this seed, set its entry in `states` to `False`.
- `includes(var)`
  Returns `True` if the variable `var` is used in the seed and its entry in `states` is `True`.
- `save_to(path)`
  Pickle the Seed and save it to the specified path.

The class has the following static methods:

- `Seed.from_binary(bitstring: str, variables: list)`
  Creates a new `Seed` object from a list of variables and a binary string. The characters in the string are read left to right, with the leftmost character corresponding to the first variable in the list. The `Seed` object is returned.
- `Seed.random(variables)`
  Creates a new `Seed` object with random variable inclusion given a list of variables. The `Seed` object is returned.
- `Seed.load_from(path)`
  Loads a pickled Seed object from the specified path and returns it.

[Return to Index](#introduction)



### `folders.py`: Folder Management Utilities

The `folders.py` script is used to access the functionality of the backend from the command line. It allows the user to import, compact, and view data about folders.

The script accepts the following command-line arguments:

- `-v` (optional): Toggle verbose mode, showing output from backend library.
- `-c` (optional): Operate in *compact* mode (see below).
- `-i varlist`  (optional): Operate in *import* mode (see below).
  - `varlist` can either be `all` to use the default list of 76 variables, or a path to a file which contains a sorted list of variable names, one per line.
- A list of Condor log folders (optional). Defaults to scanning the working directory for all folders matching `condor_log*`.

Based on the command line flags, the script behaves differently.

<u>*Import* Mode:</u> Run with `-i varlist` option.

The script will call the `import_folder` method on each of the folders specified, using the given variable list. This generates a spec file within the folder (see the section on spec files, as well as the documentation for `JobFolder` for more details). If the spec file already exists, a prompt to overwrite appears. See also: documentation for `import_folder` in `JobFolder`.

Example Usage:
To import the folders `condor_log_17.June.2020` and `condor_log_new` using the variable list stored in `15vars.txt`, the syntax would be: `python folders.py -i 15vars.txt condor_log_17.June.2020 condor_log_new`.

<u>*Compact* Mode:</u> Run with the `-c` flag.

The script will call the `compact_folder` method on each of the folders specified. This removes the condor log files and keeps only the spec files. A warning will appear for folders that could not be compacted. See also: documentation for `compact_folder` in `JobFolder`.

Example Usage:
To compact the folder `condor_log_23.June.2020`, the syntax would be: `python folders.py -c condor_log_23.June.2020`.
After running this command, the working directory would contain the spec file `condor_log_23.June.2020.jtd` and the folder will be deleted.

<u>*Information* Mode:</u> Run **without** `-c` or `-i` options.

The script will display information about the status of jobs within each of the folders specified. The folders must have a spec file, and a warning will appear if one does not exist. The generated information is based on calling `get_stats` on each of the folders. See also: documentation for `get_stats` in `JobFolder`.

If the script is called with the `-v` flag, then for each folder, the number of times each variable is used in a seed as well as the name of each failed job will be displayed.

In all cases, the number and percent of finished, failed, and unstarted jobs will be printed, as well as the number of submitted seeds.

Example Usage:
To display verbose information about the folders `condor_log_23.June.2020` and `condor_log_17.June.2020` the syntax would be: `python folders.py -v condor_log_23.June.2020 condor_log_17.June.2020`

[Return to Index](#introduction)



### `submit.py`: Job Submission and Resubmission

The `submit.py` script is used to create new Condor jobs for the variable importance calculation, and also to resubmit jobs which failed to compute a ROC-Integral value.

The script accepts the following command-line arguments:

- `-v` (optional): Toggle verbose mode, showing output from backend library.
- `-r` (optional): Run in *resubmit* mode (as opposed to submit mode - see details below).
- `--include-unstarted` (optional): Include unstarted jobs when compiling list of jobs to resubmit.
- `-p num_processes` (optional): Specify how many processes should be used to submit jobs in parallel. Default 2.
- `-n num_seeds` (optional): How many seeds to submit. Only meaningful in *submit* mode. Default 500.
- `--test` (optional): Submit *only one* job to Condor. Useful for testing whether the submission system is working. Only in *submit* mode.
- `-c correlation_percent` (optional): The percentage correlation between two variables necessary for them to count as highly correlated. Default 80.
- `-l varlist` (optional):  The variables to use when submitting jobs. Only meaningful in *submit* mode.
  - `varlist` can either be `all` to use the default list of 76 variables, or a path to a file which contains a sorted list of variable names, one per line.
- `-y year`: The dataset to use when training. Specify `2017` or `2018`.
- A list of Condor log folders (optional). Defaults to scanning the working directory for all folders matching `condor_log*` in *resubmit* mode, or submitting to a new folder named `condor_log_[day].[Month].[year]` in *submit* mode.

<u>*Resubmit* Mode</u>: Run with the `-r` flag.

In resubmit mode, the script scans the specified folders for jobs which failed to compute a ROC-Integral value, as well as jobs which have not yet been started. These jobs can be listed by running `python folders.py -v [folders...]`, which displays the names of failed jobs as well as the total number. Once resubmitted, the new output from the jobs will be stored in their existing folder.

To resubmit *unstarted* jobs as, use the `--ignore-unstarted` flag.

Example Usage:
To resubmit failed jobs in the `condor_log_17.Jun.2020` folder using 2017 data and a correlation percentage of 70, the syntax is: `python submit.py -r -y 2017 -c 70 condor_log_17.Jun.2020`.

<u>*Submit* Mode</u>: Run **without** the `-r` flag.

In submit mode, the script generates new seeds and subseeds to create jobs. By default, these are stored in a folder named `condor_log_[day].[Month].[year]`, though this can be changed by specifying an existing or alternative path to be created.

Example Usage:
To submit 50 seeds of new jobs using the variable list `15vars.txt`, to be placed in a new folder, using 2017 data and a correlation percentage of 80, to be submitted using 4 parallel processes, the syntax is: `python submit.py -y 2017 -l 15vars.txt -n 50`.

<u>Multiprocessing Capable</u>

In both modes, the script uses parallel processes to submit jobs. The number of processes can be specified using the `-p` option. By default, two processes are used. Increasing the number of processes can cause some submissions to fail (with four processes, the observed rate of failure is around 0.7%). The failed submissions are tracked, and a prompt will appear to retry submission after all other jobs have been submitted.

[Return to Index](#introduction)



### `calculate.py`: Variable Importance Calculation

The `calculate.py` script takes the results from one or several job folders and produces variable importance calculations for each of the variables used. Only successfully finished jobs can be used in the calculation, so it may be useful to check their status using `folders.py` before running this script.

The script accepts the following command-line arguments:

- `-v` (optional): Toggle verbose mode, showing output from backend library.
- `-f output_folder` (optional): Specify where the generated calculations will be stored. When not supplied, the default is a folder named `dataset_[day].[Month].[year]`.
- `-o sort_order` (optional): Specify how the resulting data per variable should be sorted, in descending order. Valid choices are:
  - `importance` (default): Sort by the "Importance" column.
  - `freq`: Sort by the "Freq." (frequency) column.
  - `sum`: Sort by the "Sum" column.
  - `mean`: Sort by the "Mean" column.
  - `rms`: Sort by the "RMS" column.
- `--sort-increasing` (optional): Sort in increasing order of specified value. This is the intuitive choice for "rms".
- A list of Condor log folders (optional). Defaults to scanning the working directory for all folders matching `condor_log*`.

<u>Files Produced</u>

The script produces three files within the specified dataset folder (see `-f` command line option).

- The `VariableImportanceResults_[#]vars.txt` file (where `[#]` is the total number of variables used in the calculation). This contains the following information:
  - The weight string.
  - The cut string.
  - The paths to the folders (or .jtd files) used in the calculation.
  - The number of variables used in the calculation.
  - The date the file was produced.
  - The normalization value.
  - For each variable, in the specified sort order (see `-o` command line option), each of the statistics listed in the statistics section.
- The `ROC_hists_[#]vars` file (where `[#]` is the total number of variables used in the calculation), which is used to create plots.
- The `VariableImportanceOrder_[#]vars.txt` file (where `[#]` is the total number of variables used in the calculation). This contains just the variable names in the specified sort order (see `-o` command line option), with one variable name per line.

<u>Example Usage</u>

To calculate variable importance from the folders `condor_log_17.Jun.2020` and `condor_log_20.Jun.2020`, with results sorted by the number of times each variable is tested, and output the data to the folder `dataset_freq`, the syntax would be:
`python calculate.py -f dataset_freq -o freq condor_log_17.Jun.2020 condor_log_20.Jun.2020`.

<u>The Calculation Process and Statistics</u>

The importance of each variable is calculated by first finding the differences between the ROC-Integral values for each variable seed and subseed. The script does this in three steps.

1. All the input folders are scanned and seed jobs (jobs which have no `subseed` value) are identified. The ROC-Integral value for each seed job is recorded, and for each variable which is included in the seed job (see the `Seed` documentation), the frequency of that variable is increased by one.
2. For each of the seed jobs found in step 1, the list of subseed jobs for that seed is found (see the documentation for `subseed_jobs` in `JobFolder`). For each variable in the subseed, if it is **not** included in the subseed but *is* included in the seed, the difference in ROC-Integral values between the seed and subseed is recorded in an list corresponding to that variable.
3. For each variable name and corresponding list of ROC-Integral differences generated in step 2, the statistics outlined in the next section are computed.

The variable importance results file stores the following calculated statistics for each variable:

- *Frequency*: How often the variable is included in a seed job.
- *Sum*: The sum of all the ROC-integral differences corresponding to the variable.
- *Mean*: The mean of all the ROC-integral differences corresponding to the variable.
- *RMS*: The standard deviation of all the ROC-integral differences corresponding to the variable.
- *Importance*: Given as *Mean* / *RMS*.

[Return to Index](#introduction)



## Condor Job Scripts

The user does not interact directly with the scripts that run on the Condor nodes. Instead, they are launched indirectly by `submit.py`, and their output is monitored by the job tracker library.

`remote.sh` is the target Condor executable. It retrieves the TTTT source code from the `CMSSW946.tgz` file, sets up the working environment, and retrieves the relevant dataset samples. Then, it launches the `remote.py` script.

`remote.py` performs the neural network training corresponding to one job. It is passed the dataset year and a base-64 encoded string of variable names by `remote.sh`. These are the variables included in the seed this job corresponds to. The neural network is then trained using these variables, and the resulting ROC-Integral value is printed to the output.

[Return to Index](#introduction)



## Hyper Parameter Optimization

Hyper Parameter Optimization is used to find the best configuration for a neural network to classify TTTT events. This process builds on the results of the variable importance rankings produced by the `calculate.py` script.

The optimization process is handled by the `hyperopt.py` script.

The script accepts the following command-line arguments:

- `-o sort_order` (optional): Specify how the variables read in from the dataset's result file should be sorted, in descending order. Valid choices are:
  - `importance` (default): Sort by the "Importance" column.
  - `freq`: Sort by the "Freq." (frequency) column.
  - `sum`: Sort by the "Sum" column.
  - `mean`: Sort by the "Mean" column.
  - `rms`: Sort by the "RMS" column.
  - A valid path, to a text file with one variable name per line. This will be treated as the sorted variable list.
- `--sort-increasing` (optional): Sort in increasing order of specified value. This is the intuitive choice for "rms".
- `-n num_vars` (optional): Specify how many of the variables, in sorted order, to use in training the neural network. Defaults to all the variables loaded.
- `-y year`: The dataset to use when training. Specify `2017` or `2018`.
- `-p parameters` (optional): Specify a path to a JSON file to use to update the static parameters and hyper parameter space used when training. See the *parameters* section for more.
- The dataset folder to use the variable importance data from and to store results in.

<u>Example Usage</u>

To perform the optimization using the variable data in the `dataset_14.Jul.2020` folder, signal and background data from the 2017 dataset, using the first 5 variables from the `custom_sort_order.txt` file, the syntax would be: `python hyperopt.py -o custom_sort_order.txt -n 5 -y 2017 dataset_14.Jul.2020`

<u>Outputs</u>

The `hyperopt.py` file produces several different files as output within the dataset folder (specified as a command-line argument).

- `dummy_opt_model.h5`: Used by TMVA during the training process. Can be safely deleted once the script finishes. File name is changeable as a parameter.
- `optimize_log_[day].[Month].[year]_[hour].txt`: A log file displaying the results of each training iteration. File name is changeable as a parameter.
- `parameters_[day].[Month].[year]_[hour].json`: A JSON file containing the parameters used in the training. See the *parameters* section and the `-p` command line option.
- `optimized_parameters_[day].[Month].[year]_[hour].txt`: A human-readable text file containing the results of the hyper parameter optimization.
- `optimized_parameters_[day].[Month].[year]_[hour].json`: A JSON file containing the results of the hyper parameter optimization.

<u>Training Parameters</u>

The parameters used for the training of the neural network are specified in `PARAMETERS` dictionary object within the script. They can be modified using a JSON file by specifying the `-p` command-line argument. The parameters used in each run of the optimization process are stored in a JSON file within the dataset.

The default parameters are:

- `static`: `["static", "epochs", "patience", "model_name", "tag", "log_file", "n_calls", "n_starts"]`. These parameters will not be included in the hyper parameter optimization process. They are statically defined by the user.
- `epochs`: `15`. The maximum number of training epochs to use in each stage of the optimization process.
- `patience`: `5`. How many epochs to wait before prematurely canceling training.
- `model_name`: `dummy_opt_model.h5` in the dataset folder. The temporary file used by TMVA during training.
- `tag`: `[day].[Month].[year]_[hour]`. Used to identify the files generated by the optimization process.
- `log_file`: `optimize_log_[day].[Month].[year]_[hour].txt` in the dataset folder. The path to the log file generated.
- `n_calls`: `50`. The number of times to run the training process when performing the optimization.
- `n_starts`: `30`. The number of random seed points to use in the optimization.
- `hidden_layers`: `[1, 3]`. (HP) The range for the number of hidden layers to include in the neural network.
- `initial_nodes`: `[num_vars, 10 * num_vars]`. (HP) The number of nodes to start with in the network, where `num_vars` is the specified by the `-n` command line argument (or equivalent use of `all` or a file containing sorted variables).
- `node_pattern`: `["static", "dynamic"]`. (HP) The type of node pattern to use when building the network.
- `batch_power`: `[8, 11]`. (HP) The batch size is determined as `2^batch_power`.
- `learning_rate`: `[1.0 * 10^-5, 1.0*10^-2]`. (HP) The rate at which the network is trained.
- `regulator`: `["none", "dropout", "normalization", "both"]`. (HP) The regulator to use for the nodes.
- `activation_function`: `["relu", "softplus", "elu"]`. (HP) The activation function to use for the nodes.

<u>The Optimization Metric</u>

When performing the optimization, the ideal trained neural network has a high ROC-Integral value. Because a minimizing search function (`gp_minimize`) is used, this means that the minimum of `1 - ROC` is equivalent to maximizing `ROC`.

To tune sensitivity, a different optimization metric can be used to map values of `1 - ROC` to more general "performance". The current metric is `log(1 - ROC)`.

[Return to Index](#introduction)

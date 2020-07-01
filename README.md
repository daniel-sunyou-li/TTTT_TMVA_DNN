# Four Top Machine Learning Classification and Importance Calculation

Introduction

## Setup

Setup

## Managing Jobs

The bulk of the data generated in this project is stored in individual jobs. Each job corresponds to one instance of training a neural network, testing it, and computing a ROC-Integral value. These jobs are defined by `.job` files, which are submitted to Condor. As the network is trained, a `.out`, `.err`, and `.log` file is also generated for each job, containing its output and information about its status.

The cycle of creating, submitting, checking the status of, and gathering results from jobs is handled by different Python scripts within the software package.

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

The class has the following static methods:

- `Seed.from_binary(bitstring: str, variables: list)`
  Creates a new `Seed` object from a list of variables and a binary string. The characters in the string are read left to right, with the leftmost character corresponding to the first variable in the list. The `Seed` object is returned.
- `Seed.random(variables)`
  Creates a new `Seed` object with random variable inclusion given a list of variables. The `Seed` object is returned.



### `folders.py`: Folder Management Utilities

The `folders.py` script is used to access the functionality of the backend from the command line. It allows the user to import, compact, and view data about folders.

The script accepts the following command-line arguments:

- 
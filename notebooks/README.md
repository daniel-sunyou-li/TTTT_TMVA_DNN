# Python notebooks for visualizing the four top analysis
These notebooks were designed to be run on swan.cern.ch[swan.cern.ch], but other jupyter notebook services should work as well. 
The order in which the notebooks are expected to be use are as follows:
### 1. `visualize_data.ipynb`
This notebook reads in the signal and background `.root` files and visualizes the variable distributions after applying cuts and weights. The intended use is to compare the same physics processes from different production years (i.e. 2017 versus 2018) and run a statistical analysis (Kolmogorov-Smirnov)[https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test] to determine if the distributions are similarly sampled.  The KS statistic is reported as _D_, as well as the corresponding _p_-value being reported. The correlation matrix for the variables is also visualized and the "high-correlation" framework is demonstrated, showing the construction of "highly-correlated groups" which are used within the seed generation framework. The notebook also allows for a subset of the correlation matrix to be visualized for further investigation.

### 2. `visualize_variable_importance.ipynb`
This notebook reads in the resulting variable importance calculation `.txt` and `.npy` files after running `calculate.py`. The `.txt` file is used to plot the ranking of the variables and the `.npy` file is used to look at individual AUC differential distributions (per variable).  It is recommended to `scp` the `dataset` containing all results so that all differnet analysis runs can be organized efficiently. The notebook selects a `dataset` containing the `.txt` and `.npy` files and searches for the corresponding files. The `dataset` name should follow the convention of `dataset_<# jets>j_<#### year>_<# correlation>cc` for the plotting to have the correct naming convention.  

The important feature to note from the results of the `calculate.py` script is the number of variables that have a positive, non-zero mean of significance.  This should be the default value used in running the hyper parameter optimization step.

### 3. `visualize_final_training.ipynb`
This notebook reads in the final optimized `.h5` model from `final.py` and applies the model to the full dataset to produce the discriminator distributions for the signal and background samples as well as plotting the ROC curve results from the _k_-fold cross validation step.

### 4. `visualize_metrics.ipynb`
This notebook is for an optional study of the importance metrics. The datapoints considered are the combined importance metrics and the corresponding DNN AUC scores obtained from hyper parameter optimization of various subsets of ranked variables. The goal of this notebook is to determine the optimal importance metric for predicting DNN performance.

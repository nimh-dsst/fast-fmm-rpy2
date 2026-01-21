# Patch Notes

## Motivation

The fastFMM R package has API changes to the fui function that necessitates changes to the fast-fmm-rpy2 wrapper. The new fastFMM version is forked at [this repo](https://github.com/awqx/fastFMM). Gabe Loewinger and aL Xin requested we update the Python fast-fmm-rpy2 wrapper.

## fastFMM R API changes

For the purposes of the Python fast-fmm-rpy2 package, only the changes to the fui function in the `fui.R` module necessitate changes. Below the relevant changes to the fastFMM package are discussed.

## fastFMM R Package Changes

### fui.R

#### Major Changes

- Addition of concurrent parameter
- Addition of override_zero_var parameter
- Addition of unsmooth parameter
- Addition of a `lick` dataset

#### Minor Changes

- num_boots parameter renamed to n_boots parameter
- subj_ID parameter renamed to subj_id parameter
- num_cores parameter renamed to n_cores parameter. Default value change from 1 to NULL.
- REs parameter renamed to randeffs

## fast-fmm-rpy2 Package Changes

The main changes to the rpy2 code is to fully integrate the new parameters for the R version of fui and testing of the new functionality.

### fmm_run.py

- All parameters in R version of fui are now available in the rpy2 version of fui
- Functions to detect version of fastFMM R package

### plot_fui.py

- Updated variable names to be compatible with new rpy2 and/or the new fastFMM code. The`betahat.var` is now imported by rpy2 as `betahat_var`.

## fast-fmm-rpy2 Notebook

The vignette for the new R version of fastFMM has been converted to a Jupyter notebook at `notebooks/fastFMM_concurrent.ipynb`.

## fast-fmm-rpy2 testing

All tests were updated to be compatable with the new dev version of fastFMM.

TODO: Make tests out of code in the `notebooks/fastFMM_concurrent.ipynb` notebook.

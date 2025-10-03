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

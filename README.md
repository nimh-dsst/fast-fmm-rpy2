# fast-fmm-rpy2
Python wrapper for the R fastFMM package

[![PyPI - Version](https://img.shields.io/pypi/v/fast-fmm-rpy2)](https://pypi.org/project/fast-fmm-rpy2)
[![DOI](https://zenodo.org/badge/952179029.svg)](https://zenodo.org/badge/latestdoi/952179029)
[![GitHub License](https://img.shields.io/github/license/nimh-dsst/fast-fmm-rpy2)](LICENSE)
[![Tests](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/test.yaml/badge.svg)](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/test.yaml)
<!-- [![Code Style](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/lint.yaml/badge.svg)](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/lint.yaml) -->

## About
The Python package `fast-fmm-rpy2` is a wrapper of the `fastFMM` R Package. It provides functions required to reproduce the analyses from the manuscript: "A Statistical Framework for Analysis of Trial-Level Temporal Dynamics in Fiber Photometry Experiments".

## Dependencies
This package requires other software to be installed. The following must already be installed
1. The R Project for Statistical Computing (R)
2. `fastFMM` R Package

#### 1. Install R
- See official R [documentation](http://r-project.org/) and Photometry FLMM [tutorial](https://github.com/gloewing/photometry_FLMM/blob/main/Tutorials/Python%20rpy2%20installation/R%20and%20rpy2%20installation%20guide.ipynb) for more information on installing R and system requirements for your system.
#### 2. Install `fastFMM` R Package
Download the $\texttt{R}$ Package `fastFMM` by running the following command within $\texttt{R}$ or $\texttt{RStudio}$:

```{R}
install.packages("fastFMM", dependencies = TRUE)
```
For more information see the `fastFMM` R package [repo](https://github.com/gloewing/fastFMM).

## Install
Assuming all the prerequisites in [Dependencies](Dependencies) are installed, `fast-fmm-rpy2` can be installed using `pip`.

```bash
pip install fast-fmm-rpy2
```
<!-- This package has many depdencies, installation on older systems may be slow. -->

As the name implis `fast-fmm-rpy2` uses Python package `rpy2` to wrap the R package. Refer to `rpy2` [documentation](https://rpy2.github.io/doc/v3.0.x/html/overview.html#installation) for troubleshooting or any [issues loading shared C libraries](https://github.com/rpy2/rpy2?tab=readme-ov-file#issues-loading-shared-c-libraries).

## API

```python
# fast_fmm_rpy2/fmm_run.py
def fui(
    csv_filepath: Path | None,
    formula: str,
    parallel: bool = True,
    import_rules=local_rules,
    r_var_name: str | None = "py_dat",
)
```

```python
# fast_fmm_rpy2/ingest.py
def read_csv_for_r(
    csv_filepath: Path, r_var_name: str = "py_dat"
) -> pd.DataFrame

def pass_pandas_to_r(df: pd.DataFrame, r_var_name: str = "py_dat") -> None

def read_csv_in_pandas_pass_to_r(
    csv_filepath: Path, r_var_name: str = "py_dat"
) -> pd.DataFrame
```

```python
# fast_fmm_rpy2/plot_fui
def plot_fui(
    fuiobj,
    num_row=None,
    xlab="Functional Domain",
    title_names=None,
    ylim=None,
    align_x=None,
    x_rescale=1,
    y_val_lim=1.1,
    y_scal_orig=0.05,
    return_data=False,
)
```

## Usage and tutorials
See [photometry_FLMM](https://github.com/gloewing/photometry_FLMM) for tutorials on using `fast-fmm-rpy2` to create Functional Mixed Models for Fiber Photometry.
<!-- to analyze XYZ data and reproduce the code and figures from the manuscript: "A Statistical Framework for Analysis of Trial-Level Temporal Dynamics in Fiber Photometry Experiments". -->

## License
This software is developed under a CC0 1.0 Universal license. See the [License](LICENSE) file for more details.

## Referencing
If you use this package please reference the following papers, as well as our [most recent Zenodo release](https://zenodo.org/badge/latestdoi/952179029):
- Cui et al. (2022) [Implementation of the fast univariate inference approach](https://doi.org/10.1080/10618600.2021.1950006)
- Loewinger et al. (2024) [A statistical framework for analysis of trial-level temporal dynamics in fiber photometry experiments.](https://doi.org/10.7554/eLife.95802)

## Contribute
<!-- 1. Have or install a recent version of uv (version >= ?)
2. Fork the repo
3. Setup a virtual environment (however you prefer)
4. Run `uv sync --extra dev`
5. Add your changes (adding/updating tests is always nice too)
6. Commit your changes + push to your fork
7. Open a PR -->

### Bump version
The versioning of this package is managed by `bump-my-version`. Bumping the version using `bump-my-version` will update the project version in the `pyproject.toml`, create a commit and create a tag.

To bump the version
1. Have or install a recent version of uv
2. Setup virtual environment and install dependencies
	```bash
	uv sync --extra dev
	```
3. Bump version
	```bash
	uv run bump-my-version bump <major|minor|patch>
	```

#### Helpful commands

Show the possible versions resulting from the bump subcommand.
```bash
uv run bump-my-version show
```

Test the bump command, don't write any files, just pretend.
```bash
uv run bump-my-version bump <major|minor|patch> --verbose --dry-run
```

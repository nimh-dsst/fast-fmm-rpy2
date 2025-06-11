# fast-fmm-rpy2
Python wrapper for the R fastFMM package

[![PyPI - Version](https://img.shields.io/pypi/v/fast-fmm-rpy2)](https://pypi.org/project/fast-fmm-rpy2)
[![DOI](https://zenodo.org/badge/952179029.svg)](https://zenodo.org/badge/latestdoi/952179029)
[![GitHub License](https://img.shields.io/github/license/nimh-dsst/fast-fmm-rpy2)](LICENSE)
[![Tests](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/test.yaml/badge.svg)](https://github.com/nimh-dsst/fast-fmm-rpy2/actions/workflows/test.yaml)

## About
The Python package `fast-fmm-rpy2` is a wrapper of the `fastFMM` R Package. It provides the functions required to reproduce the analyses from the manuscript: [A Statistical Framework for Analysis of Trial-Level Temporal Dynamics in Fiber Photometry Experiments](https://doi.org/10.7554/eLife.95802).

## Dependencies
This package has other software dependencies. The following must already be installed:
1. The R Project for Statistical Computing (R)
2. `fastFMM` R Package

#### 1. Install R
- See the official R [documentation](http://r-project.org/) and Photometry FLMM [tutorial](https://github.com/gloewing/photometry_FLMM/blob/main/Tutorials/Python%20rpy2%20installation/R%20and%20rpy2%20installation%20guide.ipynb) for more information on installing R and system requirements for your system.
> [!WARNING]
> Depending on your system and local environment you may encounter a compatibility issue between the latest version of R (4.5.0) and the latest version of `rpy2` (version 3.5.17) on Ubuntu. See [rpy2 issue](https://github.com/rpy2/rpy2/issues/1164) for more info. The issue has been fixed on the master branch of rpy2 but has not shipped with a published release yet.

#### 2. Install fastFMM R Package
Download the $\texttt{R}$ Package `fastFMM` by running the following command within $\texttt{R}$ or $\texttt{RStudio}$:

```{R}
install.packages("fastFMM", dependencies = TRUE)
```
For more information see the `fastFMM` R package [repo](https://github.com/gloewing/fastFMM).

## Install
Assuming all the prerequisites in [Dependencies](#dependencies) are installed, `fast-fmm-rpy2` can be installed using `pip`.

```bash
pip install fast-fmm-rpy2
```

As the name implies `fast-fmm-rpy2` uses the Python package `rpy2` to wrap the R package. Refer to `rpy2` [documentation](https://rpy2.github.io/doc/v3.0.x/html/overview.html#installation) for troubleshooting or any [issues loading shared C libraries](https://github.com/rpy2/rpy2?tab=readme-ov-file#issues-loading-shared-c-libraries).

## API

```python
# fast_fmm_rpy2/fmm_run.py
def fui(
    csv_filepath: Path | None,
    formula: str,
    parallel: bool = True,
    import_rules=local_rules,
    r_var_name: str | None = "py_dat",
):
    """
    Run the fastFMM model using the specified formula and data.

    Parameters
    ----------
    csv_filepath : Path or None
        The file path to the CSV file containing the data.
        If None, `r_var_name` must be provided.
    formula : str
        The formula to be used in the fastFMM model.
    parallel : bool, optional
        Whether to run the model in parallel. Default is True.
    import_rules : object, optional
        The import rules to be used for the local converter.
        Default is `local_rules`.
    r_var_name : str or None, optional
        The R variable name to be used for the data. If `csv_filepath` is None,
        this must be provided. Default is "py_dat".

    Returns
    -------
    mod : object
        The fitted fastFMM model.

    Raises
    ------
    AssertionError
        If `csv_filepath` is None and `r_var_name` is not provided.
    ValueError
        If `csv_filepath` is not None and `r_var_name` is not provided.
    """
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
):
    """
    Plot fixed effects from a functional univariate inference object.

    Parameters:
    -----------
    fuiobj : dict
        A dictionary containing the following keys:
        - betaHat: numpy array of shape (num_vars, num_points) containing
            coefficient estimates
        - betaHat_var: numpy array of shape (num_points, num_points, num_vars)
            containing variance estimates (optional)
        - argvals: numpy array of domain points
        - qn: numpy array of quantiles for joint confidence bands
            (if variance is included)
    num_row : int, optional
        Number of rows for subplot grid
    xlab : str, optional
        Label for x-axis
    title_names : list of str, optional
        Names for each coefficient plot
    ylim : tuple, optional
        Y-axis limits (min, max)
    align_x : float, optional
        Point to align x-axis to (useful for time domain)
    x_rescale : float, optional
        Scale factor for x-axis
    y_val_lim : float, optional
        Factor to extend y-axis limits
    y_scal_orig : float, optional
        Factor to adjust bottom y-axis limit
    return_data : bool, optional
        Whether to return the plotting data

    Returns:
    --------
    matplotlib.figure.Figure or tuple
        If return_data=False, returns the figure
        If return_data=True, returns (figure, list of dataframes)
    """
```

## Usage and tutorials
See [photometry_FLMM](https://github.com/gloewing/photometry_FLMM) for tutorials on using `fast-fmm-rpy2` to create Functional Mixed Models for Fiber Photometry.

### Floating point differences
The Python rpy2 implementation of fastFMM uses pandas to read in CSV files. The string of numbers in the CSV file is converted to floating point numbers using the 'roundtrip' converter, see `read_csv` [docs](https://pandas.pydata.org/docs/dev/reference/api/pandas.read_csv.html). On different systems this converter may have subtle differences with the `read.csv` function in R. See the Python [docs](https://docs.python.org/3/tutorial/floatingpoint.html) and R [docs](https://cran.r-project.org/doc/FAQ/R-FAQ.html#Why-doesn_0027t-R-think-these-numbers-are-equal_003f) for more information on the issues and limitations with floating point numbers. There are many resources outlining these issues, for example the edited reprint of David Goldberg's paper [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) or [The Anatomy of a Floating Point Number](https://www.johndcook.com/blog/2009/04/06/anatomy-of-a-floating-point-number/). Due to numerical precision limitations, arrays in R and Python are tested for near equality instead of exact equality. The tests in this package check if the floating point numbers parsed from the provided CSVs and computed models are equal within a tolerance level for Python and R.

> [!NOTE]
> Depending on the system, there may be subtle differences in floating point numbers if you run fastFMM in R versus using fast-fmm-rpy2.

## License
This software is developed under a CC0 1.0 Universal license. See the [License](LICENSE) file for more details.

## Referencing
If you use this package please reference the following papers, as well as our [most recent Zenodo release](https://zenodo.org/badge/latestdoi/952179029):
- Cui et al. (2022) [Implementation of the fast univariate inference approach](https://doi.org/10.1080/10618600.2021.1950006)
- Loewinger et al. (2024) [A statistical framework for analysis of trial-level temporal dynamics in fiber photometry experiments.](https://doi.org/10.7554/eLife.95802)

## Contribute

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
uv run bump-my-version show-bump
```

Test the bump command, don't write any files, just pretend.
```bash
uv run bump-my-version bump <major|minor|patch> --verbose --dry-run
```

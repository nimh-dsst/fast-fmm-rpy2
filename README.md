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

##### Installing using Conda/Mamba environment

- @joshlawrimore made the deicision to attempt to install R using mamba and chose to compile all of the new fastFMM dependencies. This required some trial and error in getting the correct compilers set in the `$CONDA_PREFIX/lib/R/etc/Makeconf.site file`. On @joshlawrimore's MacBook Pro with an M3 chip, you must update the files to be:

```bash
## ---- R/etc/Makeconf.site ----
## Site-specific R configuration with explicit flags

# C17 toolchain - use explicit flags instead of $(CFLAGS)
CC17 = arm64-apple-darwin20.0.0-clang
C17FLAGS = -ftree-vectorize -fPIC -fstack-protector-strong -O2 -pipe -isystem /Users/lawrimorejg/miniforge3/envs/fast-fmm-r/include -std=gnu17

# C11 toolchain
CC11 = arm64-apple-darwin20.0.0-clang
C11FLAGS = -ftree-vectorize -fPIC -fstack-protector-strong -O2 -pipe -isystem /Users/lawrimorejg/miniforge3/envs/fast-fmm-r/include -std=gnu11

# C++17 toolchain
CXX17 = arm64-apple-darwin20.0.0-clang++
CXX17FLAGS = -ftree-vectorize -fPIC -fstack-protector-strong -O2 -pipe -stdlib=libc++ -fvisibility-inlines-hidden -fmessage-length=0 -isystem /Users/lawrimorejg/miniforge3/envs/fast-fmm-r/include -std=gnu++17

# C++14 toolchain  
CXX14 = arm64-apple-darwin20.0.0-clang++
CXX14FLAGS = -ftree-vectorize -fPIC -fstack-protector-strong -O2 -pipe -stdlib=libc++ -fvisibility-inlines-hidden -fmessage-length=0 -isystem /Users/lawrimorejg/miniforge3/envs/fast-fmm-r/include -std=gnu++14

# C++11 toolchain
CXX11 = arm64-apple-darwin20.0.0-clang++
CXX11FLAGS = -ftree-vectorize -fPIC -fstack-protector-strong -O2 -pipe -stdlib=libc++ -fvisibility-inlines-hidden -fmessage-length=0 -isystem /Users/lawrimorejg/miniforge3/envs/fast-fmm-r/include -std=gnu++11

# Fortran runtime
FLIBS = -lgfortran -lquadmath -lm
```

During the conda/mamba installation you must install compilers to environment if you want a "pure" environment install:

```bash
mamba create -n fast-fmm-r -c conda-forge \
  r-base=4.4 r-devtools \
  clang_osx-arm64 clangxx_osx-arm64 gfortran_osx-arm64 \
  make cmake pkg-config llvm-openmp \
  libgit2 libcurl openssl libxml2
  ```

Then do the following to ensure the aforementioned sitefile is always included when the env is active:

```bash
mkdir -p "$CONDA_PREFIX/etc/conda/activate.d" "$CONDA_PREFIX/etc/conda/deactivate.d"

# Ensure R uses the site Makeconf
cat > "$CONDA_PREFIX/etc/conda/activate.d/r_makevars.sh" <<'EOF'
export R_MAKEVARS_SITE="$CONDA_PREFIX/lib/R/etc/Makeconf.site"
EOF
cat > "$CONDA_PREFIX/etc/conda/deactivate.d/r_makevars.sh" <<'EOF'
unset R_MAKEVARS_SITE
EOF

cat > "$CONDA_PREFIX/etc/conda/activate.d/r_libs.sh" <<'EOF'
export R_LIBS_USER="$CONDA_PREFIX/lib/R/library"
EOF
cat > "$CONDA_PREFIX/etc/conda/deactivate.d/r_libs.sh" <<'EOF'
unset R_LIBS_USER
EOF

cat > "$CONDA_PREFIX/etc/conda/activate.d/build_flags.sh" <<'EOF'
export PKG_CONFIG_PATH="$CONDA_PREFIX/lib/pkgconfig:$CONDA_PREFIX/share/pkgconfig"
export CPPFLAGS="-I$CONDA_PREFIX/include"
export LDFLAGS="-L$CONDA_PREFIX/lib -Wl,-rpath,$CONDA_PREFIX/lib"
EOF
cat > "$CONDA_PREFIX/etc/conda/deactivate.d/build_flags.sh" <<'EOF'
unset PKG_CONFIG_PATH CPPFLAGS LDFLAGS
EOF
```

check with the following:

```bash
mamba activate fast-fmm-r

# R includes your site file
R -q -e 'cat("R_MAKEVARS_SITE=", Sys.getenv("R_MAKEVARS_SITE"), "\n")'

# Compilers and flags look sane
R CMD config CC
R CMD config CXX
R CMD config CXX17
R CMD config FLIBS          # ==> should be: -lgfortran -lquadmath -lm (no .../lib/gcc..., no -lheapt_w)

# pkg-config resolves to env libs
pkg-config --libs --cflags libgit2

# New installs target the env first
R -q -e 'print(.libPaths())'  # first path should be .../envs/fast-fmm-r/lib/R/library
```

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

### Updated fastFMM R package

The updated code is sitting in Al's repo. Use devtools to install from GitHub. Current local_rules in fmm_run.py module will somewhat flatten the 4 objects returned by fui into 15. Here are the object names and python types:

``` python
0: betaHat: <class 'numpy.ndarray'>
1: betaHat_var: <class 'numpy.ndarray'>
2: qn: <class 'numpy.ndarray'>
3: aic: <class 'numpy.ndarray'>
4: betaTilde: <class 'numpy.ndarray'>
var_random: <class 'numpy.ndarray'>
residuals: <class 'rpy2.robjects.vectors.BoolVector'>
H: <class 'rpy2.robjects.vectors.BoolVector'>
R: <class 'numpy.ndarray'>
G: <class 'numpy.ndarray'>
GHat: <class 'numpy.ndarray'>
Z: <class 'rpy2.rlike.container.NamedList'>
argvals: <class 'numpy.ndarray'>
randeffs: <class 'rpy2.rinterface_lib.sexp.NULLType'>
se_mat: <class 'numpy.ndarray'>
```

For whatever reason, on @joshlawrimore's macbook pro M3, the mamba installed R and rpy2 interface (rpy2=3.5.17) doesn't allow for the dict converson of the model returned by fui anymore. Instead, use a zipped version of (mod.names(), mod.values()).

#### betaHat imported from R by rpy2 local_rules

Is a (2,43) numpy ndarray NOT a pandas DataFrame.

#### betaHat_var imported from R by rpy2 local_rules

Is a (43, 43, 2) numpy array. It is NOT inheriting the row names nor the column names using the conversion rules.

### R model contents

Calling fui in R returns a 4-element named list.

#### betaHat in R

The first element is named `betaHat` it's structure is:

```R
str(mod1$betaHat)
 num [1:2, 1:43] -0.1517 0.022 -0.1538 0.0206 -0.1575 ...
 - attr(*, "dimnames")=List of 2
  ..$ : chr [1:2] "(Intercept)" "lick_rate_050"
  ..$ : chr [1:43] "1" "2" "3" "4" ...
```

#### HHat in R

The second element is named `HHat` it's structure is:

```R
 $ HHat   : num [1, 1:43] 0.00544 0.01324 0.01554 0.00883 0.00511 ...
  ..- attr(*, "dimnames")=List of 2
  .. ..$ : chr "var.id.(Intercept)"
  .. ..$ : NULL
```

### The fui analytic and var command control what gets returned

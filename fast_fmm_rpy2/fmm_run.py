from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.rinterface as rinterface  # type: ignore
from packaging import version
from rpy2 import robjects as ro  # type: ignore
from rpy2.rinterface import NULL  # type: ignore
from rpy2.rinterface_lib.sexp import NULLType  # type: ignore
from rpy2.robjects import pandas2ri  # type: ignore
from rpy2.robjects.conversion import localconverter  # type: ignore
from rpy2.robjects.packages import importr  # type: ignore
from rpy2.robjects.vectors import IntVector  # type: ignore

from fast_fmm_rpy2.ingest import read_csv_in_pandas_pass_to_r

# R packages will be imported inside functions where conversion
# context is available


def get_fastfmm_version() -> version.Version:
    """
    Get the version of the fastFMM R package.

    Returns
    -------
    version.Version
        The version of the fastFMM package as a
        `packaging.version.Version` object.

    Raises
    ------
    ImportError
        If the fastFMM package is not available or version cannot be
        determined.
    """
    # Import R packages locally to avoid conversion context issues
    utils = importr("utils")
    try:
        # Try using utils::packageVersion (most reliable)
        pkg_version = utils.packageVersion("fastFMM")
        version_str = str(pkg_version[0])
        return version.parse(version_str)
    except Exception:
        try:
            # Fallback: use installed.packages
            version_str = str(
                ro.r('installed.packages()["fastFMM", "Version"]')[0]
            )
            return version.parse(version_str)
        except Exception as e:
            raise ImportError(f"Could not determine fastFMM version: {e}")


def check_fastfmm_version(
    min_version: str | None = None, max_version: str | None = None
) -> bool:
    """
    Check if the fastFMM version meets the specified requirements.

    Parameters
    ----------
    min_version : str, optional
        Minimum required version (inclusive).
    max_version : str, optional
        Maximum allowed version (inclusive).

    Returns
    -------
    bool
        True if version requirements are met.

    Examples
    --------
    >>> check_fastfmm_version(min_version="0.3.0") # True if >= 0.3.0
    >>> check_fastfmm_version(max_version="0.4.0") # True if <= 0.4.0
    >>> check_fastfmm_version("0.3.0", "0.4.0") # True if 0.3.0 <= v <= 0.4.0
    """
    current_version = get_fastfmm_version()

    if min_version and current_version < version.parse(min_version):
        return False
    if max_version and current_version > version.parse(max_version):
        return False

    return True


local_rules = ro.default_converter + pandas2ri.converter


@local_rules.rpy2py.register(rinterface.FloatSexpVector)
def rpy2py_floatvector(obj):
    x = np.array(obj)
    try:
        # if names is assigned, convert to pandas series
        return pd.Series(x, obj.names)
    except Exception:
        # if dimnames assigned, it's a named matrix,
        # convert to pandas dataframe
        try:
            rownames, colnames = obj.do_slot("dimnames")
            if not isinstance(rownames, NULLType) and not isinstance(
                colnames, NULLType
            ):
                x = pd.DataFrame(x, index=rownames, columns=colnames)
            else:
                x = pd.DataFrame(x, columns=colnames)

        finally:
            # plain vector/matrix
            return x


def run_with_pandas_dataframe(csv_filepath: Path, import_rules=local_rules):
    # Import R packages locally to avoid conversion context issues
    base = importr("base")
    stats = importr("stats")
    fastFMM = importr("fastFMM")
    read_csv_in_pandas_pass_to_r(
        csv_filepath=csv_filepath, r_var_name="py_dat"
    )
    with localconverter(import_rules):
        mod = fastFMM.fui(
            stats.as_formula("photometry ~ cs + (1 | id)"),
            data=base.as_symbol("py_dat"),
        )
    return mod


def run_with_r_dataframe(csv_filepath: Path, import_rules=local_rules):
    ro.r(f'dat = read.csv("{str(csv_filepath.absolute())}")')
    ro.r("mod = fui(photometry ~ cs + (1 | id), data = dat, parallel = TRUE)")
    with localconverter(import_rules):
        r_mod = ro.r("mod")
    return r_mod


def fui(
    csv_filepath: Path | None,
    formula: str,
    parallel: bool = True,
    import_rules=local_rules,
    r_var_name: str | None = "py_dat",
    family: str = "gaussian",
    analytic: bool = True,
    var: bool = True,
    silent: bool = False,
    argvals: list[int] | NULLType = NULL,
    nknots_min: int | NULLType = NULL,
    nknots_min_cov: int = 35,
    smooth_method: str = "GCV.Cp",
    splines: str = "tp",
    design_mat: bool = False,
    residuals: bool = False,
    n_boots: int = 500,
    seed: int = 1,
    subj_id: str | NULLType = NULL,
    n_cores: int | NULLType = NULL,
    caic: bool = False,
    randeffs: bool = False,
    non_neg: int = 0,
    MoM: int = 1,
    concurrent: bool = False,
    impute_outcome: bool = False,
    override_zero_var: bool = False,
    unsmooth: bool = False,
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
    import_rules : object, optional
        The import rules to be used for the local converter.
        Default is `local_rules`.
    r_var_name : str or None, optional
        The R variable name to be used for the data. If `csv_filepath` is None,
        this must be provided. Default is "py_dat".
    family : str, optional
        The family to be used in the fastFMM model.
        Default is "gaussian".
    analytic : bool, optional
        Whether to use the analytic inference approach or bootstrap.
        Default is True.
    var : bool, optional
        Whether to include the within-timepoint variance in the model.
        Default is True.
    parallel : bool, optional
        Whether to run the model in parallel. Default is True.
    silent : bool, optional
        Whether to suppress the output of the model. Default is False.
    argvals : list[int] or None, optional
        The indices of the functional domain to be used in the model.
        Default is None (i.e., use all points).
    nknots_min : int or None, optional
        Minimal number of knots in the penalized smoothing for the
        regression coefficients. Defaults to None, which then uses L/2
        where L is the dimension of the functional domain.
    nknots_min_cov : str or None, optional
        Minimal number of knots in the penalized smoothing for
        the covariance matrices. Default is 35.
    smooth_method : str, optional
        How to select smoothing parameter in step 2.
        Default is "GCV.Cp".
    splines : str, optional
        The type of spline to be used in the model.
        Default is "tp".
    design_mat : bool, optional
        Whether to return the design matrix. Default is False.
    residuals : bool, optional
        Whether to save residuals from unsmoothed LME
        Default is False.
    n_boots : int, optional
        Number of samples when using bootstrap inference.
        Default is 500.
    seed : int, optional
        Numeric value used to ensure bootstrap replicates (draws) are
        correlated across functional domains for certain bootstrap approaches.
        Default is 1.
    subj_id : str or NULLType, optional
        Name of the variable that contains subject ID.
        Default is NULL.
    n_cores : int or NULLType, optional
        The number of cores to use for parallelization.
        If not specified, defaults to 3/4ths of detected cores.
        Default is NULL.
    caic : bool, optional
        Whether to calculate CAIC.
        Default is False.
    randeffs : bool, optional
        Whether to return random effect estimates.
        Default is False.
    non_neg : int, optional
        0 - no non-negativity constrains
        1 - non-negativity constraints on every coefficient for variance,
        2 - non-negativity on average of coefficents for 1 variance term.
        Default is 0.
    MoM : int, optional
        Method of moments estimator.
        Default is 1.
    concurrent : bool, optional
        Whether to fit a concurrent model.
        Default is False.
    impute_outcome : bool, optional
        Whether to impute missing outcome values with FPCA
        Default is False.
    override_zero_var : bool, optional
        Whether to proceed with model fitting if columns have zero variance.
        Suggested for cases where individual columns have zero variance but
        interactions have non-zero variance
        Default is False.
    unsmooth : bool, optional
        Whether to return the raw estimates of coefficients and variances
        without smoothing
        Default is False.
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
    if csv_filepath is None:
        assert r_var_name is not None, (
            "r_var_name must be provided if csv_filepath is None"
        )
    elif r_var_name is not None:
        read_csv_in_pandas_pass_to_r(
            csv_filepath=csv_filepath, r_var_name=r_var_name
        )
    else:
        raise ValueError("r_var_name must be provided if csv_filepath is None")
    # Import R packages locally to avoid conversion context issues
    base = importr("base")
    stats = importr("stats")
    fastFMM = importr("fastFMM")

    if argvals is not NULL:
        argvals = IntVector(argvals)
    with localconverter(import_rules):
        mod = fastFMM.fui(
            formula=stats.as_formula(formula),
            data=base.as_symbol(r_var_name),
            parallel=parallel,
            family=family,
            analytic=analytic,
            var=var,
            silent=silent,
            argvals=argvals,
            nknots_min=nknots_min,
            nknots_min_cov=nknots_min_cov,
            smooth_method=smooth_method,
            splines=splines,
            design_mat=design_mat,
            residuals=residuals,
            n_boots=n_boots,
            seed=seed,
            subj_id=subj_id,
            n_cores=n_cores,
            caic=caic,
            randeffs=randeffs,
            non_neg=non_neg,
            MoM=MoM,
            concurrent=concurrent,
            impute_outcome=impute_outcome,
            override_zero_var=override_zero_var,
            unsmooth=unsmooth,
        )
    return mod

from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.rinterface as rinterface  # type: ignore
from rpy2 import robjects as ro  # type: ignore
from rpy2.rinterface_lib.sexp import NULLType  # type: ignore
from rpy2.robjects import pandas2ri  # type: ignore
from rpy2.robjects.conversion import localconverter  # type: ignore
from rpy2.robjects.packages import importr  # type: ignore

from fast_fmm_rpy2.ingest import read_csv_in_pandas_pass_to_r

# import R packages
base = importr("base")
utils = importr("utils")
stats = importr("stats")
fastFMM = importr("fastFMM")

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
    with localconverter(import_rules):
        mod = fastFMM.fui(
            stats.as_formula(formula),
            data=base.as_symbol(r_var_name),
            parallel=parallel,
        )
    return mod

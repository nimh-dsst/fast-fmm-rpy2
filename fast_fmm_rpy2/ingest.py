from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.rinterface as rinterface  # type: ignore
from rpy2 import robjects as ro
from rpy2.robjects import pandas2ri  # type: ignore
from rpy2.robjects.conversion import localconverter  # type: ignore


def pandas_read_in_csv_roundtrip(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, float_precision="round_trip")
    return df


def pandas_read_in_csv_default(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    return df


def pandas_read_in_csv_high_precision(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, float_precision="high")
    return df


def pandas_read_in_csv_legacy(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, float_precision="legacy")
    return df


def r_read_in_csv_rpy2_convert(filepath: Path) -> ro.vectors.DataFrame:
    ro.r(f'dat = read.csv("{str(filepath.absolute().as_posix())}")')
    dat = ro.r("dat")
    return dat


def compare_df_dat(df: pd.DataFrame, dat: ro.vectors.DataFrame):
    photometry_idx = [
        int(col_name.split(".")[-1])
        for col_name in df.columns
        if col_name.startswith("photometry.")
    ]
    results: list[dict] = []
    for col in photometry_idx:
        for row in range(len(df)):
            # adjust index for R dat
            row_j = row + 1
            dat_array = np.asarray(dat.rx(f"{row_j}", f"photometry.{col}"))
            result = np.isclose(
                dat_array[0],
                df[f"photometry.{col}"][row],
                rtol=1e-05,
                atol=1e-08,
            )
            result_dict = {
                "float_isclose": result,
                "column": f"photometry.{col}",
                "df_row": row,
                "dat_row": row_j,
                "dat_value_string": f"{dat_array[0]:.55f}",
                "df_value_string": f"{df[f'photometry.{col}'][row]:.55f}",
            }
            results.append(result_dict)
    result_df = pd.DataFrame(results)
    return result_df


def read_csv_in_pandas_pass_to_r(
    csv_filepath: Path, r_var_name: str = "py_dat"
) -> pd.DataFrame:
    # read in data using round_trip float precision to mimic R precision
    df = pd.read_csv(csv_filepath, float_precision="round_trip")

    # R uses NA_integer_, so Pandas DataFrames MUST use pd.NA and NOT np.nan
    # for NA representation
    df["trial"] = df["trial"].fillna(-1).astype("int")
    df["trial"] = df["trial"].apply(lambda x: pd.NA if x < 1 else x)
    # change index of df to match 1 to len(df) + 1 index in R
    df.index = range(1, len(df) + 1)  # type: ignore

    # convert it to an R variable
    with localconverter(pandas2ri.converter):
        ro.globalenv[r_var_name] = df
    return df


def read_csv_for_r(
    csv_filepath: Path, r_var_name: str = "py_dat"
) -> pd.DataFrame:
    # read in data using round_trip float precision to mimic R precision
    df = pd.read_csv(csv_filepath, float_precision="round_trip")

    # R uses NA_integer_, so Pandas DataFrames MUST use pd.NA and NOT np.nan
    # for NA representation
    df["trial"] = df["trial"].fillna(-1).astype("int")
    df["trial"] = df["trial"].apply(lambda x: pd.NA if x < 1 else x)
    # change index of df to match 1 to len(df) + 1 index in R
    df.index = range(1, len(df) + 1)  # type: ignore

    return df


def pass_pandas_to_r(df: pd.DataFrame, r_var_name: str = "py_dat") -> None:
    with localconverter(pandas2ri.converter):
        ro.globalenv[r_var_name] = df
    return None


def compare_df_dat_in_r(csv_filepath: Path) -> bool:
    with localconverter(ro.default_converter):
        ro.r(f'dat = read.csv("{str(csv_filepath.absolute().as_posix())}")')
    read_csv_in_pandas_pass_to_r(csv_filepath=csv_filepath)
    compare_result = (
        np.asarray(
            ro.r(
                (
                    "isTRUE(all.equal(na.omit(dat), na.omit(py_dat),"
                    "tolerance=1e-15, check.attributes=FALSE))"
                )
            )
        )
        .astype(bool)
        .item()
    )
    return compare_result


def mod_rules() -> ro.conversion.Converter:
    rules = ro.default_converter + pandas2ri.converter

    @rules.rpy2py.register(rinterface.FloatSexpVector)
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
                x = pd.DataFrame(x, index=rownames, columns=colnames)
            finally:
                # plain vector/matrix
                return x

    # dummy call to prevent pylance error
    _ = rpy2py_floatvector
    return rules

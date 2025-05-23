from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rpy2.rinterface as rinterface  # type: ignore
from matplotlib.gridspec import GridSpec
from rpy2 import robjects as ro  # type: ignore
from rpy2.rinterface_lib.sexp import NULLType  # type: ignore
from rpy2.rlike.container import OrdDict  # type: ignore
from rpy2.robjects import pandas2ri  # type: ignore
from rpy2.robjects.conversion import localconverter  # type: ignore
from rpy2.robjects.packages import importr  # type: ignore

from fast_fmm_rpy2.ingest import read_csv_in_pandas_pass_to_r


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
    # number of variables to plot
    num_var = fuiobj["betaHat"].shape[0]
    var_names = fuiobj["betaHat"].index.to_list()
    res_list = []
    if num_row is None:
        num_row = int(np.ceil(num_var / 2))
    num_col = int(np.ceil(num_var / num_row))

    align = 0 if align_x is None else align_x * x_rescale

    if title_names is None:
        try:
            title_names = fuiobj["betaHat"].index.to_list()
        except KeyError:
            title_names = [f"Variable {i}" for i in range(num_var)]

    # sanity check the number of rows with number of varibles
    if not len(fuiobj["betaHat"]) == len(title_names):
        Warning(
            "Incorrect number of title_names detected,"
            + " replacing title names in plots"
        )
        try:
            title_names = fuiobj["betaHat"].index.to_list()
        except KeyError:
            title_names = [f"Variable {i}" for i in range(num_var)]

    # line in R is  names(res_list) <- rownames(fuiobj$betaHat)
    # TODO: may need to change res_list in script to dict later on

    # Create figure and subplots
    fig = plt.figure(figsize=(5, 4 * num_row))
    gs = GridSpec(num_row, num_col, figure=fig)

    res_list = []

    for r in range(num_var):
        row = r // num_col
        col = r % num_col
        ax = fig.add_subplot(gs[row, col])

        # Create plotting dataframe
        if "betaHat.var" not in fuiobj:
            beta_hat_plt = pd.DataFrame(
                {"s": fuiobj["argvals"], "beta": fuiobj["betaHat"].iloc[r, :]}
            )

            # Plot estimate
            ax.plot(
                beta_hat_plt["s"] / x_rescale
                - align / x_rescale
                - 1 / x_rescale,
                beta_hat_plt["beta"],
                color="black",
                label="Estimate",
                linewidth=1,
            )

        else:
            var_diag = np.diag(fuiobj["betaHat.var"][:, :, r])
            beta_hat_plt = pd.DataFrame(
                {
                    "s": fuiobj["argvals"],
                    "beta": fuiobj["betaHat"].iloc[r, :],
                    "lower": fuiobj["betaHat"].iloc[r, :]
                    - 2 * np.sqrt(var_diag),
                    "upper": fuiobj["betaHat"].iloc[r, :]
                    + 2 * np.sqrt(var_diag),
                    "lower_joint": fuiobj["betaHat"].iloc[r, :]
                    - fuiobj["qn"][r] * np.sqrt(var_diag),
                    "upper_joint": fuiobj["betaHat"].iloc[r, :]
                    + fuiobj["qn"][r] * np.sqrt(var_diag),
                }
            )

            # Plot confidence bands
            x_vals = (
                beta_hat_plt["s"] / x_rescale
                - align / x_rescale
                - 1 / x_rescale
            )
            ax.fill_between(
                x_vals,
                beta_hat_plt["lower_joint"],
                beta_hat_plt["upper_joint"],
                color="gray",
                alpha=0.2,
            )
            ax.fill_between(
                x_vals,
                beta_hat_plt["lower"],
                beta_hat_plt["upper"],
                color="gray",
                alpha=0.4,
            )
            ax.plot(
                x_vals,
                beta_hat_plt["beta"],
                color="black",
                label="Estimate",
                linewidth=1,
            )

        # Add horizontal line at y=0
        ax.axhline(y=0, color="black", linestyle="--", alpha=0.75)

        # Set labels and title
        ax.set_xlabel(xlab)
        ax.set_ylabel(f"β{r}(s)")
        ax.set_title(title_names[r], fontweight="bold")

        # Set y limits
        if ylim is not None:
            ax.set_ylim(ylim)
        else:
            if "betaHat.var" not in fuiobj or fuiobj["betaHat.var"] is None:
                y_range = [
                    beta_hat_plt["beta"].min(),
                    beta_hat_plt["beta"].max(),
                ]
            else:
                y_range = [
                    beta_hat_plt["lower_joint"].min(),
                    beta_hat_plt["upper_joint"].max(),
                ]

            y_adjust = y_scal_orig * (y_range[1] - y_range[0])
            y_range[0] -= y_adjust
            y_range = [y * y_val_lim for y in y_range]
            ax.set_ylim(y_range)

        # Add vertical line at x=0 if aligned
        if align_x is not None:
            ax.axvline(
                x=0, color="black", linestyle="--", alpha=0.75, linewidth=0.5
            )

        res_list.append(beta_hat_plt)

    fig.tight_layout()

    if return_data:
        return fig, dict(zip(var_names, res_list))
    return fig


def r_export_plot_fui_results(
    csv_filepath: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # read data, run fui, run plot_fui in R
    ro.r(f'dat <- read.csv("{str(csv_filepath.absolute())}")')
    ro.r("library(fastFMM)")
    ro.r("mod <- fui(photometry ~ cs + (1 | id), data = dat, parallel = TRUE)")
    ro.r("plot_data <- plot_fui(mod, return=TRUE)")
    with (ro.default_converter + pandas2ri.converter).context():
        intercept_dict: OrdDict = ro.conversion.get_conversion().rpy2py(
            ro.r("plot_data['(Intercept)']")
        )
        r_intercept: pd.DataFrame = intercept_dict["(Intercept)"]
        cs_dict: OrdDict = ro.conversion.get_conversion().rpy2py(
            ro.r("plot_data['cs']")
        )
        r_cs: pd.DataFrame = cs_dict["cs"]
    return r_intercept, r_cs


def py_plot_fui_results(
    csv_filepath: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # read data to pandas, pass to R, run fui, pass to rpy2, run plot_fui
    read_csv_in_pandas_pass_to_r(csv_filepath)
    fastFMM = importr("fastFMM")
    base = importr("base")
    stats = importr("stats")
    mod_rules = ro.default_converter + pandas2ri.converter

    @mod_rules.rpy2py.register(rinterface.FloatSexpVector)
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

    # dummy call to prevent pylance error
    _ = rpy2py_floatvector

    with localconverter(mod_rules):
        mod = fastFMM.fui(
            stats.as_formula("photometry ~ cs + (1 | id)"),
            data=base.as_symbol("py_dat"),
        )
    _, plot_data = plot_fui(mod, return_data=True)
    py_intercept: pd.DataFrame = plot_data["(Intercept)"]
    py_cs: pd.DataFrame = plot_data["cs"]
    return py_intercept, py_cs

from pathlib import Path

import numpy as np
import pytest

from fast_fmm_rpy2.plot_fui import (
    py_plot_fui_results,
    r_export_plot_fui_results,
)


@pytest.fixture
def binary_filepath() -> Path:
    return Path(r"tests/data/binary.csv")


def test_plot_fui_compare(binary_filepath: Path) -> None:
    r_intercept, r_cs = r_export_plot_fui_results(binary_filepath)
    py_intercept, py_cs = py_plot_fui_results(binary_filepath)
    assert np.allclose(
        r_intercept.to_numpy().flatten(), py_intercept.to_numpy().flatten()
    )
    assert np.allclose(r_cs.to_numpy().flatten(), py_cs.to_numpy().flatten())
    return None

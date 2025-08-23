import pandas as pd

from recx import AbsTolCheck, EqualCheck


def test_equal_check_detects_diff(diff_frames):
    b, c = diff_frames
    res = EqualCheck().run(b, c, "B")[0]
    assert not res.passed


def test_equal_check_nan(equal_nan_frames):
    b, c = equal_nan_frames
    res = EqualCheck().run(b, c, "A")[0]
    assert res.passed


def test_abs_tol_boundary():
    df1 = pd.DataFrame({"B": [1.0, 2.0]})
    df2 = pd.DataFrame({"B": [1.05, 2.0]})
    # Use rounding to mitigate FP representation issues
    res = AbsTolCheck(tol=0.0500000001).run(df1, df2, "B")[0]
    assert res.passed


def test_abs_tol_sort(abs_tol_frames):
    b, c = abs_tol_frames
    res = AbsTolCheck(tol=0.0001, sort="desc").run(b, c, "B")[0]
    assert not res.passed
    errors = res.failed_rows["abs_error"].values
    assert errors[0] >= errors[1]

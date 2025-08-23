import pandas as pd
import pytest

from recx import AbsTolCheck, EqualCheck, Rec, RelTolCheck
from recx.checks import ColumnCheck, index_check
from recx.exceptions import RecFailedException
from recx.rec import get_col
from recx.results import CheckResult, RecResult


def test_index_check_invalid():
    df = pd.DataFrame({"id": [1]}).set_index("id")
    with pytest.raises(ValueError):
        index_check(df, df, "bad")  # type: ignore[arg-type]


def test_get_col_duplicate_column_raises():
    # Duplicate column label -> selecting returns DataFrame
    df = pd.DataFrame([[1, 2]], columns=["A", "A"])  # duplicate labels
    with pytest.raises(TypeError):
        get_col(df, "A")


def test_abs_tol_invalid_sort():
    df1 = pd.DataFrame({"x": [0, 1]})
    df2 = pd.DataFrame({"x": [1, 3]})
    check = AbsTolCheck(tol=0.1, sort="wrong")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        check.run(df1, df2, "x")


def test_rel_tol_sort_and_zero_division_handling():
    df1 = pd.DataFrame({"x": [0.0, 10.0, 20.0]})
    df2 = pd.DataFrame({"x": [0.0, 11.0, 10.0]})  # relative errors differ
    check = RelTolCheck(tol=0.05, sort="desc")
    res = check.run(df1, df2, "x")[0]
    assert not res.passed
    # Ensure rel_error column exists and sorted desc
    errs = res.failed_rows["rel_error"].values
    assert list(errs) == sorted(errs, reverse=True)


def test_rec_raise_on_failure(diff_frames):
    b, c = diff_frames
    rec = Rec(columns={"B": EqualCheck()})
    with pytest.raises(RecFailedException):
        rec.run(b, c, raise_on_failure=True)


def test_rec_result_raise_for_failures():
    df = pd.DataFrame({"x": [1, 2]})
    # Construct a failing CheckResult manually
    fail_rows = pd.DataFrame({"baseline": [1], "candidate": [2]}, index=[0])
    cr = CheckResult(
        failed_rows=fail_rows, check_name="EqualCheck", total_rows=2, column="x"
    )
    rr = RecResult(results=[cr], baseline=df, candidate=df)
    with pytest.raises(RecFailedException):
        rr.raise_for_failures()


def test_checkresult_one_liner_width_error():
    df = pd.DataFrame()
    cr = CheckResult(failed_rows=df, check_name="EqualCheck", total_rows=0)
    with pytest.raises(ValueError):
        cr.one_liner(width=1)  # too narrow


def test_checkresult_failures_str_and_mini_signature():
    fail_rows = pd.DataFrame({"baseline": [1], "candidate": [2]}, index=[0])
    cr = CheckResult(
        failed_rows=fail_rows, check_name="EqualCheck", total_rows=1, column="col1"
    )
    txt = cr.failures_str()
    assert "Showing up to" in txt and "col1" in txt


def test_recresult_summary_outputs(capsys, diff_frames):
    b, c = diff_frames
    rec = Rec(columns={"B": EqualCheck()}, align_date_col="date")
    result = rec.run(b, c)
    result.summary()  # prints
    out = capsys.readouterr().out
    assert "DataFrame Reconciliation Summary" in out
    assert "FAILED" in out
    assert "Failing rows" in out


def test_recresult_summary_all_pass(capsys):
    df = pd.DataFrame({"x": [1, 1]})
    rec = Rec(columns={"x": EqualCheck()}, check_all=False)
    res = rec.run(df, df)
    assert res.passed()
    res.summary()
    out = capsys.readouterr().out
    assert "FAILED" not in out


def test_regex_column_check():
    # Custom regex across multiple columns
    df1 = pd.DataFrame({"m1": [1, 2], "m2": [3, 4]})
    df2 = pd.DataFrame({"m1": [2, 2], "m2": [3, 5]})
    check = AbsTolCheck(tol=0.0, regex=True)
    res = check.run(df1, df2, r"m[12]")
    # Expect two results (one pass maybe, one fail) but at least length 2
    assert len(res) == 2


def test_column_check_dataframe_selection_type_error():
    class BadCheck(ColumnCheck):
        def check(
            self, baseline: pd.Series, candidate: pd.Series
        ) -> pd.DataFrame:  # pragma: no cover - trivial pass
            return pd.DataFrame()

    df = pd.DataFrame([[1, 2], [3, 4]], columns=["X", "X"])  # duplicate columns
    check = BadCheck()
    with pytest.raises(TypeError):
        check.run(df, df, "X")

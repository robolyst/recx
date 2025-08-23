import pandas as pd
import pytest

from recx import AbsTolCheck, EqualCheck, Rec, RelTolCheck
from recx.checks import ColumnCheck, index_check
from recx.results import CheckResult


def test_regex_no_match_returns_empty():
    df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2 = df1.copy()
    check = AbsTolCheck(tol=0.0, regex=True)
    # Pattern that matches nothing in intersection
    results = check.run(df1, df2, r"^z_")
    assert results == []


def test_reltol_invalid_sort():
    df1 = pd.DataFrame({"x": [1.0, 2.0]})
    df2 = pd.DataFrame({"x": [1.1, 1.9]})
    check = RelTolCheck(tol=0.2, sort="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        check.run(df1, df2, "x")


def test_reltol_zero_denominator_stabiliser():
    # candidate has zeros -> stabiliser path
    base = pd.DataFrame({"x": [0.0, 1.0, 2.0]})
    cand = pd.DataFrame({"x": [0.0, 2.0, 0.0]})
    res = RelTolCheck(tol=0.1).run(base, cand, "x")[0]
    assert not res.passed
    assert "rel_error" in res.failed_rows


def test_index_check_perfect_alignment():
    df = pd.DataFrame({"k": [1, 2], "v": [3, 4]}).set_index("k")
    missing = index_check(df, df, "missing")
    extra = index_check(df, df, "extra")
    assert missing.passed and extra.passed


def test_rec_all_columns_skipped():
    df1 = pd.DataFrame({"id": [1, 2], "val": [10, 11]}).set_index("id")
    df2 = pd.DataFrame({"id": [1, 2], "val": [99, 100]}).set_index("id")
    rec = Rec(columns={"val": None}, check_all=True)
    result = rec.run(df1, df2)
    # val skipped so only index checks run (which pass)
    assert result.passed()


def test_rec_no_columns_check_all_false():
    df1 = pd.DataFrame({"id": [1, 2], "val": [10, 11]}).set_index("id")
    df2 = pd.DataFrame({"id": [1, 2], "val": [10, 99]}).set_index("id")
    rec = Rec(columns={}, check_all=False)
    result = rec.run(df1, df2)
    # Difference ignored
    assert result.passed()


def test_rec_no_columns_check_all_true():
    df1 = pd.DataFrame({"id": [1, 2], "val": [10, 11]}).set_index("id")
    df2 = pd.DataFrame({"id": [1, 2], "val": [10, 99]}).set_index("id")
    rec = Rec(columns={}, check_all=True)
    result = rec.run(df1, df2)
    assert not result.passed()


def test_empty_dataframes():
    df1 = pd.DataFrame({"id": []}).set_index("id")
    df2 = pd.DataFrame({"id": []}).set_index("id")
    rec = Rec(columns={}, check_all=False)
    result = rec.run(df1, df2)
    assert result.passed()


def test_checkresult_signature_and_outcome_column_none():
    # build a passing index check result (column None)
    df = pd.DataFrame()
    cr = CheckResult(
        failed_rows=df, check_name="index_check", total_rows=0, column=None
    )
    sig = cr.signature()
    assert sig.startswith("index_check")
    assert cr.outcome() == "PASSED ꪜ"


def test_checkresult_one_liner_padding():
    df = pd.DataFrame()
    cr = CheckResult(failed_rows=df, check_name="Eq", total_rows=0)
    line = cr.one_liner(width=60)
    assert "..." in line and len(line) >= 60


def test_checkresult_failures_str_truncation():
    # create > disp_rows failures
    fail_rows = pd.DataFrame({"baseline": range(20), "candidate": range(20)})
    cr = CheckResult(
        failed_rows=fail_rows,
        check_name="EqualCheck",
        total_rows=20,
        disp_rows=10,
    )
    txt = cr.failures_str()
    # We display only the tail; expect last index present and first line is not raw index 0 row
    assert "19" in txt


def test_summary_log_true_paths(caplog):
    df1 = pd.DataFrame({"id": [1, 2], "val": [1, 2]}).set_index("id")
    df2 = pd.DataFrame({"id": [1, 2], "val": [1, 99]}).set_index("id")
    rec = Rec(columns={"val": EqualCheck()})
    result = rec.run(df1, df2)
    with caplog.at_level("INFO"):
        result.summary(log=True)
    combined = "\n".join(caplog.messages)
    assert "FAILED" in combined and "DataFrame Reconciliation Summary" in combined


def test_summary_log_true_no_failures(capsys):
    df = pd.DataFrame({"id": [1, 2], "val": [1, 1]}).set_index("id")
    rec = Rec(columns={"val": EqualCheck()}, check_all=False)
    result = rec.run(df, df)
    result.summary(log=True)
    out = capsys.readouterr().out
    assert "FAILED" not in out


def test_equal_all_nans():
    df1 = pd.DataFrame({"x": [None, None]})
    df2 = pd.DataFrame({"x": [None, None]})
    res = EqualCheck().run(df1, df2, "x")[0]
    assert res.passed


def test_custom_column_check_dataframe_selection_duplicate():
    class Dummy(ColumnCheck):
        def check(
            self, baseline: pd.Series, candidate: pd.Series
        ) -> pd.DataFrame:  # pragma: no cover
            return pd.DataFrame()

    df = pd.DataFrame([[1, 2], [3, 4]], columns=["D", "D"])  # duplicate col label
    with pytest.raises(TypeError):
        Dummy().run(df, df, "D")


def test_multiindex_get_col_and_rec():
    tuples = [("2024-01-01", "A"), ("2024-01-02", "B")]
    idx = pd.MultiIndex.from_tuples(tuples, names=["date", "label"])
    b = pd.DataFrame({"val": [1, 2]}, index=idx)
    c = pd.DataFrame({"val": [1, 3]}, index=idx)
    # Do not align by date to avoid current MultiIndex boolean mask limitation
    rec = Rec(columns={"val": EqualCheck()}, align_date_col=None)
    res = rec.run(b, c)
    assert not res.passed()
    # index checks should be first two results with column None
    assert res.results[0].column is None and res.results[1].column is None

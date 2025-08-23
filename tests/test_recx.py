import pandas as pd

from recx import (
    AbsTolCheck,
    EqualCheck,
    Rec,
)
from recx.checks import index_check
from recx.rec import (
    clip_to_last_common_date,
    get_col,
)


def test_get_col():
    df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
        }
    )
    df = df.set_index("A")

    assert (get_col(df, "A") == pd.Index([1, 2, 3])).all()
    assert (get_col(df.reset_index(), "A") == pd.Series([1, 2, 3])).all()


def test_clip_to_last_common_date_index():
    df1 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "value": [1, 2],
        }
    )
    df1 = df1.set_index("date")

    df2 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-03"],
            "value": [3, 4],
        }
    )
    df2 = df2.set_index("date")

    clipped_df1, clipped_df2 = clip_to_last_common_date(df1, df2, "date")

    assert clipped_df1.equals(df1)
    assert clipped_df2.equals(df2.loc[:"2023-01-01", :])


def test_clip_to_last_common_date():
    df1 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "value": [1, 2],
        }
    )

    df2 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-03"],
            "value": [3, 4],
        }
    )

    clipped_df1, clipped_df2 = clip_to_last_common_date(df1, df2, "date")

    assert clipped_df1.equals(df1)
    assert clipped_df2.equals(df2[df2["date"] <= "2023-01-01"])


def test_index_check():
    df1 = pd.DataFrame(
        {
            "A": [1, 2],
            "B": [3, 4],
        }
    )
    df1 = df1.set_index("A")

    df2 = pd.DataFrame(
        {
            "A": [2, 3],
            "B": [5, 6],
        }
    )
    df2 = df2.set_index("A")

    result = index_check(df1, df2, "missing")
    assert not result.passed

    result = index_check(df1, df2, "extra")
    assert not result.passed


def test_check_equal():
    df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df2 = pd.DataFrame({"A": [1, 2], "B": [3, 5]})
    check = EqualCheck()
    results = check.run(df1, df2, "B")

    assert len(results) == 1
    assert not results[0].passed


def test_check_abs_tol():
    df1 = pd.DataFrame({"A": [1, 2], "B": [3.0, 4.0]})
    df2 = pd.DataFrame({"A": [1, 2], "B": [3.1, 4.1]})
    check = AbsTolCheck(tol=0.1)
    results = check.run(df1, df2, "B")

    assert len(results) == 1
    assert not results[0].passed


def test_dataframe_diff():
    df1 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [3, 4],
        }
    )
    df1 = df1.set_index("date")

    df2 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [3, 5],
        }
    )
    df2 = df2.set_index("date")

    rec = Rec(columns={"B": EqualCheck()}, align_date_col="date")
    result = rec.run(df1, df2, raise_on_failure=False)

    assert not result.passed()
    assert len(result.failures()) == 1
    assert not result.failures()[0].passed


def test_skip_column_test():
    df1 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [3, 4],
        }
    )
    df1 = df1.set_index("date")

    df2 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [3, 5],  # There's a diff here
        }
    )
    df2 = df2.set_index("date")

    rec = Rec(
        columns={
            "B": None,  # Skip this column
        },
        align_date_col="date",
    )
    result = rec.run(df1, df2, raise_on_failure=False)

    assert result.passed()


def test_failure_with_sort():
    df1 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [3, 4],
        }
    )
    df1 = df1.set_index("date")

    df2 = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "A": [1, 2],
            "B": [2, 10],
        }
    )
    df2 = df2.set_index("date")

    rec = Rec(
        columns={
            "B": AbsTolCheck(tol=0.0001, sort="desc"),
        },
        align_date_col="date",
    )
    result = rec.run(df1, df2, raise_on_failure=False)

    assert not result.passed()
    assert len(result.failures()) == 1

    # Check that it is sorted
    failure = result.failures()[0]
    errors = failure.failed_rows["abs_error"].values
    assert errors[0] > errors[1]

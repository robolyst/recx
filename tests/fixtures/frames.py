import pandas as pd
import pytest


# Basic aligned baseline/candidate pair with a single differing column 'B'
@pytest.fixture
def diff_frames():
    baseline = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "A": [1, 2],
            "B": [3, 4],
        }
    ).set_index("date")
    candidate = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "A": [1, 2],
            "B": [3, 5],
        }
    ).set_index("date")
    return baseline, candidate


# Frames with a trailing date on candidate for alignment tests
@pytest.fixture
def dated_frames():
    baseline = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "value": [10, 11],
        }
    ).set_index("date")
    candidate = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "value": [10, 12, 13],
        }
    ).set_index("date")
    return baseline, candidate


# Frames designed for tolerance sorting tests
@pytest.fixture
def abs_tol_frames():
    baseline = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "B": [3.0, 4.0],
        }
    ).set_index("date")
    candidate = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "B": [2.0, 10.0],
        }
    ).set_index("date")
    return baseline, candidate


# Larger frames designed for tolerance sorting tests
@pytest.fixture
def abs_tol_frames_large():
    dates = pd.date_range(start="2024-01-01", periods=1000, freq="D")
    values = list(range(1000))
    baseline = pd.DataFrame(
        {
            "date": dates,
            "B": values,
        }
    ).set_index("date")
    candidate = pd.DataFrame(
        {
            "date": dates,
            "B": values[::-1],
        }
    ).set_index("date")
    return baseline, candidate


@pytest.fixture
def equal_nan_frames():
    baseline = pd.DataFrame({"A": [1.0, None]})
    candidate = pd.DataFrame({"A": [1.0, None]})
    return baseline, candidate


@pytest.fixture
def multi_index_frames():
    baseline = pd.DataFrame(
        {
            "vintage_date": ["2024-01-01", "2024-01-02"],
            "date": ["2024-01-01", "2024-01-02"],
            "series_id": [1, 2],
            "A": [1, 2],
            "B": [3, 4],
        }
    ).set_index(["vintage_date", "date", "series_id"])
    candidate = pd.DataFrame(
        {
            "vintage_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "series_id": [1, 2, 3],
            "A": [1, 2, 3],
            "B": [3, 4, 6],
        }
    ).set_index(["vintage_date", "date", "series_id"])
    return baseline, candidate

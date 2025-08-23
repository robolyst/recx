import pandas as pd

from recx.checks import index_check


def test_index_check_missing_and_extra():
    base = pd.DataFrame({"A": [1, 2], "B": [3, 4]}).set_index("A")
    cand = pd.DataFrame({"A": [2, 3], "B": [5, 6]}).set_index("A")
    missing = index_check(base, cand, "missing")
    extra = index_check(base, cand, "extra")
    assert not missing.passed
    assert not extra.passed

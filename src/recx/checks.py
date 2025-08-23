from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

from recx.results import CheckResult


def index_check(
    baseline: pd.DataFrame,
    candidate: pd.DataFrame,
    check: Literal["missing", "extra"],
) -> CheckResult:
    """
    Checks that there are no missing or extra indices.

    Parameters
    ----------
    baseline : pandas.DataFrame
        Baseline frame.

    candidate : pandas.DataFrame
        Candidate frame.

    check : {'missing', 'extra'}
        If *extra*, checks that candidate does not have extra indices.
        If *missing*, checks that candidate has all indices from baseline.

    Returns
    -------
    CheckResult
        Result whose ``failed_rows`` contains the rows with unmatched index values.
    """

    if check == "missing":
        missing_indices = baseline.index.difference(candidate.index)
        bad_rows = baseline.loc[missing_indices]
        total_rows = len(baseline)
        check_name = "missing_indices_check"
    elif check == "extra":
        extra_indices = candidate.index.difference(baseline.index)
        bad_rows = candidate.loc[extra_indices]
        total_rows = len(candidate)
        check_name = "extra_indices_check"
    else:
        raise ValueError("check must be either 'missing' or 'extra'")

    assert isinstance(bad_rows, pd.DataFrame)

    return CheckResult(
        failed_rows=bad_rows,
        check_name=check_name,
        total_rows=total_rows,
    )


class ColumnCheck(ABC):
    def __init__(self, regex: bool = False, **kwargs):
        self.check_name = self.__class__.__name__
        self.check_args = kwargs
        self.regex = regex

    @abstractmethod
    def check(self, baseline: pd.Series, candidate: pd.Series) -> pd.DataFrame:
        """
        Evaluate the check for a single column.

        Parameters
        ----------
        baseline : pandas.Series
            Baseline series.

        candidate : pandas.Series
            Candidate series (index-aligned with ``baseline``).

        Returns
        -------
        pandas.DataFrame
            Frame of failing rows (may include additional diagnostic columns)
            or an empty frame if the check passed entirely.
        """
        raise NotImplementedError

    def run(
        self,
        baseline: pd.DataFrame,
        candidate: pd.DataFrame,
        column: str,
    ) -> list[CheckResult]:
        """
        Execute the check for one (possibly regex) column pattern.

        Parameters
        ----------
        baseline : pandas.DataFrame
            Baseline frame containing the columns.

        candidate : pandas.DataFrame
            Candidate frame.

        column : str
            Exact column name or regex pattern (if ``regex``) selecting columns to test.

        Returns
        -------
        list[CheckResult]
            One result per concrete column matched.
        """

        if self.regex:
            baseline_cols = baseline.filter(regex=column).columns
            candidate_cols = candidate.filter(regex=column).columns
            columns = list(baseline_cols.intersection(candidate_cols))
        else:
            columns = [column]

        results: list[CheckResult] = []

        for col in columns:
            bcol = baseline[col]
            ccol = candidate[col]

            # Defensive: if a DataFrame slipped through, raise (mis-specified column)
            if not isinstance(bcol, pd.Series) or not isinstance(ccol, pd.Series):
                raise TypeError(
                    "Column selection did not return a Series; check column spec."
                )

            failed_rows = self.check(bcol, ccol)

            result = CheckResult(
                failed_rows=failed_rows,
                column=col,
                check_name=self.check_name,
                check_args=self.check_args,
                total_rows=len(baseline[col]),
            )

            results.append(result)

        return results


class EqualCheck(ColumnCheck):
    """
    Check that baseline and candidate values are exactly equal.

    NaNs (nulls) in the same position are treated as equal.
    """

    def check(self, baseline: pd.Series, candidate: pd.Series) -> pd.DataFrame:
        good_idx: pd.Series = baseline == candidate
        good_idx = good_idx | (baseline.isnull() & candidate.isnull())
        # Explicit frame build (avoid concat type ambiguity)
        bad = pd.DataFrame(
            {
                "baseline": baseline[~good_idx],
                "candidate": candidate[~good_idx],
            }
        )
        return bad


class AbsTolCheck(ColumnCheck):
    """
    Check absolute difference within tolerance.

    The absolute error ``abs(baseline - candidate)`` must be ``<= tol`` or the
    row is flagged. Matching nulls are ignored.

    Parameters
    ----------
    tol : float
        Maximum permitted absolute difference.

    sort : {'asc', 'desc'}, optional
        Sort order for failing rows by absolute error.

    regex : bool, default False
        Treat the provided column spec as a regex pattern.
    """

    def __init__(
        self,
        tol: float,
        sort: Literal["asc", "desc"] | None = None,
        regex: bool = False,
    ):
        super().__init__(regex=regex, tol=tol)
        self.tol = tol
        self.sort = sort

    def check(self, baseline: pd.Series, candidate: pd.Series) -> pd.DataFrame:
        error: pd.Series = (baseline - candidate).abs()

        good_idx = (
            # Within tolerance
            (error <= self.tol)
            # Nulls are equal
            | (baseline.isnull() & candidate.isnull())
        )

        bad = pd.DataFrame(
            {
                "baseline": baseline[~good_idx],
                "candidate": candidate[~good_idx],
                "abs_error": error[~good_idx],
            }
        )

        if self.sort is not None:
            if self.sort == "asc":
                bad = bad.sort_values(by="abs_error", ascending=True)
            elif self.sort == "desc":
                bad = bad.sort_values(by="abs_error", ascending=False)
            else:
                raise ValueError("sort must be either 'asc' or 'desc'")

        return bad


class RelTolCheck(ColumnCheck):
    """
    Check relative difference within tolerance.

    Relative error is computed as ``abs(baseline - candidate) / |candidate|``.
    A small stabiliser ``1e-10`` is used to avoid division by zero.

    Parameters
    ----------
    tol : float
        Maximum permitted relative error.

    sort : {'asc', 'desc'}, optional
        Sort order for failing rows by relative error.

    regex : bool, default False
        Treat the provided column spec as a regex pattern.
    """

    def __init__(
        self,
        tol: float,
        sort: Literal["asc", "desc"] | None = None,
        regex: bool = False,
    ):
        super().__init__(regex=regex, tol=tol)
        self.tol = tol
        self.sort = sort

    def check(self, baseline: pd.Series, candidate: pd.Series) -> pd.DataFrame:
        error: pd.Series = (baseline - candidate).abs()
        error = error / candidate.abs().replace(0, 1e-10)

        good_idx = (
            # Within tolerance
            (error <= self.tol)
            # Nulls are equal
            | (baseline.isnull() & candidate.isnull())
        )

        bad = pd.DataFrame(
            {
                "baseline": baseline[~good_idx],
                "candidate": candidate[~good_idx],
                "rel_error": error[~good_idx],
            }
        )

        if self.sort is not None:
            if self.sort == "asc":
                bad = bad.sort_values(by="rel_error", ascending=True)
            elif self.sort == "desc":
                bad = bad.sort_values(by="rel_error", ascending=False)
            else:
                raise ValueError("sort must be either 'asc' or 'desc'")

        return bad

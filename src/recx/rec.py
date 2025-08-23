import logging

import pandas as pd

from recx.checks import ColumnCheck, EqualCheck, index_check
from recx.results import CheckResult, RecResult

logger = logging.getLogger(__name__)


def get_col(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Return an index level (as Index) or a column (as Series).
    """
    if col in df.index.names:
        return df.index.get_level_values(col).to_series()

    series_or_df = df[col]

    # would occur with duplicate column labels
    if isinstance(series_or_df, pd.DataFrame):
        raise TypeError(
            "Expected a single column Series, got a DataFrame (duplicate labels?)."
        )

    return series_or_df


def clip_to_last_common_date(
    a: pd.DataFrame,
    b: pd.DataFrame,
    date_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clip both frames to their last common date.

    Useful to safely align two versions of a dataset where one includes newer data that
    we do not expect to be in the other.

    Parameters
    ----------

    a : pandas.DataFrame
        First frame (order not important).

    b : pandas.DataFrame
        Second frame.

    date_col : str
        Column name (or index level) containing date/datetime values.

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame]
        ``(a_clipped, b_clipped)`` with only rows whose ``date_col`` value is
        less than or equal to the shared maximum date.
    """
    a_dates = get_col(a, date_col)
    b_dates = get_col(b, date_col)

    latest_date = min(a_dates.max(), b_dates.max())

    clip_a = a.loc[a_dates <= latest_date]
    clip_b = b.loc[b_dates <= latest_date]

    return clip_a, clip_b


class Rec:
    """
    Configure and run reconciliation between two DataFrames.

    Steps performed when :meth:`run` is invoked:

    1. Optionally clip both frames to their last common date (``align_date_col``).
    2. Collect index presence checks (extra indices on each side).
    3. Execute explicit per-column checks provided in ``columns``.
    4. Apply a ``default_check`` to any remaining columns not explicitly covered
       (unless ``default_check`` is ``None``).

    Parameters
    ----------
    columns : dict[str, ColumnCheck | None]
        Mapping of column names (or regex patterns if the associated check has
        ``regex=True``) to checks. A value of ``None`` skips that column.

    check_all : bool, default True
        All unspecified columns will be checked with :class:`EqualCheck` if True.

    align_date_col : str, optional
        Optional date/datetime column (or index level) name used to clip both
        frames to their last common date before comparison.
    """

    def __init__(
        self,
        columns: dict[str, ColumnCheck | None],
        check_all: bool = True,
        align_date_col: str | None = None,
    ):
        self.align_date_col = align_date_col
        self.columns = columns
        self.check_all = check_all

    def run(
        self,
        baseline: pd.DataFrame,
        candidate: pd.DataFrame,
        raise_on_failure: bool = False,
    ) -> RecResult:
        """
        Execute all configured checks.

        Parameters
        ----------
        baseline : pandas.DataFrame
            Baseline frame.

        candidate : pandas.DataFrame
            Candidate frame to reconcile against the baseline.

        raise_on_failure : bool, default False
            If ``True`` raise :class:`RecFailedException` when any check fails.

        Returns
        -------
        RecResult
            The full list of check results (passing + failing). When
            ``raise_on_failure`` is ``True`` and failures occur this method raises an
            exception.
        """
        # We're going to clip both DataFrames, so so we will work with a copy. Don't
        # copy here, just setup new references.
        _baseline = baseline
        _candidate = candidate

        if self.align_date_col is not None:
            _baseline, _candidate = clip_to_last_common_date(
                _baseline,
                _candidate,
                self.align_date_col,
            )

        results: list[CheckResult] = []

        results.append(index_check(_baseline, _candidate, "missing"))
        results.append(index_check(_baseline, _candidate, "extra"))

        # Make sure the indices match
        index = _baseline.index.intersection(_candidate.index)
        _baseline = _baseline.loc[index]
        _candidate = _candidate.loc[index]

        checked_columns: set[str] = set()

        for column, check in self.columns.items():
            # We might not want to check this column
            if check is None:
                checked_columns.add(column)
                continue

            new_results = check.run(_baseline, _candidate, column)

            for result in new_results:
                if result.column is not None:
                    checked_columns.add(result.column)

            results += new_results

        # Default checks
        if self.check_all:
            # Only check the columns we haven't provided checks for
            columns = [c for c in _baseline.columns if c not in checked_columns]

            for col in columns:
                results += EqualCheck().run(_baseline, _candidate, col)

        result = RecResult(
            results=results,
            baseline=baseline,  # Pass the original frames
            candidate=candidate,
        )

        if raise_on_failure:
            result.raise_for_failures()

        return result

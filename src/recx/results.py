import logging

import pandas as pd

from recx.exceptions import RecFailedException

logger = logging.getLogger(__name__)


class CheckResult:
    """
    Result of an individual column (or index) check.

    Parameters
    ----------

    failed_rows : pandas.DataFrame
        Subset of rows (and associated columns) that *failed* the check. A zero-length
        frame indicates success.

    check_name : str
        Name of the check (usually the class name of the checker).

    total_rows : int
        Total number of rows evaluated by the check (denominator for failure ratios).

    column : str, optional
        Column name the check was applied to (``None`` for index-wide checks).

    check_args : dict, optional
        Mapping of argument names to values used to parameterise the check.

    min_dots : int, default 5
        Minimum number of dots when formatting one-line summaries.
    """

    def __init__(
        self,
        failed_rows: pd.DataFrame,
        check_name: str,
        total_rows: int,
        column: str | None = None,
        check_args: dict | None = None,
        min_dots: int = 5,
        disp_rows: int = 10,
    ):
        self.failed_rows = failed_rows
        self.column = column
        self.check_name = check_name
        self.check_args = check_args or dict()
        self.min_dots = min_dots
        self.total_rows = total_rows
        self.disp_rows = disp_rows

    @property
    def passed(self) -> bool:
        return len(self.failed_rows) == 0

    def signature(self) -> str:
        if self.check_args:
            args = ", ".join(f"{k}={v}" for k, v in self.check_args.items())
            args = f"({args})"
        else:
            args = ""

        column_prefix = f"Column '{self.column}' with " if self.column else ""

        signature = f"{column_prefix}{self.check_name}{args}"
        return signature

    def mini_signature(self) -> str:
        if self.column:
            return f"Column '{self.column}'"
        else:
            return self.check_name

    def outcome(self) -> str:
        """
        Return formatted outcome string.

        ``"PASSED"`` if there are no failing rows, otherwise a summary of the form
        ``"[<count>/<total> (<pct>%)] FAILED"``.
        """
        if self.passed:
            return "PASSED ꪜ"

        count = len(self.failed_rows)
        total = self.total_rows
        pct = (count / total) if total > 0 else 0
        return f"[{count:,.0f}/{total:,.0f} ({pct:.2%})] FAILED ❌"

    def one_liner(self, width: int | None = None) -> str:
        """
        Return the result formatted as a single line.

        Parameters
        ----------
        width : int, optional
            Target total width. If provided the line is padded with dots; if the width
            is insufficient a ``ValueError`` is raised.

        Returns
        -------
        str
            One-line summary ``"<signature> ... <outcome>"``.

        Raises
        ------
        ValueError
            If ``width`` is smaller than the minimum space required.
        """
        signature = self.signature()
        outcome = self.outcome()
        min_dots = self.min_dots

        # Make allowance for two spaces
        min_width = len(signature) + len(outcome) + min_dots + 2

        if width is not None and width < min_width:
            raise ValueError(
                f"Width must be at least {min_width} characters, got {width}"
            )

        if width is not None:
            num_dots = max(self.min_dots, width - min_width + self.min_dots)
        else:
            num_dots = self.min_dots

        dots = "." * num_dots

        line = f"{signature} {dots} {outcome}"

        return line

    def log_one_liner(self, width: int):
        line = self.one_liner(width=width)
        logger.info(line)

    def failures_str(self) -> str:
        # These are the rows we want to display to the user.
        disp = str(self.failed_rows.tail(self.disp_rows))
        title = self.mini_signature()
        subtitle = f"Showing up to {self.disp_rows} rows"

        # First create the message without the title (wrapper)
        message = f"\n{subtitle}\n\n{str(disp)}\n\n"

        message = [line for line in message.splitlines()]
        message = "\n".join(f" │   {line}" for line in message)

        message = f"{title}:\n{message}\n"
        return message

    def log_failures(self):
        for line in self.failures_str().splitlines():
            logger.info(line)


class RecResult:
    """
    Represents the result of a diff between two DataFrames.

    Parameters
    ----------
    results : list[CheckResult]
        All individual check results (passing and failing) in execution order.
    """

    def __init__(
        self,
        results: list[CheckResult],
        baseline: pd.DataFrame,
        candidate: pd.DataFrame,
    ):
        self.results = results
        self.baseline = baseline
        self.candidate = candidate

    def __getitem__(self, i):
        return self.results[i]

    def __len__(self):
        return len(self.results)

    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    def failures(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed]

    def raise_for_failures(self):
        errors = self.failures()
        if errors:
            raise RecFailedException(
                f"DataFrame diff check failed with {len(errors)} errors."
            )

    def summary(self, log=False) -> None:
        """
        Print a summary.
        """
        if log:
            print_info = logger.info
            print_error = logger.error
        else:
            print_info = print
            print_error = print

        # Decide how many characters wide the report will be
        width = max(len(r.one_liner()) for r in self.results)

        print_info("─" * width)
        print_info("DataFrame Reconciliation Summary".center(width))
        print_info("─" * width)

        # Easier reference
        b = self.baseline
        c = self.candidate

        print_info(f"Baseline: rows={len(b):,} cols={len(b.columns):,}")
        print_info(f"Candidate: rows={len(c):,} cols={len(c.columns):,}")

        print_info("")

        failures = self.failures()
        if len(failures) > 0:
            print_error(f"{len(failures)} check(s) FAILED ❌")

        for result in self.results:
            print_info(result.one_liner(width=width))

        if len(failures) > 0:
            print_info("\nFailing rows:\n")

            for result in self.results:
                if not result.passed:
                    print_info(result.failures_str())

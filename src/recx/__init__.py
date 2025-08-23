"""
Recx - DataFrame reconciliation utilities.

This package provides functionality to reconcile a *candidate* ``pandas.DataFrame``
against a *baseline* frame using a set of column-wise checks.
"""

from .checks import AbsTolCheck, ColumnCheck, EqualCheck, RelTolCheck
from .exceptions import RecFailedException
from .rec import Rec
from .results import CheckResult, RecResult

__all__ = [
    "AbsTolCheck",
    "CheckResult",
    "ColumnCheck",
    "Rec",
    "RecFailedException",
    "RecResult",
    "EqualCheck",
    "RelTolCheck",
]

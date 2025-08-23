"""Pytest configuration and fixture exposure."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent
_FIXTURES = _ROOT / "fixtures"
if str(_FIXTURES) not in sys.path:
    sys.path.insert(0, str(_FIXTURES))

from frames import *  # type: ignore  # noqa: F401,F403

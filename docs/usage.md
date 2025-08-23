---
title: Usage
---

# Usage

## Regex Column Selection

```python
from recx import Rec, AbsTolCheck

rec = Rec(columns={r"^metric_": AbsTolCheck(tol=0.01, regex=True)}, check_all=False)
```

## Relative Tolerance

```python
from recx import RelTolCheck

RelTolCheck(tol=0.05)
```

## Custom Check

```python
from recx.checks import ColumnCheck
import pandas as pd

class NonNegativeCheck(ColumnCheck):
    def check(self, baseline: pd.Series, candidate: pd.Series):
        mask = (candidate < 0) | (baseline < 0)
        return pd.DataFrame({
            "baseline": baseline[mask],
            "candidate": candidate[mask],
        })
```

Register it in `Rec(columns={"col": NonNegativeCheck()})`.

## Date Alignment

Set `align_date_col="date_col"` to clip both DataFrames to their last common date.

## Skipping Columns

Assign `None` to a column key or set `check_all=False` to ignore unspecified columns.

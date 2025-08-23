---
title: Usage
---

# Usage

## Regex Column Selection

If you have a DataFrame with many similar fields with similar names, you can select by
a regex.

```python
import pandas as pd
from recx import Rec, AbsTolCheck

df = pd.DataFrame({
    "metric_1": [0.1, 0.2, 0.3],
    "metric_2": [0.1, 0.2, 0.3],
    "metric_3": [0.1, 0.2, 0.3],
})

df2 = df.copy()
df2.loc[2, "metric_3"] = 0.6

rec = Rec({
    r"^metric_": AbsTolCheck(tol=0.01, regex=True),
})

rec.run(df, df2).summary()
```

## Build in checks

### Equal

```python
from recx import EqualCheck

EqualCheck()
```

Use for a simple equality check.

### Absolute Tolerance

```python
from recx import AbsTolCheck

AbsTolCheck(tol=0.05)
```

This will fail when `|baseline - candidate| > tol`.

### Relative Tolerance

```python
from recx import RelTolCheck

RelTolCheck(tol=0.05)
```

This will fail when `|baseline - candidate| / |candidate| > tol`.

## Custom Check

```python
from recx.checks import ColumnCheck
import pandas as pd
import numpy as np

class SignCheck(ColumnCheck):
    def check(self, baseline: pd.Series, candidate: pd.Series):
        mask = np.sign(baseline) != np.sign(candidate)

        # Return a DataFrame of the bad rows. You can any
        # diagnostic columns you like.
        return pd.DataFrame({
            "baseline": baseline[mask],
            "candidate": candidate[mask],
        })

rec = Rec({
    "col": SignCheck(),
})
```

## Date Alignment

A common task is comparing a time based dataset once it has been updated. In this
situation, the new version (the candidate) many have extra rows with dates (or
timestamps) ahead of the old version (the baseline).

You can use `align_date_col="date_col"` on the `Rec` class to skip these new dates.

```python
rec = Rec(
    columns={...},
    align_date_col="date"  # Name of the date column
)
```

## Skipping Columns

Assign `None` to a column key:
```python
rec = Rec(
    columns={
        "not_important": None,
    },
)
```

 or set `check_all=False` to ignore all unspecified columns:
```python
rec = Rec(
    check_all=False,
)
```

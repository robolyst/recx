---
title: Getting Started
---

# Getting Started

This guide walks you through the minimal steps to reconcile two DataFrames.

## 1. Install

```bash
pip install recx
```

## 2. Prepare DataFrames

Ensure both DataFrames share the same index (or a comparable index) for meaningful checks.

```python
import pandas as pd

baseline = pd.DataFrame({"id": [1,2], "price": [10.0, 11.0], "status": ["OK", "OK"]}).set_index("id")
candidate = pd.DataFrame({"id": [1,2], "price": [10.01, 12.0], "status": ["OK", "BAD"]}).set_index("id")
```

## 3. Define a Rec

```python
from recx import Rec, EqualCheck, AbsTolCheck

rec = Rec(columns={
    "price": AbsTolCheck(tol=0.05),
    "status": EqualCheck(),
})
```

## 4. Run & Summarise

```python
result = rec.run(baseline, candidate)
result.summary()
```

If differences exceed tolerance or equality fails, a formatted failure report is shown.

## 5. Interpreting Results

- `result.passed()` returns `True` if all checks passed.
- Each detail is a `CheckResult` with `failed_rows` DataFrame.
- `result.raise_for_failures()` will raise an error if any check failed.

## Next

Move on to [Usage](usage.md) for advanced patterns.

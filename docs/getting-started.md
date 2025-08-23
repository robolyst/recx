---
title: Getting Started
---

# Getting Started

This guide walks you through the minimal steps to reconcile two DataFrames.

## 1. Install

With `pip`:

```bash
pip install recx
```

with `uv`:
```bash
uv add recx
```

## 2. Prepare DataFrames

Ensure both DataFrames share the same index (or a comparable index) for meaningful
checks.

```python
import pandas as pd

baseline = pd.DataFrame({
    "id": [1,2],
    "price": [10.0, 11.0],
    "status": ["OK", "OK"],
}).set_index("id")

candidate = pd.DataFrame({
    "id": [1,2],
    "price": [10.01, 12.0],
    "status": ["OK", "BAD"],
}).set_index("id")
```

## 3. Define a Rec

Declare how you want each column to be checked.

```python
from recx import Rec, EqualCheck, AbsTolCheck

rec = Rec({
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
In this case, you'll get the following:
```plain
───────────────────────────────────────────────────────────────────────
                    DataFrame Reconciliation Summary                   
───────────────────────────────────────────────────────────────────────
Baseline: rows=2 cols=2
Candidate: rows=2 cols=2

2 check(s) FAILED ❌
missing_indices_check ........................................ PASSED ꪜ
extra_indices_check .......................................... PASSED ꪜ
Column 'price' with AbsTolCheck(tol=0.05) ..... [1/2 (50.00%)] FAILED ❌
Column 'status' with EqualCheck ............... [1/2 (50.00%)] FAILED ❌

Failing rows:

Column 'price':
 │   
 │   Showing up to 10 rows
 │   
 │       baseline  candidate  abs_error
 │   id                                
 │   2       11.0       12.0        1.0
 │   

Column 'status':
 │   
 │   Showing up to 10 rows
 │   
 │      baseline candidate
 │   id                   
 │   2        OK       BAD
 │   
```

## 5. Interpreting Results

- `result.passed()` returns `True` if all checks passed.
- `result.failures()` is a list of `CheckResult`s each with a `DataFrame` attribute `failed_rows`.
- `result.raise_for_failures()` will raise an error if any check failed.

## Next

Move on to [Usage](usage.md) for advanced patterns.

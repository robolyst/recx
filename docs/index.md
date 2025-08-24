---
title: recx
---

<img src="assets/logo.svg" width="400">


Lightweight reconciliation tests for DataFrames

[![CI Build](https://img.shields.io/github/actions/workflow/status/robolyst/recx/ci.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/robolyst/recx/actions/workflows/ci.yml?query=branch%3Amain)
[![PyPI version](https://img.shields.io/pypi/v/recx.svg?style=for-the-badge)](https://pypi.org/project/recx/)
[![PyPI license](https://img.shields.io/pypi/l/recx.svg?style=for-the-badge)](https://pypi.python.org/pypi/)
[![Project Status: Active](https://img.shields.io/badge/repo%20status-Active-Green?style=for-the-badge)](https://www.repostatus.org/#active)

Use `Rec` to compare two DataFrames (baseline vs candidate) with per-column checks (equality, absolute / relative tolerance, regex-driven selection) and clear summaries of failures.

## Features

- Declarative column mapping
- Built-in checks: equality, absolute tolerance, relative tolerance
- Index integrity checks (missing / extra index values)
- Regex column selection (`regex=True` on checks)
- Compact textual summary
- Extensible: implement custom checks by subclassing `ColumnCheck`

## Quick Example

```python
import pandas as pd
from recx import Rec, EqualCheck, AbsTolCheck

baseline = pd.DataFrame({
    "price": [100.00, 200.00, 300.00],
    "status": ["active", "inactive", "active"]
})

candidate = pd.DataFrame({
    "price": [100.00, 200.00, 301.00],
    "status": ["active", "inactive", "active"]
})

rec = Rec(columns={
    "price": AbsTolCheck(tol=0.01),
    "status": EqualCheck(),
})

result = rec.run(baseline, candidate)
result.summary()
```

## Next Steps

* Read the [Getting Started](getting-started.md) guide.
* Browse the [Usage](usage.md) examples.
* Dive into the [API Reference](api.md).

---

Feel free to open issues or PRs with suggestions or improvements.


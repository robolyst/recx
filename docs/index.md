---
title: recx
hide:
  - navigation
---

# recx

Lightweight, declarative reconciliation tests for pandas DataFrames.

Use `Rec` to compare two DataFrames (baseline vs candidate) with per-column checks (equality, absolute / relative tolerance, regex-driven selection) and clear summaries of failures.

## Key Features

- Declarative column mapping (explicit or `check_all=True`)
- Built-in checks: equality, absolute tolerance, relative tolerance
- Index integrity checks (missing / extra index values)
- Regex column selection (`regex=True` on checks)
- Compact textual summary with truncated failing rows
- Extensible: implement custom checks by subclassing `ColumnCheck`

## Quick Example

```python
from recx import Rec, EqualCheck, AbsTolCheck

rec = Rec(columns={
    "price": AbsTolCheck(tol=0.01),
    "status": EqualCheck(),
})

result = rec.run(baseline_df, candidate_df)
result.summary()
```

## Next Steps

* Read the [Getting Started](getting-started.md) guide.
* Browse the [Usage](usage.md) examples.
* Dive into the [API Reference](api.md).

## Installation

```bash
pip install recx
```

## License

MIT © Adrian Letchford

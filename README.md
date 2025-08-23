<br>
<div align="center"><a href="https://www.union.ai/pandera"><img src="docs/logo.svg" width="400"></a></div>

<h1 align="center">
  Lightweight reconciliation tests for DataFrames
</h1>

`recx` helps you compare a *candidate* `pandas.DataFrame` against a *baseline* using
declarative, column-level checks (exact equality, absolute tolerance, relative
tolerance, or custom logic). It produces structured results you can assert on in
tests or render as a concise textual summary.

> Status: Early, experimental. API may change.


## Installation

```bash
pip install recx
```

## Features

* Index presence checks (missing + extra index values) out of the box
* Built-in column checks:
	* `EqualCheck` -- exact equality (treats aligned NaNs as equal)
	* `AbsTolCheck` -- absolute error within tolerance (optional sort of failures)
	* `RelTolCheck` -- relative error within tolerance (optional sort of failures)
* Rich per-check results (`CheckResult`) and aggregate (`RecResult`).
* Easy to extend: implement a single `check` method on a `ColumnCheck` subclass

---

Feel free to open issues or PRs with suggestions or improvements.


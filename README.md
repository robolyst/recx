<br>

<div align="center">
    <a href="https://github.com/robolyst/recx">
        <img src="https://github.com/robolyst/recx/raw/main/docs/assets/logo.svg" width="400">
     </a>
</div>

<br>

<h1 align="center">
  Lightweight reconciliation tests for DataFrames
</h1>

[![CI Build](https://img.shields.io/github/actions/workflow/status/robolyst/recx/ci.yml?branch=main&label=tests&style=for-the-badge)](https://github.com/robolyst/recx/actions/workflows/ci.yml?query=branch%3Amain)
[![PyPI version](https://img.shields.io/pypi/v/recx.svg?style=for-the-badge)](https://pypi.org/project/recx/)
[![PyPI license](https://img.shields.io/pypi/l/recx.svg?style=for-the-badge)](https://pypi.python.org/pypi/)
[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://img.shields.io/badge/repo%20status-Concept-lightgrey?style=for-the-badge)](https://www.repostatus.org/#concept)

`recx` compares a *candidate* `pandas.DataFrame` against a *baseline* using declarative,
column-level checks (exact equality, absolute tolerance, relative tolerance, or custom
logic). It produces structured results you can assert on in tests or render as a concise
textual summary.

> Status: Early, experimental. API may change.

## Install

With `pip`:

```bash
pip install recx
```

with `uv`:
```bash
uv add recx
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


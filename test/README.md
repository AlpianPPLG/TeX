# `test/` — Engine Test Suite

`pytest`-based unit and integration tests for the TeX Python engine.

## What is covered

| File | Target | Focus |
|------|--------|-------|
| `test_sample_data.py` | `engine/sample_data.py` | Deterministic fixture generation, module/check coverage, pass-ratio tuning. |
| `test_scorer.py` | `engine/scorer.py` | SPI math, category scoring, severity grouping, weight handling, MANUAL exclusion. |
| `test_validator.py` | `engine/validator.py` | Draft-07 schema validation (raw audit + summary), error paths. |
| `test_html_report_builder.py` | `engine/html_report_builder.py` | HTML/Markdown rendering, HTML escaping, SPI bands, file output. |
| `test_report_builder.py` | `engine/report_builder.py` | LaTeX escaping & template rendering (no `pdflatex` required). |
| `test_data_fixtures.py` | `data/` | Committed sample fixtures validate against schemas and stay in sync with the scorer. |

`conftest.py` provides shared fixtures (rule set, generated raw audit, scorer,
scored summary, and a small hand-authored audit).

## Running

```bash
pip install pytest
python -m pytest                 # run everything
python -m pytest test/test_scorer.py -v
```

Configuration lives in [`pytest.ini`](../pytest.ini) at the repo root
(`testpaths = test`, `pythonpath = engine`).

> **Windows:** run with `PYTHONUTF8=1` if any tooling prints the engine's ✓/✗
> status glyphs.

The suite invokes **no external toolchains** (`pdflatex`, network, etc.) and
runs in well under a second.

# `reports/` — Generated Compliance Reports

This directory is the output target for TeX's report builders. A scored
[`data/audit_summary.json`](../data/audit_summary.json) is rendered into
human-readable compliance reports here.

## Report formats

| Format | Builder | Toolchain | Notes |
|--------|---------|-----------|-------|
| **HTML** | [`engine/html_report_builder.py`](../engine/html_report_builder.py) | Pure Python | Self-contained, zero-dependency, no network. **Default & portable.** |
| **Markdown** | [`engine/html_report_builder.py`](../engine/html_report_builder.py) | Pure Python | Great for PRs and terminals. |
| **PDF** | [`engine/report_builder.py`](../engine/report_builder.py) | `pdflatex` (TeX Live) | Print-ready; requires a LaTeX toolchain. |

## Generating reports

```bash
# HTML + Markdown (no LaTeX needed)
python engine/html_report_builder.py
# or as part of the full pipeline:
python engine/main.py --score --html-report

# PDF (requires pdflatex on PATH)
python engine/main.py --score --report
```

Reports are written as `report_<hostname>.html` / `report_<hostname>.md`
(and `audit_report.pdf` for the LaTeX builder).

## Committed sample

`report_prod-web-01.{html,md}` are committed as a representative sample rendered
from the demo data in `data/`. Open the HTML file in any browser to preview the
report layout — no build step required.

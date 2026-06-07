# `data/` — Runtime Audit Data

This directory holds the JSON artifacts that flow through the TeX pipeline:

```
agent/audit.sh  ──▶  raw_audit.json  ──▶  engine (scorer)  ──▶  audit_summary.json  ──▶  dashboard / reports
```

| File | Producer | Consumer | Description |
|------|----------|----------|-------------|
| `raw_audit.json` | `agent/audit.sh` (shell probes) | `engine/scorer.py` | Unscored output of every audit probe, grouped by module. |
| `audit_summary.json` | `engine/main.py --score` | `dashboard/`, `engine/report_builder.py` | Scored summary: SPI, per-category scores, findings grouped by severity. |

## Sample / demo data

The files committed here are **deterministic sample fixtures** so the dashboard,
reports, and test suite have realistic data to render without needing a live
Linux host. They are generated from the CIS rule set in
[`rules/cis_linux_v3.json`](../rules/cis_linux_v3.json).

### Regenerating

```bash
# 1. Build a fresh raw_audit.json from the rule definitions
python engine/sample_data.py                 # writes data/raw_audit.json

# 2. Score it into audit_summary.json
python engine/main.py --score                # writes data/audit_summary.json
```

`engine/sample_data.py` is fully deterministic (seeded by each control's
`cis_id`), so repeated runs produce byte-identical output. Tune the PASS/FAIL
mix with `--pass-ratio` (default `0.6`).

> On Windows, set `PYTHONUTF8=1` so the engine can print its ✓ status glyphs.

## Schemas

Both files are validated against JSON Schema Draft-07 definitions in
[`engine/validator.py`](../engine/validator.py). See
[`TEX-DOCS/API_SPECIFICATION.md`](../TEX-DOCS/API_SPECIFICATION.md) for the full
data contracts.

## Production note

In a production deployment these files are **runtime artifacts** and are
typically git-ignored. They are committed here only as representative demo data.

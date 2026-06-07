"""
Integration-style checks over the committed sample fixtures in `data/`.

These guard against the demo data drifting out of sync with the schemas and the
scoring engine (e.g. someone edits raw_audit.json by hand and forgets to
re-score).
"""

import json

import pytest

from validator import SchemaValidator


@pytest.fixture(scope="module")
def data_dir(repo_root):
    return repo_root / "data"


def test_raw_audit_fixture_exists_and_valid(data_dir):
    path = data_dir / "raw_audit.json"
    assert path.exists(), "data/raw_audit.json is missing"
    ok, error = SchemaValidator.validate_raw_audit(str(path))
    assert ok, error


def test_summary_fixture_exists_and_valid(data_dir):
    path = data_dir / "audit_summary.json"
    assert path.exists(), "data/audit_summary.json is missing"
    ok, error = SchemaValidator.validate_audit_summary(str(path))
    assert ok, error


def test_committed_summary_matches_rescored_raw(data_dir, scorer):
    """Re-scoring the committed raw audit must reproduce the committed summary."""
    raw = json.loads((data_dir / "raw_audit.json").read_text(encoding="utf-8"))
    committed = json.loads((data_dir / "audit_summary.json").read_text(encoding="utf-8"))

    rescored = scorer.generate_summary(raw)

    assert rescored["spi"] == committed["spi"]
    assert rescored["category_scores"] == committed["category_scores"]
    assert {k: len(v) for k, v in rescored["findings_by_severity"].items()} == {
        k: len(v) for k, v in committed["findings_by_severity"].items()
    }


def test_summary_severity_counts_consistent(data_dir):
    summary = json.loads((data_dir / "audit_summary.json").read_text(encoding="utf-8"))
    by_sev = summary["findings_by_severity"]
    grouped_total = sum(len(v) for v in by_sev.values())
    assert grouped_total == len(summary["all_checks"])

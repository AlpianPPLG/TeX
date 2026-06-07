"""Tests for the JSON schema validator (engine/validator.py)."""

import json

from validator import SchemaValidator


def test_validate_raw_audit_accepts_generated(tmp_path, raw_audit):
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(raw_audit), encoding="utf-8")
    ok, error = SchemaValidator.validate_raw_audit(str(path))
    assert ok, error


def test_validate_raw_audit_rejects_missing_modules(tmp_path):
    path = tmp_path / "raw.json"
    path.write_text(json.dumps({"audit_metadata": {"timestamp": 1, "hostname": "h"}}), encoding="utf-8")
    ok, error = SchemaValidator.validate_raw_audit(str(path))
    assert not ok
    assert "modules" in error


def test_validate_raw_audit_missing_file():
    ok, error = SchemaValidator.validate_raw_audit("does/not/exist.json")
    assert not ok
    assert "not found" in error.lower()


def test_validate_raw_audit_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    ok, error = SchemaValidator.validate_raw_audit(str(path))
    assert not ok
    assert "invalid json" in error.lower()


def test_validate_summary_accepts_generated(tmp_path, summary):
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(summary), encoding="utf-8")
    ok, error = SchemaValidator.validate_audit_summary(str(path))
    assert ok, error


def test_validate_summary_rejects_out_of_range_spi(tmp_path, summary):
    bad = dict(summary)
    bad["spi"] = 150
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    ok, error = SchemaValidator.validate_audit_summary(str(path))
    assert not ok
    assert "spi" in error.lower()


def test_validate_summary_rejects_missing_required(tmp_path):
    path = tmp_path / "summary.json"
    path.write_text(json.dumps({"hostname": "h"}), encoding="utf-8")
    ok, error = SchemaValidator.validate_audit_summary(str(path))
    assert not ok

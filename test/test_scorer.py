"""Tests for the CIS scoring engine (engine/scorer.py)."""

import pytest

from scorer import Scorer, SEVERITY_WEIGHTS


def test_map_findings_flattens_all_checks(scorer, raw_audit):
    findings = scorer.map_findings(raw_audit)
    total = sum(len(m["checks"]) for m in raw_audit["modules"].values())
    assert len(findings) == total


def test_findings_have_weight_and_base_severity(scorer, raw_audit):
    findings = scorer.map_findings(raw_audit)
    for f in findings:
        assert "weight" in f
        assert "base_severity" in f
        assert f["weight"] == SEVERITY_WEIGHTS[f["base_severity"]]


def test_passing_finding_severity_is_pass_but_keeps_weight(scorer, minimal_raw_audit):
    findings = scorer.map_findings(minimal_raw_audit)
    passed = next(f for f in findings if f["status"] == "PASS")
    assert passed["severity"] == "PASS"            # display severity
    assert passed["base_severity"] == "MEDIUM"     # inherent severity preserved
    assert passed["weight"] == SEVERITY_WEIGHTS["MEDIUM"]


def test_spi_credits_passing_controls(scorer, minimal_raw_audit):
    findings = scorer.map_findings(minimal_raw_audit)
    spi = scorer.calculate_spi(findings)
    # One CRITICAL (10.0) fails, one MEDIUM (5.0) passes -> 100 * 5/15 = 33.3
    assert spi == pytest.approx(33.3, abs=0.1)


def test_spi_all_pass_is_100(scorer):
    findings = [
        {"status": "PASS", "base_severity": "CRITICAL", "weight": 10.0, "module": "ssh"},
        {"status": "PASS", "base_severity": "LOW", "weight": 2.5, "module": "ssh"},
    ]
    assert scorer.calculate_spi(findings) == 100.0


def test_spi_all_fail_is_0(scorer):
    findings = [
        {"status": "FAIL", "base_severity": "CRITICAL", "weight": 10.0, "module": "ssh"},
        {"status": "FAIL", "base_severity": "HIGH", "weight": 7.5, "module": "ssh"},
    ]
    assert scorer.calculate_spi(findings) == 0.0


def test_spi_empty_findings_is_100(scorer):
    assert scorer.calculate_spi([]) == 100.0


def test_spi_within_bounds(scorer, summary):
    assert 0.0 <= summary["spi"] <= 100.0


def test_manual_controls_excluded_from_score(scorer):
    findings = [
        {"status": "PASS", "base_severity": "HIGH", "weight": 7.5, "module": "ssh"},
        {"status": "MANUAL", "base_severity": "HIGH", "weight": 7.5, "module": "ssh"},
    ]
    # MANUAL ignored -> the single PASS yields 100
    assert scorer.calculate_spi(findings) == 100.0


def test_category_scores_present_for_each_module(scorer, raw_audit):
    findings = scorer.map_findings(raw_audit)
    scores = scorer.calculate_category_scores(findings)
    modules = {f["module"] for f in findings}
    assert set(scores.keys()) == modules
    for value in scores.values():
        assert 0.0 <= value <= 100.0


def test_group_findings_by_severity_keys(scorer, raw_audit):
    findings = scorer.map_findings(raw_audit)
    grouped = scorer.group_findings_by_severity(findings)
    assert set(grouped.keys()) == {"CRITICAL", "HIGH", "MEDIUM", "LOW", "PASS"}
    regrouped_total = sum(len(v) for v in grouped.values())
    assert regrouped_total == len(findings)


def test_generate_summary_shape(scorer, raw_audit):
    summary = scorer.generate_summary(raw_audit)
    for key in (
        "generated_at",
        "hostname",
        "spi",
        "category_scores",
        "findings_by_severity",
        "all_checks",
    ):
        assert key in summary
    assert summary["hostname"] == raw_audit["audit_metadata"]["hostname"]


def test_resolve_base_severity_prefers_check_then_control(scorer):
    assert scorer.resolve_base_severity({"severity": "HIGH"}) == "HIGH"
    assert scorer.resolve_base_severity({"severity": "PASS"}, {"severity": "LOW"}) == "LOW"
    assert scorer.resolve_base_severity({}, None) == "MEDIUM"

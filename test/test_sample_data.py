"""Tests for the deterministic sample-data generator (engine/sample_data.py)."""

import sample_data


def test_generate_raw_audit_has_all_modules(raw_audit, rules):
    sections = {r.get("section") for r in rules}
    assert set(raw_audit["modules"].keys()) == sections


def test_generate_raw_audit_check_count_matches_rules(raw_audit, rules):
    total_checks = sum(len(m["checks"]) for m in raw_audit["modules"].values())
    assert total_checks == len(rules)


def test_generate_raw_audit_is_deterministic(rules):
    first = sample_data.generate_raw_audit(rules, pass_ratio=0.6)
    second = sample_data.generate_raw_audit(rules, pass_ratio=0.6)
    assert first == second


def test_metadata_is_well_formed(raw_audit):
    meta = raw_audit["audit_metadata"]
    assert isinstance(meta["timestamp"], int)
    assert meta["hostname"]
    assert meta["tex_version"] == "1.0.0"


def test_checks_have_required_fields(raw_audit):
    for module in raw_audit["modules"].values():
        for check in module["checks"]:
            for field in ("cis_id", "title", "status", "severity"):
                assert field in check
            assert check["status"] in ("PASS", "FAIL", "MANUAL")


def test_passing_checks_retain_inherent_severity(raw_audit):
    # Passing checks must keep their real severity (not "PASS") so the scorer
    # can credit their weight.
    for module in raw_audit["modules"].values():
        for check in module["checks"]:
            assert check["severity"] != "PASS"


def test_pass_ratio_tuning_changes_outcome(rules):
    low = sample_data.generate_raw_audit(rules, pass_ratio=0.1)
    high = sample_data.generate_raw_audit(rules, pass_ratio=0.95)

    def count_pass(audit):
        return sum(
            1
            for m in audit["modules"].values()
            for c in m["checks"]
            if c["status"] == "PASS"
        )

    assert count_pass(high) > count_pass(low)


def test_deterministic_unit_in_range():
    for seed in ("5.2.1", "x", "1.1.1.1", "abc"):
        value = sample_data._deterministic_unit(seed)
        assert 0.0 <= value < 1.0

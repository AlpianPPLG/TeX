"""
Shared pytest fixtures for the TeX engine test suite.

The engine modules (`scorer`, `validator`, `report_builder`,
`html_report_builder`, `sample_data`) import each other by bare module name, so
`engine/` is added to `sys.path` via `pythonpath = engine` in `pytest.ini`.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "engine"
RULES_FILE = REPO_ROOT / "rules" / "cis_linux_v3.json"

# Ensure engine modules are importable even when tests are run directly.
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def rules_file() -> Path:
    assert RULES_FILE.exists(), f"Rules file missing: {RULES_FILE}"
    return RULES_FILE


@pytest.fixture(scope="session")
def rules(rules_file: Path):
    with open(rules_file, "r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def raw_audit(rules):
    """A deterministic raw audit payload generated from the rule set."""
    import sample_data

    return sample_data.generate_raw_audit(rules, pass_ratio=0.6)


@pytest.fixture(scope="session")
def scorer(rules_file: Path):
    from scorer import Scorer

    return Scorer(str(rules_file))


@pytest.fixture(scope="session")
def summary(scorer, raw_audit):
    """A scored summary produced from the generated raw audit."""
    return scorer.generate_summary(raw_audit)


@pytest.fixture()
def minimal_raw_audit():
    """A tiny, hand-authored raw audit with a known pass/fail mix."""
    return {
        "audit_metadata": {
            "timestamp": 1749268800,
            "hostname": "test-host",
            "os_name": "Test OS",
            "kernel_version": "0.0.0",
            "audit_user": "tester",
            "tex_version": "1.0.0",
        },
        "modules": {
            "ssh": {
                "module": "ssh",
                "status": "COMPLETED",
                "checks": [
                    {
                        "cis_id": "5.2.8",
                        "title": "Ensure SSH PermitRootLogin is disabled",
                        "status": "FAIL",
                        "actual_value": "(parameter not set)",
                        "expected_value": "^PermitRootLogin\\s+no$",
                        "severity": "CRITICAL",
                        "remediation": "Set PermitRootLogin no",
                    },
                    {
                        "cis_id": "5.2.4",
                        "title": "Ensure SSH MaxAuthTries is set to 4 or less",
                        "status": "PASS",
                        "actual_value": "MaxAuthTries 4",
                        "expected_value": "^MaxAuthTries\\s+[1-4]$",
                        "severity": "MEDIUM",
                        "remediation": "Set MaxAuthTries 4",
                    },
                ],
            }
        },
    }

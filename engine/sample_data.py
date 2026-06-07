#!/usr/bin/env python3
"""
TeX Security Compliance Auditor - Sample Data Generator
Builds a deterministic, realistic `raw_audit.json` fixture directly from the
CIS rule definitions in `rules/cis_linux_v3.json`.

The generator is fully deterministic (seeded by each control's `cis_id`) so the
produced fixture is stable across runs. This is used for:
  - local demos of the scoring pipeline,
  - seeding the web dashboard with representative data,
  - regression testing of the engine (see `test/`).

Usage:
  python engine/sample_data.py                       # write data/raw_audit.json
  python engine/sample_data.py --out data/raw.json   # custom output path
  python engine/sample_data.py --pass-ratio 0.7      # tune PASS/FAIL mix
"""

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List

# Synthetic host metadata used for the generated fixture.
SAMPLE_HOST = {
    "hostname": "prod-web-01.tex.internal",
    "os_name": "Ubuntu 22.04.4 LTS",
    "kernel_version": "5.15.0-105-generic",
    "audit_user": "tex-auditor",
    "tex_version": "1.0.0",
}

# Human-readable "observed" values for failing checks, keyed by rule section.
# These make the generated fixture read like a real audit instead of generic
# placeholders.
FAIL_HINTS = {
    "ssh": "(parameter not set)",
    "firewall": "Status: inactive",
    "pam": "no lockout policy configured",
    "sudoers": "NOPASSWD entry detected",
    "filesystem": "world-writable (0777)",
    "kernel": "0",
    "users": "1 account(s) with empty password",
    "services": "service enabled and listening",
}


def _deterministic_unit(seed: str) -> float:
    """Return a stable float in [0, 1) derived from an arbitrary string."""
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    # Use the first 8 hex chars as a 32-bit integer, normalize to [0, 1).
    return int(digest[:8], 16) / 0xFFFFFFFF


def load_rules(rules_path: Path) -> List[Dict]:
    with open(rules_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_check(rule: Dict, pass_ratio: float) -> Dict:
    """Turn a single CIS rule into a synthetic audit check result."""
    cis_id = rule.get("cis_id", "unknown")
    section = rule.get("section", "unknown")

    # Deterministic PASS/FAIL decision. CRITICAL controls fail a little more
    # often so the demo data surfaces high-impact findings.
    threshold = pass_ratio
    if rule.get("severity") == "CRITICAL":
        threshold -= 0.15
    elif rule.get("severity") == "LOW":
        threshold += 0.1

    passed = _deterministic_unit(cis_id) < threshold

    expected = rule.get("expected_pattern", rule.get("expected_value", ""))
    # Mirror the shell agent's behaviour: the inherent control severity is
    # always recorded on the check; the scorer downgrades it to "PASS" for
    # passing controls while still crediting their weight.
    severity = rule.get("severity", "MEDIUM")
    if passed:
        status = "PASS"
        actual_value = expected or "compliant"
    else:
        status = "FAIL"
        actual_value = FAIL_HINTS.get(section, "non-compliant value")

    return {
        "cis_id": cis_id,
        "title": rule.get("title", "Unknown control"),
        "status": status,
        "actual_value": actual_value,
        "expected_value": expected,
        "severity": severity,
        "remediation": rule.get("remediation", ""),
    }


def generate_raw_audit(rules: List[Dict], pass_ratio: float = 0.6) -> Dict:
    """Assemble a complete raw_audit.json payload from the rule set."""
    modules: Dict[str, Dict] = {}
    timestamp = 1749268800  # Fixed timestamp -> deterministic fixture.

    for rule in rules:
        section = rule.get("section", "unknown")
        module = modules.setdefault(
            section,
            {
                "module": section,
                "status": "COMPLETED",
                "timestamp": timestamp,
                "hostname": SAMPLE_HOST["hostname"],
                "checks": [],
            },
        )
        module["checks"].append(build_check(rule, pass_ratio))

    return {
        "audit_metadata": {
            "timestamp": timestamp,
            "hostname": SAMPLE_HOST["hostname"],
            "os_name": SAMPLE_HOST["os_name"],
            "kernel_version": SAMPLE_HOST["kernel_version"],
            "audit_user": SAMPLE_HOST["audit_user"],
            "tex_version": SAMPLE_HOST["tex_version"],
        },
        "modules": modules,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TeX sample audit data")
    parser.add_argument(
        "--rules",
        default="rules/cis_linux_v3.json",
        help="Path to CIS rule definitions",
    )
    parser.add_argument(
        "--out",
        default="data/raw_audit.json",
        help="Output path for the generated raw audit JSON",
    )
    parser.add_argument(
        "--pass-ratio",
        type=float,
        default=0.6,
        help="Target fraction of controls that PASS (0.0-1.0)",
    )
    args = parser.parse_args()

    rules_path = Path(args.rules)
    if not rules_path.exists():
        print(f"[ERROR] Rules file not found: {rules_path}")
        return 1

    rules = load_rules(rules_path)
    raw_audit = generate_raw_audit(rules, pass_ratio=args.pass_ratio)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(raw_audit, handle, indent=2)
        handle.write("\n")

    total = sum(len(m["checks"]) for m in raw_audit["modules"].values())
    print(f"[OK] Wrote {out_path} ({len(raw_audit['modules'])} modules, {total} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

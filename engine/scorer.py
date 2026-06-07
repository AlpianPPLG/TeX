#!/usr/bin/env python3
"""
TeX Security Compliance Auditor - CIS Benchmark Scoring Engine
Implements weighted risk scoring based on CVSS v3.1 adapted for configuration audits
Version: 1.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Severity weights per CIS control
SEVERITY_WEIGHTS = {
    "CRITICAL": 10.0,
    "HIGH": 7.5,
    "MEDIUM": 5.0,
    "LOW": 2.5,
    "PASS": 0.0,
}


class Scorer:
    """CIS Benchmark scoring engine"""
    
    def __init__(self, rules_path: str = "rules/cis_linux_v3.json"):
        """Initialize scorer with CIS rule definitions"""
        self.rules_path = Path(rules_path)
        self.rules: List[Dict] = []
        self.load_controls()
    
    def load_controls(self) -> None:
        """Load and validate CIS control definitions"""
        try:
            with open(self.rules_path, 'r') as f:
                self.rules = json.load(f)
            print(f"[INFO] Loaded {len(self.rules)} CIS control definitions", file=sys.stderr)
        except FileNotFoundError:
            print(f"[ERROR] Rules file not found: {self.rules_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in rules file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def load_raw_audit(self, audit_file: str) -> Dict:
        """Load raw audit JSON output"""
        try:
            with open(audit_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Audit file not found: {audit_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in audit file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def classify_severity(self, check: Dict, control: Optional[Dict] = None) -> str:
        """Classify finding severity"""
        if check.get("status") == "PASS":
            return "PASS"
        
        # Use severity from check, fallback to control definition
        severity = check.get("severity") or (control.get("severity") if control else "MEDIUM")
        
        if severity not in SEVERITY_WEIGHTS:
            return "MEDIUM"
        
        return severity

    def resolve_base_severity(self, check: Dict, control: Optional[Dict] = None) -> str:
        """
        Resolve the *inherent* severity of a control, independent of whether it
        passed or failed. Used to weight passing controls so they contribute to
        the overall posture score (a passing CRITICAL control is worth more than
        a passing LOW control).
        """
        candidate = check.get("severity")
        if candidate in SEVERITY_WEIGHTS and candidate != "PASS":
            return candidate

        if control and control.get("severity") in SEVERITY_WEIGHTS:
            return control["severity"]

        return "MEDIUM"

    def map_findings(self, raw_audit: Dict) -> List[Dict]:
        """Map raw audit checks to CIS controls with severity classification"""
        findings = []
        
        # Flatten all checks from all modules
        all_checks = []
        for module_name, module_data in raw_audit.get("modules", {}).items():
            if isinstance(module_data, dict) and "checks" in module_data:
                for check in module_data.get("checks", []):
                    check["module"] = module_name
                    all_checks.append(check)
        
        # Map each check to a CIS control
        for check in all_checks:
            cis_id = check.get("cis_id")
            
            # Find matching control definition
            control = next(
                (r for r in self.rules if r.get("cis_id") == cis_id),
                None
            )
            
            severity = self.classify_severity(check, control)
            base_severity = self.resolve_base_severity(check, control)

            finding = {
                "cis_id": cis_id,
                "module": check.get("module", "unknown"),
                "title": check.get("title", control.get("title", "Unknown") if control else "Unknown"),
                "status": check.get("status", "MANUAL"),
                "actual_value": check.get("actual_value", ""),
                "expected_value": check.get("expected_value", ""),
                "severity": severity,
                "base_severity": base_severity,
                "weight": SEVERITY_WEIGHTS.get(base_severity, 0.0),
                "remediation": check.get("remediation", control.get("remediation", "") if control else ""),
                "nist_800_53": control.get("nist_800_53", []) if control else [],
            }
            
            findings.append(finding)
        
        return findings
    
    def calculate_category_scores(self, findings: List[Dict]) -> Dict[str, float]:
        """Calculate per-domain scores for radar chart"""
        modules = set(f["module"] for f in findings)
        category_scores = {}
        
        for module in modules:
            module_findings = [f for f in findings if f["module"] == module]
            
            if not module_findings:
                category_scores[module] = 100.0
                continue
            
            category_scores[module] = self._weighted_score(module_findings)
        
        return category_scores

    @staticmethod
    def _finding_weight(finding: Dict) -> float:
        """Inherent weight of a control, regardless of pass/fail outcome."""
        if "weight" in finding:
            return float(finding["weight"])
        # Backwards-compatible fallback for findings without a base weight.
        return SEVERITY_WEIGHTS.get(finding.get("base_severity", finding.get("severity", "MEDIUM")), 0.0)

    @classmethod
    def _weighted_score(cls, findings: List[Dict]) -> float:
        """
        Compute a 0-100 posture score for a set of findings.

        score = 100 * (weight of PASSED controls / weight of all scored controls)

        MANUAL controls are excluded from both numerator and denominator since
        their outcome is undetermined. A set with no scorable controls yields
        100 (nothing to fail).
        """
        scorable = [f for f in findings if f.get("status") in ("PASS", "FAIL")]
        total_weight = sum(cls._finding_weight(f) for f in scorable)

        if total_weight == 0:
            return 100.0

        passed_weight = sum(
            cls._finding_weight(f) for f in scorable if f.get("status") == "PASS"
        )

        score = 100 * (passed_weight / total_weight)
        return round(max(0.0, min(100.0, score)), 1)

    def calculate_spi(self, findings: List[Dict]) -> float:
        """
        Calculate Security Posture Index (0-100).

        SPI = 100 * (sum(weight of passed controls) / sum(weight of all controls))

        Passing a high-severity control therefore contributes more to the score
        than passing a low-severity one, and a fleet of passing controls is
        rewarded rather than ignored.
        """
        if not findings:
            return 100.0

        return self._weighted_score(findings)
    
    def group_findings_by_severity(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """Group findings by severity level"""
        grouped = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
            "PASS": [],
        }
        
        for finding in findings:
            severity = finding.get("severity", "MEDIUM")
            if severity in grouped:
                grouped[severity].append(finding)
        
        return grouped
    
    def generate_summary(self, raw_audit: Dict) -> Dict:
        """Generate scored audit summary"""
        # Map findings to CIS controls
        findings = self.map_findings(raw_audit)
        
        # Calculate scores
        spi = self.calculate_spi(findings)
        category_scores = self.calculate_category_scores(findings)
        findings_by_severity = self.group_findings_by_severity(findings)
        
        # Get metadata
        metadata = raw_audit.get("audit_metadata", {})
        
        summary = {
            "generated_at": int(__import__('time').time()),
            "hostname": metadata.get("hostname", "unknown"),
            "spi": spi,
            "category_scores": category_scores,
            "findings_by_severity": findings_by_severity,
            "all_checks": findings,
            "audit_metadata": metadata,
        }
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TeX CIS Benchmark Scoring Engine"
    )
    parser.add_argument(
        "--audit",
        default="data/raw_audit.json",
        help="Path to raw audit JSON file"
    )
    parser.add_argument(
        "--rules",
        default="rules/cis_linux_v3.json",
        help="Path to CIS rules JSON file"
    )
    parser.add_argument(
        "--output",
        default="data/audit_summary.json",
        help="Path to output scored summary JSON"
    )
    parser.add_argument(
        "--spi-only",
        action="store_true",
        help="Print SPI value and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize scorer
    scorer = Scorer(args.rules)
    
    # Load and process audit
    raw_audit = scorer.load_raw_audit(args.audit)
    summary = scorer.generate_summary(raw_audit)
    
    # Output SPI only if requested
    if args.spi_only:
        print(f"{summary['spi']:.1f}")
        return
    
    # Write summary to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"[INFO] Summary saved to {output_path}", file=sys.stderr)
    print(f"[INFO] SPI: {summary['spi']:.1f}/100", file=sys.stderr)


if __name__ == "__main__":
    main()

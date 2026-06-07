#!/usr/bin/env python3
"""
TeX Security Compliance Auditor - Main CLI Orchestrator
Coordinates the full audit → score → report pipeline
Version: 1.0
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scorer import Scorer
from validator import SchemaValidator
from report_builder import ReportBuilder


class TexOrchestrator:
    """Orchestrates the complete TeX audit pipeline"""
    
    def __init__(self, audit_file: str = "data/raw_audit.json",
                 rules_file: str = "rules/cis_linux_v3.json",
                 summary_file: str = "data/audit_summary.json",
                 output_dir: str = "reports"):
        self.audit_file = audit_file
        self.rules_file = rules_file
        self.summary_file = summary_file
        self.output_dir = output_dir
        self.scorer = None
    
    def validate_audit(self) -> bool:
        """Validate raw audit JSON"""
        print("[*] Validating raw audit...")
        is_valid, error = SchemaValidator.validate_raw_audit(self.audit_file)
        
        if is_valid:
            print("[✓] Raw audit validation passed")
            return True
        else:
            print(f"[✗] Raw audit validation failed: {error}")
            return False
    
    def score_audit(self) -> bool:
        """Score the audit and generate summary"""
        print("[*] Scoring audit...")
        
        try:
            # Initialize scorer
            self.scorer = Scorer(self.rules_file)
            
            # Load and score
            raw_audit = self.scorer.load_raw_audit(self.audit_file)
            summary = self.scorer.generate_summary(raw_audit)
            
            # Save summary
            Path(self.summary_file).parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"[✓] Scoring complete - SPI: {summary['spi']:.1f}/100")
            return True
        
        except Exception as e:
            print(f"[✗] Scoring failed: {e}")
            return False
    
    def validate_summary(self) -> bool:
        """Validate scored summary"""
        print("[*] Validating audit summary...")
        is_valid, error = SchemaValidator.validate_audit_summary(self.summary_file)
        
        if is_valid:
            print("[✓] Summary validation passed")
            return True
        else:
            print(f"[✗] Summary validation failed: {error}")
            return False
    
    def generate_report(self) -> bool:
        """Generate PDF report"""
        print("[*] Generating PDF report...")
        
        builder = ReportBuilder()
        success = builder.generate_report(self.summary_file, self.output_dir)
        
        if success:
            print("[✓] PDF report generated")
            return True
        else:
            print("[✗] PDF report generation failed")
            return False
    
    def get_spi(self) -> float:
        """Get SPI value from summary"""
        try:
            import json
            with open(self.summary_file, 'r') as f:
                summary = json.load(f)
            return summary.get('spi', 0)
        except:
            return 0
    
    def run_full_pipeline(self, skip_report: bool = False) -> bool:
        """Run complete audit → score → report pipeline"""
        print("=" * 60)
        print("TeX Security Compliance Auditor")
        print("=" * 60)
        
        # Validate audit
        if not self.validate_audit():
            return False
        
        # Score audit
        if not self.score_audit():
            return False
        
        # Validate summary
        if not self.validate_summary():
            return False
        
        # Generate report (optional)
        if not skip_report and not self.generate_report():
            return False
        
        print("=" * 60)
        print("[✓] Audit pipeline completed successfully")
        print("=" * 60)
        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="TeX Security Compliance Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py --score --report
  python3 main.py --spi-only
  python3 main.py --score --audit custom_audit.json
        """
    )
    
    parser.add_argument(
        "--audit",
        default="data/raw_audit.json",
        help="Path to raw audit JSON (default: data/raw_audit.json)"
    )
    parser.add_argument(
        "--rules",
        default="rules/cis_linux_v3.json",
        help="Path to CIS rules JSON (default: rules/cis_linux_v3.json)"
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Run scoring pipeline"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate PDF report"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for PDF reports"
    )
    parser.add_argument(
        "--spi-only",
        action="store_true",
        help="Print SPI value to stdout and exit"
    )
    parser.add_argument(
        "--validate-audit",
        action="store_true",
        help="Validate raw audit JSON only"
    )
    parser.add_argument(
        "--validate-summary",
        action="store_true",
        help="Validate audit summary JSON only"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = TexOrchestrator(
        audit_file=args.audit,
        rules_file=args.rules,
        output_dir=args.output_dir
    )
    
    # Handle validation-only modes
    if args.validate_audit:
        success = orchestrator.validate_audit()
        sys.exit(0 if success else 1)
    
    if args.validate_summary:
        success = orchestrator.validate_summary()
        sys.exit(0 if success else 1)
    
    # Handle SPI-only mode
    if args.spi_only:
        if orchestrator.score_audit():
            spi = orchestrator.get_spi()
            print(f"{spi:.1f}")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Handle score + report pipeline
    if args.score or args.report:
        skip_report = not args.report
        success = orchestrator.run_full_pipeline(skip_report=skip_report)
        sys.exit(0 if success else 1)
    
    # Default: print help
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()

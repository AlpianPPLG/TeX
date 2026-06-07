#!/usr/bin/env python3
"""
TeX LaTeX PDF Report Builder
Compiles audit summary data into professional PDF compliance reports
Version: 1.0
"""

import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ReportBuilder:
    """LaTeX-based PDF report compiler"""
    
    # Complete LaTeX escape mapping
    LATEX_ESCAPE_MAP = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    def __init__(self, template_path: str = "engine/templates/report_template.tex"):
        """Initialize report builder"""
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            print(f"[WARNING] Template not found: {template_path}", file=sys.stderr)
    
    @staticmethod
    def escape_latex(value: str) -> str:
        """Escape all LaTeX special characters"""
        if not isinstance(value, str):
            value = str(value)
        
        for char, replacement in ReportBuilder.LATEX_ESCAPE_MAP.items():
            value = value.replace(char, replacement)
        
        return value
    
    def generate_findings_table(self, findings: list) -> str:
        """Generate LaTeX table rows for findings"""
        if not findings:
            return r"\textit{No findings}" + "\n"
        
        rows = []
        for finding in findings:
            cis_id = self.escape_latex(str(finding.get("cis_id", "")))
            title = self.escape_latex(str(finding.get("title", "")))
            severity = finding.get("severity", "UNKNOWN")
            remediation = self.escape_latex(str(finding.get("remediation", "")))
            
            # Color code by severity
            color = {
                "CRITICAL": r"\textcolor{red}",
                "HIGH": r"\textcolor{orange}",
                "MEDIUM": r"\textcolor{yellow}",
                "LOW": r"\textcolor{gray}",
            }.get(severity, r"\textcolor{gray}")
            
            row = (
                f"{cis_id} & {color}{{{severity}}} & {title} & "
                f"{remediation} \\\\\n"
            )
            rows.append(row)
        
        return "".join(rows)
    
    def generate_category_table(self, category_scores: dict) -> str:
        """Generate LaTeX table for category scores"""
        rows = []
        for category, score in sorted(category_scores.items()):
            category_name = category.upper()
            score_val = f"{score:.1f}"
            
            # Color code score
            if score >= 80:
                color = r"\textcolor{green}"
            elif score >= 60:
                color = r"\textcolor{orange}"
            else:
                color = r"\textcolor{red}"
            
            row = f"{category_name} & {color}{{{score_val}}} \\\\\n"
            rows.append(row)
        
        return "".join(rows)
    
    def render_template(self, summary: Dict, output_file: str) -> bool:
        """Render LaTeX template with audit data"""
        if not self.template_path.exists():
            print(f"[ERROR] Template not found", file=sys.stderr)
            return False
        
        try:
            with open(self.template_path, 'r') as f:
                template = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read template: {e}", file=sys.stderr)
            return False
        
        # Extract data for template variables
        hostname = self.escape_latex(summary.get("hostname", "unknown"))
        spi = summary.get("spi", 0)
        generated_at = datetime.now().strftime("%d %B %Y")
        
        findings_by_severity = summary.get("findings_by_severity", {})
        category_scores = summary.get("category_scores", {})
        
        critical_count = len(findings_by_severity.get("CRITICAL", []))
        high_count = len(findings_by_severity.get("HIGH", []))
        medium_count = len(findings_by_severity.get("MEDIUM", []))
        low_count = len(findings_by_severity.get("LOW", []))
        pass_count = len(findings_by_severity.get("PASS", []))
        
        # Generate table content
        category_table = self.generate_category_table(category_scores)
        findings_table = self.generate_findings_table(
            findings_by_severity.get("CRITICAL", []) +
            findings_by_severity.get("HIGH", []) +
            findings_by_severity.get("MEDIUM", []) +
            findings_by_severity.get("LOW", [])
        )
        
        # SPI color threshold
        if spi >= 80:
            spi_color = "slagreen"
        elif spi >= 60:
            spi_color = "slaorange"
        else:
            spi_color = "slared"
        
        # Template substitution
        replacements = {
            "%%HOSTNAME%%": hostname,
            "%%AUDIT_DATE%%": generated_at,
            "%%AUDITOR_NAME%%": self.escape_latex("System Administrator"),
            "%%SPI_SCORE%%": f"{spi:.1f}",
            "%%SPI_COLOR%%": spi_color,
            "%%CRITICAL_COUNT%%": str(critical_count),
            "%%HIGH_COUNT%%": str(high_count),
            "%%MEDIUM_COUNT%%": str(medium_count),
            "%%LOW_COUNT%%": str(low_count),
            "%%PASS_COUNT%%": str(pass_count),
            "%%CATEGORY_TABLE_ROWS%%": category_table,
            "%%FINDINGS_TABLE_ROWS%%": findings_table,
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        # Write rendered template
        try:
            with open(output_file, 'w') as f:
                f.write(template)
            print(f"[INFO] Rendered LaTeX: {output_file}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to write LaTeX: {e}", file=sys.stderr)
            return False
    
    def compile_pdf(self, tex_file: str, output_dir: str, timeout: int = 30) -> bool:
        """Compile LaTeX to PDF using pdflatex"""
        tex_path = Path(tex_file)
        output_path = Path(output_dir)
        
        if not tex_path.exists():
            print(f"[ERROR] LaTeX file not found: {tex_file}", file=sys.stderr)
            return False
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # pdflatex command with security flags
        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-no-shell-escape",  # CRITICAL: Disable shell execution
            "-output-directory", str(output_path),
            tex_file,
        ]
        
        try:
            result = subprocess.run(
                cmd,
                timeout=timeout,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                print(f"[ERROR] pdflatex compilation failed", file=sys.stderr)
                print(result.stdout[-500:], file=sys.stderr)  # Last 500 chars of output
                return False
            
            # Verify PDF was created
            pdf_name = tex_path.stem + ".pdf"
            pdf_path = output_path / pdf_name
            
            if pdf_path.exists():
                print(f"[INFO] PDF compiled: {pdf_path}", file=sys.stderr)
                return True
            else:
                print(f"[ERROR] PDF not created", file=sys.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print(f"[ERROR] pdflatex compilation timed out", file=sys.stderr)
            return False
        except FileNotFoundError:
            print(f"[ERROR] pdflatex not found. Install TeX Live.", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Compilation error: {e}", file=sys.stderr)
            return False
    
    def generate_report(self, summary_file: str, output_dir: str = "reports") -> bool:
        """Generate complete PDF report from audit summary"""
        # Load summary
        try:
            with open(summary_file, 'r') as f:
                summary = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load summary: {e}", file=sys.stderr)
            return False
        
        # Create temp directory for LaTeX compilation
        with tempfile.TemporaryDirectory(prefix="tex_compile_") as tmpdir:
            tex_file = Path(tmpdir) / "audit_report.tex"
            
            # Render template
            if not self.render_template(summary, str(tex_file)):
                return False
            
            # Compile to PDF
            if not self.compile_pdf(str(tex_file), output_dir):
                return False
            
            # Move PDF to final location
            hostname = summary.get("hostname", "audit").replace(" ", "_")
            timestamp = datetime.now().strftime("%Y_%m_%d")
            pdf_name = f"TeX_Audit_Report_{hostname}_{timestamp}.pdf"
            
            src_pdf = Path(output_dir) / "audit_report.pdf"
            dst_pdf = Path(output_dir) / pdf_name
            
            if src_pdf.exists():
                src_pdf.rename(dst_pdf)
                print(f"[INFO] Report saved: {dst_pdf}", file=sys.stderr)
                return True
            
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TeX LaTeX Report Builder")
    parser.add_argument("--summary", default="data/audit_summary.json",
                        help="Input audit summary JSON")
    parser.add_argument("--output-dir", default="reports",
                        help="Output directory for PDF")
    parser.add_argument("--template", default="engine/templates/report_template.tex",
                        help="LaTeX template file")
    
    args = parser.parse_args()
    
    builder = ReportBuilder(args.template)
    success = builder.generate_report(args.summary, args.output_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

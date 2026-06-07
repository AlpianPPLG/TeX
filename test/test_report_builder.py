"""
Tests for the LaTeX report builder (engine/report_builder.py).

These exercise the pure-Python rendering/escaping logic only; they never invoke
`pdflatex`, so they run in any environment regardless of whether TeX Live is
installed.
"""

from report_builder import ReportBuilder


def test_escape_latex_special_characters():
    assert ReportBuilder.escape_latex("100%") == r"100\%"
    assert ReportBuilder.escape_latex("a_b") == r"a\_b"
    assert ReportBuilder.escape_latex("x&y") == r"x\&y"
    assert ReportBuilder.escape_latex("#1") == r"\#1"


def test_escape_latex_non_string():
    assert ReportBuilder.escape_latex(42) == "42"


def test_generate_findings_table_empty():
    builder = ReportBuilder()
    out = builder.generate_findings_table([])
    assert "No findings" in out


def test_generate_findings_table_rows():
    builder = ReportBuilder()
    findings = [
        {"cis_id": "5.2.8", "title": "Root login", "severity": "CRITICAL", "remediation": "fix"},
    ]
    out = builder.generate_findings_table(findings)
    assert "5.2.8" in out
    assert "CRITICAL" in out
    assert r"\textcolor{red}" in out


def test_generate_category_table_color_coding():
    builder = ReportBuilder()
    out = builder.generate_category_table({"ssh": 95.0, "pam": 30.0})
    assert "SSH" in out and "PAM" in out
    assert r"\textcolor{green}" in out   # high score
    assert r"\textcolor{red}" in out     # low score


def test_render_template_writes_tex(tmp_path, summary):
    builder = ReportBuilder()
    out_file = tmp_path / "report.tex"
    ok = builder.render_template(summary, str(out_file))
    assert ok
    content = out_file.read_text(encoding="utf-8")
    # Placeholders must be substituted.
    assert "%%HOSTNAME%%" not in content
    assert "%%SPI_SCORE%%" not in content
    assert summary["hostname"].replace(".", ".") in content or "internal" in content

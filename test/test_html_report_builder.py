"""Tests for the HTML/Markdown report builder (engine/html_report_builder.py)."""

import html_report_builder as hrb


def test_render_html_contains_core_sections(summary):
    out = hrb.render_html(summary)
    assert "<!DOCTYPE html>" in out
    assert summary["hostname"] in out
    assert "Security Posture Index" in out
    assert "Compliance by Category" in out
    assert "Findings" in out


def test_render_html_escapes_special_characters():
    summary = {
        "hostname": "h<script>",
        "spi": 50,
        "category_scores": {"ssh": 50.0},
        "findings_by_severity": {
            "CRITICAL": [
                {
                    "cis_id": "1.1",
                    "title": "Title & <b>bold</b>",
                    "module": "ssh",
                    "severity": "CRITICAL",
                    "remediation": "do x & y",
                }
            ],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
            "PASS": [],
        },
        "all_checks": [],
    }
    out = hrb.render_html(summary)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "Title &amp; &lt;b&gt;bold&lt;/b&gt;" in out


def test_spi_band_and_color_thresholds():
    assert hrb.spi_band(95) == "Strong"
    assert hrb.spi_band(70) == "Moderate"
    assert hrb.spi_band(45) == "Weak"
    assert hrb.spi_band(10) == "Critical"
    assert hrb.spi_color(95) == "#16a34a"
    assert hrb.spi_color(70) == "#d97706"
    assert hrb.spi_color(10) == "#dc2626"


def test_render_markdown_table(summary):
    md = hrb.render_markdown(summary)
    assert md.startswith("# TeX Security Compliance Report")
    assert "| Severity | Count |" in md
    assert "| Domain | Score |" in md


def test_generate_report_writes_files(tmp_path, summary):
    import json

    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    out_dir = tmp_path / "reports"

    builder = hrb.HTMLReportBuilder()
    ok = builder.generate_report(str(summary_path), str(out_dir))
    assert ok

    host = summary["hostname"].split(".")[0]
    assert (out_dir / f"report_{host}.html").exists()
    assert (out_dir / f"report_{host}.md").exists()


def test_generate_report_missing_summary(tmp_path):
    builder = hrb.HTMLReportBuilder()
    assert builder.generate_report(str(tmp_path / "nope.json"), str(tmp_path)) is False


def test_empty_findings_render_friendly_message():
    summary = {
        "hostname": "clean-host",
        "spi": 100,
        "category_scores": {"ssh": 100.0},
        "findings_by_severity": {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
            "PASS": [],
        },
        "all_checks": [],
    }
    out = hrb.render_html(summary)
    assert "No findings" in out

#!/usr/bin/env python3
"""
TeX Security Compliance Auditor - HTML Report Builder
Compiles a scored `audit_summary.json` into a self-contained, zero-dependency
HTML compliance report (no external CSS/JS/fonts, no network access required).

This is the portable counterpart to the LaTeX/PDF builder (`report_builder.py`):
it requires no `pdflatex` toolchain, so it works anywhere Python runs and is the
default report format for environments without TeX Live.

Usage:
  python engine/html_report_builder.py                       # data/audit_summary.json -> reports/
  python engine/html_report_builder.py --summary path.json --out-dir reports
"""

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "PASS"]

SEVERITY_COLORS = {
    "CRITICAL": "#dc2626",
    "HIGH": "#ea580c",
    "MEDIUM": "#d97706",
    "LOW": "#2563eb",
    "PASS": "#16a34a",
}


def esc(value) -> str:
    """HTML-escape an arbitrary value."""
    return html.escape(str(value), quote=True)


def spi_band(spi: float) -> str:
    if spi >= 80:
        return "Strong"
    if spi >= 60:
        return "Moderate"
    if spi >= 40:
        return "Weak"
    return "Critical"


def spi_color(spi: float) -> str:
    if spi >= 80:
        return "#16a34a"
    if spi >= 60:
        return "#d97706"
    return "#dc2626"


def _severity_counts(summary: Dict) -> Dict[str, int]:
    by_sev = summary.get("findings_by_severity", {})
    return {sev: len(by_sev.get(sev, [])) for sev in SEVERITY_ORDER}


def _summary_cards(counts: Dict[str, int]) -> str:
    cards = []
    for sev in SEVERITY_ORDER:
        cards.append(
            f'<div class="card" style="border-top:4px solid {SEVERITY_COLORS[sev]}">'
            f'<div class="card-count">{counts[sev]}</div>'
            f'<div class="card-label">{esc(sev)}</div></div>'
        )
    return "\n".join(cards)


def _category_rows(category_scores: Dict[str, float]) -> str:
    rows = []
    for category, score in sorted(category_scores.items()):
        score = float(score)
        bar_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
        rows.append(
            f"<tr><td class='cat-name'>{esc(category.upper())}</td>"
            f"<td class='cat-bar-cell'><div class='bar-track'>"
            f"<div class='bar-fill' style='width:{score:.1f}%;background:{bar_color}'></div>"
            f"</div></td>"
            f"<td class='cat-score'>{score:.1f}</td></tr>"
        )
    return "\n".join(rows)


def _finding_rows(findings: List[Dict]) -> str:
    if not findings:
        return "<tr><td colspan='5' class='empty'>No findings 🎉</td></tr>"

    rows = []
    for f in findings:
        sev = f.get("severity", "MEDIUM")
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        remediation = esc(f.get("remediation", "")).replace("\n", "<br>")
        rows.append(
            "<tr>"
            f"<td class='mono'>{esc(f.get('cis_id', ''))}</td>"
            f"<td><span class='pill' style='background:{color}'>{esc(sev)}</span></td>"
            f"<td>{esc(f.get('title', ''))}</td>"
            f"<td class='mono'>{esc(f.get('module', ''))}</td>"
            f"<td class='rem'>{remediation}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_html(summary: Dict) -> str:
    """Render the full HTML report document from a scored summary."""
    hostname = summary.get("hostname", "unknown")
    spi = float(summary.get("spi", 0))
    counts = _severity_counts(summary)
    category_scores = summary.get("category_scores", {})

    generated_ts = summary.get("generated_at")
    if generated_ts:
        generated_at = datetime.fromtimestamp(generated_ts, tz=timezone.utc).strftime(
            "%d %B %Y, %H:%M UTC"
        )
    else:
        generated_at = datetime.now(tz=timezone.utc).strftime("%d %B %Y, %H:%M UTC")

    by_sev = summary.get("findings_by_severity", {})
    actionable = (
        by_sev.get("CRITICAL", [])
        + by_sev.get("HIGH", [])
        + by_sev.get("MEDIUM", [])
        + by_sev.get("LOW", [])
    )
    total_checks = len(summary.get("all_checks", []))
    pass_count = counts["PASS"]
    fail_count = total_checks - pass_count

    metadata = summary.get("audit_metadata", {})
    os_name = metadata.get("os_name", "—")
    kernel = metadata.get("kernel_version", "—")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TeX Compliance Report — {esc(hostname)}</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: #f3f4f6; color: #111827;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.5;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 32px 20px 64px; }}
  header.report {{
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #fff; border-radius: 16px; padding: 32px; margin-bottom: 24px;
  }}
  header.report h1 {{ margin: 0 0 4px; font-size: 26px; letter-spacing: -0.02em; }}
  header.report .sub {{ color: #94a3b8; font-size: 14px; }}
  .meta-grid {{ display: flex; flex-wrap: wrap; gap: 24px; margin-top: 20px; font-size: 13px; }}
  .meta-grid div span {{ display: block; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; font-size: 11px; }}
  .meta-grid div b {{ font-weight: 600; }}
  .spi-wrap {{ display: flex; align-items: center; gap: 24px; background:#fff; border-radius:16px; padding:24px; margin-bottom:24px; box-shadow:0 1px 2px rgba(0,0,0,.06); }}
  .gauge {{ position: relative; width: 132px; height: 132px; flex: none; }}
  .gauge svg {{ transform: rotate(-90deg); }}
  .gauge .val {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
  .gauge .val b {{ font-size: 30px; }}
  .gauge .val small {{ color:#6b7280; font-size:11px; }}
  .spi-text h2 {{ margin: 0 0 4px; font-size: 18px; }}
  .spi-text p {{ margin: 0; color:#6b7280; font-size:14px; max-width: 520px; }}
  .cards {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }}
  .card {{ background:#fff; border-radius:12px; padding:16px; text-align:center; box-shadow:0 1px 2px rgba(0,0,0,.06); }}
  .card-count {{ font-size: 28px; font-weight: 700; }}
  .card-label {{ font-size: 11px; color:#6b7280; text-transform:uppercase; letter-spacing:.06em; margin-top:4px; }}
  section.block {{ background:#fff; border-radius:16px; padding:24px; margin-bottom:24px; box-shadow:0 1px 2px rgba(0,0,0,.06); }}
  section.block h3 {{ margin:0 0 16px; font-size:16px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ text-align:left; color:#6b7280; font-weight:600; text-transform:uppercase; letter-spacing:.04em; font-size:11px; padding:8px 10px; border-bottom:1px solid #e5e7eb; }}
  td {{ padding:10px; border-bottom:1px solid #f3f4f6; vertical-align:top; }}
  .mono {{ font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size:12px; }}
  .pill {{ color:#fff; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600; }}
  .bar-track {{ background:#e5e7eb; border-radius:999px; height:8px; width:100%; min-width:120px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:999px; }}
  .cat-name {{ font-weight:600; white-space:nowrap; }}
  .cat-score {{ text-align:right; font-variant-numeric: tabular-nums; font-weight:600; }}
  .cat-bar-cell {{ width: 70%; }}
  .rem {{ color:#374151; }}
  .empty {{ text-align:center; color:#16a34a; padding:24px; font-weight:600; }}
  footer {{ text-align:center; color:#9ca3af; font-size:12px; margin-top:8px; }}
  @media (max-width: 640px) {{
    .cards {{ grid-template-columns: repeat(2, 1fr); }}
    .spi-wrap {{ flex-direction: column; text-align:center; }}
    table {{ font-size:12px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="report">
    <h1>⚔ TeX Security Compliance Report</h1>
    <div class="sub">CIS Benchmark for Linux v3 · Generated {esc(generated_at)}</div>
    <div class="meta-grid">
      <div><span>Host</span><b>{esc(hostname)}</b></div>
      <div><span>Operating System</span><b>{esc(os_name)}</b></div>
      <div><span>Kernel</span><b>{esc(kernel)}</b></div>
      <div><span>Controls Evaluated</span><b>{total_checks}</b></div>
      <div><span>Passed / Failed</span><b>{pass_count} / {fail_count}</b></div>
    </div>
  </header>

  <div class="spi-wrap">
    <div class="gauge">
      <svg width="132" height="132" viewBox="0 0 132 132">
        <circle cx="66" cy="66" r="58" fill="none" stroke="#e5e7eb" stroke-width="12"/>
        <circle cx="66" cy="66" r="58" fill="none" stroke="{spi_color(spi)}" stroke-width="12"
                stroke-linecap="round" stroke-dasharray="{spi/100*364.4:.1f} 364.4"/>
      </svg>
      <div class="val"><b style="color:{spi_color(spi)}">{spi:.1f}</b><small>SPI / 100</small></div>
    </div>
    <div class="spi-text">
      <h2>Security Posture Index — {spi_band(spi)}</h2>
      <p>The SPI is a severity-weighted score across all evaluated CIS controls.
         A higher score reflects stronger compliance. This host has
         <b>{len(actionable)}</b> actionable finding(s) requiring remediation.</p>
    </div>
  </div>

  <div class="cards">
    {_summary_cards(counts)}
  </div>

  <section class="block">
    <h3>Compliance by Category</h3>
    <table>
      <thead><tr><th>Domain</th><th>Score</th><th>Value</th></tr></thead>
      <tbody>
        {_category_rows(category_scores)}
      </tbody>
    </table>
  </section>

  <section class="block">
    <h3>Findings &amp; Remediation ({len(actionable)})</h3>
    <table>
      <thead><tr><th>CIS ID</th><th>Severity</th><th>Title</th><th>Module</th><th>Remediation</th></tr></thead>
      <tbody>
        {_finding_rows(actionable)}
      </tbody>
    </table>
  </section>

  <footer>Generated by TeX v{esc(metadata.get('tex_version', '1.0.0'))} · Zero-Dependency Security Compliance Auditor</footer>
</div>
</body>
</html>
"""


def render_markdown(summary: Dict) -> str:
    """Render a Markdown version of the report (handy for PRs / terminals)."""
    hostname = summary.get("hostname", "unknown")
    spi = float(summary.get("spi", 0))
    counts = _severity_counts(summary)
    category_scores = summary.get("category_scores", {})
    by_sev = summary.get("findings_by_severity", {})
    actionable = (
        by_sev.get("CRITICAL", [])
        + by_sev.get("HIGH", [])
        + by_sev.get("MEDIUM", [])
        + by_sev.get("LOW", [])
    )

    lines = [
        f"# TeX Security Compliance Report — {hostname}",
        "",
        f"**Security Posture Index:** {spi:.1f}/100 ({spi_band(spi)})",
        "",
        "## Severity Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev} | {counts[sev]} |")

    lines += ["", "## Compliance by Category", "", "| Domain | Score |", "|--------|-------|"]
    for category, score in sorted(category_scores.items()):
        lines.append(f"| {category.upper()} | {float(score):.1f} |")

    lines += ["", f"## Findings ({len(actionable)})", "", "| CIS ID | Severity | Module | Title |", "|--------|----------|--------|-------|"]
    if not actionable:
        lines.append("| — | — | — | No findings |")
    else:
        for f in actionable:
            title = str(f.get("title", "")).replace("|", "\\|")
            lines.append(
                f"| {f.get('cis_id','')} | {f.get('severity','')} | {f.get('module','')} | {title} |"
            )
    lines.append("")
    return "\n".join(lines)


class HTMLReportBuilder:
    """Builds self-contained HTML (and Markdown) compliance reports."""

    def generate_report(self, summary_file: str, output_dir: str = "reports") -> bool:
        try:
            with open(summary_file, "r", encoding="utf-8") as handle:
                summary = json.load(handle)
        except FileNotFoundError:
            print(f"[ERROR] Summary file not found: {summary_file}")
            return False
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Invalid JSON in summary file: {exc}")
            return False

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        host = str(summary.get("hostname", "host")).split(".")[0]
        html_path = out_dir / f"report_{host}.html"
        md_path = out_dir / f"report_{host}.md"

        html_path.write_text(render_html(summary), encoding="utf-8")
        md_path.write_text(render_markdown(summary), encoding="utf-8")

        print(f"[OK] Wrote {html_path}")
        print(f"[OK] Wrote {md_path}")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TeX HTML compliance report")
    parser.add_argument("--summary", default="data/audit_summary.json", help="Path to audit_summary.json")
    parser.add_argument("--out-dir", default="reports", help="Output directory for reports")
    args = parser.parse_args()

    builder = HTMLReportBuilder()
    ok = builder.generate_report(args.summary, args.out_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

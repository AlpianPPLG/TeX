# 📁 Project Structure Documentation (PSD)
## TeX — Security Compliance Auditor

**Version**: 1.0  
**Date**: 07 June 2026  

---

## 1. Complete Directory Tree

```text
TeX/
│
├── TEX-DOCS/                       # 📚 Systems Engineering Documentation
│   ├── INDEX.md
│   ├── README.md
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── PSD.md                      # (This File)
│   ├── API_SPECIFICATION.md
│   ├── SECURITY_MODEL.md
│   ├── TESTING_STRATEGY.md
│   ├── DEPLOYMENT_STRATEGY.md
│   └── DEVELOPMENT_ROADMAP.md
│
├── agent/                          # 🔍 Shell Audit Probe Layer
│   ├── audit.sh                    # Master orchestration script
│   ├── audit.conf                  # Runtime configuration
│   └── modules/                    # Modular domain probe scripts
│       ├── ssh.sh                  # CIS Section 5.2: SSH daemon
│       ├── firewall.sh             # CIS Section 3.5: Firewall
│       ├── pam.sh                  # CIS Section 5.3: PAM
│       ├── sudoers.sh              # CIS Section 5.4: sudo
│       ├── filesystem.sh           # CIS Section 6: File permissions
│       ├── kernel.sh               # CIS Section 3.1-3.3: sysctl
│       ├── users.sh                # CIS Section 5.1: User accounts
│       └── services.sh             # CIS Section 2: Services
│
├── engine/                         # 🐍 Python Scoring & Report Engine
│   ├── main.py                     # CLI entrypoint
│   ├── scorer.py                   # CIS scoring & SPI calculation
│   ├── report_builder.py           # LaTeX renderer & pdflatex wrapper
│   ├── validator.py                # JSON schema validation
│   └── templates/
│       └── report_template.tex     # LaTeX audit report blueprint
│
├── rules/                          # 📋 Machine-Readable CIS Definitions
│   └── cis_linux_v3.json           # All 157 CIS control definitions
│
├── dashboard/                      # 🌐 Zero-Dependency Web Interface
│   ├── index.html                  # HTML5 semantic shell
│   ├── style.css                   # Custom property-based CSS
│   ├── app.js                      # Compiled output from TypeScript
│   ├── tsconfig.json               # TypeScript compiler configuration
│   └── src/
│       ├── main.ts                 # TypeScript entrypoint
│       ├── rule-engine.ts          # Audit data filter & grouping logic
│       ├── renderer.ts             # SVG chart rendering engine
│       └── types.ts                # Shared TypeScript interfaces
│
├── data/                           # 📊 Runtime Data (Git-ignored)
│   ├── raw_audit.json              # Shell agent output
│   └── audit_summary.json          # Scored summary for dashboard
│
├── reports/                        # 📄 Compiled PDF Reports (Git-ignored)
│   └── TeX_Audit_Report_YYYY_MM_DD.pdf
│
└── .gitignore                      # Excludes data/ and reports/ from VCS
```

---

## 2. Component-Level File Descriptions

### 📂 `agent/` — Shell Audit Probe Layer

```
+----------------------------------------------------------------+
|                     SHELL AUDIT LAYER                          |
+----------------------------------------------------------------+
|  audit.conf → audit.sh → [ssh.sh | firewall.sh | kernel.sh …] |
|                                ↓                                |
|                    data/raw_audit.json                          |
+----------------------------------------------------------------+
```

#### `agent/audit.sh` (Master Orchestrator Script)
The primary entry point for all audit operations. Responsibilities:
- Parse `audit.conf` for enabled/disabled modules and output path.
- Execute each enabled module as a subprocess, capturing stdout.
- Validate each module's JSON output with a lightweight `jq` check (if available) or regex fallback.
- Assemble all module outputs into a single `raw_audit.json` file.
- Append execution metadata: hostname, OS version, kernel version, and audit timestamp.

#### `agent/audit.conf` (Configuration File)
Plain-text key-value configuration controlling audit behavior:
```bash
# Output directory for raw audit data
OUTPUT_DIR=../data

# Module toggles (yes/no)
ENABLE_SSH=yes
ENABLE_FIREWALL=yes
ENABLE_PAM=yes
ENABLE_SUDOERS=yes
ENABLE_FILESYSTEM=yes
ENABLE_KERNEL=yes
ENABLE_USERS=yes
ENABLE_SERVICES=yes

# Severity threshold: only report findings at or above this level
# Values: CRITICAL, HIGH, MEDIUM, LOW
MIN_SEVERITY=LOW
```

---

### 📂 `engine/` — Python Scoring Engine

#### `engine/main.py` (CLI Entrypoint)
Accepts CLI arguments and orchestrates the scoring and report generation workflow:
```
Usage: python3 main.py [OPTIONS]

Options:
  --score           Run CIS scoring on data/raw_audit.json
  --report          Compile LaTeX PDF report
  --diff <file>     Compare current audit against a previous snapshot
  --output-dir DIR  Directory to write PDF reports (default: ./reports)
  --month YYYY-MM   Generate report for a specific month
  --spi-only        Print Security Posture Index to stdout and exit
```

#### `engine/scorer.py` (CIS Benchmark Scoring)
Core scoring logic. Key functions:
- `load_controls(path)` — Loads and validates `cis_linux_v3.json`.
- `map_findings(raw_audit, controls)` — Maps shell output to CIS controls.
- `calculate_spi(mapped_findings)` — Computes global Security Posture Index.
- `calculate_category_scores(mapped_findings)` — Computes per-domain scores for radar chart.
- `classify_severity(finding, control)` — Assigns CRITICAL/HIGH/MEDIUM/LOW/PASS.

#### `engine/report_builder.py` (LaTeX Compiler Wrapper)
- `escape_latex(value: str) → str` — Applies full LaTeX character escaping.
- `render_template(template_path, variables)` — String substitution into `.tex` template.
- `compile_pdf(tex_source, output_dir)` — Spawns sandboxed `pdflatex` subprocess.
- `cleanup_artifacts(temp_dir)` — Removes `.aux`, `.log`, `.out` files post-compilation.

---

### 📂 `dashboard/` — Web Interface

#### `dashboard/tsconfig.json` (TypeScript Compiler Config)
```json
{
  "compilerOptions": {
    "target": "ES6",
    "module": "None",
    "strict": true,
    "noImplicitAny": true,
    "outFile": "app.js",
    "removeComments": true,
    "sourceMap": false
  },
  "include": ["src/**/*.ts"]
}
```

> **Important**: `"module": "None"` is intentional. This compiles all TypeScript files into a single, concatenated `app.js` with no module system — making it loadable directly as a `<script>` tag in a browser without any module bundler or Node.js runtime.

---

### 📂 `rules/` — CIS Control Definitions

#### `rules/cis_linux_v3.json` (Machine-Readable Rule Database)
Contains 157 CIS control definitions. Each entry specifies the expected state, severity, and NIST mapping:
```json
[
  {
    "cis_id": "5.2.8",
    "section": "ssh",
    "title": "Ensure SSH PermitRootLogin is disabled",
    "level": 1,
    "severity": "CRITICAL",
    "expected_pattern": "^PermitRootLogin\\s+no$",
    "config_file": "/etc/ssh/sshd_config",
    "nist_800_53": ["AC-6", "IA-2"],
    "remediation": "Edit /etc/ssh/sshd_config, set 'PermitRootLogin no', then run: systemctl restart sshd"
  }
]
```

---

## 3. Data Flow & Dependency Graph

```mermaid
graph TD
    conf[audit.conf] -->|configures| master[audit.sh]
    master -->|spawns| ssh[ssh.sh]
    master -->|spawns| fw[firewall.sh]
    master -->|spawns| kern[kernel.sh]
    master -->|spawns| other[...other modules]
    
    ssh -->|JSON stdout| master
    fw -->|JSON stdout| master
    kern -->|JSON stdout| master
    other -->|JSON stdout| master
    
    master -->|writes| raw[data/raw_audit.json]
    rules[rules/cis_linux_v3.json] -->|loaded by| scorer[engine/scorer.py]
    raw -->|read by| scorer
    
    scorer -->|scored findings| summary[data/audit_summary.json]
    scorer -->|variables| builder[engine/report_builder.py]
    tmpl[engine/templates/report_template.tex] -->|template| builder
    builder -->|spawns sandboxed| latex[pdflatex binary]
    latex -->|compiles| pdf[reports/TeX_Audit_Report.pdf]
    
    summary -->|fetched by| ts[dashboard/app.js (from TypeScript)]
    ts -->|renders SVG| ui[dashboard/index.html]
```

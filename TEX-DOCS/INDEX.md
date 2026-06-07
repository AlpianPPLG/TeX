# 📚 TeX — Documentation Index
> **Security Compliance Auditor & Hardening Report Generator**

Welcome to the official systems engineering documentation for **TeX**, an enterprise-grade, zero-dependency Linux security compliance auditor. This repository encompasses the complete technical specification — from low-level shell probing mechanics and TypeScript rule engine design, to LaTeX PDF report compilation pipelines and CIS Benchmark scoring algorithms.

---

## 🚀 1. Project Orientation & Requirements

Start here to understand the system's goals, stakeholders, and compliance targets:

- **[README.md](README.md)** — High-level project overview, feature summary, tech stack rationale, prerequisites, and quick-start commands.
- **[PRD.md](PRD.md)** — Product Requirements Document: system objectives, Key Performance Targets (KPT), compliance frameworks (CIS/NIST/STIG), user personas, priority matrix, and non-functional requirements.

---

## 🏗️ 2. System Architecture & Low-Level Design

Deep-dive into the data flows, component interactions, and algorithmic design:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Full systems engineering analysis: audit pipeline state machine, CIS Benchmark scoring algorithm, TypeScript rule engine design, SVG radar chart mathematics, LaTeX sandboxing architecture, and component interaction sequence diagrams.
- **[PSD.md](PSD.md)** — Project Structure Documentation: folder responsibilities, file-level role mapping, and configuration management.
- **[API_SPECIFICATION.md](API_SPECIFICATION.md)** — Inter-component data contracts: Shell-to-Python JSON schema, Python-to-Dashboard JSON schema (Draft-07), LaTeX template variable interface, and CIS rule definition DSL format.
- **[SECURITY_MODEL.md](SECURITY_MODEL.md)** — Comprehensive security threat model: attack surface analysis, LaTeX injection mitigations, Shell injection prevention, privilege separation design, and audit trail integrity guarantees.

---

## 🧪 3. Verification & Quality Assurance

Comprehensive testing, fault injection, and benchmark validation strategies:

- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** — Multi-tier testing methodology: CIS scoring unit tests, rule engine regression suites, shell stub injection testing, LaTeX fuzzing for compiler safety, and cross-browser SVG rendering validation.

---

## 🚀 4. Deployment & Operations

Production-grade deployment configurations and operational runbooks:

- **[DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md)** — Deployment models: one-shot audit execution, systemd daemon scheduling, hardened service unit configurations, TeX Live environment setup, Nginx static dashboard hosting, SELinux/AppArmor policy profiles, and logrotate management.

---

## 📅 5. Project Roadmap

Timeline, milestones, and deliverable checklists:

- **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** — 5-week phased development roadmap with daily task checklists, MVP success criteria, post-MVP feature targets, and compliance certification milestones.

---

## 🛠️ 6. Quick Reference: Directory Tree

```text
TeX/
│
├── TEX-DOCS/                       # 📚 Systems Engineering Documentation
│   ├── INDEX.md                    # Navigation Index (This File)
│   ├── README.md                   # Project Overview & Quick-Start
│   ├── PRD.md                      # Product Requirements Document
│   ├── ARCHITECTURE.md             # System Design & Algorithms
│   ├── PSD.md                      # Project Structure Documentation
│   ├── API_SPECIFICATION.md        # Data Contracts & Schemas
│   ├── SECURITY_MODEL.md           # Threat Model & Mitigations
│   ├── TESTING_STRATEGY.md         # QA & Verification Strategy
│   ├── DEPLOYMENT_STRATEGY.md      # Production Deployment Guide
│   └── DEVELOPMENT_ROADMAP.md      # Timeline & Milestones
│
├── agent/                          # 🔍 Shell Audit Probe Layer
│   ├── audit.sh                    # Master audit orchestration script
│   ├── modules/                    # Modular audit probe scripts
│   │   ├── ssh.sh                  # SSH daemon configuration checks
│   │   ├── firewall.sh             # ufw/iptables rule inspection
│   │   ├── pam.sh                  # PAM stack configuration checks
│   │   ├── sudoers.sh              # sudo privilege escalation checks
│   │   ├── filesystem.sh           # Critical file permissions & SUID/SGID
│   │   ├── kernel.sh               # Kernel sysctl hardening parameters
│   │   ├── users.sh                # User account & password policy checks
│   │   └── services.sh             # Unnecessary running services check
│   └── audit.conf                  # Audit configuration file
│
├── engine/                         # 🐍 Python Scoring & Compilation Engine
│   ├── main.py                     # CLI entrypoint & audit orchestrator
│   ├── scorer.py                   # CIS Benchmark scoring & risk calculator
│   ├── report_builder.py           # LaTeX template renderer & pdflatex wrapper
│   ├── validator.py                # JSON output schema validation
│   └── templates/
│       └── report_template.tex     # LaTeX audit report blueprint
│
├── rules/                          # 📋 CIS Benchmark Rule Definitions
│   └── cis_linux_v3.json           # Machine-readable CIS control definitions
│
├── dashboard/                      # 🌐 Zero-Dependency Web Interface
│   ├── index.html                  # HTML5 audit cockpit shell
│   ├── style.css                   # Premium dark-mode CSS styling
│   ├── app.js                      # Compiled Vanilla JS (from TypeScript)
│   ├── src/
│   │   ├── main.ts                 # TypeScript entrypoint
│   │   ├── rule-engine.ts          # Type-safe audit rule parser & filter
│   │   ├── renderer.ts             # SVG radar chart renderer
│   │   └── types.ts                # Shared TypeScript type definitions
│   └── tsconfig.json               # TypeScript compile configuration
│
└── data/                           # 📊 Runtime Data (Git-ignored in production)
    ├── raw_audit.json              # Raw audit output from Shell agent
    └── audit_summary.json          # Scored & categorized summary for dashboard
```

---

**Last Updated**: 07 June 2026  
**Version**: 1.0.0  
**Status**: 📝 Planning & Architecture Phase  
**Next Step**: Begin Phase 1 — Shell Audit Agent Module Development

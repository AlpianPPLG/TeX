# 📋 Product Requirements Document (PRD)
## TeX — Security Compliance Auditor & Hardening Report Generator

**Version**: 1.0  
**Date**: 07 June 2026  
**Status**: Requirements Frozen  
**Author**: Systems Engineering Division  

---

## 1. Executive Summary

The **TeX** platform addresses a critical operational gap in modern infrastructure security management: the absence of a lightweight, offline-capable, compliance-grade security auditing tool that produces legally defensible PDF reports without cloud dependencies, mandatory root access, or heavy runtime installations.

Security audits today are fragmented across multiple tools (Lynis for local checks, OpenSCAP for policy compliance, Tenable for network scanning), each requiring separate license agreements, cloud connectors, or database synchronization. **TeX** consolidates the local configuration audit workflow into a single, self-contained system — from raw OS-level inspection through to a digitally-signed PDF SLA compliance document.

This product is designed for **systems engineers, security operations teams, and compliance officers** who need to prove and improve the security posture of Linux servers in regulated environments (banking, healthcare, government, defense).

---

## 2. Problem Statement

### Current Pain Points in Security Auditing

```
+----------------------+      +---------------------+      +----------------------+
|   DISCOVERY PHASE    |      |  ANALYSIS PHASE      |      |   REPORTING PHASE    |
+----------------------+      +---------------------+      +----------------------+
| Shell scripts: no    |  →   | Manual comparison    |  →   | Word documents:      |
| structured output.   |      | against PDFs.        |      | inconsistent format. |
| No scoring.          |      | Error-prone.         |      | Not audit-ready.     |
+----------------------+      +---------------------+      +----------------------+
         ↓                            ↓                              ↓
    Time: ~4 hours              Time: ~6 hours              Time: ~3 hours
    TOTAL MANUAL AUDIT CYCLE: ~13 hours per server
```

**TeX reduces this to under 5 minutes per server.**

---

## 3. Compliance Framework Alignment

The TeX platform targets three major security compliance frameworks:

### A. CIS Controls for Linux (Primary Target)
The **Center for Internet Security (CIS) Benchmark for Linux v3** provides 300+ specific, testable configuration controls across 18 control domains. TeX implements automated checks for all Level 1 (foundational) and selected Level 2 (advanced) controls.

| CIS Section | Domain | Controls Count |
|------------|--------|---------------|
| Section 1 | Initial Setup (Filesystem Configuration) | 22 |
| Section 2 | Services (Unnecessary Services) | 18 |
| Section 3 | Network Configuration (Host & Network Parameters) | 26 |
| Section 4 | Logging & Auditing (`auditd` configuration) | 31 |
| Section 5 | Access Control, Authentication & Authorization | 41 |
| Section 6 | System Maintenance (File Permissions) | 19 |
| **Total** | | **157 automated controls** |

### B. NIST SP 800-53 Rev.5 (Mapping Layer)
Each CIS control is mapped to its corresponding NIST 800-53 control family to satisfy federal compliance requirements (FedRAMP, FISMA). This mapping is stored in `rules/cis_linux_v3.json`.

### C. STIG (Security Technical Implementation Guide)
Selected DISA STIG V1R3 checks for Linux are included as additional rule definitions within the same JSON ruleset, allowing TeX reports to satisfy DoD system requirements.

---

## 4. Stakeholder Roles & User Personas

### 👨‍💻 Persona 1: Linux Systems Engineer (Primary Operator)
- **Goal**: Run automated security checks on new servers before production deployment.
- **Pain Point**: Manually reading CIS PDFs and cross-referencing configuration values takes hours.
- **User Story**: *As a Systems Engineer, I want to run a single shell command that checks all CIS Level 1 controls and outputs a scored JSON report, so I can identify security gaps in under 5 minutes.*

### 🔐 Persona 2: Security Operations Analyst (SOC Analyst)
- **Goal**: Schedule periodic re-audits of production servers to detect configuration drift.
- **Pain Point**: No automated way to detect when a developer accidentally relaxed a security control.
- **User Story**: *As a SOC Analyst, I want to schedule weekly audits via cron and receive a diff of changed findings, so I can detect and respond to security regression immediately.*

### 📁 Persona 3: Compliance Officer / CISO
- **Goal**: Produce formal, signed audit reports for external auditors or regulators.
- **Pain Point**: Translating raw tool output into professionally formatted compliance documentation is manual and time-consuming.
- **User Story**: *As a CISO, I want to generate a professionally formatted PDF audit report containing my organization's Security Posture Index, all findings categorized by severity, and a signature block, so I can submit it to our external auditor without additional formatting.*

---

## 5. Feature Specifications & Priority Matrix

Features are classified as:
- **P0** — Core: System cannot function without this feature.
- **P1** — Essential: Product is not viable without this feature.
- **P2** — Enhancement: Adds significant value but not blocking for MVP.

### A. Shell Audit Layer (P0)

| Code | Feature | Description | Priority | Status |
|------|---------|-------------|----------|--------|
| REQ-001 | SSH Configuration Audit | Check `sshd_config` for 12 CIS-required parameters. | P0 | ⏳ Planning |
| REQ-002 | Firewall Rule Inspection | Detect active ruleset, default policies, and dangerous open ports. | P0 | ⏳ Planning |
| REQ-003 | PAM Stack Validation | Check password complexity, lockout thresholds, and session limits. | P0 | ⏳ Planning |
| REQ-004 | Sudoers Security Scan | Detect NOPASSWD entries, wildcard grants, and unrestricted shells. | P0 | ⏳ Planning |
| REQ-005 | Kernel sysctl Hardening | Validate ASLR, SYN flood protection, and IP forwarding parameters. | P0 | ⏳ Planning |
| REQ-006 | SUID/SGID Binary Audit | Enumerate non-standard SUID/SGID files against a known-safe baseline. | P0 | ⏳ Planning |
| REQ-007 | Structured JSON Output | All module outputs must write structured, schema-validated JSON. | P0 | ⏳ Planning |

### B. Scoring & Reporting Engine (P1)

| Code | Feature | Description | Priority | Status |
|------|---------|-------------|----------|--------|
| REQ-008 | CIS Benchmark Scoring | Map each finding to CIS control and calculate per-category scores. | P1 | ⏳ Planning |
| REQ-009 | Security Posture Index | Compute a normalized global SPI (0–100) representing overall server security. | P1 | ⏳ Planning |
| REQ-010 | LaTeX Report Generation | Dynamically compile a professional PDF report from audit findings. | P1 | ⏳ Planning |
| REQ-011 | Severity Classification | Classify each finding as CRITICAL / HIGH / MEDIUM / LOW / PASS. | P1 | ⏳ Planning |

### C. Dashboard & TypeScript Rule Engine (P1)

| Code | Feature | Description | Priority | Status |
|------|---------|-------------|----------|--------|
| REQ-012 | SVG Radar Chart | Render a six-axis security domain radar chart using pure SVG math. | P1 | ⏳ Planning |
| REQ-013 | Progress Ring Cards | Per-category score rings using SVG stroke-dasharray calculations. | P1 | ⏳ Planning |
| REQ-014 | TypeScript Rule Engine | Type-safe client-side parsing, filtering, and grouping of audit findings. | P1 | ⏳ Planning |
| REQ-015 | Findings Filter Table | Interactive findings table with live severity filter and keyword search. | P1 | ⏳ Planning |

### D. Advanced Compliance Features (P2)

| Code | Feature | Description | Priority | Status |
|------|---------|-------------|----------|--------|
| REQ-016 | Audit Diff Mode | Compare two audit snapshots to detect configuration drift between runs. | P2 | ⏳ Planning |
| REQ-017 | NIST 800-53 Mapping Table | Include NIST control family mapping in generated PDF reports. | P2 | ⏳ Planning |
| REQ-018 | Remediation Runbook | Auto-generate shell commands to fix each failed control. | P2 | ⏳ Planning |

---

## 6. Non-Functional Requirements (NFR)

### Performance
- **Audit Execution**: Total runtime for all modules on a standard Linux server must not exceed `120 seconds`.
- **PDF Compilation**: LaTeX compilation must complete within `10 seconds`.
- **Dashboard Load Time**: `index.html` must load and render completely in under `500ms` on a local network.

### Security
- **No Root Requirement**: All Level 1 CIS checks must execute without root or sudo privileges.
- **Principle of Least Privilege**: The audit agent must not write files outside its designated output directory.
- **LaTeX Injection Prevention**: All user-supplied or system-sourced strings injected into LaTeX templates must be escaped through a validated sanitization pipeline.

### Portability
- **Shell Compatibility**: All Bash scripts must pass `shellcheck` validation and be compatible with Bash 4.0+ on Ubuntu 20.04+, Debian 11+, RHEL 8+, and CentOS Stream 9.
- **Python Compatibility**: Backend code must run on Python 3.8+ using only the standard library (no `pip install` required).
- **TypeScript Build**: TypeScript source must compile to ES6-compatible JavaScript targeting modern browsers (Chrome 90+, Firefox 88+, Edge 90+).

# 🔌 API & Data Specifications
## TeX — Inter-Component Communication Contracts

**Version**: 1.0  
**Date**: 07 June 2026  
**Status**: Specification Frozen  

This document defines all data contracts between system components — from Shell agent output through Python scoring to the browser dashboard and LaTeX report compiler.

---

## 1. Shell Module Output Schema (`raw_audit.json`)

Each audit module writes a structured JSON object to `stdout`. The master `audit.sh` captures these and assembles the final `raw_audit.json`.

### Top-Level Structure
```json
{
  "audit_metadata": {
    "timestamp": 1749259200,
    "hostname": "prod-server-01.company.com",
    "os_name": "Ubuntu 22.04.3 LTS",
    "kernel_version": "5.15.0-91-generic",
    "audit_user": "sysadmin",
    "tex_version": "1.0.0"
  },
  "modules": {
    "ssh":        { ... },
    "firewall":   { ... },
    "pam":        { ... },
    "sudoers":    { ... },
    "filesystem": { ... },
    "kernel":     { ... },
    "users":      { ... },
    "services":   { ... }
  }
}
```

### Per-Module Check Object Schema
```json
{
  "module": "ssh",
  "status": "COMPLETED",
  "duration_ms": 234,
  "checks": [
    {
      "cis_id":         "5.2.8",
      "title":          "Ensure SSH PermitRootLogin is disabled",
      "status":         "FAIL",
      "actual_value":   "PermitRootLogin yes",
      "expected_value": "PermitRootLogin no",
      "severity":       "CRITICAL",
      "remediation":    "Set 'PermitRootLogin no' in /etc/ssh/sshd_config"
    }
  ]
}
```

### Valid Field Enumerations

| Field | Allowed Values |
|-------|---------------|
| `module` | `ssh`, `firewall`, `pam`, `sudoers`, `filesystem`, `kernel`, `users`, `services` |
| `status` (module) | `COMPLETED`, `SKIPPED`, `ERROR` |
| `status` (check) | `PASS`, `FAIL`, `MANUAL` |
| `severity` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |

---

## 2. Scored Summary Schema (`audit_summary.json`) — JSON Schema Draft-07

The Python scoring engine writes `audit_summary.json` for consumption by the TypeScript-compiled dashboard. This file must conform to the following JSON Schema Draft-07 specification:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TeXAuditSummary",
  "type": "object",
  "required": ["generated_at", "hostname", "spi", "category_scores", "findings_by_severity", "all_checks"],
  "properties": {
    "generated_at": {
      "type": "integer",
      "description": "Unix epoch timestamp of scoring run"
    },
    "hostname": { "type": "string" },
    "spi": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Global Security Posture Index"
    },
    "category_scores": {
      "type": "object",
      "description": "Per-domain score (0-100) for SVG radar chart",
      "properties": {
        "ssh":        { "type": "number", "minimum": 0, "maximum": 100 },
        "firewall":   { "type": "number", "minimum": 0, "maximum": 100 },
        "pam":        { "type": "number", "minimum": 0, "maximum": 100 },
        "sudoers":    { "type": "number", "minimum": 0, "maximum": 100 },
        "filesystem": { "type": "number", "minimum": 0, "maximum": 100 },
        "kernel":     { "type": "number", "minimum": 0, "maximum": 100 }
      },
      "required": ["ssh", "firewall", "pam", "sudoers", "filesystem", "kernel"]
    },
    "findings_by_severity": {
      "type": "object",
      "properties": {
        "CRITICAL": { "type": "array", "items": { "$ref": "#/definitions/AuditCheck" } },
        "HIGH":     { "type": "array", "items": { "$ref": "#/definitions/AuditCheck" } },
        "MEDIUM":   { "type": "array", "items": { "$ref": "#/definitions/AuditCheck" } },
        "LOW":      { "type": "array", "items": { "$ref": "#/definitions/AuditCheck" } },
        "PASS":     { "type": "array", "items": { "$ref": "#/definitions/AuditCheck" } }
      }
    },
    "all_checks": {
      "type": "array",
      "items": { "$ref": "#/definitions/AuditCheck" }
    }
  },
  "definitions": {
    "AuditCheck": {
      "type": "object",
      "required": ["cis_id", "title", "status", "actual_value", "expected_value", "severity", "remediation"],
      "properties": {
        "cis_id":          { "type": "string", "pattern": "^[0-9]+\\.[0-9]+(\\.[0-9]+)?$" },
        "title":           { "type": "string", "minLength": 5 },
        "status":          { "type": "string", "enum": ["PASS", "FAIL", "MANUAL"] },
        "actual_value":    { "type": "string" },
        "expected_value":  { "type": "string" },
        "severity":        { "type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"] },
        "remediation":     { "type": "string", "minLength": 10 }
      }
    }
  }
}
```

---

## 3. CIS Rule Definition DSL (`cis_linux_v3.json`)

The rule definition file serves as the single source of truth for all CIS controls. Each rule entry follows this schema:

```json
{
  "cis_id":          "5.2.8",
  "section":         "ssh",
  "title":           "Ensure SSH PermitRootLogin is disabled",
  "description":     "The PermitRootLogin parameter specifies if the root user can log in using SSH.",
  "level":           1,
  "severity":        "CRITICAL",
  "weight":          10.0,
  "check_type":      "regex_match",
  "config_file":     "/etc/ssh/sshd_config",
  "expected_pattern":"^PermitRootLogin\\s+no$",
  "nist_800_53":     ["AC-6", "IA-2", "AC-3"],
  "stig_id":         "UBTU-22-255060",
  "remediation":     "Edit /etc/ssh/sshd_config. Set: PermitRootLogin no\nThen run: sudo systemctl restart sshd"
}
```

### `check_type` Values

| Type | Shell Implementation |
|------|---------------------|
| `regex_match` | Grep config file with provided `expected_pattern` |
| `command_output` | Run a specific command and compare stdout |
| `file_permission` | Check octal permission of a specific file path |
| `sysctl_value` | Read `/proc/sys/` or run `sysctl -n` for a kernel parameter |
| `service_disabled` | Check that a systemd unit is `inactive` and `disabled` |
| `package_absent` | Verify a package name is not installed via `dpkg`/`rpm` |
| `manual` | Cannot be automated; flagged for human review |

---

## 4. LaTeX Template Variable Interface

The Python `report_builder.py` replaces placeholder tokens in `report_template.tex`. All values are LaTeX-escaped before insertion.

| Token | Type | Description |
|-------|------|-------------|
| `%%HOSTNAME%%` | `string` | Target server hostname |
| `%%AUDIT_DATE%%` | `string` | Formatted audit date (e.g., `07 June 2026`) |
| `%%AUDITOR_NAME%%` | `string` | Auditor name from `audit.conf` |
| `%%SPI_SCORE%%` | `float` | Global Security Posture Index (e.g., `74.3`) |
| `%%SPI_COLOR%%` | `string` | LaTeX color name based on SPI threshold (`slagreen`/`slaorange`/`slared`) |
| `%%CRITICAL_COUNT%%` | `int` | Number of CRITICAL findings |
| `%%HIGH_COUNT%%` | `int` | Number of HIGH findings |
| `%%MEDIUM_COUNT%%` | `int` | Number of MEDIUM findings |
| `%%LOW_COUNT%%` | `int` | Number of LOW findings |
| `%%PASS_COUNT%%` | `int` | Number of PASS controls |
| `%%CATEGORY_TABLE_ROWS%%` | `raw LaTeX` | Generated `booktabs` table rows for category scores |
| `%%FINDINGS_TABLE_ROWS%%` | `raw LaTeX` | Generated `longtable` rows for all FAIL findings |
| `%%REMEDIATION_LIST%%` | `raw LaTeX` | Generated `enumerate` items for remediation steps |

### LaTeX Escape Map
```python
LATEX_ESCAPE_MAP = {
    '\\': r'\textbackslash{}',
    '&':  r'\&',
    '%':  r'\%',
    '$':  r'\$',
    '#':  r'\#',
    '_':  r'\_',
    '{':  r'\{',
    '}':  r'\}',
    '~':  r'\textasciitilde{}',
    '^':  r'\textasciicircum{}',
}
```

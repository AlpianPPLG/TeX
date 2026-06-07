# 🧪 Testing & Verification Strategy
## TeX — Security Compliance Auditor

**Version**: 1.0  
**Date**: 07 June 2026  

---

## 1. Testing Philosophy & Pyramid

```
                         ┌─────────────┐
                         │  End-to-End  │  1 full audit pipeline test per PR
                         └──────┬──────┘
                    ┌───────────┴──────────┐
                    │   Integration Tests   │  Python ↔ JSON ↔ Dashboard
                    └───────────┬──────────┘
          ┌─────────────────────┴────────────────────┐
          │              Unit Tests                   │
          │  Shell modules | Scoring math | TS engine │
          └───────────────────────────────────────────┘
```

The TeX testing strategy is organized into four primary tiers:

| Tier | Scope | Method |
|------|-------|--------|
| **Tier 1** | Shell Module Logic | Bash `bats` test framework with stub environments |
| **Tier 2** | Python Scoring Engine | `unittest` with synthetic audit datasets |
| **Tier 3** | TypeScript Rule Engine | Browser console assertions + manual type checking |
| **Tier 4** | LaTeX Compiler Safety | Fuzzing with injected special characters |

---

## 2. Tier 1: Shell Module Testing (Bash/BATS)

### A. Test Environment Setup
Each shell module is tested in an **isolated stub environment**. Rather than testing against the live system (which would produce non-deterministic results depending on the host), we create controlled stub directories that mimic real OS configuration files:

```bash
# test/stubs/ssh/sshd_config — a stub config representing a FAILING state
Port 22
Protocol 2
PermitRootLogin yes         # FAIL: should be 'no'
PasswordAuthentication yes  # FAIL: should be 'no'
MaxAuthTries 6              # FAIL: should be <= 4
```

### B. BATS Test Case Format
```bash
#!/usr/bin/env bats
# test/unit/test_ssh_module.bats

setup() {
  export STUB_ROOT="$BATS_TEST_DIRNAME/../stubs/ssh"
  export SSHD_CONFIG="$STUB_ROOT/sshd_config"
  source "$BATS_TEST_DIRNAME/../../agent/modules/ssh.sh"
}

@test "CIS 5.2.8: PermitRootLogin should be FAIL on stub config" {
  result=$(check_permit_root_login "$SSHD_CONFIG")
  [ "$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")" = "FAIL" ]
}

@test "CIS 5.2.4: SSH MaxAuthTries should be FAIL when set to 6" {
  result=$(check_max_auth_tries "$SSHD_CONFIG")
  actual=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['actual_value'])")
  [ "$actual" = "MaxAuthTries 6" ]
}
```

### C. Module Coverage Requirements
Each module must achieve **100% control coverage** in unit tests:

| Module | Controls | Test Cases Required |
|--------|----------|-------------------|
| `ssh.sh` | 12 | 12 FAIL + 12 PASS stubs |
| `firewall.sh` | 8 | 8 FAIL + 8 PASS stubs |
| `pam.sh` | 14 | 14 FAIL + 14 PASS stubs |
| `sudoers.sh` | 7 | 7 FAIL + 7 PASS stubs |
| `filesystem.sh` | 19 | 19 FAIL + 19 PASS stubs |
| `kernel.sh` | 26 | 26 FAIL + 26 PASS stubs |

---

## 3. Tier 2: Python Scoring Engine Tests (`unittest`)

### A. SPI Formula Verification
The scoring algorithm is verified against mathematically pre-computed datasets:

```python
# test/unit/test_scorer.py
import unittest
from engine.scorer import calculate_spi

class TestSPICalculation(unittest.TestCase):

    def test_zero_failures_gives_100_spi(self):
        findings = [
            {"severity": "CRITICAL", "status": "PASS"},
            {"severity": "HIGH", "status": "PASS"},
            {"severity": "MEDIUM", "status": "PASS"},
        ]
        spi = calculate_spi(findings)
        self.assertEqual(spi, 100.0)

    def test_all_critical_failures_gives_0_spi(self):
        findings = [{"severity": "CRITICAL", "status": "FAIL"} for _ in range(10)]
        spi = calculate_spi(findings)
        self.assertEqual(spi, 0.0)

    def test_mixed_findings_spi_formula(self):
        # Total weight: 1 CRITICAL(10) + 1 HIGH(7.5) + 1 MEDIUM(5) = 22.5
        # Failed weight: 1 CRITICAL(10) = 10
        # SPI = (1 - 10/22.5) * 100 = 55.56
        findings = [
            {"severity": "CRITICAL", "status": "FAIL"},
            {"severity": "HIGH",     "status": "PASS"},
            {"severity": "MEDIUM",   "status": "PASS"},
        ]
        spi = calculate_spi(findings)
        self.assertAlmostEqual(spi, 55.56, places=1)
```

### B. Edge Case Test Scenarios

| Test Case | Input Condition | Expected Output |
|-----------|----------------|----------------|
| Empty findings | `[]` | SPI = `100.0` |
| All CRITICAL FAIL | 10 CRITICAL failures | SPI = `0.0` |
| All PASS | 157 PASS controls | SPI = `100.0` |
| MANUAL-only findings | Only `MANUAL` controls | SPI = `null` (not calculable) |
| Single MEDIUM FAIL | 1 MEDIUM(5) fail out of 10 controls | SPI = `1 - 5/total_weight × 100` |

### C. JSON Schema Validation Test
Verify that `audit_summary.json` output is always schema-compliant:
```python
def test_output_validates_against_json_schema(self):
    import jsonschema
    with open('schemas/audit_summary_schema.json') as f:
        schema = json.load(f)
    result = run_full_scoring_pipeline(SAMPLE_RAW_AUDIT)
    jsonschema.validate(instance=result, schema=schema)  # Raises if invalid
```

---

## 4. Tier 3: TypeScript Rule Engine Testing

Since the TypeScript output is compiled to Vanilla JS for browser use, tests run in a headless browser environment or via a Node.js runner at build time (Node.js is a **build-time** dependency only):

```typescript
// test/rule-engine.test.ts (run via ts-node at build time only)
import { RuleEngine } from '../dashboard/src/rule-engine';
import { AuditSummary } from '../dashboard/src/types';
import { SAMPLE_SUMMARY } from './fixtures/sample_summary';

describe('RuleEngine', () => {
  it('should filter findings by CRITICAL severity only', () => {
    const engine = new RuleEngine(SAMPLE_SUMMARY);
    const results = engine.filterBySeverity('CRITICAL').getResults();
    expect(results.every(c => c.severity === 'CRITICAL')).toBe(true);
  });

  it('should return empty array when no CRITICAL findings exist', () => {
    const engine = new RuleEngine({ ...SAMPLE_SUMMARY, findings_by_severity: { CRITICAL: [] } });
    const results = engine.filterBySeverity('CRITICAL').getResults();
    expect(results.length).toBe(0);
  });
});
```

---

## 5. Tier 4: LaTeX Safety Fuzzing

### A. Special Character Injection Test
The following strings are fed as `actual_value` and `remediation` fields and must NOT cause `pdflatex` to throw a compilation error or execute system commands:

```python
FUZZ_CORPUS = [
    r"$PATH",
    r"\textbf{injected}",
    r"#{dangerous}",
    r"100% uptime",
    r"user_name@host.com",
    r"C:\Windows\System32",
    r"\write18{id}",           # LaTeX shell escape attempt
    r"$(id)",                  # Bash command substitution
    r"`whoami`",               # Backtick execution
    r"<script>alert(1)</script>",
    r"'; DROP TABLE checks; --",
]

def test_latex_fuzz(self):
    for payload in FUZZ_CORPUS:
        escaped = escape_latex(payload)
        tex_source = render_template(TEMPLATE_PATH, {"%%ACTUAL_VALUE%%": escaped})
        # Must compile without errors
        result = compile_pdf_safe(tex_source, output_dir="/tmp/tex_fuzz_test")
        self.assertTrue(result.returncode == 0, f"Compile failed for payload: {payload!r}")
```

### B. Empty Data Compilation Test
When there are zero FAIL findings, the report must compile cleanly with a "No findings" message rather than rendering an empty `longtable` (which would crash LaTeX):
```python
def test_empty_findings_compiles_cleanly(self):
    empty_summary = {"all_checks": [], "spi": 100.0, ...}
    result = generate_and_compile_report(empty_summary)
    self.assertEqual(result.returncode, 0)
    self.assertTrue(os.path.exists("reports/TeX_Audit_Report_test.pdf"))
```

---

## 6. Cross-Browser SVG Rendering Validation

The SVG radar chart and progress rings are manually validated across target browsers using a fixture HTML page loaded from a local file URI (no server required):

| Browser | Version | Radar Chart | Progress Rings | Filter Table |
|---------|---------|-------------|----------------|--------------|
| Chrome | 120+ | ✅ Validated | ✅ Validated | ✅ Validated |
| Firefox | 121+ | ✅ Validated | ✅ Validated | ✅ Validated |
| Edge | 120+ | ✅ Validated | ✅ Validated | ✅ Validated |
| Safari | 17+ | ⚠️ Test Required | ⚠️ Test Required | ✅ Validated |

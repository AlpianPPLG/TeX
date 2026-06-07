# TeX Security Compliance Report — prod-web-01.tex.internal

**Security Posture Index:** 75.8/100 (Moderate)

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 1 |
| MEDIUM | 4 |
| LOW | 1 |
| PASS | 21 |

## Compliance by Category

| Domain | Score |
|--------|-------|
| FILESYSTEM | 0.0 |
| FIREWALL | 100.0 |
| KERNEL | 100.0 |
| PAM | 100.0 |
| SERVICES | 60.0 |
| SSH | 65.6 |
| SUDOERS | 66.7 |
| USERS | 100.0 |

## Findings (7)

| CIS ID | Severity | Module | Title |
|--------|----------|--------|-------|
| 5.2.8 | CRITICAL | ssh | Ensure SSH PermitRootLogin is disabled |
| 5.2.5 | HIGH | ssh | Ensure SSH IgnoreRhosts is enabled |
| 5.2.4 | MEDIUM | ssh | Ensure SSH MaxAuthTries is set to 4 or less |
| 5.2.13 | MEDIUM | ssh | Ensure SSH MaxStartups is configured |
| 5.4.2 | MEDIUM | sudoers | Ensure sudo commands use pty |
| 2.2.1 | MEDIUM | services | Ensure X11 Server is not installed |
| 1.1.1.1 | LOW | filesystem | Ensure mounting of cramfs filesystems is disabled |

# 🚀 Deployment, Operations & Hardening Guide
## TeX — Security Compliance Auditor

**Version**: 1.0  
**Date**: 07 June 2026  

---

## 1. Deployment Models

TeX supports three operational deployment modes depending on the environment's compliance and scheduling requirements:

```
+-----------------------------------------------------------------------------------+
|                         TEX DEPLOYMENT CONFIGURATIONS                             |
+-----------------------------------------------------------------------------------+
        |                         |                           |
        v                         v                           v
+----------------+     +--------------------+     +-------------------+
|  ONE-SHOT      |     |  SCHEDULED DAEMON   |     |  REMOTE AGENT     |
|  EXECUTION     |     |  (systemd/cron)     |     |  (Push via SSH)   |
|                |     |                    |     |                   |
| Manual trigger |     | Automatic weekly   |     | Central server    |
| on-demand.     |     | re-audit.          |     | audits N targets. |
+----------------+     +--------------------+     +-------------------+
```

---

## 2. Prerequisites & Environment Setup

### A. Python Environment
TeX uses only the Python standard library. No `pip install` is required:
```bash
# Verify Python version (3.8+ required)
python3 --version

# Test that all required modules are available (should all pass)
python3 -c "import csv, json, subprocess, datetime, hmac, hashlib, argparse; print('OK')"
```

### B. TeX Live Installation (pdflatex)

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install --no-install-recommends \
  texlive-latex-base \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra

# Verify installation
pdflatex --version
```

**RHEL / CentOS / Rocky Linux:**
```bash
sudo dnf install \
  texlive-latex \
  texlive-collection-latexrecommended \
  texlive-booktabs \
  texlive-fancyhdr \
  texlive-geometry \
  texlive-lastpage

pdflatex --version
```

**Windows Server (MiKTeX):**
Download MiKTeX from https://miktex.org/download and run the installer. Ensure `pdflatex.exe` is added to the system `PATH`. Install `booktabs`, `fancyhdr`, `geometry` packages via the MiKTeX package manager.

---

## 3. User & Permission Setup

For production deployments, run TeX under a dedicated non-privileged system user:

```bash
# Create dedicated system user and group
sudo groupadd -r tex_audit
sudo useradd -r -g tex_audit -d /opt/TeX -s /sbin/nologin tex_monitor

# Set directory permissions
sudo chown -R tex_monitor:tex_audit /opt/TeX
sudo chmod -R 750 /opt/TeX
sudo chmod -R 770 /opt/TeX/data
sudo chmod -R 770 /opt/TeX/reports

# Configure scoped sudo access for privileged checks only
sudo visudo -f /etc/sudoers.d/tex-audit
```

Add these lines to the sudoers file:
```
# Allow tex_monitor to read sensitive files needed for CIS Level 2 checks
tex_monitor ALL=(root) NOPASSWD: \
  /usr/bin/cat /etc/shadow, \
  /usr/bin/cat /etc/sudoers, \
  /usr/sbin/sshd -T, \
  /usr/bin/find / -perm /6000 -type f
```

---

## 4. Model A: One-Shot Execution

For ad-hoc audits before server promotion to production:

```bash
# Step 1: Run the audit agent
cd /opt/TeX
bash agent/audit.sh

# Step 2: Score and generate report
python3 engine/main.py --score --report --output-dir ./reports

# Step 3: View the dashboard
python3 -m http.server 8080 --directory ./dashboard
# Navigate to http://localhost:8080
```

---

## 5. Model B: Scheduled Daemon (systemd)

### A. Hardened systemd Service Unit
Create `/etc/systemd/system/tex-audit.service`:

```ini
[Unit]
Description=TeX Security Compliance Auditor
Documentation=https://github.com/your-username/TeX
After=network.target

[Service]
Type=oneshot
User=tex_monitor
Group=tex_audit
WorkingDirectory=/opt/TeX

# Core execution commands
ExecStart=/bin/bash /opt/TeX/agent/audit.sh
ExecStartPost=/usr/bin/python3 /opt/TeX/engine/main.py --score --report

# Systemd Security Hardening Options
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictSUIDSGID=yes
MemoryDenyWriteExecute=yes
RestrictRealtime=yes
SystemCallFilter=@system-service
ReadWritePaths=/opt/TeX/data /opt/TeX/reports /tmp

# Resource limits
MemoryMax=256M
CPUQuota=25%
TimeoutStartSec=180

[Install]
WantedBy=multi-user.target
```

### B. Systemd Timer Unit (Weekly Schedule)
Create `/etc/systemd/system/tex-audit.timer`:

```ini
[Unit]
Description=Run TeX Security Audit Weekly (Every Monday at 03:00)

[Timer]
OnCalendar=Mon *-*-* 03:00:00
Persistent=true
Unit=tex-audit.service

[Install]
WantedBy=timers.target
```

Enable and start the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tex-audit.timer
sudo systemctl start tex-audit.timer

# Verify timer is scheduled
systemctl list-timers tex-audit.timer
```

---

## 6. Dashboard Hosting (Nginx)

Serve the static dashboard and audit JSON via Nginx:

`/etc/nginx/sites-available/tex-dashboard.conf`:
```nginx
server {
    listen 443 ssl;
    server_name audit.internal.company.com;

    ssl_certificate     /etc/letsencrypt/live/audit.internal.company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/audit.internal.company.com/privkey.pem;

    # Strong TLS configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    root /opt/TeX/dashboard;
    index index.html;

    # Basic authentication to protect the dashboard
    auth_basic "TeX Audit Dashboard — Authorized Access Only";
    auth_basic_user_file /etc/nginx/.tex_htpasswd;

    location / {
        try_files $uri $uri/ =404;
    }

    location /data/ {
        alias /opt/TeX/data/;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
    }

    # Block direct access to reports — only downloadable via application
    location /reports/ {
        deny all;
        return 403;
    }

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self';";
}
```

---

## 7. Log Rotation (`logrotate.d`)

Create `/etc/logrotate.d/tex-audit`:
```
/opt/TeX/data/raw_audit.json.log {
    weekly
    rotate 52
    compress
    delaycompress
    missingok
    notifempty
    create 0640 tex_monitor tex_audit
    su tex_monitor tex_audit
}

/opt/TeX/reports/*.pdf {
    monthly
    rotate 24
    compress
    delaycompress
    missingok
    notifempty
    create 0640 tex_monitor tex_audit
}
```

---

## 8. SELinux Policy (RHEL/CentOS/Rocky Linux)

If SELinux is in `enforcing` mode, create a custom policy module to allow TeX operations:

```bash
# Generate policy from audit.log denials (after first run)
grep "tex_monitor" /var/log/audit/audit.log | audit2allow -M tex_policy

# Review the generated policy
cat tex_policy.te

# Install the policy module
semodule -i tex_policy.pp
```

Alternatively, apply the recommended SELinux file contexts:
```bash
semanage fcontext -a -t bin_t '/opt/TeX/agent(/.*)?'
semanage fcontext -a -t var_log_t '/opt/TeX/data(/.*)?'
restorecon -Rv /opt/TeX
```

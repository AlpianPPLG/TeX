#!/bin/bash
################################################################################
# TeX — Filesystem Security Audit Module
# CIS Section 1.1, 6.1-6.2: Filesystem Configurations
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="filesystem"

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 1.1.1.1: Ensure mounting of cramfs filesystems is disabled
  if grep -q "^install cramfs /bin/true" /etc/modprobe.d/* 2>/dev/null; then
    STATUS="PASS"
    ACTUAL="cramfs mounting disabled"
  else
    STATUS="FAIL"
    ACTUAL="cramfs mounting not disabled"
  fi
  echo "    {\"cis_id\": \"1.1.1.1\", \"title\": \"Ensure mounting of cramfs filesystems is disabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"cramfs mounting disabled\", \"severity\": \"LOW\", \"remediation\": \"Disable cramfs: echo 'install cramfs /bin/true' | sudo tee -a /etc/modprobe.d/cramfs.conf\"},"
  
  # CIS 6.1.1: Ensure permissions on /etc/passwd are configured
  if [[ -f "/etc/passwd" ]]; then
    PERMS=$(stat -c "%a" /etc/passwd 2>/dev/null)
    if [[ "$PERMS" == "644" ]]; then
      STATUS="PASS"
      ACTUAL="Permissions: $PERMS"
    else
      STATUS="FAIL"
      ACTUAL="Permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="File not found"
  fi
  echo "    {\"cis_id\": \"6.1.1\", \"title\": \"Ensure permissions on /etc/passwd are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 644\", \"severity\": \"MEDIUM\", \"remediation\": \"Set permissions: sudo chmod 644 /etc/passwd\"},"
  
  # CIS 6.1.2: Ensure permissions on /etc/shadow are configured
  if [[ -f "/etc/shadow" ]]; then
    PERMS=$(stat -c "%a" /etc/shadow 2>/dev/null)
    if [[ "$PERMS" =~ ^0?00$ ]]; then
      STATUS="PASS"
      ACTUAL="Permissions: $PERMS"
    else
      STATUS="FAIL"
      ACTUAL="Permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="File not found"
  fi
  echo "    {\"cis_id\": \"6.1.2\", \"title\": \"Ensure permissions on /etc/shadow are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 000\", \"severity\": \"HIGH\", \"remediation\": \"Set permissions: sudo chmod 000 /etc/shadow\"},"
  
  # CIS 6.1.3: Ensure permissions on /etc/group are configured
  if [[ -f "/etc/group" ]]; then
    PERMS=$(stat -c "%a" /etc/group 2>/dev/null)
    if [[ "$PERMS" == "644" ]]; then
      STATUS="PASS"
      ACTUAL="Permissions: $PERMS"
    else
      STATUS="FAIL"
      ACTUAL="Permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="File not found"
  fi
  echo "    {\"cis_id\": \"6.1.3\", \"title\": \"Ensure permissions on /etc/group are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 644\", \"severity\": \"MEDIUM\", \"remediation\": \"Set permissions: sudo chmod 644 /etc/group\"},"
  
  # CIS 6.1.4: Ensure permissions on /etc/gshadow are configured
  if [[ -f "/etc/gshadow" ]]; then
    PERMS=$(stat -c "%a" /etc/gshadow 2>/dev/null)
    if [[ "$PERMS" =~ ^0?00$ ]]; then
      STATUS="PASS"
      ACTUAL="Permissions: $PERMS"
    else
      STATUS="FAIL"
      ACTUAL="Permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="File not found"
  fi
  echo "    {\"cis_id\": \"6.1.4\", \"title\": \"Ensure permissions on /etc/gshadow are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 000\", \"severity\": \"HIGH\", \"remediation\": \"Set permissions: sudo chmod 000 /etc/gshadow\"},"
  
  # CIS 6.2.1: Ensure no world writable files exist (simplified check)
  WORLD_WRITABLE=$(find / -xdev -type f -perm -0002 2>/dev/null | wc -l)
  if [[ "$WORLD_WRITABLE" -eq 0 ]]; then
    STATUS="PASS"
    ACTUAL="No world-writable files"
  else
    STATUS="FAIL"
    ACTUAL="Found $WORLD_WRITABLE world-writable files"
  fi
  echo "    {\"cis_id\": \"6.2.1\", \"title\": \"Ensure no world writable files exist\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"No world-writable files\", \"severity\": \"HIGH\", \"remediation\": \"Review and correct world-writable files\"},"
  
  # CIS 6.2.2: Ensure no unowned files or directories exist (simplified check)
  UNOWNED=$(find / -xdev \( -nouser -o -nogroup \) 2>/dev/null | wc -l)
  if [[ "$UNOWNED" -eq 0 ]]; then
    STATUS="PASS"
    ACTUAL="No unowned files or directories"
  else
    STATUS="FAIL"
    ACTUAL="Found $UNOWNED unowned files/directories"
  fi
  echo "    {\"cis_id\": \"6.2.2\", \"title\": \"Ensure no unowned files or directories exist\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"No unowned files\", \"severity\": \"MEDIUM\", \"remediation\": \"Review and correct unowned files\"},"
  
  # CIS 6.2.13: Audit SUID executables (count only, simplified)
  SUID_COUNT=$(find / -xdev -type f -perm -4000 2>/dev/null | wc -l)
  echo "    {\"cis_id\": \"6.2.13\", \"title\": \"Audit SUID executables\", \"status\": \"PASS\", \"actual_value\": \"Found $SUID_COUNT SUID files\", \"expected_value\": \"Review against baseline\", \"severity\": \"LOW\", \"remediation\": \"Review SUID files: find / -xdev -type f -perm -4000\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

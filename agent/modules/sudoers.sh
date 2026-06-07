#!/bin/bash
################################################################################
# TeX — Sudo Security Audit Module
# CIS Section 5.4: sudo Configuration
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="sudoers"

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 5.4.2: Ensure sudo commands use pty
  if grep -r "^Defaults use_pty" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | grep -q .; then
    STATUS="PASS"
    ACTUAL="use_pty enabled"
  else
    STATUS="FAIL"
    ACTUAL="use_pty not configured"
  fi
  echo "    {\"cis_id\": \"5.4.2\", \"title\": \"Ensure sudo commands use pty\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Defaults use_pty configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Add 'Defaults use_pty' to /etc/sudoers\"},"
  
  # CIS 5.4.3: Ensure sudo log file exists
  if grep -r "^Defaults logfile" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | grep -q .; then
    STATUS="PASS"
    ACTUAL=$(grep -r "^Defaults logfile" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | head -1)
  else
    STATUS="FAIL"
    ACTUAL="logfile not configured"
  fi
  echo "    {\"cis_id\": \"5.4.3\", \"title\": \"Ensure sudo log file exists\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Defaults logfile configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Add 'Defaults logfile' to /etc/sudoers\"},"
  
  # CIS 5.4.4: Ensure users are restricted to dedicated log file for sudo
  if grep -r "^Defaults logfile=" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | grep -q .; then
    STATUS="PASS"
    ACTUAL="dedicated logfile configured"
  else
    STATUS="FAIL"
    ACTUAL="dedicated logfile not configured"
  fi
  echo "    {\"cis_id\": \"5.4.4\", \"title\": \"Ensure users are restricted to dedicated log file for sudo\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Dedicated logfile configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Configure dedicated sudo logfile\"},"
  
  # CIS 5.4.5: Ensure sudo authentication timeout is configured correctly
  if grep -r "^Defaults timestamp_timeout" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | grep -q .; then
    STATUS="PASS"
    ACTUAL=$(grep -r "^Defaults timestamp_timeout" /etc/sudoers /etc/sudoers.d/ 2>/dev/null | head -1)
  else
    STATUS="FAIL"
    ACTUAL="timestamp_timeout not configured"
  fi
  echo "    {\"cis_id\": \"5.4.5\", \"title\": \"Ensure sudo authentication timeout is configured correctly\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Defaults timestamp_timeout configured\", \"severity\": \"LOW\", \"remediation\": \"Set timestamp_timeout in /etc/sudoers\"},"
  
  # CIS 5.4.6: Ensure access to the sudoers files is restricted
  if [[ -f "/etc/sudoers" ]]; then
    PERMS=$(stat -c "%a" /etc/sudoers 2>/dev/null)
    if [[ "$PERMS" == "440" ]]; then
      STATUS="PASS"
      ACTUAL="Permissions: $PERMS"
    else
      STATUS="FAIL"
      ACTUAL="Permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="sudoers file not found"
  fi
  echo "    {\"cis_id\": \"5.4.6\", \"title\": \"Ensure access to the sudoers files is restricted\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 440\", \"severity\": \"MEDIUM\", \"remediation\": \"Set correct permissions: sudo chmod 440 /etc/sudoers\"},"
  
  # CIS 5.4.7: Ensure sudoers.d directory is configured
  if [[ -d "/etc/sudoers.d" ]]; then
    PERMS=$(stat -c "%a" /etc/sudoers.d 2>/dev/null)
    if [[ "$PERMS" == "750" ]]; then
      STATUS="PASS"
      ACTUAL="sudoers.d exists with correct permissions"
    else
      STATUS="FAIL"
      ACTUAL="sudoers.d exists with permissions: $PERMS"
    fi
  else
    STATUS="FAIL"
    ACTUAL="sudoers.d directory not found"
  fi
  echo "    {\"cis_id\": \"5.4.7\", \"title\": \"Ensure sudoers.d directory is configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Permissions: 750\", \"severity\": \"MEDIUM\", \"remediation\": \"Create /etc/sudoers.d and set permissions to 750\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

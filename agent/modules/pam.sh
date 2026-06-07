#!/bin/bash
################################################################################
# TeX — PAM Stack Configuration Audit Module
# CIS Section 5.3-5.4: PAM Configuration
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="pam"
PWQUALITY_FILE="/etc/security/pwquality.conf"

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 5.3.1: Ensure password creation requirements are configured
  if [[ -f "$PWQUALITY_FILE" ]]; then
    if grep -q "^minlen" "$PWQUALITY_FILE"; then
      STATUS="PASS"
      ACTUAL=$(grep "^minlen" "$PWQUALITY_FILE" | head -1)
    else
      STATUS="FAIL"
      ACTUAL="minlen parameter not configured"
    fi
  else
    STATUS="FAIL"
    ACTUAL="pwquality.conf not found"
  fi
  echo "    {\"cis_id\": \"5.3.1\", \"title\": \"Ensure password creation requirements are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"minlen >= 14\", \"severity\": \"HIGH\", \"remediation\": \"Configure /etc/security/pwquality.conf with password complexity requirements\"},"
  
  # CIS 5.3.2: Ensure lockout for failed password attempts is configured
  if [[ -f "/etc/pam.d/common-auth" ]] && grep -q "pam_tally" "/etc/pam.d/common-auth"; then
    STATUS="PASS"
    ACTUAL="pam_tally configured"
  else
    STATUS="FAIL"
    ACTUAL="pam_tally not configured"
  fi
  echo "    {\"cis_id\": \"5.3.2\", \"title\": \"Ensure lockout for failed password attempts is configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"pam_tally or pam_faillock configured\", \"severity\": \"HIGH\", \"remediation\": \"Configure pam_tally or pam_faillock in /etc/pam.d/common-auth\"},"
  
  # CIS 5.3.3: Ensure password reuse is limited
  if [[ -f "$PWQUALITY_FILE" ]] && grep -q "^remember" "$PWQUALITY_FILE"; then
    STATUS="PASS"
    ACTUAL=$(grep "^remember" "$PWQUALITY_FILE" | head -1)
  else
    STATUS="FAIL"
    ACTUAL="remember parameter not configured"
  fi
  echo "    {\"cis_id\": \"5.3.3\", \"title\": \"Ensure password reuse is limited\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"remember >= 5\", \"severity\": \"MEDIUM\", \"remediation\": \"Set remember parameter in /etc/pam.d/common-password\"},"
  
  # CIS 5.3.4: Ensure PAM password quality requirements for the root user are configured
  if [[ -f "$PWQUALITY_FILE" ]] && grep -q "^enforce_for_root" "$PWQUALITY_FILE"; then
    STATUS="PASS"
    ACTUAL="enforce_for_root enabled"
  else
    STATUS="FAIL"
    ACTUAL="enforce_for_root not configured"
  fi
  echo "    {\"cis_id\": \"5.3.4\", \"title\": \"Ensure PAM password quality requirements for the root user are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"enforce_for_root configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Add enforce_for_root to /etc/security/pwquality.conf\"},"
  
  # CIS 5.4.1.1: Ensure sudo is installed
  if command -v sudo &> /dev/null; then
    STATUS="PASS"
    ACTUAL="sudo installed"
  else
    STATUS="FAIL"
    ACTUAL="sudo not installed"
  fi
  echo "    {\"cis_id\": \"5.4.1.1\", \"title\": \"Ensure sudo is installed\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"sudo installed\", \"severity\": \"MEDIUM\", \"remediation\": \"Install sudo: sudo apt install sudo\"},"
  
  # CIS 5.4.1.2: Ensure sudo uses pty
  if [[ -f "/etc/sudoers" ]] && grep -q "^Defaults use_pty" "/etc/sudoers"; then
    STATUS="PASS"
    ACTUAL="use_pty enabled"
  else
    STATUS="FAIL"
    ACTUAL="use_pty not configured"
  fi
  echo "    {\"cis_id\": \"5.4.1.2\", \"title\": \"Ensure sudo uses pty\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Defaults use_pty configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Add 'Defaults use_pty' to /etc/sudoers\"},"
  
  # CIS 5.4.1.3: Ensure sudo log file exists
  if [[ -f "/etc/sudoers" ]] && grep -q "^Defaults logfile" "/etc/sudoers"; then
    STATUS="PASS"
    ACTUAL="logfile configured"
  else
    STATUS="FAIL"
    ACTUAL="logfile not configured"
  fi
  echo "    {\"cis_id\": \"5.4.1.3\", \"title\": \"Ensure sudo log file exists\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Defaults logfile='/var/log/sudo.log' configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Add 'Defaults logfile' to /etc/sudoers\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

#!/bin/bash
################################################################################
# TeX — SSH Configuration Audit Module
# CIS Section 5.2: SSH Server Configuration
# Version: 1.0
################################################################################

set -o pipefail

SSHD_CONFIG="${SSHD_CONFIG:-/etc/ssh/sshd_config}"
TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="ssh"

# Helper function to check config parameter
check_ssh_param() {
  local param=$1
  local expected=$2
  local severity=$3
  local cis_id=$4
  local title=$5
  
  if [[ ! -f "$SSHD_CONFIG" ]]; then
    echo "{\"cis_id\": \"$cis_id\", \"title\": \"$title\", \"status\": \"FAIL\", \"actual_value\": \"File not found\", \"expected_value\": \"$expected\", \"severity\": \"$severity\", \"remediation\": \"SSH config file not found\"}"
    return
  fi
  
  # Handle case-insensitive matching
  local actual=$(grep -i "^${param}" "$SSHD_CONFIG" | head -1)
  
  if [[ -z "$actual" ]]; then
    actual="(parameter not set)"
    STATUS="FAIL"
  else
    # Check if value matches expected
    if [[ "$actual" =~ $expected ]]; then
      STATUS="PASS"
    else
      STATUS="FAIL"
    fi
  fi
  
  echo "{\"cis_id\": \"$cis_id\", \"title\": \"$title\", \"status\": \"$STATUS\", \"actual_value\": \"$actual\", \"expected_value\": \"$expected\", \"severity\": \"$severity\", \"remediation\": \"Set $param to $expected in /etc/ssh/sshd_config\"}"
}

# Generate JSON output
{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 5.2.1: SSH Protocol
  echo -n "    "
  check_ssh_param "Protocol" "^Protocol\\s+2$" "CRITICAL" "5.2.1" "Ensure SSH Protocol is set to 2"
  echo ","
  
  # CIS 5.2.4: SSH MaxAuthTries
  echo -n "    "
  check_ssh_param "MaxAuthTries" "^MaxAuthTries\\s+[1-4]$" "MEDIUM" "5.2.4" "Ensure SSH MaxAuthTries is set to 4 or less"
  echo ","
  
  # CIS 5.2.5: SSH IgnoreRhosts
  echo -n "    "
  check_ssh_param "IgnoreRhosts" "^IgnoreRhosts\\s+yes$" "HIGH" "5.2.5" "Ensure SSH IgnoreRhosts is enabled"
  echo ","
  
  # CIS 5.2.6: SSH HostbasedAuthentication
  echo -n "    "
  check_ssh_param "HostbasedAuthentication" "^HostbasedAuthentication\\s+no$" "HIGH" "5.2.6" "Ensure SSH HostbasedAuthentication is disabled"
  echo ","
  
  # CIS 5.2.8: SSH PermitRootLogin
  echo -n "    "
  check_ssh_param "PermitRootLogin" "^PermitRootLogin\\s+no$" "CRITICAL" "5.2.8" "Ensure SSH PermitRootLogin is disabled"
  echo ","
  
  # CIS 5.2.9: SSH PermitEmptyPasswords
  echo -n "    "
  check_ssh_param "PermitEmptyPasswords" "^PermitEmptyPasswords\\s+no$" "CRITICAL" "5.2.9" "Ensure SSH PermitEmptyPasswords is disabled"
  echo ","
  
  # CIS 5.2.10: SSH PermitUserEnvironment
  echo -n "    "
  check_ssh_param "PermitUserEnvironment" "^PermitUserEnvironment\\s+no$" "MEDIUM" "5.2.10" "Ensure SSH PermitUserEnvironment is disabled"
  echo ","
  
  # CIS 5.2.12: SSH X11Forwarding
  echo -n "    "
  check_ssh_param "X11Forwarding" "^X11Forwarding\\s+no$" "MEDIUM" "5.2.12" "Ensure SSH X11Forwarding is disabled"
  echo ","
  
  # CIS 5.2.13: SSH MaxStartups
  echo -n "    "
  check_ssh_param "MaxStartups" "^MaxStartups\\s+" "MEDIUM" "5.2.13" "Ensure SSH MaxStartups is configured"
  echo ","
  
  # CIS 5.2.14: SSH MaxSessions
  echo -n "    "
  check_ssh_param "MaxSessions" "^MaxSessions\\s+([1-9]|10)$" "LOW" "5.2.14" "Ensure SSH MaxSessions is set to 10 or less"
  echo ","
  
  # CIS 5.2.15: SSH LoginGraceTime
  echo -n "    "
  check_ssh_param "LoginGraceTime" "^LoginGraceTime\\s+" "LOW" "5.2.15" "Ensure SSH LoginGraceTime is set to one minute or less"
  echo ","
  
  # CIS 5.2.16: SSH Banner
  echo -n "    "
  check_ssh_param "Banner" "^Banner\\s+" "LOW" "5.2.16" "Ensure SSH Banner is configured"
  
  echo ""
  echo "  ]"
  echo "}"
} 

exit 0

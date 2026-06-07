#!/bin/bash
################################################################################
# TeX — Firewall Configuration Audit Module
# CIS Section 3.5: Firewall Configuration
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="firewall"

check_firewall_status() {
  if command -v ufw &> /dev/null; then
    ufw status 2>/dev/null | head -1
  else
    echo "UFW not installed"
  fi
}

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 3.5.1.1: Ensure ufw is installed
  if command -v ufw &> /dev/null; then
    STATUS="PASS"
    ACTUAL="ufw installed"
  else
    STATUS="FAIL"
    ACTUAL="ufw not installed"
  fi
  echo "    {\"cis_id\": \"3.5.1.1\", \"title\": \"Ensure ufw is installed\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"ufw installed\", \"severity\": \"MEDIUM\", \"remediation\": \"Install ufw: sudo apt install ufw\"},"
  
  # CIS 3.5.1.2: Ensure ufw service is enabled
  if command -v ufw &> /dev/null && systemctl is-enabled ufw &>/dev/null; then
    STATUS="PASS"
    ACTUAL="ufw enabled"
  else
    STATUS="FAIL"
    ACTUAL="ufw not enabled or installed"
  fi
  echo "    {\"cis_id\": \"3.5.1.2\", \"title\": \"Ensure ufw service is enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"ufw enabled\", \"severity\": \"HIGH\", \"remediation\": \"Enable ufw: sudo systemctl enable ufw && sudo systemctl start ufw\"},"
  
  # CIS 3.5.2.1: Ensure default deny firewall policy
  if command -v ufw &> /dev/null; then
    POLICY=$(ufw status 2>/dev/null | grep "Default:" | head -1)
    if [[ "$POLICY" =~ "deny (incoming)" ]] && [[ "$POLICY" =~ "allow (outgoing)" ]]; then
      STATUS="PASS"
      ACTUAL="$POLICY"
    else
      STATUS="FAIL"
      ACTUAL="$POLICY"
    fi
  else
    STATUS="FAIL"
    ACTUAL="ufw not installed"
  fi
  echo "    {\"cis_id\": \"3.5.2.1\", \"title\": \"Ensure default deny firewall policy\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Default: deny incoming, allow outgoing\", \"severity\": \"HIGH\", \"remediation\": \"Configure: sudo ufw default deny incoming && sudo ufw default allow outgoing\"},"
  
  # CIS 3.5.2.2: Ensure ufw loopback traffic is configured
  if command -v ufw &> /dev/null && ufw status numbered 2>/dev/null | grep -q "127.0.0.1"; then
    STATUS="PASS"
    ACTUAL="loopback configured"
  else
    STATUS="FAIL"
    ACTUAL="loopback not configured"
  fi
  echo "    {\"cis_id\": \"3.5.2.2\", \"title\": \"Ensure ufw loopback traffic is configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Loopback interface rules configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Configure loopback: sudo ufw allow in on lo && sudo ufw deny in from 127.0.0.1/8 to any port 22\"},"
  
  # CIS 3.5.2.3: Ensure outbound connections are configured (simplified)
  if command -v ufw &> /dev/null && ufw status 2>/dev/null | grep -q "allow out"; then
    STATUS="PASS"
    ACTUAL="outbound rules configured"
  else
    STATUS="FAIL"
    ACTUAL="outbound rules not properly configured"
  fi
  echo "    {\"cis_id\": \"3.5.2.3\", \"title\": \"Ensure outbound connections are configured\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Outbound rules configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Review and configure ufw outbound rules as needed\"},"
  
  # CIS 3.5.3.1: Ensure firewall rules exist for all open ports
  OPEN_PORTS=$(ss -tlnup 2>/dev/null | grep LISTEN | awk '{print $4}' | cut -d: -f2 | sort -u)
  if [[ -z "$OPEN_PORTS" ]]; then
    STATUS="PASS"
    ACTUAL="no listening ports"
  else
    STATUS="FAIL"
    ACTUAL="Listening ports: $(echo $OPEN_PORTS | tr '\n' ' ')"
  fi
  echo "    {\"cis_id\": \"3.5.3.1\", \"title\": \"Ensure firewall rules exist for all open ports\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"All open ports have firewall rules\", \"severity\": \"HIGH\", \"remediation\": \"Review open ports and create firewall rules for each\"},"
  
  # CIS 3.5.3.2: Ensure firewall rules exist for IPv6
  if command -v ufw &> /dev/null && ufw status 2>/dev/null | grep -q "v6"; then
    STATUS="PASS"
    ACTUAL="IPv6 rules configured"
  else
    STATUS="FAIL"
    ACTUAL="IPv6 rules not configured"
  fi
  echo "    {\"cis_id\": \"3.5.3.2\", \"title\": \"Ensure firewall rules exist for IPv6\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"IPv6 firewall rules configured\", \"severity\": \"MEDIUM\", \"remediation\": \"Configure ufw for IPv6 or disable IPv6 if not needed\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

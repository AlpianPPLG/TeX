#!/bin/bash
################################################################################
# TeX — Kernel Hardening Audit Module
# CIS Section 3.1-3.3: Kernel Parameters
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="kernel"

check_sysctl() {
  local param=$1
  local expected=$2
  local severity=$3
  local cis_id=$4
  local title=$5
  
  # Try to read from /proc/sys first, then fall back to sysctl
  local proc_path="/proc/sys/$(echo $param | tr '.' '/')"
  
  if [[ -r "$proc_path" ]]; then
    actual=$(cat "$proc_path" 2>/dev/null)
  else
    actual=$(sysctl -n "$param" 2>/dev/null)
  fi
  
  if [[ -z "$actual" ]]; then
    STATUS="FAIL"
    actual="(parameter not accessible)"
  elif [[ "$actual" == "$expected" ]]; then
    STATUS="PASS"
  else
    STATUS="FAIL"
  fi
  
  echo "{\"cis_id\": \"$cis_id\", \"title\": \"$title\", \"status\": \"$STATUS\", \"actual_value\": \"$param = $actual\", \"expected_value\": \"$param = $expected\", \"severity\": \"$severity\", \"remediation\": \"Set $param = $expected in /etc/sysctl.conf\"}"
}

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 3.1.1: Ensure IP forwarding is disabled
  echo -n "    "
  check_sysctl "net.ipv4.ip_forward" "0" "HIGH" "3.1.1" "Ensure IP forwarding is disabled"
  echo ","
  
  # CIS 3.2.1: Ensure ICMP redirects are not accepted
  echo -n "    "
  check_sysctl "net.ipv4.conf.all.accept_redirects" "0" "HIGH" "3.2.1" "Ensure ICMP redirects are not accepted"
  echo ","
  
  # CIS 3.2.2: Ensure secure ICMP redirects are not accepted
  echo -n "    "
  check_sysctl "net.ipv4.conf.all.secure_redirects" "0" "HIGH" "3.2.2" "Ensure secure ICMP redirects are not accepted"
  echo ","
  
  # CIS 3.2.3: Ensure dangerous ICMP redirects are not accepted
  echo -n "    "
  check_sysctl "net.ipv4.conf.default.accept_redirects" "0" "HIGH" "3.2.3" "Ensure dangerous ICMP redirects are not accepted"
  echo ","
  
  # CIS 3.3.1: Ensure source routed packets are not accepted
  echo -n "    "
  check_sysctl "net.ipv4.conf.all.send_redirects" "0" "MEDIUM" "3.3.1" "Ensure source routed packets are not accepted"
  echo ","
  
  # CIS 3.3.2: Ensure TCP SYN Cookies is enabled
  echo -n "    "
  check_sysctl "net.ipv4.tcp_syncookies" "1" "HIGH" "3.3.2" "Ensure TCP SYN Cookies is enabled"
  echo ","
  
  # CIS 3.4.1: Ensure ASLR is enabled
  echo -n "    "
  check_sysctl "kernel.randomize_va_space" "2" "HIGH" "3.4.1" "Ensure ASLR is enabled"
  echo ","
  
  # CIS 3.5.1.1: Ensure core dumps are restricted
  echo -n "    "
  check_sysctl "kernel.core_uses_pid" "1" "MEDIUM" "3.5.1.1" "Ensure core dumps are restricted"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

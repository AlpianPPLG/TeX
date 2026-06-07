#!/bin/bash
################################################################################
# TeX — Services Security Audit Module
# CIS Section 2: Services Configuration
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="services"

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 2.1.1: Ensure xinetd is not installed
  if ! dpkg -l 2>/dev/null | grep -q "^ii.*xinetd"; then
    STATUS="PASS"
    ACTUAL="xinetd not installed"
  else
    STATUS="FAIL"
    ACTUAL="xinetd installed"
  fi
  echo "    {\"cis_id\": \"2.1.1\", \"title\": \"Ensure xinetd is not installed\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"xinetd not installed\", \"severity\": \"HIGH\", \"remediation\": \"Remove xinetd: sudo apt purge xinetd\"},"
  
  # CIS 2.2.1: Ensure X11 Server is not installed
  if ! dpkg -l 2>/dev/null | grep -q "xserver-xorg"; then
    STATUS="PASS"
    ACTUAL="X11 not installed"
  else
    STATUS="FAIL"
    ACTUAL="X11 packages installed"
  fi
  echo "    {\"cis_id\": \"2.2.1\", \"title\": \"Ensure X11 Server is not installed\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"X11 not installed\", \"severity\": \"MEDIUM\", \"remediation\": \"Remove X11: sudo apt purge xserver-xorg-*\"},"
  
  # CIS 2.2.2: Ensure Avahi Server is not enabled (simplified check)
  if systemctl is-enabled avahi-daemon 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="Avahi enabled"
  else
    STATUS="PASS"
    ACTUAL="Avahi not enabled"
  fi
  echo "    {\"cis_id\": \"2.2.2\", \"title\": \"Ensure Avahi Server is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Avahi disabled\", \"severity\": \"MEDIUM\", \"remediation\": \"Disable Avahi: sudo systemctl disable avahi-daemon\"},"
  
  # CIS 2.3.1: Ensure Cups is not enabled
  if systemctl is-enabled cups 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="CUPS enabled"
  else
    STATUS="PASS"
    ACTUAL="CUPS not enabled"
  fi
  echo "    {\"cis_id\": \"2.3.1\", \"title\": \"Ensure Cups is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"CUPS disabled\", \"severity\": \"MEDIUM\", \"remediation\": \"Disable CUPS: sudo systemctl disable cups\"},"
  
  # CIS 2.4.1: Ensure DHCP Server is not enabled
  if systemctl is-enabled isc-dhcp-server 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="DHCP Server enabled"
  else
    STATUS="PASS"
    ACTUAL="DHCP Server not enabled"
  fi
  echo "    {\"cis_id\": \"2.4.1\", \"title\": \"Ensure DHCP Server is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"DHCP Server disabled\", \"severity\": \"HIGH\", \"remediation\": \"Disable DHCP: sudo systemctl disable isc-dhcp-server\"},"
  
  # CIS 2.5.1: Ensure DNS Server (BIND) is not enabled
  if systemctl is-enabled bind9 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="BIND DNS enabled"
  else
    STATUS="PASS"
    ACTUAL="BIND DNS not enabled"
  fi
  echo "    {\"cis_id\": \"2.5.1\", \"title\": \"Ensure DNS Server is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"DNS Server disabled\", \"severity\": \"MEDIUM\", \"remediation\": \"Disable BIND: sudo systemctl disable bind9\"},"
  
  # CIS 2.6.1: Ensure Samba is not enabled
  if systemctl is-enabled smbd 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="Samba enabled"
  else
    STATUS="PASS"
    ACTUAL="Samba not enabled"
  fi
  echo "    {\"cis_id\": \"2.6.1\", \"title\": \"Ensure Samba is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Samba disabled\", \"severity\": \"HIGH\", \"remediation\": \"Disable Samba: sudo systemctl disable smbd\"},"
  
  # CIS 2.7.1: Ensure HTTP Proxy Server is not enabled
  if systemctl is-enabled squid 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="Squid enabled"
  else
    STATUS="PASS"
    ACTUAL="Squid not enabled"
  fi
  echo "    {\"cis_id\": \"2.7.1\", \"title\": \"Ensure HTTP Proxy Server is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"Squid disabled\", \"severity\": \"MEDIUM\", \"remediation\": \"Disable Squid: sudo systemctl disable squid\"},"
  
  # CIS 2.8.1: Ensure NFS Server is not enabled
  if systemctl is-enabled nfs-server 2>/dev/null | grep -q "enabled"; then
    STATUS="FAIL"
    ACTUAL="NFS Server enabled"
  else
    STATUS="PASS"
    ACTUAL="NFS Server not enabled"
  fi
  echo "    {\"cis_id\": \"2.8.1\", \"title\": \"Ensure NFS Server is not enabled\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"NFS disabled\", \"severity\": \"HIGH\", \"remediation\": \"Disable NFS: sudo systemctl disable nfs-server\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

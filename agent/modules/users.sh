#!/bin/bash
################################################################################
# TeX — User Account Security Audit Module
# CIS Section 5.1: User and Group Settings
# Version: 1.0
################################################################################

set -o pipefail

TIMESTAMP=$(date +%s)
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
MODULE="users"
LOGIN_DEFS="/etc/login.defs"

{
  echo "{"
  echo "  \"module\": \"$MODULE\","
  echo "  \"status\": \"COMPLETED\","
  echo "  \"timestamp\": $TIMESTAMP,"
  echo "  \"hostname\": \"$HOSTNAME\","
  echo "  \"checks\": ["
  
  # CIS 5.1.1: Ensure password expiration is 365 days or less
  if [[ -f "$LOGIN_DEFS" ]]; then
    PASS_MAX_DAYS=$(grep "^PASS_MAX_DAYS" "$LOGIN_DEFS" | awk '{print $2}')
    if [[ -n "$PASS_MAX_DAYS" ]] && [[ $PASS_MAX_DAYS -le 365 ]]; then
      STATUS="PASS"
      ACTUAL="PASS_MAX_DAYS = $PASS_MAX_DAYS"
    else
      STATUS="FAIL"
      ACTUAL="PASS_MAX_DAYS = ${PASS_MAX_DAYS:-not set}"
    fi
  else
    STATUS="FAIL"
    ACTUAL="login.defs not found"
  fi
  echo "    {\"cis_id\": \"5.1.1\", \"title\": \"Ensure password expiration is 365 days or less\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"PASS_MAX_DAYS <= 365\", \"severity\": \"MEDIUM\", \"remediation\": \"Set PASS_MAX_DAYS in /etc/login.defs\"},"
  
  # CIS 5.1.2: Ensure minimum days between password changes is 1 or greater
  if [[ -f "$LOGIN_DEFS" ]]; then
    PASS_MIN_DAYS=$(grep "^PASS_MIN_DAYS" "$LOGIN_DEFS" | awk '{print $2}')
    if [[ -n "$PASS_MIN_DAYS" ]] && [[ $PASS_MIN_DAYS -ge 1 ]]; then
      STATUS="PASS"
      ACTUAL="PASS_MIN_DAYS = $PASS_MIN_DAYS"
    else
      STATUS="FAIL"
      ACTUAL="PASS_MIN_DAYS = ${PASS_MIN_DAYS:-not set}"
    fi
  else
    STATUS="FAIL"
    ACTUAL="login.defs not found"
  fi
  echo "    {\"cis_id\": \"5.1.2\", \"title\": \"Ensure minimum days between password changes is 1 or greater\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"PASS_MIN_DAYS >= 1\", \"severity\": \"LOW\", \"remediation\": \"Set PASS_MIN_DAYS in /etc/login.defs\"},"
  
  # CIS 5.1.3: Ensure password expiration warning days is 14 or greater
  if [[ -f "$LOGIN_DEFS" ]]; then
    PASS_WARN_AGE=$(grep "^PASS_WARN_AGE" "$LOGIN_DEFS" | awk '{print $2}')
    if [[ -n "$PASS_WARN_AGE" ]] && [[ $PASS_WARN_AGE -ge 14 ]]; then
      STATUS="PASS"
      ACTUAL="PASS_WARN_AGE = $PASS_WARN_AGE"
    else
      STATUS="FAIL"
      ACTUAL="PASS_WARN_AGE = ${PASS_WARN_AGE:-not set}"
    fi
  else
    STATUS="FAIL"
    ACTUAL="login.defs not found"
  fi
  echo "    {\"cis_id\": \"5.1.3\", \"title\": \"Ensure password expiration warning days is 14 or greater\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"PASS_WARN_AGE >= 14\", \"severity\": \"LOW\", \"remediation\": \"Set PASS_WARN_AGE in /etc/login.defs\"},"
  
  # CIS 5.1.4: Ensure inactive password lock is 30 days or less
  if [[ -f "$LOGIN_DEFS" ]]; then
    INACTIVE=$(grep "^INACTIVE" "$LOGIN_DEFS" | awk '{print $2}')
    if [[ -n "$INACTIVE" ]] && [[ $INACTIVE -le 30 ]] && [[ $INACTIVE -ge 0 ]]; then
      STATUS="PASS"
      ACTUAL="INACTIVE = $INACTIVE"
    else
      STATUS="FAIL"
      ACTUAL="INACTIVE = ${INACTIVE:-not set}"
    fi
  else
    STATUS="FAIL"
    ACTUAL="login.defs not found"
  fi
  echo "    {\"cis_id\": \"5.1.4\", \"title\": \"Ensure inactive password lock is 30 days or less\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"INACTIVE <= 30\", \"severity\": \"MEDIUM\", \"remediation\": \"Set INACTIVE in /etc/login.defs\"},"
  
  # CIS 5.1.5: Ensure all users have a valid login shell
  INVALID_SHELLS=$(awk -F: '($NF != \"bin/false\" && $NF != \"bin/true\" && $NF != \"nologin\" && $NF != \"/bin/false\" && $NF != \"/bin/true\" && $NF != \"/usr/sbin/nologin\" && $3 >= 1000 && $1 != \"nfsnobody\") {print}' /etc/passwd 2>/dev/null | wc -l)
  if [[ $INVALID_SHELLS -eq 0 ]]; then
    STATUS="PASS"
    ACTUAL="All users have valid login shells"
  else
    STATUS="FAIL"
    ACTUAL="$INVALID_SHELLS users with invalid shells"
  fi
  echo "    {\"cis_id\": \"5.1.5\", \"title\": \"Ensure all users have a valid login shell\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"All users have valid login shells\", \"severity\": \"MEDIUM\", \"remediation\": \"Review and fix user shells in /etc/passwd\"},"
  
  # CIS 5.2.1: Ensure accounts in /etc/passwd use shadowed passwords
  NO_SHADOW=$(awk -F: '($2 != \"x\" && $2 != \"!\" && $2 != \"*\") {print}' /etc/passwd 2>/dev/null | wc -l)
  if [[ $NO_SHADOW -eq 0 ]]; then
    STATUS="PASS"
    ACTUAL="All accounts use shadowed passwords"
  else
    STATUS="FAIL"
    ACTUAL="$NO_SHADOW accounts not using shadowed passwords"
  fi
  echo "    {\"cis_id\": \"5.2.1\", \"title\": \"Ensure accounts in /etc/passwd use shadowed passwords\", \"status\": \"$STATUS\", \"actual_value\": \"$ACTUAL\", \"expected_value\": \"All accounts use shadowed passwords\", \"severity\": \"HIGH\", \"remediation\": \"Enable password shadowing for all accounts\"}"
  
  echo ""
  echo "  ]"
  echo "}"
}

exit 0

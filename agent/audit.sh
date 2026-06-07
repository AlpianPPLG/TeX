#!/bin/bash
################################################################################
# TeX — Security Compliance Auditor
# Master Orchestration Script
# Version: 1.0
# Date: 07 June 2026
#
# This script orchestrates all modular audit probes and assembles raw audit
# output into a structured JSON file with integrity signing.
################################################################################

set -o pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/audit.conf"

# Validate audit.conf exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo -e "${RED}ERROR: audit.conf not found at ${CONFIG_FILE}${NC}" >&2
  exit 1
fi

# Source configuration
source "$CONFIG_FILE"

# Validate OUTPUT_DIR contains only safe path characters
if [[ ! "$OUTPUT_DIR" =~ ^[a-zA-Z0-9_./-]+$ ]]; then
  echo -e "${RED}ERROR: Invalid OUTPUT_DIR value in audit.conf${NC}" >&2
  exit 1
fi

# Create output directory if it doesn't exist
OUTPUT_DIR_ABS="$(cd "$SCRIPT_DIR" && mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)"
if [[ ! -d "$OUTPUT_DIR_ABS" ]]; then
  echo -e "${RED}ERROR: Failed to create output directory${NC}" >&2
  exit 1
fi

RAW_AUDIT_FILE="${OUTPUT_DIR_ABS}/raw_audit.json"
AUDIT_LOG_FILE="${OUTPUT_DIR_ABS}/audit.log"
TEMP_DIR="/tmp/tex_audit_$$"
MODULES_DIR="${SCRIPT_DIR}/modules"

# Cleanup function
cleanup() {
  if [[ -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}

trap cleanup EXIT

# Create temp directory
mkdir -p "$TEMP_DIR"

# Collect system metadata
HOSTNAME=$(hostname -f 2>/dev/null || hostname)
OS_NAME=$(lsb_release -d -s 2>/dev/null || uname -s)
KERNEL_VERSION=$(uname -r)
AUDIT_TIMESTAMP=$(date +%s)
AUDIT_USER=$(whoami)
TEX_VERSION="1.0.0"

echo "Starting TeX Security Audit..." | tee "$AUDIT_LOG_FILE"
echo "Hostname: $HOSTNAME" | tee -a "$AUDIT_LOG_FILE"
echo "OS: $OS_NAME" | tee -a "$AUDIT_LOG_FILE"
echo "Timestamp: $AUDIT_TIMESTAMP" | tee -a "$AUDIT_LOG_FILE"
echo "" | tee -a "$AUDIT_LOG_FILE"

# Initialize modules array
declare -A MODULE_RESULTS

# Module execution timeout
TIMEOUT=$((AUDIT_TIMEOUT > 0 ? AUDIT_TIMEOUT : 120))

# Execute each enabled module
MODULES=("ssh" "firewall" "pam" "sudoers" "filesystem" "kernel" "users" "services")

for MODULE in "${MODULES[@]}"; do
  MODULE_VAR="ENABLE_${MODULE^^}"
  
  # Check if module is enabled in config
  if [[ "${!MODULE_VAR,,}" != "yes" ]]; then
    echo "Skipping ${MODULE} (disabled in config)" | tee -a "$AUDIT_LOG_FILE"
    continue
  fi
  
  MODULE_SCRIPT="${MODULES_DIR}/${MODULE}.sh"
  
  if [[ ! -f "$MODULE_SCRIPT" ]]; then
    echo -e "${YELLOW}WARNING: Module script not found: ${MODULE_SCRIPT}${NC}" | tee -a "$AUDIT_LOG_FILE"
    continue
  fi
  
  echo "Running ${MODULE} audit..." | tee -a "$AUDIT_LOG_FILE"
  
  MODULE_OUTPUT_FILE="${TEMP_DIR}/${MODULE}_output.json"
  
  # Execute module with timeout
  if timeout "$TIMEOUT" bash "$MODULE_SCRIPT" > "$MODULE_OUTPUT_FILE" 2>&1; then
    MODULE_RESULTS[$MODULE]="COMPLETED"
    echo -e "${GREEN}✓ ${MODULE} completed${NC}" | tee -a "$AUDIT_LOG_FILE"
  else
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 124 ]]; then
      MODULE_RESULTS[$MODULE]="TIMEOUT"
      echo -e "${RED}✗ ${MODULE} timed out${NC}" | tee -a "$AUDIT_LOG_FILE"
    else
      MODULE_RESULTS[$MODULE]="ERROR"
      echo -e "${RED}✗ ${MODULE} failed with exit code ${EXIT_CODE}${NC}" | tee -a "$AUDIT_LOG_FILE"
    fi
  fi
done

# Assemble raw_audit.json
echo "Assembling raw audit output..." | tee -a "$AUDIT_LOG_FILE"

{
  echo "{"
  echo "  \"audit_metadata\": {"
  echo "    \"timestamp\": $AUDIT_TIMESTAMP,"
  echo "    \"hostname\": \"$HOSTNAME\","
  echo "    \"os_name\": \"$OS_NAME\","
  echo "    \"kernel_version\": \"$KERNEL_VERSION\","
  echo "    \"audit_user\": \"$AUDIT_USER\","
  echo "    \"tex_version\": \"$TEX_VERSION\""
  echo "  },"
  echo "  \"modules\": {"
  
  FIRST=true
  for MODULE in "${MODULES[@]}"; do
    MODULE_OUTPUT_FILE="${TEMP_DIR}/${MODULE}_output.json"
    
    if [[ -f "$MODULE_OUTPUT_FILE" ]]; then
      if [[ $FIRST == true ]]; then
        FIRST=false
      else
        echo ","
      fi
      
      # Extract module content without wrapping braces
      MODULE_CONTENT=$(cat "$MODULE_OUTPUT_FILE" 2>/dev/null | sed 's/^{//; s/}$//')
      echo "    \"$MODULE\": {$MODULE_CONTENT}"
    fi
  done
  
  echo ""
  echo "  }"
  echo "}"
} > "$RAW_AUDIT_FILE"

if [[ -f "$RAW_AUDIT_FILE" ]]; then
  echo -e "${GREEN}✓ Raw audit saved to: ${RAW_AUDIT_FILE}${NC}" | tee -a "$AUDIT_LOG_FILE"
else
  echo -e "${RED}✗ Failed to create raw audit file${NC}" | tee -a "$AUDIT_LOG_FILE"
  exit 1
fi

# Generate HMAC integrity signature if enabled
if [[ "${ENABLE_HMAC_SIGNING,,}" == "yes" ]]; then
  echo "Generating HMAC integrity signature..." | tee -a "$AUDIT_LOG_FILE"
  
  SESSION_KEY=$(openssl rand -hex 32 2>/dev/null)
  if [[ -z "$SESSION_KEY" ]]; then
    echo -e "${YELLOW}WARNING: OpenSSL not available, skipping HMAC signature${NC}" | tee -a "$AUDIT_LOG_FILE"
  else
    HMAC=$(openssl dgst -sha256 -hmac "$SESSION_KEY" "$RAW_AUDIT_FILE" 2>/dev/null | awk '{print $2}')
    
    if [[ -n "$HMAC" ]]; then
      echo "$HMAC" > "${RAW_AUDIT_FILE}.sig"
      echo "$SESSION_KEY" > "${RAW_AUDIT_FILE}.key"
      chmod 600 "${RAW_AUDIT_FILE}.key"
      echo -e "${GREEN}✓ HMAC signature created${NC}" | tee -a "$AUDIT_LOG_FILE"
    fi
  fi
fi

echo "" | tee -a "$AUDIT_LOG_FILE"
echo -e "${GREEN}Audit completed successfully!${NC}" | tee -a "$AUDIT_LOG_FILE"
echo "Audit log saved to: $AUDIT_LOG_FILE" | tee -a "$AUDIT_LOG_FILE"

exit 0

#!/usr/bin/env python3
"""
TeX JSON Schema Validator
Validates raw audit and scored output against JSON Schema Draft-07
Version: 1.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple


class SchemaValidator:
    """JSON schema validator for audit outputs"""
    
    # JSON Schema Draft-07 for raw_audit.json
    RAW_AUDIT_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "TeXRawAudit",
        "type": "object",
        "required": ["audit_metadata", "modules"],
        "properties": {
            "audit_metadata": {
                "type": "object",
                "required": ["timestamp", "hostname"],
                "properties": {
                    "timestamp": {"type": "integer"},
                    "hostname": {"type": "string"},
                    "os_name": {"type": "string"},
                    "kernel_version": {"type": "string"},
                    "audit_user": {"type": "string"},
                    "tex_version": {"type": "string"},
                }
            },
            "modules": {"type": "object"}
        }
    }
    
    # JSON Schema Draft-07 for audit_summary.json
    AUDIT_SUMMARY_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "TeXAuditSummary",
        "type": "object",
        "required": ["generated_at", "hostname", "spi", "category_scores", "findings_by_severity", "all_checks"],
        "properties": {
            "generated_at": {"type": "integer"},
            "hostname": {"type": "string"},
            "spi": {
                "type": "number",
                "minimum": 0,
                "maximum": 100
            },
            "category_scores": {
                "type": "object",
                "properties": {
                    "ssh": {"type": "number", "minimum": 0, "maximum": 100},
                    "firewall": {"type": "number", "minimum": 0, "maximum": 100},
                    "pam": {"type": "number", "minimum": 0, "maximum": 100},
                    "sudoers": {"type": "number", "minimum": 0, "maximum": 100},
                    "filesystem": {"type": "number", "minimum": 0, "maximum": 100},
                    "kernel": {"type": "number", "minimum": 0, "maximum": 100},
                    "users": {"type": "number", "minimum": 0, "maximum": 100},
                    "services": {"type": "number", "minimum": 0, "maximum": 100},
                }
            },
            "findings_by_severity": {
                "type": "object",
                "properties": {
                    "CRITICAL": {"type": "array"},
                    "HIGH": {"type": "array"},
                    "MEDIUM": {"type": "array"},
                    "LOW": {"type": "array"},
                    "PASS": {"type": "array"},
                }
            },
            "all_checks": {"type": "array"}
        }
    }
    
    @staticmethod
    def validate_json(data: Dict, schema: Dict) -> Tuple[bool, str]:
        """
        Basic JSON schema validation (simplified without jsonschema library)
        Returns: (is_valid, error_message)
        """
        try:
            # Check required fields
            required = schema.get("required", [])
            for field in required:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Type checking
            if data.get("audit_metadata") is not None:
                if not isinstance(data.get("audit_metadata"), dict):
                    return False, "audit_metadata must be an object"
            
            # SPI bounds check
            if "spi" in data:
                spi = data["spi"]
                if not isinstance(spi, (int, float)) or spi < 0 or spi > 100:
                    return False, f"SPI must be between 0 and 100, got {spi}"
            
            return True, ""
        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_raw_audit(audit_file: str) -> Tuple[bool, str]:
        """Validate raw audit JSON file"""
        try:
            with open(audit_file, 'r') as f:
                data = json.load(f)
            
            is_valid, error = SchemaValidator.validate_json(
                data,
                SchemaValidator.RAW_AUDIT_SCHEMA
            )
            
            return is_valid, error
        
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except FileNotFoundError:
            return False, f"File not found: {audit_file}"
    
    @staticmethod
    def validate_audit_summary(summary_file: str) -> Tuple[bool, str]:
        """Validate audit summary JSON file"""
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
            
            is_valid, error = SchemaValidator.validate_json(
                data,
                SchemaValidator.AUDIT_SUMMARY_SCHEMA
            )
            
            return is_valid, error
        
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except FileNotFoundError:
            return False, f"File not found: {summary_file}"


def main():
    """Main entry point for validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TeX JSON Schema Validator")
    parser.add_argument("--audit", help="Validate raw audit JSON")
    parser.add_argument("--summary", help="Validate audit summary JSON")
    
    args = parser.parse_args()
    
    if args.audit:
        is_valid, error = SchemaValidator.validate_raw_audit(args.audit)
        if is_valid:
            print(f"[OK] {args.audit} is valid")
            sys.exit(0)
        else:
            print(f"[ERROR] {args.audit}: {error}", file=sys.stderr)
            sys.exit(1)
    
    if args.summary:
        is_valid, error = SchemaValidator.validate_audit_summary(args.summary)
        if is_valid:
            print(f"[OK] {args.summary} is valid")
            sys.exit(0)
        else:
            print(f"[ERROR] {args.summary}: {error}", file=sys.stderr)
            sys.exit(1)
    
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

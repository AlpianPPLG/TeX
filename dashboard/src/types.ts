/**
 * TeX Dashboard - Shared Type Definitions
 * Version: 1.0
 */

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'PASS';
export type CheckStatus = 'FAIL' | 'PASS' | 'MANUAL';
export type ProbeModule = 'ssh' | 'firewall' | 'pam' | 'sudoers' | 'filesystem' | 'kernel' | 'users' | 'services';

export interface AuditCheck {
  cis_id: string;
  module: string;
  title: string;
  status: CheckStatus;
  actual_value: string;
  expected_value: string;
  severity: Severity;
  remediation: string;
  nist_800_53?: string[];
}

export interface AuditSummary {
  generated_at: number;
  hostname: string;
  spi: number;
  category_scores: Record<ProbeModule | string, number>;
  findings_by_severity: Record<Severity, AuditCheck[]>;
  all_checks: AuditCheck[];
  audit_metadata?: {
    timestamp: number;
    hostname: string;
    os_name?: string;
    kernel_version?: string;
    audit_user?: string;
    tex_version?: string;
  };
}

export interface RadarPoint {
  x: number;
  y: number;
  label: string;
}

export interface SVGRadarConfig {
  centerX: number;
  centerY: number;
  radius: number;
  axisCount: number;
}

/**
 * TeX Dashboard — Shared Type Definitions
 * Mirrors the engine's `audit_summary.json` contract (see engine/scorer.py).
 */

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'PASS'
export type CheckStatus = 'FAIL' | 'PASS' | 'MANUAL'
export type ProbeModule =
  | 'ssh'
  | 'firewall'
  | 'pam'
  | 'sudoers'
  | 'filesystem'
  | 'kernel'
  | 'users'
  | 'services'

export interface AuditCheck {
  cis_id: string
  module: string
  title: string
  status: CheckStatus
  actual_value: string
  expected_value: string
  severity: Severity
  base_severity?: Severity
  weight?: number
  remediation: string
  nist_800_53?: string[]
}

export interface AuditMetadata {
  timestamp: number
  hostname: string
  os_name?: string
  kernel_version?: string
  audit_user?: string
  tex_version?: string
}

export interface AuditSummary {
  generated_at: number
  hostname: string
  spi: number
  category_scores: Record<string, number>
  findings_by_severity: Record<Severity, AuditCheck[]>
  all_checks: AuditCheck[]
  audit_metadata?: AuditMetadata
}

export const SEVERITY_ORDER: Severity[] = [
  'CRITICAL',
  'HIGH',
  'MEDIUM',
  'LOW',
  'PASS',
]

export const ACTIONABLE_SEVERITIES: Severity[] = [
  'CRITICAL',
  'HIGH',
  'MEDIUM',
  'LOW',
]

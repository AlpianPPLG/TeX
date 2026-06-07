/**
 * TeX Dashboard — Audit data access + presentation helpers.
 */

import summaryJson from '@/data/audit_summary.json'
import type { AuditCheck, AuditSummary, Severity } from './types'
import { ACTIONABLE_SEVERITIES, SEVERITY_ORDER } from './types'

export const auditSummary = summaryJson as unknown as AuditSummary

/** Tailwind / token metadata for each severity level. */
export const SEVERITY_META: Record<
  Severity,
  { label: string; dot: string; text: string; bg: string; ring: string }
> = {
  CRITICAL: {
    label: 'Critical',
    dot: 'bg-red-500',
    text: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-500/10',
    ring: 'ring-red-500/30',
  },
  HIGH: {
    label: 'High',
    dot: 'bg-orange-500',
    text: 'text-orange-600 dark:text-orange-400',
    bg: 'bg-orange-500/10',
    ring: 'ring-orange-500/30',
  },
  MEDIUM: {
    label: 'Medium',
    dot: 'bg-amber-500',
    text: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-500/10',
    ring: 'ring-amber-500/30',
  },
  LOW: {
    label: 'Low',
    dot: 'bg-blue-500',
    text: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-500/10',
    ring: 'ring-blue-500/30',
  },
  PASS: {
    label: 'Pass',
    dot: 'bg-emerald-500',
    text: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-500/10',
    ring: 'ring-emerald-500/30',
  },
}

export interface SpiBand {
  label: string
  tone: 'good' | 'warn' | 'bad'
  color: string
  description: string
}

export function getSpiBand(spi: number): SpiBand {
  if (spi >= 80)
    return {
      label: 'Strong',
      tone: 'good',
      color: 'text-emerald-500',
      description: 'This host is well-hardened against the CIS Benchmark.',
    }
  if (spi >= 60)
    return {
      label: 'Moderate',
      tone: 'warn',
      color: 'text-amber-500',
      description: 'Several controls require attention to improve posture.',
    }
  if (spi >= 40)
    return {
      label: 'Weak',
      tone: 'bad',
      color: 'text-orange-500',
      description: 'Significant hardening gaps detected across domains.',
    }
  return {
    label: 'Critical',
    tone: 'bad',
    color: 'text-red-500',
    description: 'Urgent remediation required — posture is critically low.',
  }
}

export function severityCounts(
  summary: AuditSummary
): Record<Severity, number> {
  const counts = {} as Record<Severity, number>
  for (const sev of SEVERITY_ORDER) {
    counts[sev] = summary.findings_by_severity[sev]?.length ?? 0
  }
  return counts
}

export function actionableFindings(summary: AuditSummary): AuditCheck[] {
  return ACTIONABLE_SEVERITIES.flatMap(
    (sev) => summary.findings_by_severity[sev] ?? []
  )
}

export function totals(summary: AuditSummary) {
  const all = summary.all_checks ?? []
  const passed = all.filter((c) => c.status === 'PASS').length
  const failed = all.filter((c) => c.status === 'FAIL').length
  const manual = all.filter((c) => c.status === 'MANUAL').length
  return { total: all.length, passed, failed, manual }
}

export function categoryList(
  summary: AuditSummary
): { module: string; score: number }[] {
  return Object.entries(summary.category_scores)
    .map(([module, score]) => ({ module, score }))
    .sort((a, b) => a.score - b.score)
}

export function scoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-500'
  if (score >= 60) return 'text-amber-500'
  return 'text-red-500'
}

export function scoreBarColor(score: number): string {
  if (score >= 80) return 'bg-emerald-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}

export function formatTimestamp(ts: number): string {
  if (!ts) return '—'
  const date = new Date(ts * 1000)
  return date.toLocaleString('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export const MODULE_LABELS: Record<string, string> = {
  ssh: 'SSH',
  firewall: 'Firewall',
  pam: 'PAM',
  sudoers: 'Sudoers',
  filesystem: 'Filesystem',
  kernel: 'Kernel',
  users: 'Users',
  services: 'Services',
}

export function moduleLabel(module: string): string {
  return MODULE_LABELS[module] ?? module.toUpperCase()
}

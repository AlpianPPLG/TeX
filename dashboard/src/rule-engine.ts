/**
 * TeX Dashboard - Type-Safe Rule Engine
 * Client-side filtering and grouping of audit findings
 * Version: 1.0
 */

import { AuditCheck, AuditSummary, Severity, CheckStatus } from './types';

export class RuleEngine {
  private checks: AuditCheck[];
  private originalChecks: AuditCheck[];

  constructor(summary: AuditSummary) {
    this.checks = summary.all_checks || [];
    this.originalChecks = [...this.checks];
  }

  /**
   * Filter findings by severity level
   */
  filterBySeverity(severity: Severity): RuleEngine {
    this.checks = this.checks.filter((c) => c.severity === severity);
    return this;
  }

  /**
   * Filter findings by status (PASS/FAIL/MANUAL)
   */
  filterByStatus(status: CheckStatus): RuleEngine {
    this.checks = this.checks.filter((c) => c.status === status);
    return this;
  }

  /**
   * Filter findings by module/domain
   */
  filterByModule(module: string): RuleEngine {
    this.checks = this.checks.filter((c) => c.module === module);
    return this;
  }

  /**
   * Search findings by title or CIS ID (case-insensitive)
   */
  searchByTitle(keyword: string): RuleEngine {
    const q = keyword.toLowerCase();
    this.checks = this.checks.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.cis_id.toLowerCase().includes(q)
    );
    return this;
  }

  /**
   * Limit results to top N findings
   */
  limit(n: number): RuleEngine {
    this.checks = this.checks.slice(0, n);
    return this;
  }

  /**
   * Sort findings by severity (critical first)
   */
  sortBySeverity(): RuleEngine {
    const severityOrder: Record<Severity, number> = {
      CRITICAL: 1,
      HIGH: 2,
      MEDIUM: 3,
      LOW: 4,
      PASS: 5,
    };
    
    this.checks.sort(
      (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
    );
    return this;
  }

  /**
   * Get current filtered results
   */
  getResults(): AuditCheck[] {
    return this.checks;
  }

  /**
   * Reset to original unfiltered checks
   */
  reset(): RuleEngine {
    this.checks = [...this.originalChecks];
    return this;
  }

  /**
   * Get count of filtered results
   */
  count(): number {
    return this.checks.length;
  }

  /**
   * Get count by severity
   */
  countBySeverity(): Record<Severity, number> {
    const counts: Record<Severity, number> = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
      PASS: 0,
    };

    this.originalChecks.forEach((check) => {
      counts[check.severity]++;
    });

    return counts;
  }

  /**
   * Get unique modules
   */
  getModules(): string[] {
    return Array.from(new Set(this.originalChecks.map((c) => c.module)));
  }

  /**
   * Get all findings for a specific module
   */
  getModuleFindings(module: string): AuditCheck[] {
    return this.originalChecks.filter((c) => c.module === module);
  }

  /**
   * Get top N critical findings
   */
  getTopCritical(n: number = 10): AuditCheck[] {
    return this.originalChecks
      .filter((c) => c.severity === 'CRITICAL')
      .slice(0, n);
  }

  /**
   * Export findings as CSV
   */
  exportAsCSV(): string {
    const headers = [
      'CIS ID',
      'Module',
      'Title',
      'Status',
      'Severity',
      'Actual Value',
      'Expected Value',
      'Remediation',
    ];

    const rows = this.checks.map((check) => [
      check.cis_id,
      check.module,
      check.title,
      check.status,
      check.severity,
      `"${check.actual_value}"`,
      `"${check.expected_value}"`,
      `"${check.remediation}"`,
    ]);

    return (
      [headers, ...rows].map((row) => row.join(',')).join('\n') + '\n'
    );
  }
}

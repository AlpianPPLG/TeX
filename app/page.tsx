import {
  Activity,
  AlertTriangle,
  ListChecks,
  ShieldCheck,
  ShieldX,
} from 'lucide-react'

import {
  actionableFindings,
  auditSummary,
  categoryList,
  getSpiBand,
  severityCounts,
  totals,
} from '@/lib/audit'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'
import { SpiGauge } from '@/components/dashboard/spi-gauge'
import { StatCard } from '@/components/dashboard/stat-card'
import { RadarChart } from '@/components/dashboard/radar-chart'
import { CategoryScores } from '@/components/dashboard/category-scores'
import { SeverityDistribution } from '@/components/dashboard/severity-distribution'
import { FindingsTable } from '@/components/dashboard/findings-table'

export default function Page() {
  const summary = auditSummary
  const band = getSpiBand(summary.spi)
  const counts = severityCounts(summary)
  const { total, passed, failed } = totals(summary)
  const actionable = actionableFindings(summary)
  const criticalHigh = counts.CRITICAL + counts.HIGH
  const categories = categoryList(summary)
  const meta = summary.audit_metadata

  return (
    <div className="min-h-screen bg-background text-foreground">
      <DashboardHeader summary={summary} />

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Title row */}
        <div className="mb-6 flex flex-col gap-1">
          <h2 className="text-2xl font-bold tracking-tight">
            Compliance Dashboard
          </h2>
          <p className="text-sm text-muted-foreground">
            CIS Benchmark for Linux v3 ·{' '}
            <span className="font-medium text-foreground">{summary.hostname}</span>
            {meta?.os_name ? ` · ${meta.os_name}` : ''}
            {meta?.kernel_version ? ` · kernel ${meta.kernel_version}` : ''}
          </p>
        </div>

        {/* Posture + stats */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Security Posture Index</CardTitle>
              <CardDescription>{band.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center pb-8 pt-2">
              <SpiGauge spi={summary.spi} />
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:col-span-2">
            <StatCard
              label="Controls Evaluated"
              value={total}
              sublabel="Total CIS checks"
              icon={ListChecks}
              accent="text-foreground"
              iconBg="bg-muted"
            />
            <StatCard
              label="Passed"
              value={passed}
              sublabel={`${((passed / (total || 1)) * 100).toFixed(0)}% compliant`}
              icon={ShieldCheck}
              accent="text-emerald-500"
              iconBg="bg-emerald-500/10"
            />
            <StatCard
              label="Failed"
              value={failed}
              sublabel="Require remediation"
              icon={ShieldX}
              accent="text-red-500"
              iconBg="bg-red-500/10"
            />
            <StatCard
              label="Critical & High"
              value={criticalHigh}
              sublabel="High-impact findings"
              icon={AlertTriangle}
              accent="text-orange-500"
              iconBg="bg-orange-500/10"
            />
          </div>
        </div>

        {/* Radar + categories + severity */}
        <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Domain Coverage</CardTitle>
              <CardDescription>Per-module compliance radar</CardDescription>
            </CardHeader>
            <CardContent>
              <RadarChart data={categories} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Compliance by Category</CardTitle>
              <CardDescription>Weighted score per domain</CardDescription>
            </CardHeader>
            <CardContent>
              <CategoryScores data={categories} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Severity Distribution</CardTitle>
              <CardDescription>
                {actionable.length} actionable finding
                {actionable.length === 1 ? '' : 's'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SeverityDistribution counts={counts} />
            </CardContent>
          </Card>
        </div>

        {/* Findings table */}
        <Card className="mt-5">
          <CardHeader className="flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="size-4 text-muted-foreground" />
              <div>
                <CardTitle>Control Findings</CardTitle>
                <CardDescription>
                  Search, filter, and inspect every audited control
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <FindingsTable checks={summary.all_checks} />
          </CardContent>
        </Card>

        <footer className="mt-10 border-t border-border pt-6 text-center text-xs text-muted-foreground">
          Generated by TeX v{meta?.tex_version ?? '1.0.0'} · Zero-Dependency
          Security Compliance Auditor · Audited by {meta?.audit_user ?? 'tex-auditor'}
        </footer>
      </main>
    </div>
  )
}

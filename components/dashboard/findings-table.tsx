'use client'

import * as React from 'react'
import {
  ChevronDown,
  Search,
  ShieldCheck,
  XCircle,
} from 'lucide-react'

import { cn } from '@/lib/utils'
import { moduleLabel } from '@/lib/audit'
import { SEVERITY_ORDER, type AuditCheck, type Severity } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { SeverityBadge } from '@/components/dashboard/severity-badge'

type StatusFilter = 'ALL' | 'FAIL' | 'PASS'
type SortKey = 'severity' | 'cis_id' | 'module' | 'title'

const SEVERITY_RANK: Record<Severity, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
  PASS: 4,
}

export function FindingsTable({ checks }: { checks: AuditCheck[] }) {
  const [query, setQuery] = React.useState('')
  const [status, setStatus] = React.useState<StatusFilter>('ALL')
  const [severity, setSeverity] = React.useState<Severity | 'ALL'>('ALL')
  const [moduleFilter, setModuleFilter] = React.useState<string>('ALL')
  const [sortKey, setSortKey] = React.useState<SortKey>('severity')
  const [expanded, setExpanded] = React.useState<string | null>(null)

  const modules = React.useMemo(
    () => Array.from(new Set(checks.map((c) => c.module))).sort(),
    [checks],
  )

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase()
    const rows = checks.filter((c) => {
      if (status !== 'ALL' && c.status !== status) return false
      if (severity !== 'ALL' && c.severity !== severity) return false
      if (moduleFilter !== 'ALL' && c.module !== moduleFilter) return false
      if (q) {
        const haystack = `${c.cis_id} ${c.title} ${c.module}`.toLowerCase()
        if (!haystack.includes(q)) return false
      }
      return true
    })

    rows.sort((a, b) => {
      if (sortKey === 'severity')
        return SEVERITY_RANK[a.severity] - SEVERITY_RANK[b.severity]
      return String(a[sortKey]).localeCompare(String(b[sortKey]))
    })
    return rows
  }, [checks, query, status, severity, moduleFilter, sortKey])

  const statusTabs: StatusFilter[] = ['ALL', 'FAIL', 'PASS']

  return (
    <div className="flex flex-col gap-4">
      {/* Controls */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full lg:max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by CIS ID, title, module…"
            className="pl-9"
            aria-label="Search findings"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* status tabs */}
          <div className="inline-flex rounded-lg border border-border bg-muted/40 p-0.5">
            {statusTabs.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setStatus(t)}
                className={cn(
                  'rounded-md px-3 py-1 text-xs font-medium transition-colors',
                  status === t
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground',
                )}
              >
                {t === 'ALL' ? 'All' : t === 'FAIL' ? 'Failed' : 'Passed'}
              </button>
            ))}
          </div>

          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value as Severity | 'ALL')}
            aria-label="Filter by severity"
            className="h-8 rounded-lg border border-border bg-background px-2 text-xs font-medium outline-none focus-visible:ring-3 focus-visible:ring-ring/40 dark:bg-input/30"
          >
            <option value="ALL">All severities</option>
            {SEVERITY_ORDER.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            aria-label="Filter by module"
            className="h-8 rounded-lg border border-border bg-background px-2 text-xs font-medium outline-none focus-visible:ring-3 focus-visible:ring-ring/40 dark:bg-input/30"
          >
            <option value="ALL">All modules</option>
            {modules.map((m) => (
              <option key={m} value={m}>
                {moduleLabel(m)}
              </option>
            ))}
          </select>

          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
            aria-label="Sort findings"
            className="h-8 rounded-lg border border-border bg-background px-2 text-xs font-medium outline-none focus-visible:ring-3 focus-visible:ring-ring/40 dark:bg-input/30"
          >
            <option value="severity">Sort: Severity</option>
            <option value="cis_id">Sort: CIS ID</option>
            <option value="module">Sort: Module</option>
            <option value="title">Sort: Title</option>
          </select>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Showing <span className="font-semibold text-foreground">{filtered.length}</span> of{' '}
        {checks.length} controls
      </p>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-border">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="bg-muted/50 text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">CIS ID</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Module</th>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="w-10 px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-10 text-center text-muted-foreground">
                    No controls match the current filters.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const key = `${c.module}-${c.cis_id}`
                  const isOpen = expanded === key
                  return (
                    <React.Fragment key={key}>
                      <tr
                        className={cn(
                          'cursor-pointer border-t border-border transition-colors hover:bg-muted/40',
                          isOpen && 'bg-muted/40',
                        )}
                        onClick={() => setExpanded(isOpen ? null : key)}
                      >
                        <td className="px-4 py-3">
                          {c.status === 'PASS' ? (
                            <ShieldCheck className="size-4 text-emerald-500" />
                          ) : c.status === 'FAIL' ? (
                            <XCircle className="size-4 text-red-500" />
                          ) : (
                            <span className="text-xs text-muted-foreground">MANUAL</span>
                          )}
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">{c.cis_id}</td>
                        <td className="max-w-xs px-4 py-3">
                          <span className="line-clamp-1">{c.title}</span>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="muted">{moduleLabel(c.module)}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <SeverityBadge severity={c.severity} />
                        </td>
                        <td className="px-4 py-3">
                          <ChevronDown
                            className={cn(
                              'size-4 text-muted-foreground transition-transform',
                              isOpen && 'rotate-180',
                            )}
                          />
                        </td>
                      </tr>
                      {isOpen ? (
                        <tr className="border-t border-border bg-muted/20">
                          <td colSpan={6} className="px-4 py-4">
                            <div className="grid gap-4 md:grid-cols-2">
                              <DetailRow label="Expected" value={c.expected_value || '—'} mono />
                              <DetailRow label="Observed" value={c.actual_value || '—'} mono />
                              <div className="md:col-span-2">
                                <DetailRow
                                  label="Remediation"
                                  value={c.remediation || 'No remediation provided.'}
                                  pre
                                />
                              </div>
                              {c.nist_800_53 && c.nist_800_53.length > 0 ? (
                                <div className="md:col-span-2">
                                  <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                    NIST 800-53 Mapping
                                  </p>
                                  <div className="flex flex-wrap gap-1.5">
                                    {c.nist_800_53.map((tag) => (
                                      <Badge key={tag} variant="outline">
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              ) : null}
                            </div>
                          </td>
                        </tr>
                      ) : null}
                    </React.Fragment>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function DetailRow({
  label,
  value,
  mono,
  pre,
}: {
  label: string
  value: string
  mono?: boolean
  pre?: boolean
}) {
  return (
    <div>
      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p
        className={cn(
          'rounded-md bg-background px-3 py-2 text-sm',
          mono && 'font-mono text-xs',
          pre && 'whitespace-pre-wrap',
        )}
      >
        {value}
      </p>
    </div>
  )
}

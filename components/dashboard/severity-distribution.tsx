import { cn } from '@/lib/utils'
import { SEVERITY_META } from '@/lib/audit'
import { SEVERITY_ORDER, type Severity } from '@/lib/types'

export function SeverityDistribution({
  counts,
}: {
  counts: Record<Severity, number>
}) {
  const total = SEVERITY_ORDER.reduce((sum, s) => sum + counts[s], 0) || 1

  return (
    <div className="flex flex-col gap-4">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-muted">
        {SEVERITY_ORDER.map((sev) => {
          const pct = (counts[sev] / total) * 100
          if (pct === 0) return null
          return (
            <div
              key={sev}
              className={cn('h-full transition-all', SEVERITY_META[sev].dot)}
              style={{ width: `${pct}%` }}
              title={`${SEVERITY_META[sev].label}: ${counts[sev]}`}
            />
          )
        })}
      </div>

      <ul className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
        {SEVERITY_ORDER.map((sev) => (
          <li key={sev} className="flex items-center justify-between gap-2 text-sm">
            <span className="flex items-center gap-2 text-muted-foreground">
              <span className={cn('size-2.5 rounded-full', SEVERITY_META[sev].dot)} />
              {SEVERITY_META[sev].label}
            </span>
            <span className="font-semibold tabular-nums">{counts[sev]}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

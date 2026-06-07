import { cn } from '@/lib/utils'
import { SEVERITY_META } from '@/lib/audit'
import type { Severity } from '@/lib/types'

export function SeverityBadge({
  severity,
  className,
}: {
  severity: Severity
  className?: string
}) {
  const meta = SEVERITY_META[severity]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset',
        meta.bg,
        meta.text,
        meta.ring,
        className,
      )}
    >
      <span className={cn('size-1.5 rounded-full', meta.dot)} />
      {meta.label}
    </span>
  )
}

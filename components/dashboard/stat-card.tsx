import type { LucideIcon } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'

export function StatCard({
  label,
  value,
  sublabel,
  icon: Icon,
  accent = 'text-foreground',
  iconBg = 'bg-muted',
}: {
  label: string
  value: React.ReactNode
  sublabel?: string
  icon: LucideIcon
  accent?: string
  iconBg?: string
}) {
  return (
    <Card className="group relative overflow-hidden p-5 transition-all hover:shadow-md hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {label}
          </p>
          <p className={cn('mt-2 text-3xl font-bold tabular-nums', accent)}>
            {value}
          </p>
          {sublabel ? (
            <p className="mt-1 truncate text-xs text-muted-foreground">
              {sublabel}
            </p>
          ) : null}
        </div>
        <div
          className={cn(
            'flex size-10 shrink-0 items-center justify-center rounded-lg transition-transform group-hover:scale-110',
            iconBg,
          )}
        >
          <Icon className={cn('size-5', accent)} />
        </div>
      </div>
    </Card>
  )
}

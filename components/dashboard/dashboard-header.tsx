import { Server } from 'lucide-react'

import { formatTimestamp } from '@/lib/audit'
import type { AuditSummary } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/theme-toggle'
import { PrintButton } from '@/components/dashboard/print-button'

export function DashboardHeader({ summary }: { summary: AuditSummary }) {
  const meta = summary.audit_metadata
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-foreground text-background">
            <svg
              fill="currentColor"
              viewBox="0 0 147 70"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
              className="size-5"
            >
              <path d="M56 50.2031V14H70V60.1562C70 65.5928 65.5928 70 60.1562 70C57.5605 70 54.9982 68.9992 53.1562 67.1573L0 14H19.7969L56 50.2031Z" />
              <path d="M147 56H133V23.9531L100.953 56H133V70H96.6875C85.8144 70 77 61.1856 77 50.3125V14H91V46.1562L123.156 14H91V0H127.312C138.186 0 147 8.81439 147 19.6875V56Z" />
            </svg>
          </div>
          <div>
            <h1 className="flex items-center gap-2 text-base font-semibold leading-none tracking-tight">
              TeX
              <Badge variant="muted" className="font-normal">
                v{meta?.tex_version ?? '1.0.0'}
              </Badge>
            </h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Security Compliance Auditor
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 text-sm md:flex">
            <Server className="size-4 text-muted-foreground" />
            <span className="font-medium">{summary.hostname}</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground">
              {formatTimestamp(summary.generated_at)}
            </span>
          </div>
          <PrintButton />
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}

'use client'

import { Download } from 'lucide-react'

import { Button } from '@/components/ui/button'

export function PrintButton() {
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => window.print()}
      className="gap-1.5"
    >
      <Download className="size-4" />
      <span className="hidden sm:inline">Export</span>
    </Button>
  )
}

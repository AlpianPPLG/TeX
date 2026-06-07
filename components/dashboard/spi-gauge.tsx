'use client'

import * as React from 'react'

import { cn } from '@/lib/utils'
import { getSpiBand } from '@/lib/audit'

const SIZE = 200
const STROKE = 16
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

function gaugeStroke(spi: number): string {
  if (spi >= 80) return 'stroke-emerald-500'
  if (spi >= 60) return 'stroke-amber-500'
  if (spi >= 40) return 'stroke-orange-500'
  return 'stroke-red-500'
}

export function SpiGauge({ spi }: { spi: number }) {
  const band = getSpiBand(spi)
  const [progress, setProgress] = React.useState(0)
  const [display, setDisplay] = React.useState(0)

  React.useEffect(() => {
    const id = requestAnimationFrame(() => setProgress(spi))
    return () => cancelAnimationFrame(id)
  }, [spi])

  // Animated count-up for the numeric value.
  React.useEffect(() => {
    let raf = 0
    const start = performance.now()
    const duration = 900
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplay(spi * eased)
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [spi])

  const offset = CIRCUMFERENCE - (progress / 100) * CIRCUMFERENCE

  return (
    <div className="relative flex items-center justify-center">
      <svg
        width={SIZE}
        height={SIZE}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="-rotate-90"
        role="img"
        aria-label={`Security Posture Index ${spi.toFixed(1)} out of 100`}
      >
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          strokeWidth={STROKE}
          className="stroke-muted"
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          className={cn(
            'transition-[stroke-dashoffset] duration-1000 ease-out',
            gaugeStroke(spi),
          )}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={cn('text-5xl font-bold tabular-nums', band.color)}>
          {display.toFixed(1)}
        </span>
        <span className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          SPI / 100
        </span>
        <span className={cn('mt-1 text-sm font-semibold', band.color)}>
          {band.label}
        </span>
      </div>
    </div>
  )
}

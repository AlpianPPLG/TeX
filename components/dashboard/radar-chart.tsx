'use client'

import * as React from 'react'

import { moduleLabel } from '@/lib/audit'

interface RadarDatum {
  module: string
  score: number
}

const SIZE = 320
const CENTER = SIZE / 2
const RADIUS = 118
const RINGS = [0.25, 0.5, 0.75, 1]

function polar(angle: number, radius: number): [number, number] {
  const a = angle - Math.PI / 2 // start at top
  return [CENTER + radius * Math.cos(a), CENTER + radius * Math.sin(a)]
}

export function RadarChart({ data }: { data: RadarDatum[] }) {
  const [shown, setShown] = React.useState(false)

  React.useEffect(() => {
    const id = requestAnimationFrame(() => setShown(true))
    return () => cancelAnimationFrame(id)
  }, [])

  const n = data.length
  const step = (2 * Math.PI) / Math.max(1, n)

  const valuePoints = data.map((d, i) => {
    const r = (Math.max(0, Math.min(100, d.score)) / 100) * RADIUS * (shown ? 1 : 0.001)
    return polar(i * step, r)
  })

  const polygon = valuePoints.map(([x, y]) => `${x},${y}`).join(' ')

  return (
    <div className="flex items-center justify-center">
      <svg
        width="100%"
        height="auto"
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="max-w-[340px]"
        role="img"
        aria-label="Per-domain compliance radar chart"
      >
        {/* grid rings */}
        {RINGS.map((ring) => (
          <polygon
            key={ring}
            points={data
              .map((_, i) => polar(i * step, RADIUS * ring).join(','))
              .join(' ')}
            fill="none"
            className="stroke-border"
            strokeWidth={1}
          />
        ))}

        {/* axes */}
        {data.map((d, i) => {
          const [x, y] = polar(i * step, RADIUS)
          return (
            <line
              key={d.module}
              x1={CENTER}
              y1={CENTER}
              x2={x}
              y2={y}
              className="stroke-border"
              strokeWidth={1}
            />
          )
        })}

        {/* value polygon */}
        <polygon
          points={polygon}
          className="fill-primary/15 stroke-primary transition-all duration-700 ease-out"
          strokeWidth={2}
        />

        {/* value dots */}
        {valuePoints.map(([x, y], i) => (
          <circle
            key={data[i].module}
            cx={x}
            cy={y}
            r={3.5}
            className="fill-primary transition-all duration-700 ease-out"
          />
        ))}

        {/* labels */}
        {data.map((d, i) => {
          const [x, y] = polar(i * step, RADIUS + 18)
          const anchor =
            Math.abs(x - CENTER) < 12 ? 'middle' : x > CENTER ? 'start' : 'end'
          return (
            <text
              key={`label-${d.module}`}
              x={x}
              y={y}
              textAnchor={anchor as 'start' | 'middle' | 'end'}
              dominantBaseline="middle"
              className="fill-muted-foreground text-[10px] font-medium"
            >
              {moduleLabel(d.module)}
            </text>
          )
        })}
      </svg>
    </div>
  )
}

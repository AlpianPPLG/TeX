import { cn } from '@/lib/utils'
import { moduleLabel, scoreBarColor, scoreColor } from '@/lib/audit'
import { Progress } from '@/components/ui/progress'

interface CategoryDatum {
  module: string
  score: number
}

export function CategoryScores({ data }: { data: CategoryDatum[] }) {
  return (
    <ul className="flex flex-col gap-4">
      {data.map((d) => (
        <li key={d.module} className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">{moduleLabel(d.module)}</span>
            <span className={cn('font-semibold tabular-nums', scoreColor(d.score))}>
              {d.score.toFixed(1)}
            </span>
          </div>
          <Progress
            value={d.score}
            indicatorClassName={scoreBarColor(d.score)}
          />
        </li>
      ))}
    </ul>
  )
}

import type { UnionWin } from '../types'
import { formatMonthDate } from '../utils/dateFormatters'
import { WinItem } from './WinItem'

interface MonthSectionProps {
    monthKey: string
    wins: UnionWin[]
}

/**
 * Section component displaying wins grouped by month
 */
export const MonthSection: React.FC<MonthSectionProps> = ({ monthKey, wins }) => {
    const formattedMonth = formatMonthDate(monthKey)

    return (
        <section>
            <h2 className="text-lg font-light text-gray-900 mb-4">
                {formattedMonth}
            </h2>
            <ol className="space-y-5">
                {wins.map((win) => (
                    <WinItem key={win.id} win={win} />
                ))}
            </ol>
        </section>
    )
}

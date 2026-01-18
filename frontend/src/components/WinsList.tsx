import type { UnionWin } from '../types'
import { groupByMonth } from '../utils/groupingHelpers'
import { MonthSection } from './MonthSection'

interface WinsListProps {
    wins: UnionWin[]
    searchQuery: string
}

/**
 * Component to display a list of wins grouped by month
 */
export const WinsList: React.FC<WinsListProps> = ({ wins, searchQuery }) => {
    const groupedWins = groupByMonth(wins)

    if (wins.length === 0) {
        return (
            <p className="text-center text-gray-500 text-sm py-8">
                No wins found matching "{searchQuery}"
            </p>
        )
    }

    return (
        <div className="space-y-8">
            {groupedWins.map(([monthKey, monthWins]) => (
                <MonthSection
                    key={monthKey}
                    monthKey={monthKey}
                    wins={monthWins}
                />
            ))}
        </div>
    )
}

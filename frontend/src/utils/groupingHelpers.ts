import type { UnionWin } from '../types'
import { getMonthKey } from './dateFormatters'

/**
 * Group wins by month and sort in descending order
 */
export const groupByMonth = (items: UnionWin[]): [string, UnionWin[]][] => {
    const grouped: Record<string, UnionWin[]> = {}

    items.forEach((item) => {
        const date = new Date(item.date)
        const key = getMonthKey(date)
        if (!grouped[key]) {
            grouped[key] = []
        }
        grouped[key].push(item)
    })

    return Object.entries(grouped).sort((a, b) => b[0].localeCompare(a[0]))
}

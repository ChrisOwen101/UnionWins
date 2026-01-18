import type { UnionWin } from '../types'
import { getDomain } from './urlHelpers'

/**
 * Filter wins based on a search query
 */
export const filterWinsByQuery = (wins: UnionWin[], query: string): UnionWin[] => {
    const lowerQuery = query.toLowerCase()

    return wins.filter((win) =>
        win.title.toLowerCase().includes(lowerQuery) ||
        win.union_name?.toLowerCase().includes(lowerQuery) ||
        win.summary.toLowerCase().includes(lowerQuery) ||
        getDomain(win.url).toLowerCase().includes(lowerQuery)
    )
}

import type { UnionWin, WinType } from '../types'
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

/**
 * Parse win_types string into array of individual types
 */
export const parseWinTypes = (winTypes?: string): string[] => {
    if (!winTypes) return []
    return winTypes.split(',').map(t => t.trim()).filter(Boolean)
}

/**
 * Filter wins by type and union name
 */
export const filterWinsByTypeAndUnion = (
    wins: UnionWin[],
    selectedType: WinType | '',
    selectedUnion: string
): UnionWin[] => {
    return wins.filter(win => {
        const winTypesList = parseWinTypes(win.win_types)
        const typeMatch = !selectedType || winTypesList.includes(selectedType)
        const unionMatch = !selectedUnion || win.union_name === selectedUnion
        return typeMatch && unionMatch
    })
}

/**
 * Filter wins by multiple types and union name
 */
export const filterWinsByTypesAndUnion = (
    wins: UnionWin[],
    selectedTypes: WinType[],
    selectedUnion: string
): UnionWin[] => {
    return wins.filter(win => {
        const winTypesList = parseWinTypes(win.win_types)
        // If no types selected, show all. Otherwise, show wins that have ANY of the selected types
        const typeMatch = selectedTypes.length === 0 || selectedTypes.some(type => winTypesList.includes(type))
        const unionMatch = !selectedUnion || win.union_name === selectedUnion
        return typeMatch && unionMatch
    })
}

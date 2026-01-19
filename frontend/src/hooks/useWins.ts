import { useState, useEffect, useCallback, useRef } from 'react'
import type { UnionWin } from '../types'

interface PaginatedResponse {
    wins: UnionWin[]
    months: string[]
    has_more: boolean
    total_months: number
}

interface SearchResponse {
    wins: UnionWin[]
    query: string
    total: number
}

interface UseWinsResult {
    wins: UnionWin[]
    loading: boolean
    loadingMore: boolean
    error: Error | null
    hasMore: boolean
    loadMore: () => void
    searchWins: (query: string) => Promise<void>
    clearSearch: () => void
    isSearching: boolean
    searchQuery: string
}

/**
 * Custom hook to fetch What Have Unions Done For Us from the API with lazy loading.
 * Loads 3 months at a time and supports API-based search.
 */
export const useWins = (): UseWinsResult => {
    const [wins, setWins] = useState<UnionWin[]>([])
    const [loading, setLoading] = useState(true)
    const [loadingMore, setLoadingMore] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    const [hasMore, setHasMore] = useState(true)
    const [monthOffset, setMonthOffset] = useState(0)
    const [isSearching, setIsSearching] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const initialLoadDone = useRef(false)

    // Initial load - first 3 months
    useEffect(() => {
        if (initialLoadDone.current) return
        initialLoadDone.current = true

        const fetchInitialWins = async () => {
            try {
                setLoading(true)
                const response = await fetch('/api/wins/paginated?month_offset=0&num_months=3')
                if (!response.ok) {
                    throw new Error('Failed to fetch wins')
                }
                const data: PaginatedResponse = await response.json()
                setWins(data.wins)
                setHasMore(data.has_more)
                setMonthOffset(3)
            } catch (err) {
                console.error('Error fetching wins:', err)
                setError(err as Error)
            } finally {
                setLoading(false)
            }
        }

        fetchInitialWins()
    }, [])

    // Load more months
    const loadMore = useCallback(async () => {
        if (loadingMore || !hasMore || isSearching) return

        try {
            setLoadingMore(true)
            const response = await fetch(
                `/api/wins/paginated?month_offset=${monthOffset}&num_months=3`
            )
            if (!response.ok) {
                throw new Error('Failed to fetch more wins')
            }
            const data: PaginatedResponse = await response.json()
            setWins(prev => [...prev, ...data.wins])
            setHasMore(data.has_more)
            setMonthOffset(prev => prev + 3)
        } catch (err) {
            console.error('Error loading more wins:', err)
            setError(err as Error)
        } finally {
            setLoadingMore(false)
        }
    }, [monthOffset, loadingMore, hasMore, isSearching])

    // Search wins via API
    const searchWins = useCallback(async (query: string) => {
        if (!query.trim()) {
            clearSearch()
            return
        }

        try {
            setIsSearching(true)
            setSearchQuery(query)
            setLoading(true)
            const response = await fetch(
                `/api/wins/query?q=${encodeURIComponent(query)}`
            )
            if (!response.ok) {
                throw new Error('Failed to search wins')
            }
            const data: SearchResponse = await response.json()
            setWins(data.wins)
            setHasMore(false)
        } catch (err) {
            console.error('Error searching wins:', err)
            setError(err as Error)
        } finally {
            setLoading(false)
        }
    }, [])

    // Clear search and reload initial data
    const clearSearch = useCallback(async () => {
        setIsSearching(false)
        setSearchQuery('')
        setMonthOffset(0)

        try {
            setLoading(true)
            const response = await fetch('/api/wins/paginated?month_offset=0&num_months=3')
            if (!response.ok) {
                throw new Error('Failed to fetch wins')
            }
            const data: PaginatedResponse = await response.json()
            setWins(data.wins)
            setHasMore(data.has_more)
            setMonthOffset(3)
        } catch (err) {
            console.error('Error fetching wins:', err)
            setError(err as Error)
        } finally {
            setLoading(false)
        }
    }, [])

    return {
        wins,
        loading,
        loadingMore,
        error,
        hasMore,
        loadMore,
        searchWins,
        clearSearch,
        isSearching,
        searchQuery
    }
}

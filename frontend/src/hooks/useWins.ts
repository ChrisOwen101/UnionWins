import { useState, useEffect } from 'react'
import type { UnionWin } from '../types'

// Extend Window interface for SSR data
declare global {
    interface Window {
        __INITIAL_DATA__?: {
            wins: UnionWin[]
        }
    }
}

interface UseWinsResult {
    wins: UnionWin[]
    loading: boolean
    error: Error | null
}

/**
 * Custom hook to fetch What Have Unions Done For Us from the API.
 * Uses server-side rendered data if available for faster initial load.
 */
export const useWins = (): UseWinsResult => {
    // Check for pre-loaded SSR data
    const hasSSRData = typeof window !== 'undefined' &&
        window.__INITIAL_DATA__?.wins &&
        window.__INITIAL_DATA__.wins.length > 0

    const [wins, setWins] = useState<UnionWin[]>(
        hasSSRData ? window.__INITIAL_DATA__!.wins : []
    )
    const [loading, setLoading] = useState(!hasSSRData)
    const [error, setError] = useState<Error | null>(null)

    useEffect(() => {
        // Skip API call if we already have SSR data
        if (hasSSRData) {
            return
        }

        const fetchWins = async () => {
            try {
                const response = await fetch('/api/wins')
                if (!response.ok) {
                    throw new Error('Failed to fetch wins')
                }
                const data = await response.json()
                setWins(data)
            } catch (err) {
                console.error('Error fetching wins:', err)
                setError(err as Error)
            } finally {
                setLoading(false)
            }
        }

        fetchWins()
    }, [hasSSRData])

    return { wins, loading, error }
}

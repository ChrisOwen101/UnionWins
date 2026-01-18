import { useState, useEffect } from 'react'
import type { UnionWin } from '../types'

interface UseWinsResult {
    wins: UnionWin[]
    loading: boolean
    error: Error | null
}

/**
 * Custom hook to fetch union wins from the API
 */
export const useWins = (): UseWinsResult => {
    const [wins, setWins] = useState<UnionWin[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    useEffect(() => {
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
    }, [])

    return { wins, loading, error }
}

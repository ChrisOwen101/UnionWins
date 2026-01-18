import { useState, useEffect } from 'react'

interface SearchRequest {
    id: number
    status: string
    date_range: string
    new_wins_found: number
    error_message: string | null
    created_at: string
    updated_at: string
}

/**
 * Component to display running and recent search requests
 * Polls the backend every 5 seconds for updates
 */
export const AdminSearchStatus: React.FC = () => {
    const [searches, setSearches] = useState<SearchRequest[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [countdown, setCountdown] = useState(5)

    const fetchSearchStatus = async () => {
        try {
            const response = await fetch('/api/wins/search/status')
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
            const data = await response.json()
            setSearches(data)
            setError('')
            setCountdown(5) // Reset countdown after fetch
        } catch (err) {
            setError((err as Error).message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        // Initial fetch
        fetchSearchStatus()

        // Set up polling every 5 seconds
        const fetchInterval = setInterval(fetchSearchStatus, 5000)

        // Set up countdown every second
        const countdownInterval = setInterval(() => {
            setCountdown((prev) => (prev <= 1 ? 5 : prev - 1))
        }, 1000)

        // Cleanup on unmount
        return () => {
            clearInterval(fetchInterval)
            clearInterval(countdownInterval)
        }
    }, [])

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'pending':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200'
            case 'processing':
                return 'bg-blue-100 text-blue-800 border-blue-200'
            case 'completed':
                return 'bg-green-100 text-green-800 border-green-200'
            case 'failed':
                return 'bg-red-100 text-red-800 border-red-200'
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pending':
                return '⏳'
            case 'processing':
                return '🔄'
            case 'completed':
                return '✅'
            case 'failed':
                return '❌'
            default:
                return '•'
        }
    }

    const formatDate = (isoString: string) => {
        const date = new Date(isoString)
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        })
    }

    if (loading && searches.length === 0) {
        return (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">
                    Search Status
                </h2>
                <p className="text-sm text-gray-500">Loading search status...</p>
            </div>
        )
    }

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">
                    Search Status
                </h2>
                <span className="text-xs text-gray-500">
                    Updates in {countdown}s
                </span>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    Error loading searches: {error}
                </div>
            )}

            {searches.length === 0 ? (
                <p className="text-sm text-gray-500">No searches yet</p>
            ) : (
                <div className="space-y-3">
                    {searches.map((search) => (
                        <div
                            key={search.id}
                            className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-lg">
                                            {getStatusIcon(search.status)}
                                        </span>
                                        <span
                                            className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(
                                                search.status
                                            )}`}
                                        >
                                            {search.status.toUpperCase()}
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            #{search.id}
                                        </span>
                                    </div>

                                    <p className="text-sm font-medium text-gray-900 mb-1">
                                        {search.date_range}
                                    </p>

                                    <div className="flex items-center gap-4 text-xs text-gray-600">
                                        <span>
                                            Started: {formatDate(search.created_at)}
                                        </span>
                                        {search.status !== 'pending' && (
                                            <span>
                                                Updated: {formatDate(search.updated_at)}
                                            </span>
                                        )}
                                        {search.status === 'completed' && (
                                            <span className="font-medium text-green-700">
                                                {search.new_wins_found} wins found
                                            </span>
                                        )}
                                    </div>

                                    {search.error_message && (
                                        <p className="mt-2 text-xs text-red-600">
                                            Error: {search.error_message}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

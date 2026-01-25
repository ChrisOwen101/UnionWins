import { useState, useEffect, useRef, useCallback } from 'react'
import { UnionWin } from '../types'

interface EditingWin extends UnionWin {
    isEditing: boolean
}

interface AdminRecentWinsProps {
    adminPassword: string
}

export function AdminRecentWins({ adminPassword }: AdminRecentWinsProps) {
    const [wins, setWins] = useState<EditingWin[]>([])
    const [loading, setLoading] = useState(true)
    const [loadingMore, setLoadingMore] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [monthOffset, setMonthOffset] = useState(0)
    const [hasMore, setHasMore] = useState(true)
    const observerRef = useRef<IntersectionObserver | null>(null)
    const loadMoreRef = useRef<HTMLDivElement | null>(null)

    const fetchInitialWins = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await fetch('/api/wins/paginated?month_offset=0&num_months=3')
            if (!response.ok) {
                throw new Error('Failed to fetch wins')
            }
            const data = await response.json()
            const winsWithEdit = data.wins.map((win: UnionWin) => ({
                ...win,
                isEditing: false
            }))
            setWins(winsWithEdit)
            setHasMore(data.has_more)
            setMonthOffset(3)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchInitialWins()
    }, [fetchInitialWins])

    const loadMoreWins = useCallback(async () => {
        if (loadingMore || !hasMore) return

        try {
            setLoadingMore(true)
            const response = await fetch(`/api/wins/paginated?month_offset=${monthOffset}&num_months=3`)
            if (!response.ok) {
                throw new Error('Failed to fetch more wins')
            }
            const data = await response.json()
            const winsWithEdit = data.wins.map((win: UnionWin) => ({
                ...win,
                isEditing: false
            }))
            setWins(prev => [...prev, ...winsWithEdit])
            setHasMore(data.has_more)
            setMonthOffset(prev => prev + 3)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoadingMore(false)
        }
    }, [loadingMore, hasMore, monthOffset])

    // Set up intersection observer for lazy loading
    useEffect(() => {
        if (loading || !hasMore) return

        observerRef.current = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hasMore && !loadingMore) {
                    loadMoreWins()
                }
            },
            { threshold: 0.1 }
        )

        if (loadMoreRef.current) {
            observerRef.current.observe(loadMoreRef.current)
        }

        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect()
            }
        }
    }, [loading, hasMore, loadingMore, loadMoreWins])

    const toggleEdit = (id: number) => {
        setWins(wins.map(win =>
            win.id === id ? { ...win, isEditing: !win.isEditing } : win
        ))
    }

    const updateField = (id: number, field: keyof UnionWin, value: string) => {
        setWins(wins.map(win =>
            win.id === id ? { ...win, [field]: value } : win
        ))
    }

    const saveWin = async (id: number) => {
        const win = wins.find(w => w.id === id)
        if (!win) return

        try {
            const response = await fetch(`/api/wins/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Password': adminPassword,
                },
                body: JSON.stringify({
                    title: win.title,
                    union_name: win.union_name,
                    emoji: win.emoji,
                    date: win.date,
                    url: win.url,
                    summary: win.summary,
                }),
            })

            if (!response.ok) {
                throw new Error('Failed to update win')
            }

            const updatedWin = await response.json()
            setWins(wins.map(w =>
                w.id === id ? { ...updatedWin, isEditing: false } : w
            ))
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save win')
        }
    }

    const cancelEdit = () => {
        // Refresh to get original data
        fetchInitialWins()
    }

    const deleteWin = async (id: number) => {
        if (!confirm('Are you sure you want to delete this win? This action cannot be undone.')) {
            return
        }

        try {
            const response = await fetch(`/api/wins/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                throw new Error('Failed to delete win')
            }

            // Remove the win from the local state
            setWins(wins.filter(w => w.id !== id))
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete win')
        }
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Wins</h2>
                <p className="text-gray-500">Loading...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Wins</h2>
                <p className="text-red-600">Error: {error}</p>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Wins ({wins.length} loaded{hasMore ? ', scroll for more' : ''})</h2>
            <div className="space-y-4">
                {wins.map((win) => (
                    <div key={win.id} className="border rounded-lg p-4">
                        {win.isEditing ? (
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Emoji
                                    </label>
                                    <input
                                        type="text"
                                        value={win.emoji || ''}
                                        onChange={(e) => updateField(win.id, 'emoji', e.target.value)}
                                        className="w-20 border rounded px-2 py-1 text-2xl"
                                        placeholder="🎉"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Title
                                    </label>
                                    <input
                                        type="text"
                                        value={win.title}
                                        onChange={(e) => updateField(win.id, 'title', e.target.value)}
                                        className="w-full border rounded px-3 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Union Name
                                    </label>
                                    <input
                                        type="text"
                                        value={win.union_name || ''}
                                        onChange={(e) => updateField(win.id, 'union_name', e.target.value)}
                                        className="w-full border rounded px-3 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Date
                                    </label>
                                    <input
                                        type="date"
                                        value={win.date}
                                        onChange={(e) => updateField(win.id, 'date', e.target.value)}
                                        className="border rounded px-3 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        URL
                                    </label>
                                    <input
                                        type="url"
                                        value={win.url}
                                        onChange={(e) => updateField(win.id, 'url', e.target.value)}
                                        className="w-full border rounded px-3 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Summary
                                    </label>
                                    <textarea
                                        value={win.summary}
                                        onChange={(e) => updateField(win.id, 'summary', e.target.value)}
                                        className="w-full border rounded px-3 py-2 h-24"
                                    />
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => saveWin(win.id)}
                                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                                    >
                                        Save
                                    </button>
                                    <button
                                        onClick={() => cancelEdit()}
                                        className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-start gap-3">
                                        {win.emoji && (
                                            <span className="text-2xl flex-shrink-0">{win.emoji}</span>
                                        )}
                                        <div>
                                            <h3 className="font-semibold text-lg">{win.title}</h3>
                                            {win.union_name && (
                                                <p className="text-sm text-gray-600">{win.union_name}</p>
                                            )}
                                            <p className="text-sm text-gray-500">{win.date}</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-2 flex-shrink-0">
                                        <button
                                            onClick={() => toggleEdit(win.id)}
                                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => deleteWin(win.id)}
                                            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                                <a
                                    href={win.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:underline text-sm break-all"
                                >
                                    {win.url}
                                </a>
                            </div>
                        )}
                    </div>
                ))}
                {hasMore && (
                    <div ref={loadMoreRef} className="py-4 text-center">
                        {loadingMore ? (
                            <p className="text-gray-500">Loading more wins...</p>
                        ) : (
                            <p className="text-gray-400">Scroll to load more</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

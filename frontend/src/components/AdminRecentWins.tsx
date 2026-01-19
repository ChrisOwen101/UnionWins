import { useState, useEffect } from 'react'
import { UnionWin } from '../types'

interface EditingWin extends UnionWin {
    isEditing: boolean
}

export function AdminRecentWins() {
    const [wins, setWins] = useState<EditingWin[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchRecentWins()
    }, [])

    const fetchRecentWins = async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await fetch('/api/wins')
            if (!response.ok) {
                throw new Error('Failed to fetch wins')
            }
            const allWins = await response.json()
            // Get the 20 most recent wins
            const recentWins = allWins.slice(0, 20).map((win: UnionWin) => ({
                ...win,
                isEditing: false
            }))
            setWins(recentWins)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }

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

    const cancelEdit = (id: number) => {
        // Refresh to get original data
        fetchRecentWins()
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Wins (Last 20)</h2>
                <p className="text-gray-500">Loading...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Wins (Last 20)</h2>
                <p className="text-red-600">Error: {error}</p>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Wins (Last 20)</h2>
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
                                        onClick={() => cancelEdit(win.id)}
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
                                    <button
                                        onClick={() => toggleEdit(win.id)}
                                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex-shrink-0"
                                    >
                                        Edit
                                    </button>
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
            </div>
        </div>
    )
}

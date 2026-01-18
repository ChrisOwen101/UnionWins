import { useState, useEffect } from 'react'
import type { PendingWin } from '../types'

export function AdminPendingSubmissions() {
    const [pendingWins, setPendingWins] = useState<PendingWin[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [processingId, setProcessingId] = useState<number | null>(null)

    const fetchPendingSubmissions = async () => {
        try {
            const response = await fetch('/api/submissions/pending')
            if (!response.ok) throw new Error('Failed to fetch pending submissions')
            const data = await response.json()
            setPendingWins(data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchPendingSubmissions()
    }, [])

    const handleReview = async (id: number, action: 'approve' | 'reject') => {
        setProcessingId(id)
        setError('')

        try {
            const response = await fetch(`/api/submissions/${id}/review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action }),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to process review')
            }

            // Remove the reviewed item from the list
            setPendingWins(prev => prev.filter(win => win.id !== id))
        } catch (err: any) {
            setError(err.message)
        } finally {
            setProcessingId(null)
        }
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-bold mb-4">Pending Submissions</h2>
                <p className="text-gray-500">Loading...</p>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Pending Submissions</h2>
                <button
                    onClick={fetchPendingSubmissions}
                    className="text-sm text-blue-600 hover:text-blue-800"
                >
                    Refresh
                </button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <p className="text-red-800">{error}</p>
                </div>
            )}

            {pendingWins.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                    No pending submissions to review
                </p>
            ) : (
                <div className="space-y-4">
                    {pendingWins.map((win) => (
                        <div
                            key={win.id}
                            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                        >
                            <div className="flex gap-4">
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-bold text-lg mb-1 truncate">
                                        {win.title}
                                    </h3>
                                    {win.union_name && (
                                        <p className="text-sm text-gray-600 mb-2">
                                            {win.emoji} {win.union_name}
                                        </p>
                                    )}
                                    <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                                        {win.summary}
                                    </p>
                                    <div className="flex flex-wrap gap-2 text-xs text-gray-500 mb-3">
                                        <span>📅 {win.date}</span>
                                        {win.submitted_by && (
                                            <span>👤 Submitted by: {win.submitted_by}</span>
                                        )}
                                    </div>
                                    <a
                                        href={win.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-sm text-blue-600 hover:underline truncate block"
                                    >
                                        {win.url}
                                    </a>
                                </div>
                            </div>

                            <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200">
                                <button
                                    onClick={() => handleReview(win.id, 'approve')}
                                    disabled={processingId === win.id}
                                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {processingId === win.id ? 'Processing...' : '✓ Approve'}
                                </button>
                                <button
                                    onClick={() => handleReview(win.id, 'reject')}
                                    disabled={processingId === win.id}
                                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {processingId === win.id ? 'Processing...' : '✗ Reject'}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

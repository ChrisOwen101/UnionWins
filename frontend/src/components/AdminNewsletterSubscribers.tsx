import { useState, useEffect } from 'react'

interface NewsletterSubscriber {
    id: number
    email: string
    name: string | null
    frequency: string
    is_active: boolean
    created_at: string
    updated_at: string
}

interface AdminNewsletterSubscribersProps {
    adminPassword: string
}

export function AdminNewsletterSubscribers({ adminPassword }: AdminNewsletterSubscribersProps) {
    const [subscribers, setSubscribers] = useState<NewsletterSubscriber[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [deletingId, setDeletingId] = useState<number | null>(null)
    const [previewId, setPreviewId] = useState<number | null>(null)
    const [previewHtml, setPreviewHtml] = useState<string>('')
    const [loadingPreview, setLoadingPreview] = useState(false)

    const fetchSubscribers = async () => {
        setLoading(true)
        setError('')

        try {
            const response = await fetch('/api/admin/newsletter-subscribers', {
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                throw new Error('Failed to fetch subscribers')
            }

            const data = await response.json()
            setSubscribers(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load subscribers')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchSubscribers()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [adminPassword])

    const handleDelete = async (subscriberId: number) => {
        if (!confirm('Are you sure you want to delete this subscriber?')) {
            return
        }

        setDeletingId(subscriberId)

        try {
            const response = await fetch(`/api/admin/newsletter-subscribers/${subscriberId}`, {
                method: 'DELETE',
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                throw new Error('Failed to delete subscriber')
            }

            // Remove from local state
            setSubscribers(subscribers.filter(s => s.id !== subscriberId))
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete subscriber')
        } finally {
            setDeletingId(null)
        }
    }

    const handlePreview = async (subscriberId: number) => {
        setLoadingPreview(true)
        setPreviewId(subscriberId)
        setPreviewHtml('')

        try {
            const response = await fetch(`/api/admin/newsletter-preview/${subscriberId}`, {
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                throw new Error('Failed to load preview')
            }

            const html = await response.text()
            setPreviewHtml(html)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load preview')
            setPreviewId(null)
        } finally {
            setLoadingPreview(false)
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
    }

    const activeCount = subscribers.filter(s => s.is_active).length
    const dailyCount = subscribers.filter(s => s.is_active && s.frequency === 'daily').length
    const weeklyCount = subscribers.filter(s => s.is_active && s.frequency === 'weekly').length
    const monthlyCount = subscribers.filter(s => s.is_active && s.frequency === 'monthly').length

    if (loading) {
        return (
            <div className="flex justify-center py-8">
                <div className="text-gray-600">Loading subscribers...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                {error}
            </div>
        )
    }

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-3">Newsletter Subscribers</h2>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <div className="text-2xl font-bold text-gray-900">{activeCount}</div>
                        <div className="text-xs text-gray-600">Active Subscribers</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                        <div className="text-2xl font-bold text-blue-900">{dailyCount}</div>
                        <div className="text-xs text-blue-600">Daily</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                        <div className="text-2xl font-bold text-green-900">{weeklyCount}</div>
                        <div className="text-xs text-green-600">Weekly</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                        <div className="text-2xl font-bold text-purple-900">{monthlyCount}</div>
                        <div className="text-xs text-purple-600">Monthly</div>
                    </div>
                </div>
            </div>

            {subscribers.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    No newsletter subscribers yet.
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Email
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Name
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Frequency
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Subscribed
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {subscribers.map((subscriber) => (
                                <tr key={subscriber.id} className="hover:bg-gray-50">
                                    <td className="px-4 py-3 text-sm text-gray-900">
                                        {subscriber.email}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600">
                                        {subscriber.name || '-'}
                                    </td>
                                    <td className="px-4 py-3 text-sm">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${subscriber.frequency === 'daily'
                                                ? 'bg-blue-100 text-blue-800'
                                                : subscriber.frequency === 'weekly'
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-purple-100 text-purple-800'
                                            }`}>
                                            {subscriber.frequency.charAt(0).toUpperCase() + subscriber.frequency.slice(1)}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${subscriber.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-gray-100 text-gray-800'
                                            }`}>
                                            {subscriber.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-600">
                                        {formatDate(subscriber.created_at)}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-right">
                                        <div className="flex gap-2 justify-end">
                                            <button
                                                onClick={() => handlePreview(subscriber.id)}
                                                className="text-blue-600 hover:text-blue-900 transition-colors"
                                                title="Preview email"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                </svg>
                                            </button>
                                            <button
                                                onClick={() => handleDelete(subscriber.id)}
                                                disabled={deletingId === subscriber.id}
                                                className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                                title="Delete subscriber"
                                            >
                                                {deletingId === subscriber.id ? (
                                                    <span className="text-xs">Deleting...</span>
                                                ) : (
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                )}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Preview Modal */}
            {previewId !== null && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
                    onClick={() => setPreviewId(null)}
                >
                    <div
                        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex justify-between items-center p-4 border-b">
                            <h3 className="text-lg font-semibold">Email Preview</h3>
                            <button
                                onClick={() => setPreviewId(null)}
                                className="text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <div className="p-4 overflow-y-auto max-h-[calc(90vh-80px)]">
                            {loadingPreview ? (
                                <div className="flex justify-center py-8">
                                    <div className="text-gray-600">Loading preview...</div>
                                </div>
                            ) : previewHtml ? (
                                <iframe
                                    srcDoc={previewHtml}
                                    className="w-full h-[600px] border border-gray-200 rounded"
                                    title="Email Preview"
                                    sandbox="allow-same-origin"
                                />
                            ) : null}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

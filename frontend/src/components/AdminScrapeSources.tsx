import { useState, useEffect } from 'react'
import { format } from 'date-fns'

interface ScrapeSource {
    id: number
    url: string
    organization_name: string | null
    last_scraped_at: string | null
    is_active: number
    created_at: string
}

export function AdminScrapeSources() {
    const [sources, setSources] = useState<ScrapeSource[]>([])
    const [loading, setLoading] = useState(true)
    const [newUrl, setNewUrl] = useState('')
    const [newOrg, setNewOrg] = useState('')
    const [adding, setAdding] = useState(false)
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

    useEffect(() => {
        fetchSources()
    }, [])

    const fetchSources = async () => {
        try {
            setLoading(true)
            const response = await fetch('/api/scraping/sources')
            if (!response.ok) throw new Error('Failed to fetch sources')
            const data = await response.json()
            setSources(data)
        } catch (err) {
            console.error(err)
            setMessage({ type: 'error', text: 'Failed to load sources' })
        } finally {
            setLoading(false)
        }
    }

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newUrl) return

        try {
            setAdding(true)
            const response = await fetch('/api/scraping/sources', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: newUrl, organization_name: newOrg || null })
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.detail || 'Failed to add source')
            }

            await fetchSources()
            setNewUrl('')
            setNewOrg('')
            setMessage({ type: 'success', text: 'Source added successfully' })
        } catch (err) {
            setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to add source' })
        } finally {
            setAdding(false)
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to remove this source?')) return

        try {
            const response = await fetch(`/api/scraping/sources/${id}`, { method: 'DELETE' })
            if (!response.ok) throw new Error('Failed to delete source')

            setSources(sources.filter(s => s.id !== id))
            setMessage({ type: 'success', text: 'Source removed' })
        } catch (err) {
            setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to delete source' })
        }
    }

    const handleRun = async (id: number) => {
        try {
            const response = await fetch(`/api/scraping/run/${id}`, { method: 'POST' })
            if (!response.ok) throw new Error('Failed to start scrape')
            setMessage({ type: 'success', text: 'Scrape job started in background' })
        } catch (err) {
            setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to start scrape' })
        }
    }

    const handleRunAll = async () => {
        try {
            const response = await fetch('/api/scraping/run-all', { method: 'POST' })
            if (!response.ok) throw new Error('Failed to start scrape all')
            setMessage({ type: 'success', text: 'All scrape jobs started in background' })
        } catch (err) {
            setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to start scrape all' })
        }
    }

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">Scrape Sources</h2>
                        <p className="text-sm text-gray-500 mt-1">Manage external websites to scrape for wins</p>
                    </div>
                    <button
                        onClick={handleRunAll}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        Run All Scrapers
                    </button>
                </div>

                {message && (
                    <div className={`p-4 rounded-md mb-6 ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                        {message.text}
                        <button onClick={() => setMessage(null)} className="float-right font-bold ml-2">&times;</button>
                    </div>
                )}

                <form onSubmit={handleAdd} className="bg-gray-50 p-4 rounded-md mb-6 border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Add New Source</h3>
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <input
                                type="url"
                                placeholder="https://example.com/news"
                                value={newUrl}
                                onChange={e => setNewUrl(e.target.value)}
                                className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div className="w-48">
                            <input
                                type="text"
                                placeholder="Organization Name (opt)"
                                value={newOrg}
                                onChange={e => setNewOrg(e.target.value)}
                                className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={adding}
                            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm font-medium disabled:opacity-50"
                        >
                            {adding ? 'Adding...' : 'Add Source'}
                        </button>
                    </div>
                </form>

                {loading ? (
                    <div className="text-center py-8 text-gray-500">Loading sources...</div>
                ) : sources.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">No sources added yet.</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="py-3 px-4 font-semibold text-sm text-gray-600">URL</th>
                                    <th className="py-3 px-4 font-semibold text-sm text-gray-600">Organization</th>
                                    <th className="py-3 px-4 font-semibold text-sm text-gray-600">Last Scraped</th>
                                    <th className="py-3 px-4 font-semibold text-sm text-gray-600 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sources.map(source => (
                                    <tr key={source.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm text-gray-800 break-all max-w-xs">
                                            <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                                {source.url}
                                            </a>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-600">{source.organization_name || '-'}</td>
                                        <td className="py-3 px-4 text-sm text-gray-600">
                                            {source.last_scraped_at ? format(new Date(source.last_scraped_at), 'PPP p') : 'Never'}
                                        </td>
                                        <td className="py-3 px-4 text-right space-x-2">
                                            <button
                                                onClick={() => handleRun(source.id)}
                                                className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded hover:bg-indigo-200"
                                            >
                                                Run Now
                                            </button>
                                            <button
                                                onClick={() => handleDelete(source.id)}
                                                className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200"
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}

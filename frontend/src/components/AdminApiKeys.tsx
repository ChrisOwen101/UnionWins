import { useState, useEffect, useCallback } from 'react'

interface ApiKey {
    id: number
    name: string
    email: string
    description: string | null
    is_active: boolean
    created_at: string
    last_used_at: string | null
}

interface NewApiKey extends ApiKey {
    api_key: string
}

interface AdminApiKeysProps {
    adminPassword: string
}

export function AdminApiKeys({ adminPassword }: AdminApiKeysProps) {
    const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [newKeyResult, setNewKeyResult] = useState<NewApiKey | null>(null)

    // Form state
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [description, setDescription] = useState('')
    const [creating, setCreating] = useState(false)

    const fetchApiKeys = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await fetch('/api/admin/api-keys', {
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })
            if (!response.ok) {
                throw new Error('Failed to fetch API keys')
            }
            const data = await response.json()
            setApiKeys(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }, [adminPassword])

    useEffect(() => {
        fetchApiKeys()
    }, [fetchApiKeys])

    const createApiKey = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!name.trim() || !email.trim()) return

        try {
            setCreating(true)
            setError(null)
            const response = await fetch('/api/admin/api-keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Password': adminPassword,
                },
                body: JSON.stringify({
                    name: name.trim(),
                    email: email.trim(),
                    description: description.trim() || null,
                }),
            })

            if (!response.ok) {
                throw new Error('Failed to create API key')
            }

            const newKey = await response.json()
            setNewKeyResult(newKey)
            setShowCreateForm(false)
            setName('')
            setEmail('')
            setDescription('')
            fetchApiKeys()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create API key')
        } finally {
            setCreating(false)
        }
    }

    const toggleApiKey = async (id: number, isActive: boolean) => {
        try {
            const response = await fetch(`/api/admin/api-keys/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Password': adminPassword,
                },
                body: JSON.stringify({ is_active: isActive }),
            })

            if (!response.ok) {
                throw new Error('Failed to update API key')
            }

            fetchApiKeys()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update API key')
        }
    }

    const deleteApiKey = async (id: number) => {
        if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
            return
        }

        try {
            const response = await fetch(`/api/admin/api-keys/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                throw new Error('Failed to delete API key')
            }

            fetchApiKeys()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete API key')
        }
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        alert('API key copied to clipboard!')
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">API Keys</h2>
                <p className="text-gray-500">Loading...</p>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">API Keys</h2>
                <button
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                    {showCreateForm ? 'Cancel' : 'Generate New Key'}
                </button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
                    {error}
                </div>
            )}

            {/* New Key Result */}
            {newKeyResult && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h3 className="font-semibold text-green-800 mb-2">
                        ✅ API Key Created Successfully
                    </h3>
                    <p className="text-sm text-green-700 mb-3">
                        Make sure to copy this key now. You won't be able to see it again!
                    </p>
                    <div className="flex items-center gap-2 bg-white p-3 rounded border">
                        <code className="flex-1 text-sm font-mono break-all">
                            {newKeyResult.api_key}
                        </code>
                        <button
                            onClick={() => copyToClipboard(newKeyResult.api_key)}
                            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 flex-shrink-0"
                        >
                            Copy
                        </button>
                    </div>
                    <button
                        onClick={() => setNewKeyResult(null)}
                        className="mt-3 text-sm text-green-700 hover:underline"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            {/* Create Form */}
            {showCreateForm && (
                <form onSubmit={createApiKey} className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold mb-4">Generate New API Key</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Name *
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full border rounded px-3 py-2"
                                placeholder="John Doe"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Email *
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full border rounded px-3 py-2"
                                placeholder="john@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Description (optional)
                            </label>
                            <input
                                type="text"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="w-full border rounded px-3 py-2"
                                placeholder="Purpose of this API key"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={creating || !name.trim() || !email.trim()}
                            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
                        >
                            {creating ? 'Creating...' : 'Generate Key'}
                        </button>
                    </div>
                </form>
            )}

            {/* API Keys List */}
            {apiKeys.length === 0 ? (
                <p className="text-gray-500">No API keys have been created yet.</p>
            ) : (
                <div className="space-y-4">
                    {apiKeys.map((key) => (
                        <div
                            key={key.id}
                            className={`border rounded-lg p-4 ${key.is_active ? 'bg-white' : 'bg-gray-100'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold">{key.name}</h3>
                                        <span
                                            className={`px-2 py-0.5 text-xs rounded ${key.is_active
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-gray-200 text-gray-600'
                                                }`}
                                        >
                                            {key.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600">{key.email}</p>
                                    {key.description && (
                                        <p className="text-sm text-gray-500 mt-1">{key.description}</p>
                                    )}
                                    <div className="text-xs text-gray-400 mt-2">
                                        Created: {new Date(key.created_at).toLocaleDateString()}
                                        {key.last_used_at && (
                                            <span className="ml-4">
                                                Last used: {new Date(key.last_used_at).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => toggleApiKey(key.id, !key.is_active)}
                                        className={`px-3 py-1 text-sm rounded ${key.is_active
                                                ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                                                : 'bg-green-100 text-green-800 hover:bg-green-200'
                                            }`}
                                    >
                                        {key.is_active ? 'Disable' : 'Enable'}
                                    </button>
                                    <button
                                        onClick={() => deleteApiKey(key.id)}
                                        className="px-3 py-1 text-sm bg-red-100 text-red-800 rounded hover:bg-red-200"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

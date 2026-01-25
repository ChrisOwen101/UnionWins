import { useState } from 'react'
import { AdminHeader } from './components/AdminHeader'
import { AdminSearchPanel } from './components/AdminSearchPanel'
import { AdminSearchStatus } from './components/AdminSearchStatus'
import { AdminPendingSubmissions } from './components/AdminPendingSubmissions'
import { AdminRecentWins } from './components/AdminRecentWins'
import { AdminApiKeys } from './components/AdminApiKeys'
import { AdminNewsletterSubscribers } from './components/AdminNewsletterSubscribers'

type TabId = 'pending' | 'recent' | 'search' | 'status' | 'api-keys' | 'newsletter'

interface Tab {
    id: TabId
    label: string
}

const tabs: Tab[] = [
    { id: 'pending', label: 'Pending Submissions' },
    { id: 'recent', label: 'Recent Wins' },
    { id: 'search', label: 'Search' },
    { id: 'status', label: 'Search Status' },
    { id: 'api-keys', label: 'API Keys' },
    { id: 'newsletter', label: 'Newsletter' },
]

function AdminLogin({ onLogin }: { onLogin: (password: string) => void }) {
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            const response = await fetch('/api/admin/verify-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password }),
            })

            const data = await response.json()

            if (data.valid) {
                onLogin(password)
            } else {
                setError('Invalid password')
            }
        } catch {
            setError('Failed to verify password')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                <h1 className="text-2xl font-bold mb-6 text-center">Admin Login</h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter admin password"
                            autoFocus
                        />
                    </div>
                    {error && (
                        <p className="text-red-600 text-sm mb-4">{error}</p>
                    )}
                    <button
                        type="submit"
                        disabled={loading || !password}
                        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                    >
                        {loading ? 'Verifying...' : 'Login'}
                    </button>
                </form>
                <p className="text-center text-sm text-gray-500 mt-4">
                    <a href="/" className="text-blue-600 hover:underline">← Back to home</a>
                </p>
            </div>
        </div>
    )
}

function AdminDashboard({ adminPassword }: { adminPassword: string }) {
    const [activeTab, setActiveTab] = useState<TabId>('pending')

    return (
        <div className="min-h-screen bg-white">
            <AdminHeader
                title="What Have Unions Done For Us - Admin"
                subtitle="Administrative tools"
            />

            <main className="max-w-4xl mx-auto px-4 py-6">
                {/* Tab Navigation */}
                <div className="border-b border-gray-200 mb-6">
                    <nav className="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                                    whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                                    ${activeTab === tab.id
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }
                                `}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Tab Content */}
                <div>
                    {activeTab === 'pending' && <AdminPendingSubmissions adminPassword={adminPassword} />}
                    {activeTab === 'recent' && <AdminRecentWins adminPassword={adminPassword} />}
                    {activeTab === 'search' && <AdminSearchPanel adminPassword={adminPassword} />}
                    {activeTab === 'status' && <AdminSearchStatus />}
                    {activeTab === 'api-keys' && <AdminApiKeys adminPassword={adminPassword} />}
                    {activeTab === 'newsletter' && <AdminNewsletterSubscribers adminPassword={adminPassword} />}
                </div>
            </main>
        </div>
    )
}

function Admin() {
    const [adminPassword, setAdminPassword] = useState<string | null>(() => {
        // Check if password is stored in sessionStorage
        return sessionStorage.getItem('adminPassword')
    })

    const handleLogin = (password: string) => {
        sessionStorage.setItem('adminPassword', password)
        setAdminPassword(password)
    }

    if (!adminPassword) {
        return <AdminLogin onLogin={handleLogin} />
    }

    return <AdminDashboard adminPassword={adminPassword} />
}

export default Admin

import { useState } from 'react'
import { AdminHeader } from './components/AdminHeader'
import { AdminSearchPanel } from './components/AdminSearchPanel'
import { AdminSearchStatus } from './components/AdminSearchStatus'
import { AdminPendingSubmissions } from './components/AdminPendingSubmissions'
import { AdminRecentWins } from './components/AdminRecentWins'
import { AdminApiKeys } from './components/AdminApiKeys'
import { AdminScrapeSources } from './components/AdminScrapeSources'
import { AdminNewsletterSubscribers } from './components/AdminNewsletterSubscribers'
import { Footer } from './components/Footer'

type TabId = 'pending' | 'recent' | 'search' | 'status' | 'api-keys' | 'newsletter' | 'scraping'

interface Tab {
    id: TabId
    label: string
}

const tabs: Tab[] = [
    { id: 'pending', label: 'Pending Submissions' },
    { id: 'recent', label: 'Recent Wins' },
    { id: 'search', label: 'Search' },
    { id: 'status', label: 'Search Status' },
    { id: 'scraping', label: 'Scraping' },
    { id: 'api-keys', label: 'API Keys' },
    { id: 'newsletter', label: 'Newsletter' },
]

function AdminLogin({ onLogin }: { onLogin: (password: string) => void }) {
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [errorId] = useState('login-error')
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
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                            Password <span aria-label="required">*</span>
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter admin password"
                            autoFocus
                            aria-required="true"
                            aria-invalid={error ? 'true' : 'false'}
                            aria-describedby={error ? errorId : undefined}
                        />
                    </div>
                    {error && (
                        <div id={errorId} role="alert" className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                            <p className="text-red-800 text-sm">{error}</p>
                        </div>
                    )}
                    <button
                        type="submit"
                        disabled={loading || !password}
                        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        aria-label={loading ? 'Verifying password' : 'Login to admin dashboard'}
                    >
                        {loading ? 'Verifying...' : 'Login'}
                    </button>
                </form>
                <p className="text-center text-sm text-gray-500 mt-4">
                    <a href="/" className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 rounded">← Back to home</a>
                </p>
            </div>
        </div>
    )
}

function AdminDashboard({ adminPassword }: { adminPassword: string }) {
    const [activeTab, setActiveTab] = useState<TabId>('pending')

    const handleKeyDown = (e: React.KeyboardEvent) => {
        const currentIndex = tabs.findIndex(t => t.id === activeTab)
        let nextIndex = currentIndex

        if (e.key === 'ArrowLeft') {
            nextIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1
            e.preventDefault()
        } else if (e.key === 'ArrowRight') {
            nextIndex = currentIndex === tabs.length - 1 ? 0 : currentIndex + 1
            e.preventDefault()
        } else if (e.key === 'Home') {
            nextIndex = 0
            e.preventDefault()
        } else if (e.key === 'End') {
            nextIndex = tabs.length - 1
            e.preventDefault()
        }

        if (nextIndex !== currentIndex) {
            setActiveTab(tabs[nextIndex].id)
        }
    }

    return (
        <div className="min-h-screen bg-white">
            <AdminHeader
                title="What Have Unions Done For Us - Admin"
                subtitle="Administrative tools"
            />

            <main id="main-content" className="max-w-4xl mx-auto px-4 py-6" tabIndex={-1}>
                {/* Tab Navigation */}
                <div className="border-b border-gray-200 mb-6">
                    <div role="tablist" aria-label="Admin dashboard navigation" className="-mb-px flex space-x-8 overflow-x-auto">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                onKeyDown={handleKeyDown}
                                role="tab"
                                aria-selected={activeTab === tab.id}
                                aria-controls={`panel-${tab.id}`}
                                className={`
                                    whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500
                                    ${activeTab === tab.id
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }
                                `}
                                tabIndex={activeTab === tab.id ? 0 : -1}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Tab Content */}
                <div>
                    {activeTab === 'pending' && (
                        <div role="tabpanel" id="panel-pending" aria-labelledby="tab-pending">
                            <AdminPendingSubmissions adminPassword={adminPassword} />
                        </div>
                    )}
                    {activeTab === 'recent' && (
                        <div role="tabpanel" id="panel-recent" aria-labelledby="tab-recent">
                            <AdminRecentWins adminPassword={adminPassword} />
                        </div>
                    )}
                    {activeTab === 'search' && (
                        <div role="tabpanel" id="panel-search" aria-labelledby="tab-search">
                            <AdminSearchPanel adminPassword={adminPassword} />
                        </div>
                    )}
                    {activeTab === 'status' && (
                        <div role="tabpanel" id="panel-status" aria-labelledby="tab-status">
                            <AdminSearchStatus />
                        </div>
                    )}
                    {activeTab === 'scraping' && (
                        <div role="tabpanel" id="panel-scraping" aria-labelledby="tab-scraping">
                            <AdminScrapeSources />
                        </div>
                    )}
                    {activeTab === 'api-keys' && (
                        <div role="tabpanel" id="panel-api-keys" aria-labelledby="tab-api-keys">
                            <AdminApiKeys adminPassword={adminPassword} />
                        </div>
                    )}
                    {activeTab === 'newsletter' && (
                        <div role="tabpanel" id="panel-newsletter" aria-labelledby="tab-newsletter">
                            <AdminNewsletterSubscribers adminPassword={adminPassword} />
                        </div>
                    )}
                </div>
            </main>
            <Footer />
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

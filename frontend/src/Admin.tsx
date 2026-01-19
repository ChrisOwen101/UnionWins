import { useState } from 'react'
import { AdminHeader } from './components/AdminHeader'
import { AdminSearchPanel } from './components/AdminSearchPanel'
import { AdminSearchStatus } from './components/AdminSearchStatus'
import { AdminPendingSubmissions } from './components/AdminPendingSubmissions'
import { AdminRecentWins } from './components/AdminRecentWins'

type TabId = 'pending' | 'recent' | 'search' | 'status'

interface Tab {
    id: TabId
    label: string
}

const tabs: Tab[] = [
    { id: 'pending', label: 'Pending Submissions' },
    { id: 'recent', label: 'Recent Wins' },
    { id: 'search', label: 'Search' },
    { id: 'status', label: 'Search Status' },
]

function Admin() {
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
                    <nav className="-mb-px flex space-x-8" aria-label="Tabs">
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
                    {activeTab === 'pending' && <AdminPendingSubmissions />}
                    {activeTab === 'recent' && <AdminRecentWins />}
                    {activeTab === 'search' && <AdminSearchPanel />}
                    {activeTab === 'status' && <AdminSearchStatus />}
                </div>
            </main>
        </div>
    )
}

export default Admin

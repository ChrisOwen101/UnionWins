import { AdminHeader } from './components/AdminHeader'
import { AdminSearchPanel } from './components/AdminSearchPanel'
import { AdminSearchStatus } from './components/AdminSearchStatus'
import { AdminQuickActions } from './components/AdminQuickActions'
import { AdminPendingSubmissions } from './components/AdminPendingSubmissions'

function Admin() {
    return (
        <div className="min-h-screen bg-white">
            <AdminHeader
                title="What Have Unions Done For Us - Admin"
                subtitle="Administrative tools"
            />

            <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
                <AdminPendingSubmissions />
                <AdminSearchPanel />
                <AdminSearchStatus />
                <AdminQuickActions />
            </main>
        </div>
    )
}

export default Admin

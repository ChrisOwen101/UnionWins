import { AdminHeader } from './components/AdminHeader'
import { AdminSearchPanel } from './components/AdminSearchPanel'
import { AdminQuickActions } from './components/AdminQuickActions'
import { AdminPendingSubmissions } from './components/AdminPendingSubmissions'

function Admin() {
    return (
        <div className="min-h-screen bg-white">
            <AdminHeader
                title="Union Wins - Admin"
                subtitle="Administrative tools"
            />

            <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
                <AdminPendingSubmissions />
                <AdminSearchPanel />
                <AdminQuickActions />
            </main>
        </div>
    )
}

export default Admin

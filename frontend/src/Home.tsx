import { useState } from 'react'
import { useWins } from './hooks/useWins'
import { filterWinsByQuery } from './utils/filterHelpers'
import { Header } from './components/Header'
import { SearchInput } from './components/SearchInput'
import { LoadingState } from './components/LoadingState'
import { WinsList } from './components/WinsList'
import { SubmitWinModal } from './components'

function Home() {
    const { wins, loading } = useWins()
    const [searchQuery, setSearchQuery] = useState('')
    const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false)

    const filteredWins = filterWinsByQuery(wins, searchQuery)

    const handleSubmitWin = async (url: string, submittedBy?: string) => {
        const response = await fetch('/api/submissions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, submitted_by: submittedBy }),
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to submit win')
        }

        return response.json()
    }

    return (
        <div className="min-h-screen bg-neutral-50">
            <Header
                title="What Have Unions Done For Us?"
                showAdminLink
                onSubmitClick={() => setIsSubmitModalOpen(true)}
            />

            <main className="max-w-3xl mx-auto px-5 py-6">
                <SearchInput
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder="Search wins by title, union, source, or keyword..."
                />

                {loading ? (
                    <LoadingState />
                ) : (
                    <WinsList wins={filteredWins} searchQuery={searchQuery} />
                )}
            </main>

            <SubmitWinModal
                isOpen={isSubmitModalOpen}
                onClose={() => setIsSubmitModalOpen(false)}
                onSubmit={handleSubmitWin}
            />
        </div>
    )
}

export default Home

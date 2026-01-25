import { useState } from 'react'
import { useWins } from './hooks/useWins'
import { Header } from './components/Header'
import { SearchInput } from './components/SearchInput'
import { LoadingState } from './components/LoadingState'
import { WinsList } from './components/WinsList'
import { SubmitWinModal, NewsletterNotification } from './components'

function Home() {
    const {
        wins,
        loading,
        loadingMore,
        hasMore,
        loadMore,
        searchWins,
        clearSearch,
        isSearching,
        searchQuery
    } = useWins()
    const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false)

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

            <main id="main-content" className="max-w-3xl mx-auto px-5 py-6" tabIndex={-1}>
                <SearchInput
                    onSearch={searchWins}
                    onClear={clearSearch}
                    placeholder="Search wins by title, union, source, or keyword..."
                    isSearching={loading && isSearching}
                />

                {loading && !isSearching ? (
                    <LoadingState />
                ) : (
                    <WinsList
                        wins={wins}
                        searchQuery={searchQuery}
                        hasMore={hasMore && !isSearching}
                        loadMore={loadMore}
                        loadingMore={loadingMore}
                        onSubmitClick={() => setIsSubmitModalOpen(true)}
                    />
                )}
            </main>

            <SubmitWinModal
                isOpen={isSubmitModalOpen}
                onClose={() => setIsSubmitModalOpen(false)}
                onSubmit={handleSubmitWin}
            />

            <NewsletterNotification delayMs={10000} />
        </div>
    )
}

export default Home

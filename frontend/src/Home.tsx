import { useState, useMemo, useEffect } from 'react'
import { useWins } from './hooks/useWins'
import { Header } from './components/Header'
import { SearchInput } from './components/SearchInput'
import { LoadingState } from './components/LoadingState'
import { WinsList } from './components/WinsList'
import { SubmitWinModal, NewsletterNotification, FilterControls } from './components'
import { filterWinsByTypesAndUnion } from './utils/filterHelpers'
import type { WinType } from './types'

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
    const [selectedTypes, setSelectedTypes] = useState<WinType[]>([])
    const [selectedUnion, setSelectedUnion] = useState<string>('')
    const [isFiltersExpanded, setIsFiltersExpanded] = useState(false)
    const [allUnions, setAllUnions] = useState<string[]>([])
    const [isSearchHovered, setIsSearchHovered] = useState(false)
    const [isFiltersHovered, setIsFiltersHovered] = useState(false)

    // Fetch unions for autocomplete
    useEffect(() => {
        fetch('/api/wins/unions')
            .then(res => res.json())
            .then(data => setAllUnions(data))
            .catch(err => console.error('Failed to fetch unions:', err))
    }, [])

    // Apply filters to wins
    const filteredWins = useMemo(() => {
        return filterWinsByTypesAndUnion(wins, selectedTypes, selectedUnion)
    }, [wins, selectedTypes, selectedUnion])

    const handleSearchFocus = () => {
        setIsFiltersExpanded(true)
    }

    const handleSearchBlur = () => {
        // Don't close if search or filters are being hovered
        if (!isSearchHovered && !isFiltersHovered) {
            setIsFiltersExpanded(false)
        }
    }

    const handleToggleFilters = () => {
        setIsFiltersExpanded(!isFiltersExpanded)
    }

    const handleUnionSelect = (union: string) => {
        setSelectedUnion(union)
    }

    const activeFilterCount = selectedTypes.length + (selectedUnion ? 1 : 0)

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
                    onFocus={handleSearchFocus}
                    onBlur={handleSearchBlur}
                    placeholder="Search wins or type a union name..."
                    isSearching={loading && isSearching}
                    unions={allUnions}
                    onUnionSelect={handleUnionSelect}
                    activeFilterCount={activeFilterCount}
                    onToggleFilters={handleToggleFilters}
                    onHoverChange={setIsSearchHovered}
                />

                <FilterControls
                    wins={wins}
                    selectedTypes={selectedTypes}
                    selectedUnion={selectedUnion}
                    onTypesChange={setSelectedTypes}
                    onUnionChange={setSelectedUnion}
                    isExpanded={isFiltersExpanded}
                    onHoverChange={setIsFiltersHovered}
                />

                {loading && !isSearching ? (
                    <LoadingState />
                ) : (
                    <WinsList
                        wins={filteredWins}
                        searchQuery={searchQuery}
                        hasMore={hasMore && !isSearching && selectedTypes.length === 0 && selectedUnion === ''}
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

            <NewsletterNotification delayMs={5000} />
        </div>
    )
}

export default Home

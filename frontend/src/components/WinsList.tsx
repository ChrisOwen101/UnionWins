import { useEffect, useRef, useCallback } from 'react'
import type { UnionWin } from '../types'
import { groupByMonth } from '../utils/groupingHelpers'
import { MonthSection } from './MonthSection'

interface WinsListProps {
    wins: UnionWin[]
    searchQuery: string
    hasMore: boolean
    loadMore: () => void
    loadingMore: boolean
    onSubmitClick?: () => void
}

/**
 * Component to display a list of wins grouped by month with infinite scroll
 */
export const WinsList: React.FC<WinsListProps> = ({
    wins,
    searchQuery,
    hasMore,
    loadMore,
    loadingMore,
    onSubmitClick
}) => {
    const groupedWins = groupByMonth(wins)
    const observerRef = useRef<IntersectionObserver | null>(null)
    const loadMoreRef = useRef<HTMLDivElement>(null)
    const resultsStatusId = 'results-status'

    const handleObserver = useCallback(
        (entries: IntersectionObserverEntry[]) => {
            const target = entries[0]
            if (target.isIntersecting && hasMore && !loadingMore) {
                loadMore()
            }
        },
        [hasMore, loadMore, loadingMore]
    )

    useEffect(() => {
        const element = loadMoreRef.current
        if (!element) return

        observerRef.current = new IntersectionObserver(handleObserver, {
            root: null,
            rootMargin: '100px',
            threshold: 0
        })

        observerRef.current.observe(element)

        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect()
            }
        }
    }, [handleObserver])

    if (wins.length === 0 && searchQuery) {
        return (
            <div role="region" aria-labelledby={resultsStatusId} aria-live="polite" aria-atomic="true">
                <p id={resultsStatusId} className="text-center text-gray-700 text-sm py-8">
                    No wins found matching "{searchQuery}"
                </p>
            </div>
        )
    }

    if (wins.length === 0) {
        return (
            <div role="region" aria-labelledby={resultsStatusId} aria-live="polite" aria-atomic="true">
                <p id={resultsStatusId} className="text-center text-gray-700 text-sm py-8">
                    No wins to display
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            <div role="region" aria-labelledby={resultsStatusId}>
                <p id={resultsStatusId} className="sr-only">
                    {wins.length} union {wins.length === 1 ? 'win' : 'wins'} displayed
                </p>
            </div>

            {groupedWins.map(([monthKey, monthWins]) => (
                <MonthSection
                    key={monthKey}
                    monthKey={monthKey}
                    wins={monthWins}
                />
            ))}

            {/* Infinite scroll trigger */}
            <div ref={loadMoreRef} className="h-10">
                {loadingMore && (
                    <div className="flex justify-center py-4" role="status" aria-live="polite">
                        <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" aria-hidden="true" />
                        <span className="sr-only">Loading more wins</span>
                    </div>
                )}
                {!hasMore && wins.length > 0 && (
                    <p className="text-center text-gray-600 text-sm py-4">
                        You've reached the beginning.{' '}
                        <button
                            onClick={onSubmitClick}
                            className="text-orange-600 hover:text-orange-700 font-medium"
                            aria-label="Submit a new union win"
                        >
                            Submit a win
                        </button>
                    </p>
                )}
            </div>
        </div>
    )
}

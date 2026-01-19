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
            <p className="text-center text-gray-700 text-sm py-8">
                No wins found matching "{searchQuery}"
            </p>
        )
    }

    if (wins.length === 0) {
        return (
            <p className="text-center text-gray-700 text-sm py-8">
                No wins to display
            </p>
        )
    }

    return (
        <div className="space-y-8">
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
                    <div className="flex justify-center py-4">
                        <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                )}
                {!hasMore && wins.length > 0 && (
                    <p className="text-center text-gray-600 text-sm py-4">
                        You've reached the beginning.{' '}
                        <button
                            onClick={onSubmitClick}
                            className="text-orange-500 hover:text-orange-600 font-medium"
                        >
                            Submit a win
                        </button>
                    </p>
                )}
            </div>
        </div>
    )
}

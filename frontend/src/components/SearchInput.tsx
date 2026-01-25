import { useState, useEffect, useRef } from 'react'

interface SearchInputProps {
    onSearch: (query: string) => void
    onClear: () => void
    placeholder?: string
    isSearching?: boolean
}

/**
 * Search input component with debounced API search
 */
export const SearchInput: React.FC<SearchInputProps> = ({
    onSearch,
    onClear,
    placeholder = 'Search...',
    isSearching = false
}) => {
    const [inputValue, setInputValue] = useState('')
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const statusId = useRef('search-status')

    useEffect(() => {
        // Clear any existing timeout
        if (debounceRef.current) {
            clearTimeout(debounceRef.current)
        }

        // Debounce the search
        debounceRef.current = setTimeout(() => {
            if (inputValue.trim()) {
                onSearch(inputValue)
            } else {
                onClear()
            }
        }, 300)

        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current)
            }
        }
    }, [inputValue, onSearch, onClear])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value)
    }

    const handleClear = () => {
        setInputValue('')
        onClear()
    }

    return (
        <div className="mb-6 relative">
            <label htmlFor="search-input" className="sr-only">
                Search wins
            </label>
            <input
                id="search-input"
                type="search"
                placeholder={placeholder}
                value={inputValue}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent pr-10"
                aria-describedby={isSearching ? statusId.current : undefined}
                autoComplete="off"
            />
            {inputValue && (
                <button
                    onClick={handleClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1"
                    type="button"
                    aria-label="Clear search"
                    title="Clear search (Ctrl+A then Delete)"
                >
                    ✕
                </button>
            )}
            {isSearching && inputValue && (
                <div className="absolute right-10 top-1/2 -translate-y-1/2" aria-label="Searching">
                    <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                </div>
            )}
            {isSearching && (
                <div id={statusId.current} className="sr-only" role="status" aria-live="polite">
                    Searching for "{inputValue}"
                </div>
            )}
        </div>
    )
}

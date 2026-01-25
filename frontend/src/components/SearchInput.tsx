import { useState, useEffect, useRef } from 'react'

interface SearchInputProps {
    onSearch: (query: string) => void
    onClear: () => void
    onFocus?: () => void
    onBlur?: () => void
    placeholder?: string
    isSearching?: boolean
    unions?: string[]
    onUnionSelect?: (union: string) => void
    activeFilterCount?: number
    onToggleFilters?: () => void
    onHoverChange?: (isHovering: boolean) => void
}

/**
 * Search input component with debounced API search and union autocomplete
 */
export const SearchInput: React.FC<SearchInputProps> = ({
    onSearch,
    onClear,
    onFocus,
    onBlur,
    placeholder = 'Search...',
    isSearching = false,
    unions = [],
    onUnionSelect,
    activeFilterCount = 0,
    onToggleFilters,
    onHoverChange
}) => {
    const [inputValue, setInputValue] = useState('')
    const [showSuggestions, setShowSuggestions] = useState(false)
    const [selectedIndex, setSelectedIndex] = useState(-1)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const statusId = useRef('search-status')
    const inputRef = useRef<HTMLInputElement>(null)
    const suggestionsRef = useRef<HTMLUListElement>(null)

    // Filter unions based on input
    const filteredUnions = unions.filter(union =>
        union.toLowerCase().includes(inputValue.toLowerCase())
    ).slice(0, 8) // Limit to 8 suggestions

    const shouldShowSuggestions = showSuggestions && inputValue.length > 0 && filteredUnions.length > 0

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

    // Reset selected index when suggestions change
    useEffect(() => {
        setSelectedIndex(-1)
    }, [filteredUnions.length])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value)
        setShowSuggestions(true)
    }

    const handleClear = () => {
        setInputValue('')
        setShowSuggestions(false)
        onClear()
    }

    const handleFocus = () => {
        setShowSuggestions(true)
        onFocus?.()
    }

    const handleBlur = () => {
        // Delay to allow click on suggestion
        setTimeout(() => {
            setShowSuggestions(false)
            onBlur?.()
        }, 150)
    }

    const handleUnionClick = (union: string) => {
        setInputValue('')
        setShowSuggestions(false)
        onUnionSelect?.(union)
        inputRef.current?.blur()
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (!shouldShowSuggestions) return

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault()
                setSelectedIndex(prev =>
                    prev < filteredUnions.length - 1 ? prev + 1 : prev
                )
                break
            case 'ArrowUp':
                e.preventDefault()
                setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
                break
            case 'Enter':
                if (selectedIndex >= 0 && selectedIndex < filteredUnions.length) {
                    e.preventDefault()
                    handleUnionClick(filteredUnions[selectedIndex])
                }
                break
            case 'Escape':
                setShowSuggestions(false)
                setSelectedIndex(-1)
                break
        }
    }

    return (
        <div className="mb-4">
            <div
                className="flex items-center gap-2"
                onMouseEnter={() => onHoverChange?.(true)}
                onMouseLeave={() => onHoverChange?.(false)}
            >
                <div className="relative flex-1">
                    <label htmlFor="search-input" className="sr-only">
                        Search wins
                    </label>
                    <input
                        ref={inputRef}
                        id="search-input"
                        type="search"
                        placeholder={placeholder}
                        value={inputValue}
                        onChange={handleChange}
                        onFocus={handleFocus}
                        onBlur={handleBlur}
                        onKeyDown={handleKeyDown}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent pr-10"
                        aria-describedby={isSearching ? statusId.current : undefined}
                        aria-expanded={shouldShowSuggestions}
                        aria-autocomplete="list"
                        aria-controls={shouldShowSuggestions ? 'union-suggestions' : undefined}
                        aria-activedescendant={selectedIndex >= 0 ? `suggestion-${selectedIndex}` : undefined}
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

                    {/* Union Autocomplete Suggestions */}
                    {shouldShowSuggestions && (
                        <ul
                            ref={suggestionsRef}
                            id="union-suggestions"
                            role="listbox"
                            className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto"
                        >
                            <li className="px-3 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100">
                                Filter by Union
                            </li>
                            {filteredUnions.map((union, index) => (
                                <li
                                    key={union}
                                    id={`suggestion-${index}`}
                                    role="option"
                                    aria-selected={index === selectedIndex}
                                    onClick={() => handleUnionClick(union)}
                                    className={`px-3 py-2 cursor-pointer text-sm transition-colors ${index === selectedIndex
                                            ? 'bg-orange-50 text-orange-700'
                                            : 'text-gray-700 hover:bg-gray-50'
                                        }`}
                                >
                                    <span className="flex items-center gap-2">
                                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                        </svg>
                                        {union}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                {/* Filter Indicator Button */}
                <div className={`flex-shrink-0 transition-all duration-200 ease-in-out overflow-hidden ${activeFilterCount > 0 ? 'max-w-24 opacity-100' : 'max-w-0 opacity-0'
                    }`}>
                    {onToggleFilters && (
                        <button
                            type="button"
                            onClick={onToggleFilters}
                            className="flex items-center gap-2 px-3 py-2 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-700 hover:bg-orange-100 transition-colors whitespace-nowrap"
                            aria-label={`${activeFilterCount} filter${activeFilterCount > 1 ? 's' : ''} active. Click to view.`}
                            title="View active filters"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                            </svg>
                            <span className="font-medium">{activeFilterCount}</span>
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}

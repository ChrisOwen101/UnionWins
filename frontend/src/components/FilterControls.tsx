import { useMemo, useState, useEffect } from 'react'
import type { UnionWin, WinType } from '../types'
import { WIN_TYPES } from '../types'

interface FilterControlsProps {
    wins: UnionWin[]
    selectedTypes: WinType[]
    selectedUnion: string
    onTypesChange: (types: WinType[]) => void
    onUnionChange: (union: string) => void
    isExpanded: boolean
    onHoverChange?: (isHovering: boolean) => void
}

/**
 * Filter controls for filtering wins by type and union name
 */
export const FilterControls: React.FC<FilterControlsProps> = ({
    wins,
    selectedTypes,
    selectedUnion,
    onTypesChange,
    onUnionChange,
    isExpanded,
    onHoverChange
}) => {
    // Fetch canonical union list from API
    const [allUnions, setAllUnions] = useState<string[]>([])

    useEffect(() => {
        fetch('/api/wins/unions')
            .then(res => res.json())
            .then(data => setAllUnions(data))
            .catch(err => console.error('Failed to fetch unions:', err))
    }, [])

    // Extract unique win types that are actually present in the data
    const availableTypes = useMemo(() => {
        const types = new Set<WinType>()
        wins.forEach(win => {
            if (win.win_types) {
                // Parse comma-separated win types
                const winTypesList = win.win_types.split(',').map(t => t.trim())
                winTypesList.forEach(type => {
                    if (WIN_TYPES.includes(type as WinType)) {
                        types.add(type as WinType)
                    }
                })
            }
        })
        return WIN_TYPES.filter(type => types.has(type))
    }, [wins])

    const hasFilters = selectedTypes.length > 0 || selectedUnion !== ''

    const handleClearFilters = () => {
        onTypesChange([])
        onUnionChange('')
    }

    const handleTypeToggle = (type: WinType) => {
        if (selectedTypes.includes(type)) {
            onTypesChange(selectedTypes.filter(t => t !== type))
        } else {
            onTypesChange([...selectedTypes, type])
        }
    }

    return (
        <div className="mb-4">
            {/* Filter Panel */}
            <div
                id="filter-panel"
                className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                    }`}
                onMouseEnter={() => onHoverChange?.(true)}
                onMouseLeave={() => onHoverChange?.(false)}
            >
                <div className="py-3 px-4 bg-gray-50 rounded-lg border border-gray-200 space-y-4">
                    {/* Type Filters */}
                    <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">
                            Filter by Win Type
                        </span>
                        <div className="flex flex-wrap gap-2">
                            {availableTypes.map(type => {
                                const isSelected = selectedTypes.includes(type)
                                return (
                                    <button
                                        key={type}
                                        type="button"
                                        onClick={() => handleTypeToggle(type)}
                                        className={`inline-flex items-center px-3 py-1.5 text-sm rounded-full border transition-all duration-150 ${isSelected
                                                ? 'bg-orange-50 border-orange-300 text-orange-700 shadow-sm'
                                                : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                                            }`}
                                        aria-pressed={isSelected}
                                    >
                                        {isSelected && (
                                            <svg className="w-3.5 h-3.5 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                            </svg>
                                        )}
                                        {type}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    {/* Union Filter */}
                    <div>
                        <label htmlFor="filter-union" className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">
                            Filter by Union
                        </label>
                        <select
                            id="filter-union"
                            value={selectedUnion}
                            onChange={(e) => onUnionChange(e.target.value)}
                            className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 w-full max-w-xs"
                            aria-label="Filter by union name"
                        >
                            <option value="">All Unions</option>
                            {allUnions.map(name => (
                                <option key={name} value={name}>
                                    {name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Clear Filters */}
                    {hasFilters && (
                        <button
                            onClick={handleClearFilters}
                            className="inline-flex items-center gap-1.5 text-sm text-orange-600 hover:text-orange-700 transition-colors"
                            aria-label="Clear all filters"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            Clear all filters
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}

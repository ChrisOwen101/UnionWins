interface SearchInputProps {
    value: string
    onChange: (value: string) => void
    placeholder?: string
}

/**
 * Search input component for filtering wins
 */
export const SearchInput: React.FC<SearchInputProps> = ({
    value,
    onChange,
    placeholder = 'Search...'
}) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.value)
    }

    return (
        <div className="mb-6">
            <input
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
        </div>
    )
}

import { useState } from 'react'

/**
 * Admin panel for searching new What Have Unions Done For Us
 */
export const AdminSearchPanel: React.FC = () => {
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const [days, setDays] = useState(7)
    const [customDate, setCustomDate] = useState('')

    const handleSearch = async () => {
        setLoading(true)
        setMessage('')

        try {
            // Build request body with configurable parameters
            const requestBody: { days: number; date?: string } = { days }
            if (customDate) {
                requestBody.date = customDate
            }

            const response = await fetch('/api/wins/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()

            if (data.message && data.note) {
                setMessage(`${data.message} - ${data.note}`)
            } else if (data.message) {
                setMessage(data.message)
            } else if (data.detail) {
                // Handle FastAPI error format
                setMessage(`Error: ${data.detail}`)
            } else {
                setMessage('Search completed with unexpected response format')
            }
        } catch (err) {
            setMessage('Error: ' + (err as Error).message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-2">
                Search for New What Have Unions Done For Us
            </h2>
            <p className="text-sm text-gray-600 mb-4">
                Trigger OpenAI deep research to find recent union victories.
            </p>

            <div className="space-y-4 mb-4">
                <div>
                    <label htmlFor="days" className="block text-sm font-medium text-gray-700 mb-1">
                        Number of Days to Search
                    </label>
                    <input
                        id="days"
                        type="number"
                        min="1"
                        max="365"
                        value={days}
                        onChange={(e) => setDays(parseInt(e.target.value) || 7)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        Search for wins from the last {days} day{days !== 1 ? 's' : ''}
                    </p>
                </div>

                <div>
                    <label htmlFor="customDate" className="block text-sm font-medium text-gray-700 mb-1">
                        Custom End Date (Optional)
                    </label>
                    <input
                        id="customDate"
                        type="date"
                        value={customDate}
                        onChange={(e) => setCustomDate(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        {customDate
                            ? `Search up to ${customDate}`
                            : 'Leave empty to search up to today'}
                    </p>
                </div>
            </div>

            <button
                onClick={handleSearch}
                disabled={loading}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
                {loading ? 'Searching...' : 'Search for New Wins'}
            </button>

            {message && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded text-sm text-gray-700">
                    {message}
                </div>
            )}
        </div>
    )
}

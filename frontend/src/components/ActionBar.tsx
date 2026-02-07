import { Link } from 'react-router-dom'

interface ActionBarProps {
    onSubmitClick?: () => void
}

/**
 * Action bar component that sits below the header
 * Contains Stats and Submit buttons
 */
export const ActionBar: React.FC<ActionBarProps> = ({ onSubmitClick }) => {
    return (
        <div className="bg-white border-b border-gray-200">
            <div className="max-w-3xl mx-auto px-5 py-3">
                <nav aria-label="Action bar navigation" className="flex items-center justify-end gap-3">
                    <Link
                        to="/stats"
                        className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="View statistics and charts"
                        aria-label="View statistics page"
                    >
                        📊 Stats
                    </Link>
                    {onSubmitClick && (
                        <button
                            onClick={onSubmitClick}
                            className="bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium px-4 py-2 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
                            title="Submit a union win"
                            aria-label="Open submit union win dialog"
                        >
                            + Submit Win
                        </button>
                    )}
                </nav>
            </div>
        </div>
    )
}

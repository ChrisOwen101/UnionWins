import { Link } from 'react-router-dom'

interface HeaderProps {
    title: string
    subtitle?: string
    onSubmitClick?: () => void
}

/**
 * Full-width header component with title and action buttons
 */
export const Header: React.FC<HeaderProps> = ({ title, subtitle, onSubmitClick }) => {
    return (
        <header className="bg-white border-b border-gray-200 px-5 py-4">
            <div className="max-w-6xl mx-auto">
                <div>
                    <h1 className="text-4xl font-light text-gray-900">{title}</h1>
                    {subtitle && (
                        <p className="text-gray-600 mt-1">{subtitle}</p>
                    )}
                </div>
                <nav aria-label="Primary navigation" className="flex flex-wrap items-center justify-end gap-2 sm:gap-4 mt-4">
                    <Link
                        to="/about"
                        className="inline-flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-3 sm:px-4 py-2 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="Learn more about this site"
                        aria-label="About page"
                    >
                        <span>ℹ️</span><span className="hidden sm:inline sm:ml-2"> About</span>
                    </Link>
                    <Link
                        to="/newsletter"
                        className="inline-flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-3 sm:px-4 py-2 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="Subscribe to our newsletter"
                        aria-label="Newsletter page"
                    >
                        <span>📧</span><span className="hidden sm:inline sm:ml-2"> Newsletter</span>
                    </Link>
                    <Link
                        to="/stats"
                        className="inline-flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-3 sm:px-4 py-2 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="View statistics and charts"
                        aria-label="View statistics page"
                    >
                        <span>📊</span><span className="hidden sm:inline sm:ml-2"> Stats</span>
                    </Link>
                    {onSubmitClick && (
                        <button
                            onClick={onSubmitClick}
                            className="inline-flex items-center justify-center bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium px-3 sm:px-4 py-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
                            title="Submit a union win"
                            aria-label="Open submit union win dialog"
                        >
                            <span className="sm:hidden">➕</span>
                            <span className="hidden sm:inline">+ Submit Win</span>
                        </button>
                    )}
                </nav>
            </div>
        </header>
    )
}

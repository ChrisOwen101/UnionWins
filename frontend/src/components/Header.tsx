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
            <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-light text-gray-900">{title}</h1>
                    {subtitle && (
                        <p className="text-gray-600 mt-1">{subtitle}</p>
                    )}
                </div>
                <nav aria-label="Primary navigation" className="flex flex-wrap items-center gap-3">
                    <Link
                        to="/about"
                        className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="Learn more about this site"
                        aria-label="About page"
                    >
                        ℹ️ About
                    </Link>
                    <Link
                        to="/newsletter"
                        className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        title="Subscribe to our newsletter"
                        aria-label="Newsletter page"
                    >
                        📧 Newsletter
                    </Link>
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
        </header>
    )
}

import { Link } from 'react-router-dom'

/**
 * Footer component with links to legal pages and other information
 */
export const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear()

    return (
        <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="max-w-3xl mx-auto px-5 py-6">
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-gray-600">
                        © {currentYear} What Have Unions Done For Us?
                    </p>
                    <nav aria-label="Footer navigation" className="flex gap-4">
                        <Link
                            to="/terms"
                            className="text-sm text-gray-600 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 rounded px-2 py-1"
                        >
                            Terms of Service
                        </Link>
                        <Link
                            to="/privacy"
                            className="text-sm text-gray-600 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 rounded px-2 py-1"
                        >
                            Privacy Policy
                        </Link>
                    </nav>
                </div>
            </div>
        </footer>
    )
}

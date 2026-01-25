interface HeaderProps {
    title: string
    subtitle?: string
    showAdminLink?: boolean
    onSubmitClick?: () => void
}

/**
 * Header component with title and optional admin link
 */
export const Header: React.FC<HeaderProps> = ({ title, subtitle, onSubmitClick }) => {
    return (
        <header className="bg-white border-b border-gray-200 px-5 py-4">
            <div className="max-w-3xl mx-auto flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-light text-gray-900">{title}</h1>
                    {subtitle && (
                        <p className="text-gray-600 mt-1">{subtitle}</p>
                    )}
                </div>
                <div className="flex items-center gap-4">
                    {onSubmitClick && (
                        <button
                            onClick={onSubmitClick}
                            className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium"
                            title="Submit a union win"
                        >
                            + Submit
                        </button>
                    )}
                </div>
            </div>
        </header>
    )
}

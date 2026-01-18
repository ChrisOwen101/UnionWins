interface AdminHeaderProps {
    title: string
    subtitle: string
}

/**
 * Admin-specific header component
 */
export const AdminHeader: React.FC<AdminHeaderProps> = ({ title, subtitle }) => {
    return (
        <header className="bg-gray-900 px-4 py-3 border-b border-gray-200">
            <div className="max-w-4xl mx-auto flex items-center gap-3">
                <div className="w-8 h-8 bg-red-600 flex items-center justify-center text-white font-bold text-sm">
                    U
                </div>
                <div>
                    <h1 className="font-bold text-white text-base">{title}</h1>
                    <p className="text-gray-400 text-xs">{subtitle}</p>
                </div>
                <a
                    href="/"
                    className="ml-auto text-sm text-gray-400 hover:text-white"
                >
                    ← Back to home
                </a>
            </div>
        </header>
    )
}

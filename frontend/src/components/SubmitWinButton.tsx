interface SubmitWinButtonProps {
    onClick: () => void
}

export function SubmitWinButton({ onClick }: SubmitWinButtonProps) {
    return (
        <button
            onClick={onClick}
            className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            aria-label="Open submit union win form"
        >
            <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                />
            </svg>
            Submit a Union Win
        </button>
    )
}

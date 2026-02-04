interface LoadingStateProps {
    message?: string
    fillScreen?: boolean
}

/**
 * Loading state component
 */
export const LoadingState: React.FC<LoadingStateProps> = ({
    message = 'Loading...',
    fillScreen = false
}) => {
    return (
        <div
            role="status"
            aria-live="polite"
            aria-busy="true"
            className={`text-center py-8 flex items-center justify-center ${fillScreen ? 'min-h-[calc(100vh-200px)]' : ''}`}
        >
            <div className="inline-flex gap-2 items-center">
                <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" aria-hidden="true" />
                <p className="text-gray-500 text-sm">
                    {message}
                </p>
            </div>
        </div>
    )
}

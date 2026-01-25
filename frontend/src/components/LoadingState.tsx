interface LoadingStateProps {
    message?: string
}

/**
 * Loading state component
 */
export const LoadingState: React.FC<LoadingStateProps> = ({
    message = 'Loading...'
}) => {
    return (
        <div role="status" aria-live="polite" aria-busy="true" className="text-center py-8">
            <div className="inline-flex gap-2 items-center">
                <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" aria-hidden="true" />
                <p className="text-gray-500 text-sm">
                    {message}
                </p>
            </div>
        </div>
    )
}

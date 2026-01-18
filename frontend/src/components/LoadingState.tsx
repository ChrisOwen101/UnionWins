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
        <p className="text-center text-gray-500 text-sm py-8">
            {message}
        </p>
    )
}

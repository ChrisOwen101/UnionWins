import { useState } from 'react'

interface SubmitWinModalProps {
    isOpen: boolean
    onClose: () => void
    onSubmit: (url: string, submittedBy?: string) => Promise<void>
}

export function SubmitWinModal({ isOpen, onClose, onSubmit }: SubmitWinModalProps) {
    const [url, setUrl] = useState('')
    const [submittedBy, setSubmittedBy] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    if (!isOpen) return null

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setSuccess(false)

        if (!url.trim()) {
            setError('Please enter a URL')
            return
        }

        // Basic URL validation
        try {
            new URL(url)
        } catch {
            setError('Please enter a valid URL')
            return
        }

        setIsSubmitting(true)

        try {
            await onSubmit(url, submittedBy.trim() || undefined)
            setSuccess(true)
            setUrl('')
            setSubmittedBy('')

            // Auto close after success
            setTimeout(() => {
                onClose()
                setSuccess(false)
            }, 2000)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to submit. Please try again.')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleClose = () => {
        if (!isSubmitting) {
            setUrl('')
            setSubmittedBy('')
            setError('')
            setSuccess(false)
            onClose()
        }
    }

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={handleClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">
                        Submit a Union Win
                    </h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                        disabled={isSubmitting}
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {success ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                        <p className="text-green-800 font-medium">
                            ✓ Submission received! It will be reviewed by an admin.
                        </p>
                    </div>
                ) : (
                    <>
                        <p className="text-gray-600 mb-4">
                            Share a news article or blog post about a recent union victory.
                            Our AI will extract the details and an admin will review before publishing.
                        </p>

                        <form onSubmit={handleSubmit}>
                            <div className="mb-4">
                                <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                                    Article URL *
                                </label>
                                <input
                                    type="text"
                                    id="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://example.com/union-victory"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                    disabled={isSubmitting}
                                    required
                                />
                            </div>

                            <div className="mb-6">
                                <label htmlFor="submittedBy" className="block text-sm font-medium text-gray-700 mb-2">
                                    Your Name or Email (optional)
                                </label>
                                <input
                                    type="text"
                                    id="submittedBy"
                                    value={submittedBy}
                                    onChange={(e) => setSubmittedBy(e.target.value)}
                                    placeholder="Jane Doe or jane@example.com"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                    disabled={isSubmitting}
                                />
                            </div>

                            {error && (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                                    <p className="text-red-800 text-sm">{error}</p>
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={handleClose}
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                                    disabled={isSubmitting}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Submitting...' : 'Submit'}
                                </button>
                            </div>
                        </form>
                    </>
                )}
            </div>
        </div>
    )
}

import { useState, useEffect, useRef, useCallback } from 'react'

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
    const [errorId] = useState('modal-error')
    const [success, setSuccess] = useState(false)
    const dialogRef = useRef<HTMLDivElement>(null)
    const previousFocusRef = useRef<HTMLElement | null>(null)

    const handleClose = useCallback(() => {
        if (!isSubmitting) {
            setUrl('')
            setSubmittedBy('')
            setError('')
            setSuccess(false)
            onClose()
        }
    }, [isSubmitting, onClose])

    // Handle focus trap and keyboard
    useEffect(() => {
        if (!isOpen) return

        // Store the current focus
        previousFocusRef.current = document.activeElement as HTMLElement

        // Move focus to first input
        const firstInput = dialogRef.current?.querySelector('input')
        firstInput?.focus()

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && !isSubmitting) {
                handleClose()
            }
        }

        window.addEventListener('keydown', handleKeyDown)
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
            // Restore focus when modal closes
            previousFocusRef.current?.focus()
        }
    }, [isOpen, isSubmitting, handleClose])

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

    if (!isOpen) return null

    return (
        <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            onClick={handleClose}
            role="presentation"
        >
            <div
                ref={dialogRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
                aria-describedby={error ? errorId : undefined}
                className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex justify-between items-center mb-4">
                    <h2 id="modal-title" className="text-2xl font-bold text-gray-900">
                        Submit a Union Win
                    </h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors p-1"
                        disabled={isSubmitting}
                        aria-label="Close dialog"
                        title="Close dialog (Esc)"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {success ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4" role="status" aria-live="polite">
                        <p className="text-green-800 font-medium">
                            ✓ Submission received! It will be reviewed by an admin.
                        </p>
                    </div>
                ) : (
                    <>
                        <p className="text-gray-600 mb-4">
                            Share a news article or blog post about a recent union victory. We'll extract the details and an admin will review before publishing.
                        </p>

                        <p className="text-gray-600 mb-4">
                            Want to bulk upload multiple wins? Email us <a href="mailto:cowen19921@gmail.com" className="text-orange-600 hover:underline">
                                here
                            </a> and we'll be in touch.
                        </p>

                        <form onSubmit={handleSubmit}>
                            <div className="mb-4">
                                <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                                    URL <span aria-label="required">*</span>
                                </label>
                                <input
                                    type="url"
                                    id="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://example.com/union-victory"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                    disabled={isSubmitting}
                                    aria-required="true"
                                    aria-invalid={error ? 'true' : 'false'}
                                    aria-describedby={error ? errorId : undefined}
                                    required
                                />
                            </div>

                            <div className="mb-6">
                                <label htmlFor="submittedBy" className="block text-sm font-medium text-gray-700 mb-2">
                                    Email <span className="text-gray-500">(optional)</span>
                                </label>
                                <input
                                    type="email"
                                    id="submittedBy"
                                    value={submittedBy}
                                    onChange={(e) => setSubmittedBy(e.target.value)}
                                    placeholder="Jane Doe or jane@example.com"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                    disabled={isSubmitting}
                                />
                            </div>

                            {error && (
                                <div id={errorId} className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4" role="alert">
                                    <p className="text-red-800 text-sm">{error}</p>
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={handleClose}
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                                    disabled={isSubmitting}
                                    aria-label="Cancel submission"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                                    disabled={isSubmitting}
                                    aria-label={isSubmitting ? 'Submitting form' : 'Submit form'}
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

import { useState, useEffect, useCallback } from 'react'

type Frequency = 'daily' | 'weekly' | 'monthly'

interface NewsletterNotificationProps {
    /** Delay in milliseconds before showing the notification */
    delayMs?: number
}

const STORAGE_KEY = 'newsletter_dismissed'
const DISMISS_DURATION_DAYS = 7

export function NewsletterNotification({ delayMs = 7000 }: NewsletterNotificationProps) {
    const [isVisible, setIsVisible] = useState(false)
    const [email, setEmail] = useState('')
    const [name, setName] = useState('')
    const [frequency, setFrequency] = useState<Frequency>('weekly')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    const checkIfDismissed = useCallback((): boolean => {
        const dismissed = localStorage.getItem(STORAGE_KEY)
        if (!dismissed) return false

        const dismissedTime = parseInt(dismissed, 10)
        const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24)
        return daysSinceDismissed < DISMISS_DURATION_DAYS
    }, [])

    useEffect(() => {
        if (checkIfDismissed()) return

        const timer = setTimeout(() => {
            setIsVisible(true)
        }, delayMs)

        return () => clearTimeout(timer)
    }, [delayMs, checkIfDismissed])

    const handleDismiss = () => {
        localStorage.setItem(STORAGE_KEY, Date.now().toString())
        setIsVisible(false)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!email.trim()) {
            setError('Please enter your email')
            return
        }

        // Basic email validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailPattern.test(email)) {
            setError('Please enter a valid email')
            return
        }

        setIsSubmitting(true)

        try {
            const response = await fetch('/api/newsletter/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email.trim(),
                    name: name.trim() || null,
                    frequency,
                }),
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to subscribe')
            }

            setSuccess(true)
            localStorage.setItem(STORAGE_KEY, Date.now().toString())

            // Auto-hide after success
            setTimeout(() => {
                setIsVisible(false)
            }, 3000)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Something went wrong')
        } finally {
            setIsSubmitting(false)
        }
    }

    if (!isVisible) return null

    return (
        <div className="fixed bottom-4 right-4 z-40 animate-subtle-fade">
            <div className="bg-gray-50 rounded-lg shadow-sm border border-gray-200 w-80 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-gray-700 to-gray-600 px-4 py-2 flex justify-between items-center">
                    <h3 className="text-white font-medium text-xs tracking-wide">
                        ✊ Union Wins Updates
                    </h3>
                    <button
                        onClick={handleDismiss}
                        className="text-white/60 hover:text-white/90 transition-colors duration-200"
                        aria-label="Dismiss notification"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-3">
                    {success ? (
                        <div className="text-center py-1">
                            <div className="text-gray-600 text-sm mb-0.5">✓</div>
                            <p className="text-gray-700 font-medium text-xs">You're subscribed!</p>
                            <p className="text-gray-500 text-xs">Check your inbox.</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            <p className="text-gray-600 text-xs mb-2.5 leading-relaxed">
                                Get notified about union victories.
                            </p>

                            <div className="space-y-2">
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="your@email.com"
                                    className="w-full px-2.5 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-transparent placeholder-gray-400"
                                    disabled={isSubmitting}
                                    required
                                />

                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Name (optional)"
                                    className="w-full px-2.5 py-1.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-transparent placeholder-gray-400"
                                    disabled={isSubmitting}
                                />

                                <div className="flex gap-1">
                                    {(['daily', 'weekly', 'monthly'] as const).map((freq) => (
                                        <button
                                            key={freq}
                                            type="button"
                                            onClick={() => setFrequency(freq)}
                                            disabled={isSubmitting}
                                            className={`flex-1 px-1.5 py-1 text-xs font-medium rounded transition-colors duration-150 ${frequency === freq
                                                ? 'bg-gray-700 text-white'
                                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                                }`}
                                        >
                                            {freq.charAt(0).toUpperCase() + freq.slice(1)}
                                        </button>
                                    ))}
                                </div>

                                {error && (
                                    <p className="text-gray-600 text-xs">{error}</p>
                                )}

                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="w-full bg-gray-700 text-white py-1.5 px-3 rounded text-xs font-medium hover:bg-gray-600 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isSubmitting ? 'Subscribing...' : 'Subscribe'}
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    )
}

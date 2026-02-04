import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Footer } from './components/Footer'

type Frequency = 'daily' | 'weekly' | 'monthly'

function Newsletter() {
    const [email, setEmail] = useState('')
    const [name, setName] = useState('')
    const [frequency, setFrequency] = useState<Frequency>('weekly')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!email.trim()) {
            setError('Please enter your email')
            return
        }

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
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Something went wrong')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="min-h-screen bg-neutral-50 flex flex-col">
            <header className="bg-white border-b border-gray-200 px-5 py-4">
                <div className="max-w-3xl mx-auto">
                    <Link
                        to="/"
                        className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium"
                    >
                        ← Back to Home
                    </Link>
                </div>
            </header>

            <main id="main-content" className="max-w-3xl mx-auto px-5 py-8 flex-grow w-full">
                <h1 className="text-4xl font-light text-gray-900 mb-4">Newsletter</h1>
                <p className="text-gray-600">
                    Stay informed about the latest union wins and achievements. Get summarised updates delivered directly to your inbox.
                </p>

                <section className="mt-12 mb-12">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-3">What you'll receive</h2>
                    <ul className="space-y-3">
                        <li className="flex items-start gap-3">
                            <span className="text-orange-500 mt-0.5" aria-hidden="true">✓</span>
                            <span className="text-gray-700">Curated summaries of recent union victories</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="text-orange-500 mt-0.5" aria-hidden="true">✓</span>
                            <span className="text-gray-700">Highlights of significant workplace improvements</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="text-orange-500 mt-0.5" aria-hidden="true">✓</span>
                            <span className="text-gray-700">Updates on labour rights achievements</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="text-orange-500 mt-0.5" aria-hidden="true">✓</span>
                            <span className="text-gray-700">No spam, just the wins that matter</span>
                        </li>
                    </ul>
                </section>

                {success ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center mt-6">
                        <div className="text-green-600 text-4xl mb-4" aria-hidden="true">✓</div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">You're subscribed!</h2>
                        <p className="text-gray-600 mb-4">
                            Thank you for subscribing. You'll receive your first update soon.
                        </p>
                        <Link
                            to="/"
                            className="inline-block px-6 py-2 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
                        >
                            Back to Union Wins
                        </Link>
                    </div>
                ) : (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Subscribe to Updates</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label htmlFor="newsletter-email" className="block text-sm font-medium text-gray-700 mb-1">
                                    Email address <span className="text-red-500">*</span>
                                </label>
                                <input
                                    id="newsletter-email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="your@email.com"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent placeholder-gray-400"
                                    disabled={isSubmitting}
                                    aria-required="true"
                                />
                            </div>

                            <div>
                                <label htmlFor="newsletter-name" className="block text-sm font-medium text-gray-700 mb-1">
                                    Name <span className="text-gray-400">(optional)</span>
                                </label>
                                <input
                                    id="newsletter-name"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Your name"
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent placeholder-gray-400"
                                    disabled={isSubmitting}
                                />
                            </div>

                            <div>
                                <label htmlFor="newsletter-frequency" className="block text-sm font-medium text-gray-700 mb-1">
                                    How often would you like updates?
                                </label>
                                <select
                                    id="newsletter-frequency"
                                    value={frequency}
                                    onChange={(e) => setFrequency(e.target.value as Frequency)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white"
                                    disabled={isSubmitting}
                                >
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                    <option value="monthly">Monthly</option>
                                </select>
                            </div>

                            {error && (
                                <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-2" role="alert">
                                    {error}
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="w-full px-6 py-3 bg-orange-500 text-white font-semibold rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
                            >
                                {isSubmitting ? 'Subscribing...' : 'Subscribe'}
                            </button>
                        </form>

                        <p className="text-xs text-gray-500 mt-4 text-center">
                            We respect your privacy. Unsubscribe at any time.
                        </p>
                    </div>
                )}
            </main>

            <Footer />
        </div>
    )
}

export default Newsletter

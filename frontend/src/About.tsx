import { Link } from 'react-router-dom'
import { Footer } from './components/Footer'

function About() {
    return (
        <div className="min-h-screen bg-neutral-50">
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

            <main className="max-w-3xl mx-auto px-5 py-8">
                <h1 className="text-4xl font-light text-gray-900 mb-8">About</h1>

                <div className="prose prose-gray max-w-none">
                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">What is this?</h2>
                        <p className="text-gray-700 mb-4">
                            What Have Unions Done For Us? is a collection of recent union victories and achievements.
                            We track and showcase the real-world impact unions have on workers' lives, from wage increases
                            and better benefits to improved working conditions and landmark agreements.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Why?</h2>
                        <p className="text-gray-700 mb-4">
                            In an era where union organizing is experiencing a resurgence, it's important to document
                            and celebrate these wins. This platform serves as both a record of union achievements and
                            inspiration for workers considering organizing their own workplaces.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">How does it work?</h2>
                        <p className="text-gray-700 mb-4">
                            We collect union wins from various sources including news articles, union announcements,
                            and community submissions. Each win is verified and categorized to make it easy to browse
                            and search through the victories.
                        </p>
                        <p className="text-gray-700 mb-4">
                            You can submit union wins using the "Submit Win" button, search for specific unions or
                            topics, and filter by win type to find exactly what you're looking for.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Get Involved</h2>
                        <p className="text-gray-700 mb-4">
                            Know of a recent union win we haven't covered? Submit it using the form on the homepage.
                            Want to stay updated? Subscribe to our newsletter to get the latest union victories
                            delivered to your inbox.
                        </p>
                    </section>
                </div>
            </main>

            <Footer />
        </div>
    )
}

export default About

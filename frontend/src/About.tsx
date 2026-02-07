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
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Why?</h2>
                        <p className="text-gray-700 mb-4">
                            Every day, <strong>unions across the UK are winning victories for workers</strong>. From securing better pay and benefits to improving working conditions and fighting for workers' rights, unions are making a real difference in people's lives. However, <strong>these wins are often forgotten</strong> or lost in the noise of daily news. What Have Unions Done For Us? aims to change that by creating a central hub to celebrate and highlight the incredible work unions are doing across the country.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">What?</h2>
                        <p className="text-gray-700 mb-4">
                            What Have Unions Done For Us? is a collection of recent union victories and achievements.
                            We track and showcase the real-world impact unions have on workers' lives, from wage increases
                            and better benefits to improved working conditions and landmark agreements.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">How?</h2>
                        <p className="text-gray-700 mb-4">
                            We collect union wins from various sources including news articles, union announcements,
                            and community submissions. Each win is verified and categorised to make it easy to browse
                            and search through the victories.
                        </p>
                        <p className="text-gray-700 mb-4">
                            You can submit union wins using the "Submit Win" button, search for specific unions or
                            topics, and filter by win type to find exactly what you're looking for.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Who?</h2>
                        <p className="text-gray-700 mb-4">
                            This project was created by Chris Owen, a political technologist and software developer.
                            If you have any questions, suggestions, or want to contribute, feel free to reach out at
                            <a href="mailto:cowen19921@gmail.com " className="text-orange-600 hover:underline">
                                cowen19921@gmail.com
                            </a> or connect on <a
                                href="https://www.linkedin.com/in/chrisowen101/"
                                className="text-orange-600 hover:underline"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                LinkedIn
                            </a>.
                        </p>
                    </section>
                </div>
            </main>

            <Footer />
        </div>
    )
}

export default About

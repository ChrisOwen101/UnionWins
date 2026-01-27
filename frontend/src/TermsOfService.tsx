import { Link } from 'react-router-dom'
import { Footer } from './components/Footer'

function TermsOfService() {
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
                <h1 className="text-4xl font-light text-gray-900 mb-8">Terms of Service</h1>

                <div className="prose prose-gray max-w-none">
                    <p className="text-gray-600 mb-6">
                        Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                    </p>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
                        <p className="text-gray-700 mb-4">
                            By accessing and using What Have Unions Done For Us? ("the Service"), you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
                        <p className="text-gray-700 mb-4">
                            What Have Unions Done For Us? is a platform that aggregates and displays information about union victories, achievements, and campaigns. The Service allows users to:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Browse union wins and achievements</li>
                            <li>Search for specific unions or types of wins</li>
                            <li>Submit union wins for review</li>
                            <li>Subscribe to newsletters (optional)</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Submissions</h2>
                        <p className="text-gray-700 mb-4">
                            When submitting content to the Service, you agree that:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Your submissions are factual and not misleading</li>
                            <li>You have the right to submit the content</li>
                            <li>Your submissions do not violate any laws or third-party rights</li>
                            <li>You grant us the right to display and distribute submitted content</li>
                            <li>We may moderate, edit, or remove submissions at our discretion</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Acceptable Use</h2>
                        <p className="text-gray-700 mb-4">
                            You agree not to:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Submit false, misleading, or defamatory information</li>
                            <li>Abuse or overload the Service's systems</li>
                            <li>Attempt unauthorized access to the Service</li>
                            <li>Use the Service for any illegal purpose</li>
                            <li>Harass, threaten, or abuse other users</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Intellectual Property</h2>
                        <p className="text-gray-700 mb-4">
                            The Service and its original content, features, and functionality are owned by What Have Unions Done For Us? and are protected by international copyright, trademark, and other intellectual property laws.
                        </p>
                        <p className="text-gray-700 mb-4">
                            Union wins and related information may be sourced from public sources and third parties. We respect intellectual property rights and expect users to do the same.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Disclaimer of Warranties</h2>
                        <p className="text-gray-700 mb-4">
                            The Service is provided "as is" without warranties of any kind, either express or implied. We do not guarantee:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>The accuracy or completeness of information displayed</li>
                            <li>Uninterrupted or error-free service</li>
                            <li>The security of data transmitted through the Service</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Limitation of Liability</h2>
                        <p className="text-gray-700 mb-4">
                            To the fullest extent permitted by law, What Have Unions Done For Us? shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. External Links</h2>
                        <p className="text-gray-700 mb-4">
                            The Service may contain links to third-party websites. We are not responsible for the content, privacy policies, or practices of external sites.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Modifications to Service</h2>
                        <p className="text-gray-700 mb-4">
                            We reserve the right to modify, suspend, or discontinue the Service at any time without notice. We are not liable for any modification, suspension, or discontinuation of the Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Changes to Terms</h2>
                        <p className="text-gray-700 mb-4">
                            We may update these Terms of Service from time to time. Changes will be effective immediately upon posting. Your continued use of the Service constitutes acceptance of the updated terms.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Governing Law</h2>
                        <p className="text-gray-700 mb-4">
                            These Terms shall be governed by and construed in accordance with applicable laws, without regard to conflict of law provisions.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Contact Information</h2>
                        <p className="text-gray-700 mb-4">
                            If you have any questions about these Terms of Service, please contact us through our submission form.
                        </p>
                    </section>
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default TermsOfService

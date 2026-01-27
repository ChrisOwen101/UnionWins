import { Link } from 'react-router-dom'
import { Footer } from './components/Footer'

function PrivacyPolicy() {
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
                <h1 className="text-4xl font-light text-gray-900 mb-8">Privacy Policy</h1>

                <div className="prose prose-gray max-w-none">
                    <p className="text-gray-600 mb-6">
                        Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                    </p>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
                        <p className="text-gray-700 mb-4">
                            What Have Unions Done For Us? ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service.
                        </p>
                        <p className="text-gray-700 mb-4">
                            Please read this privacy policy carefully. If you do not agree with the terms of this privacy policy, please do not access the Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>

                        <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">Information You Provide</h3>
                        <p className="text-gray-700 mb-4">
                            We may collect information that you voluntarily provide when using the Service, including:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li><strong>Newsletter Subscription:</strong> Email address when subscribing to newsletters</li>
                            <li><strong>Win Submissions:</strong> URL and optional name when submitting union wins</li>
                            <li><strong>API Access:</strong> Email address when requesting API access</li>
                        </ul>

                        <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">Automatically Collected Information</h3>
                        <p className="text-gray-700 mb-4">
                            When you access the Service, we may automatically collect certain information, including:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Log data (IP address, browser type, pages visited, time spent)</li>
                            <li>Device information (device type, operating system)</li>
                            <li>Usage data (features used, interactions with the Service)</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
                        <p className="text-gray-700 mb-4">
                            We use the information we collect for the following purposes:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>To provide, maintain, and improve the Service</li>
                            <li>To send newsletter emails to subscribers</li>
                            <li>To process and display submitted union wins</li>
                            <li>To manage API access and authentication</li>
                            <li>To analyze usage patterns and improve user experience</li>
                            <li>To detect and prevent fraud or abuse</li>
                            <li>To comply with legal obligations</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Sharing Your Information</h2>
                        <p className="text-gray-700 mb-4">
                            We do not sell, trade, or rent your personal information to third parties. We may share your information in the following circumstances:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li><strong>Service Providers:</strong> With third-party vendors who perform services on our behalf (e.g., email delivery, hosting)</li>
                            <li><strong>Legal Requirements:</strong> When required by law or to protect our rights and safety</li>
                            <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
                            <li><strong>With Your Consent:</strong> When you explicitly agree to share information</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Cookies and Tracking Technologies</h2>
                        <p className="text-gray-700 mb-4">
                            We may use cookies and similar tracking technologies to track activity on our Service. Cookies are small data files stored on your device. You can instruct your browser to refuse cookies or to indicate when a cookie is being sent.
                        </p>
                        <p className="text-gray-700 mb-4">
                            We use cookies for:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Session management</li>
                            <li>Remembering user preferences</li>
                            <li>Analytics and performance monitoring</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Retention</h2>
                        <p className="text-gray-700 mb-4">
                            We retain your personal information only for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required by law.
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li>Newsletter subscriptions: Until you unsubscribe</li>
                            <li>Win submissions: Indefinitely as part of our historical record</li>
                            <li>API keys: Until revoked or account is deleted</li>
                            <li>Log data: Typically 90 days</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Your Privacy Rights</h2>
                        <p className="text-gray-700 mb-4">
                            Depending on your location, you may have the following rights:
                        </p>
                        <ul className="list-disc pl-6 text-gray-700 mb-4">
                            <li><strong>Access:</strong> Request access to your personal information</li>
                            <li><strong>Correction:</strong> Request correction of inaccurate information</li>
                            <li><strong>Deletion:</strong> Request deletion of your personal information</li>
                            <li><strong>Opt-out:</strong> Unsubscribe from newsletters at any time</li>
                            <li><strong>Data Portability:</strong> Request a copy of your data in a portable format</li>
                            <li><strong>Object:</strong> Object to processing of your personal information</li>
                        </ul>
                        <p className="text-gray-700 mb-4">
                            To exercise these rights, please contact us through our submission form.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Data Security</h2>
                        <p className="text-gray-700 mb-4">
                            We implement appropriate technical and organizational security measures to protect your personal information. However, no method of transmission over the Internet or electronic storage is 100% secure, and we cannot guarantee absolute security.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Third-Party Links</h2>
                        <p className="text-gray-700 mb-4">
                            The Service may contain links to third-party websites. We are not responsible for the privacy practices or content of these external sites. We encourage you to review the privacy policies of any third-party sites you visit.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Children's Privacy</h2>
                        <p className="text-gray-700 mb-4">
                            Our Service is not directed to children under the age of 13. We do not knowingly collect personal information from children under 13. If you become aware that a child has provided us with personal information, please contact us.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. International Data Transfers</h2>
                        <p className="text-gray-700 mb-4">
                            Your information may be transferred to and maintained on servers located outside of your state, province, country, or other governmental jurisdiction where data protection laws may differ. By using the Service, you consent to this transfer.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Changes to This Privacy Policy</h2>
                        <p className="text-gray-700 mb-4">
                            We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Contact Us</h2>
                        <p className="text-gray-700 mb-4">
                            If you have questions or concerns about this Privacy Policy, please contact us through our submission form.
                        </p>
                    </section>
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default PrivacyPolicy

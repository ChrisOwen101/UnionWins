import { Header, Footer } from './components'

function ApiSignup() {
    const developerEmail = 'chris@whathaveunionsdoneforus.uk'

    return (
        <div className="min-h-screen bg-white">
            <Header
                title="What Have Unions Done For Us"
                subtitle="API Access"
            />

            <main className="max-w-2xl mx-auto px-4 py-12">
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <h1 className="text-3xl font-bold mb-6">API Access</h1>

                    <div className="prose">
                        <p className="text-gray-700 mb-6">
                            Want to build something with our union wins data? We offer free API access
                            to developers, researchers, and organisations working to promote labour rights.
                        </p>

                        <h2 className="text-xl font-semibold mt-8 mb-4">What you get</h2>
                        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
                            <li>Access to all union win records</li>
                            <li>Search functionality across all data</li>
                            <li>Paginated endpoints for efficient data loading</li>
                            <li>JSON responses for easy integration</li>
                        </ul>

                        <h2 className="text-xl font-semibold mt-8 mb-4">API Endpoints</h2>
                        <div className="bg-gray-50 rounded-lg p-4 mb-6">
                            <code className="text-sm">
                                <div className="mb-2">
                                    <span className="text-green-600 font-semibold">GET</span>{' '}
                                    <span className="text-blue-600">/api/wins</span>
                                    <span className="text-gray-500 ml-2">- Get all wins</span>
                                </div>
                                <div className="mb-2">
                                    <span className="text-green-600 font-semibold">GET</span>{' '}
                                    <span className="text-blue-600">/api/wins/paginated</span>
                                    <span className="text-gray-500 ml-2">- Get wins with pagination</span>
                                </div>
                                <div>
                                    <span className="text-green-600 font-semibold">GET</span>{' '}
                                    <span className="text-blue-600">/api/wins/query?q=search</span>
                                    <span className="text-gray-500 ml-2">- Search wins</span>
                                </div>
                            </code>
                        </div>

                        <h2 className="text-xl font-semibold mt-8 mb-4">Authentication</h2>
                        <p className="text-gray-700 mb-4">
                            All API requests require an API key. Include your key in the request header:
                        </p>
                        <div className="bg-gray-50 rounded-lg p-4 mb-6">
                            <code className="text-sm text-gray-700">
                                X-API-Key: your_api_key_here
                            </code>
                        </div>

                        <h2 className="text-xl font-semibold mt-8 mb-4">Request an API Key</h2>
                        <p className="text-gray-700 mb-6">
                            To request an API key, please send an email to the developer with:
                        </p>
                        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
                            <li>Your name</li>
                            <li>Your organisation (if applicable)</li>
                            <li>What you plan to build with the API</li>
                            <li>Expected usage volume</li>
                        </ul>

                        <div className="mt-8 p-6 bg-blue-50 rounded-lg text-center">
                            <p className="text-gray-700 mb-4">
                                Ready to get started?
                            </p>
                            <a
                                href={`mailto:${developerEmail}?subject=Union%20Wins%20API%20Key%20Request&body=Hi%2C%0A%0AI%27d%20like%20to%20request%20an%20API%20key%20for%20the%20Union%20Wins%20API.%0A%0AName%3A%20%0AOrganization%3A%20%0AProject%20description%3A%20%0AExpected%20usage%3A%20%0A%0AThanks!`}
                                className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                📧 Email {developerEmail}
                            </a>
                        </div>

                        <div className="mt-8 text-center">
                            <a
                                href="/"
                                className="text-blue-600 hover:underline"
                            >
                                ← Back to Union Wins
                            </a>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}

export default ApiSignup

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './Home'
import Admin from './Admin'
import ApiSignup from './ApiSignup'
import Stats from './Stats'
import TermsOfService from './TermsOfService'
import PrivacyPolicy from './PrivacyPolicy'

function App() {
    const skipToMainContent = () => {
        const mainContent = document.getElementById('main-content')
        if (mainContent) {
            mainContent.focus()
            mainContent.scrollIntoView()
        }
    }

    return (
        <Router>
            {/* Skip to main content link for keyboard navigation */}
            <a
                href="#main-content"
                onClick={skipToMainContent}
                className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:bg-blue-600 focus:text-white focus:px-4 focus:py-2"
            >
                Skip to main content
            </a>

            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/api-signup" element={<ApiSignup />} />
                <Route path="/stats" element={<Stats />} />
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
            </Routes>
        </Router>
    )
}

export default App

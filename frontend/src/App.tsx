import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './Home'
import Admin from './Admin'
import ApiSignup from './ApiSignup'

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/api-signup" element={<ApiSignup />} />
            </Routes>
        </Router>
    )
}

export default App

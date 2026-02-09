import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Umami Analytics - Only enabled in production
if (import.meta.env.PROD) {
  const script = document.createElement('script');
  script.defer = true;
  script.src = 'https://analytics.whathaveunionsdoneforus.uk/script.js';
  script.dataset.websiteId = '9984204a-d911-46e4-8212-8ca2e7ca9ad1';
  document.head.appendChild(script);
}

ReactDOM.createRoot(document.getElementById('root')!).render(<App />)

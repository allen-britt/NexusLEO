import { Link, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CasePage from './pages/CasePage';

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="header__brand">
          <Link to="/">NexusLEO Demo UI</Link>
        </div>
        <div className="header__right">
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            API Docs
          </a>
        </div>
      </header>

      <main className="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/cases/:id" element={<CasePage />} />
        </Routes>
      </main>
    </div>
  );
}

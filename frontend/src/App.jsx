/**
 * App Component — Root layout for the Wiki Quiz App.
 * Manages two tabs: Generate Quiz (Tab 1) and Past Quizzes (Tab 2).
 */

import { useState } from 'react';
import GenerateQuiz from './components/GenerateQuiz';
import PastQuizzes from './components/PastQuizzes';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('generate');

  return (
    <div className="app-container">
      {/* ── Header ──────────────────────────────────── */}
      <header className="app-header">
        <h1 className="app-logo">
          <span>📚</span> Wiki Quiz
        </h1>
        <p className="app-subtitle">
          Generate AI-powered quizzes from any Wikipedia article
        </p>
      </header>

      {/* ── Tab Navigation ──────────────────────────── */}
      <div className="tab-container">
        <button
          className={`tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
          id="tab-generate"
        >
          🎯 Generate Quiz
        </button>
        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
          id="tab-history"
        >
          📋 Past Quizzes
        </button>
      </div>

      {/* ── Tab Content ─────────────────────────────── */}
      <main>
        {activeTab === 'generate' ? <GenerateQuiz /> : <PastQuizzes />}
      </main>

      {/* ── Footer ──────────────────────────────────── */}
      <footer style={{
        textAlign: 'center',
        padding: '40px 0',
        color: 'var(--text-muted)',
        fontSize: '0.8rem'
      }}>
        Built with FastAPI, LangChain, Gemini & React
      </footer>
    </div>
  );
}

export default App;

/**
 * QuizDisplay Component
 * Renders the structured, card-based quiz layout showing article info,
 * entities, sections, questions, and related topics.
 */

import { useState } from 'react';
import TakeQuiz from './TakeQuiz';

const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

export default function QuizDisplay({ data }) {
  const [showTakeQuiz, setShowTakeQuiz] = useState(false);

  if (!data) return null;

  if (showTakeQuiz) {
    return (
      <TakeQuiz
        questions={data.quiz}
        title={data.title}
        onBack={() => setShowTakeQuiz(false)}
      />
    );
  }

  return (
    <div className="quiz-results">
      {/* ── Article Header ──────────────────────────────────── */}
      <div className="quiz-header">
        <h2 className="quiz-title">{data.title}</h2>
        <p className="quiz-summary">{data.summary}</p>
        <div className="quiz-meta">
          <span className="meta-badge">
            <span className="badge-icon">📝</span>
            {data.quiz.length} Questions
          </span>
          <span className="meta-badge">
            <span className="badge-icon">📑</span>
            {data.sections?.length || 0} Sections
          </span>
          <span className="meta-badge">
            <span className="badge-icon">🔗</span>
            <a href={data.url} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit' }}>
              Source
            </a>
          </span>
          <button className="btn-take-quiz" onClick={() => setShowTakeQuiz(true)}>
            🎯 Take Quiz
          </button>
        </div>
      </div>

      {/* ── Key Entities ───────────────────────────────────── */}
      {data.key_entities && (
        <>
          <div className="section-header">
            <h3 className="section-title">
              <span className="icon">🏷️</span> Key Entities
            </h3>
          </div>
          <div className="entities-grid">
            {data.key_entities.people?.length > 0 && (
              <div className="entity-card">
                <div className="entity-type">👤 People</div>
                <ul className="entity-list">
                  {data.key_entities.people.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.key_entities.organizations?.length > 0 && (
              <div className="entity-card">
                <div className="entity-type">🏛️ Organizations</div>
                <ul className="entity-list">
                  {data.key_entities.organizations.map((o, i) => (
                    <li key={i}>{o}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.key_entities.locations?.length > 0 && (
              <div className="entity-card">
                <div className="entity-type">📍 Locations</div>
                <ul className="entity-list">
                  {data.key_entities.locations.map((l, i) => (
                    <li key={i}>{l}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </>
      )}

      {/* ── Sections ────────────────────────────────────────── */}
      {data.sections?.length > 0 && (
        <>
          <div className="section-header">
            <h3 className="section-title">
              <span className="icon">📑</span> Article Sections
            </h3>
          </div>
          <div className="sections-list">
            {data.sections.map((s, i) => (
              <span className="section-tag" key={i}>{s}</span>
            ))}
          </div>
        </>
      )}

      {/* ── Quiz Questions ──────────────────────────────────── */}
      <div className="section-header">
        <h3 className="section-title">
          <span className="icon">❓</span> Quiz Questions
        </h3>
        <span className="section-count">{data.quiz.length} questions</span>
      </div>

      <div className="questions-list">
        {data.quiz.map((q, index) => (
          <div className="question-card" key={index}>
            <div className="question-top">
              <span className="question-number">Q{index + 1}</span>
              <span className={`difficulty-badge difficulty-${q.difficulty}`}>
                {q.difficulty}
              </span>
            </div>
            <p className="question-text">{q.question}</p>

            <div className="options-grid">
              {q.options.map((opt, i) => (
                <div
                  className={`option-item ${opt === q.answer ? 'correct' : ''}`}
                  key={i}
                >
                  <span className="option-letter">{OPTION_LETTERS[i]}</span>
                  <span>{opt}</span>
                </div>
              ))}
            </div>

            <div className="answer-section">
              <div className="answer-label">✅ Answer</div>
              <div className="answer-text">{q.answer}</div>
              <div className="explanation-text">{q.explanation}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Related Topics ──────────────────────────────────── */}
      {data.related_topics?.length > 0 && (
        <div className="related-topics">
          <div className="section-header" style={{ marginTop: 0 }}>
            <h3 className="section-title">
              <span className="icon">🔗</span> Related Topics
            </h3>
          </div>
          <div className="topics-list">
            {data.related_topics.map((topic, i) => (
              <a
                key={i}
                className="topic-chip"
                href={`https://en.wikipedia.org/wiki/${encodeURIComponent(topic.replace(/ /g, '_'))}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                {topic}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

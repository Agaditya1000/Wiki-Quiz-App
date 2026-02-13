/**
 * TakeQuiz Component
 * Interactive quiz mode where answers are hidden until the user submits.
 * Tracks selections, scores the quiz, and shows results.
 */

import { useState } from 'react';

const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

export default function TakeQuiz({ questions, title, onBack }) {
    const [answers, setAnswers] = useState({});       // { questionIndex: selectedOption }
    const [submitted, setSubmitted] = useState(false);
    const [score, setScore] = useState(0);

    // Handle option selection
    const handleSelect = (qIndex, option) => {
        if (submitted) return;
        setAnswers(prev => ({ ...prev, [qIndex]: option }));
    };

    // Submit and calculate score
    const handleSubmit = () => {
        let correct = 0;
        questions.forEach((q, i) => {
            if (answers[i] === q.answer) correct++;
        });
        setScore(correct);
        setSubmitted(true);
    };

    // Reset quiz
    const handleRetry = () => {
        setAnswers({});
        setSubmitted(false);
        setScore(0);
    };

    const answeredCount = Object.keys(answers).length;
    const totalQuestions = questions.length;
    const progressPercent = (answeredCount / totalQuestions) * 100;

    // Score-based feedback message
    const getScoreMessage = () => {
        const pct = (score / totalQuestions) * 100;
        if (pct === 100) return '🏆 Perfect score! Outstanding!';
        if (pct >= 80) return '🌟 Excellent work! Very impressive!';
        if (pct >= 60) return '👍 Good job! Keep learning!';
        if (pct >= 40) return '📚 Not bad! Review the article for more details.';
        return '💪 Keep trying! Read the article and try again.';
    };

    return (
        <div className="take-quiz-container">
            {/* ── Header ─────────────────────────────────── */}
            <div className="quiz-header">
                <h2 className="quiz-title">📝 {title} — Quiz</h2>
                <div className="quiz-meta">
                    <span className="meta-badge">
                        <span className="badge-icon">❓</span>
                        {totalQuestions} Questions
                    </span>
                    {!submitted && (
                        <span className="meta-badge">
                            <span className="badge-icon">✏️</span>
                            {answeredCount} / {totalQuestions} Answered
                        </span>
                    )}
                    <button className="btn-secondary" onClick={onBack}>
                        ← Back to Results
                    </button>
                </div>
            </div>

            {/* ── Score Card (shown after submit) ─────────── */}
            {submitted && (
                <div className="quiz-score">
                    <div className="quiz-score-number">{score} / {totalQuestions}</div>
                    <div className="quiz-score-label">
                        {Math.round((score / totalQuestions) * 100)}% Correct
                    </div>
                    <div className="quiz-score-message">{getScoreMessage()}</div>
                    <div className="quiz-actions">
                        <button className="btn-secondary" onClick={handleRetry}>
                            🔄 Retry Quiz
                        </button>
                        <button className="btn-secondary" onClick={onBack}>
                            📊 View Full Results
                        </button>
                    </div>
                </div>
            )}

            {/* ── Progress Bar ───────────────────────────── */}
            {!submitted && (
                <>
                    <div className="quiz-progress">
                        <div
                            className="quiz-progress-bar"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                    <div className="quiz-progress-text">
                        {answeredCount} of {totalQuestions} questions answered
                    </div>
                </>
            )}

            {/* ── Questions ──────────────────────────────── */}
            <div className="questions-list">
                {questions.map((q, qIndex) => {
                    const userAnswer = answers[qIndex];
                    const isCorrect = userAnswer === q.answer;

                    return (
                        <div className="take-quiz-card" key={qIndex}>
                            <div className="question-top">
                                <span className="question-number">Q{qIndex + 1}</span>
                                <span className={`difficulty-badge difficulty-${q.difficulty}`}>
                                    {q.difficulty}
                                </span>
                            </div>
                            <p className="question-text">{q.question}</p>

                            <div className="take-quiz-options">
                                {q.options.map((opt, oIndex) => {
                                    let className = 'take-quiz-option';
                                    if (submitted) {
                                        if (opt === q.answer) className += ' correct-answer';
                                        else if (opt === userAnswer && !isCorrect) className += ' wrong-answer';
                                    } else if (opt === userAnswer) {
                                        className += ' selected';
                                    }

                                    return (
                                        <button
                                            key={oIndex}
                                            className={className}
                                            onClick={() => handleSelect(qIndex, opt)}
                                            disabled={submitted}
                                        >
                                            <span className="option-letter">{OPTION_LETTERS[oIndex]}</span>
                                            <span>{opt}</span>
                                        </button>
                                    );
                                })}
                            </div>

                            {/* Show explanation after submit */}
                            {submitted && (
                                <div className="answer-section" style={{ marginTop: '12px' }}>
                                    <div className="answer-label">
                                        {isCorrect ? '✅ Correct!' : '❌ Incorrect'}
                                    </div>
                                    <div className="answer-text">Answer: {q.answer}</div>
                                    <div className="explanation-text">{q.explanation}</div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* ── Submit Button ──────────────────────────── */}
            {!submitted && (
                <div className="quiz-actions">
                    <button
                        className="btn-submit-quiz"
                        onClick={handleSubmit}
                        disabled={answeredCount < totalQuestions}
                    >
                        {answeredCount < totalQuestions
                            ? `Answer all questions (${answeredCount}/${totalQuestions})`
                            : '🎯 Submit Answers'}
                    </button>
                </div>
            )}
        </div>
    );
}

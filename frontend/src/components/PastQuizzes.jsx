/**
 * PastQuizzes Component (Tab 2)
 * Displays a table of previously generated quizzes.
 * Clicking "Details" fetches full quiz data and shows it in a modal.
 */

import { useState, useEffect } from 'react';
import QuizModal from './QuizModal';

const API_BASE = 'http://localhost:8000/api/quiz';

export default function PastQuizzes() {
    const [quizzes, setQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedQuiz, setSelectedQuiz] = useState(null);
    const [modalLoading, setModalLoading] = useState(false);

    // ── Fetch quiz history on mount ─────────────────────────────────
    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/history`);
            if (!res.ok) throw new Error('Failed to fetch history');
            const data = await res.json();
            setQuizzes(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // ── Fetch full quiz details and show modal ──────────────────────
    const handleDetails = async (id) => {
        setModalLoading(true);
        try {
            const res = await fetch(`${API_BASE}/${id}`);
            if (!res.ok) throw new Error('Failed to fetch quiz details');
            const data = await res.json();
            setSelectedQuiz(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setModalLoading(false);
        }
    };

    // ── Format date for display ─────────────────────────────────────
    const formatDate = (dateStr) => {
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div className="history-container">
            {/* Error */}
            {error && (
                <div className="error-container">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div className="loading-container">
                    <div className="loading-spinner" />
                    <div className="loading-text">Loading quiz history...</div>
                </div>
            )}

            {/* Empty State */}
            {!loading && quizzes.length === 0 && !error && (
                <div className="history-empty">
                    <div className="history-empty-icon">📭</div>
                    <div className="history-empty-text">No quizzes yet</div>
                    <div className="history-empty-sub">
                        Generate your first quiz from Tab 1 to see it here!
                    </div>
                </div>
            )}

            {/* History Table */}
            {!loading && quizzes.length > 0 && (
                <div className="history-table-wrapper">
                    <table className="history-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Title</th>
                                <th>URL</th>
                                <th>Questions</th>
                                <th>Created</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quizzes.map((quiz, index) => (
                                <tr key={quiz.id}>
                                    <td>{index + 1}</td>
                                    <td className="history-title">{quiz.title}</td>
                                    <td>
                                        <a
                                            className="history-url"
                                            href={quiz.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            title={quiz.url}
                                        >
                                            {quiz.url.replace('https://en.wikipedia.org/wiki/', '')}
                                        </a>
                                    </td>
                                    <td className="history-count">{quiz.question_count}</td>
                                    <td className="history-date">{formatDate(quiz.created_at)}</td>
                                    <td>
                                        <button
                                            className="btn-details"
                                            onClick={() => handleDetails(quiz.id)}
                                            disabled={modalLoading}
                                        >
                                            {modalLoading ? '...' : 'Details'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Quiz Detail Modal */}
            {selectedQuiz && (
                <QuizModal
                    data={selectedQuiz}
                    onClose={() => setSelectedQuiz(null)}
                />
            )}
        </div>
    );
}

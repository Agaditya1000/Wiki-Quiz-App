/**
 * GenerateQuiz Component (Tab 1)
 * Provides URL input, triggers quiz generation, and displays results.
 * Includes URL preview and loading states.
 */

import { useState, useCallback } from 'react';
import QuizDisplay from './QuizDisplay';

import API_BASE from '../config';

export default function GenerateQuiz() {
    const [url, setUrl] = useState('');
    const [preview, setPreview] = useState(null);
    const [quizData, setQuizData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [previewLoading, setPreviewLoading] = useState(false);

    // ── URL Preview (auto-fetch title) ──────────────────────────────
    const handleUrlBlur = useCallback(async () => {
        const trimmed = url.trim();
        if (!trimmed || !trimmed.includes('wikipedia.org/wiki/')) {
            setPreview(null);
            return;
        }
        setPreviewLoading(true);
        try {
            const res = await fetch(
                `${API_BASE}/preview/url?url=${encodeURIComponent(trimmed)}`
            );
            if (res.ok) {
                const data = await res.json();
                setPreview(data);
            } else {
                setPreview(null);
            }
        } catch {
            setPreview(null);
        } finally {
            setPreviewLoading(false);
        }
    }, [url]);

    // ── Generate Quiz ───────────────────────────────────────────────
    const handleGenerate = async () => {
        const trimmed = url.trim();
        if (!trimmed) return;

        setLoading(true);
        setError(null);
        setQuizData(null);

        try {
            const res = await fetch(`${API_BASE}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: trimmed }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to generate quiz');
            }

            const data = await res.json();
            setQuizData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // ── Handle Enter key ────────────────────────────────────────────
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !loading) {
            handleGenerate();
        }
    };

    return (
        <div>
            {/* ── URL Input Section ──────────────────────────── */}
            <div className="input-section">
                <label className="input-label">Wikipedia Article URL</label>
                <div className="input-group">
                    <input
                        type="url"
                        className="url-input"
                        placeholder="https://en.wikipedia.org/wiki/Alan_Turing"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onBlur={handleUrlBlur}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                        id="wiki-url-input"
                    />
                    <button
                        className="btn-primary"
                        onClick={handleGenerate}
                        disabled={loading || !url.trim()}
                        id="generate-quiz-btn"
                    >
                        {loading ? '⏳ Generating...' : '🚀 Generate Quiz'}
                    </button>
                </div>

                {/* URL Preview */}
                {previewLoading && (
                    <div className="url-preview">
                        <span className="preview-icon">⏳</span>
                        <span>Checking URL...</span>
                    </div>
                )}
                {preview && !previewLoading && (
                    <div className="url-preview">
                        <span className="preview-icon">✅</span>
                        <span>Article found: <strong>{preview.title}</strong></span>
                    </div>
                )}
            </div>

            {/* ── Error State ────────────────────────────────── */}
            {error && (
                <div className="error-container">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                </div>
            )}

            {/* ── Loading State ──────────────────────────────── */}
            {loading && (
                <div className="loading-container">
                    <div className="loading-spinner" />
                    <div className="loading-text">Generating your quiz...</div>
                    <div className="loading-subtext">
                        Scraping article & creating questions with AI. This may take 15-30 seconds.
                    </div>
                </div>
            )}

            {/* ── Quiz Results ───────────────────────────────── */}
            {quizData && !loading && <QuizDisplay data={quizData} />}
        </div>
    );
}

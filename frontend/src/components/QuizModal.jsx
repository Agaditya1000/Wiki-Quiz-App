/**
 * QuizModal Component
 * Overlay modal that reuses QuizDisplay to show quiz details
 * from the history tab. Closes on backdrop click or button.
 */

import QuizDisplay from './QuizDisplay';

export default function QuizModal({ data, onClose }) {
    if (!data) return null;

    // Close on backdrop click (not on modal content click)
    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className="modal-overlay" onClick={handleOverlayClick}>
            <div className="modal-content">
                <button className="modal-close" onClick={onClose} title="Close">
                    ✕
                </button>
                <QuizDisplay data={data} />
            </div>
        </div>
    );
}

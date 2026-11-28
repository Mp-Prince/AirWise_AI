import { useState } from 'react';
import routineService from '../../../services/routineService.js';
import SourceCitationList from './SourceCitationList.jsx';

const PRIORITY_BADGE = {
  high: 'text-bg-danger',
  medium: 'text-bg-warning',
  low: 'text-bg-info',
};

const REC_TO_ROUTINE_TYPE = {
  health: 'exercise',
  commute: 'commute',
  indoor_air: 'indoor_air',
  energy: 'energy',
  planning: 'other',
  general: 'other',
};

/**
 * Single user or assistant chat message with structured recommendations,
 * citations, environmental context timestamp, copy, add-to-planner, and feedback controls.
 */
export default function ChatMessage({ message, onFeedback }) {
  const [copied, setCopied] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(null);
  const [addedRecs, setAddedRecs] = useState({});
  const isUser = message.role === 'user';

  const handleAddRecToPlanner = async (rec, idx) => {
    if (addedRecs[idx]) return;
    setAddedRecs((prev) => ({ ...prev, [idx]: 'saving' }));
    try {
      const today = new Date().toISOString().slice(0, 10);
      await routineService.createRoutine({
        name: rec.title.slice(0, 160),
        description: rec.action,
        routine_type: REC_TO_ROUTINE_TYPE[rec.category] || 'other',
        routine_date: today,
        start_time: '08:00:00',
        end_time: '08:30:00',
        reminder_minutes: 15,
      });
      setAddedRecs((prev) => ({ ...prev, [idx]: 'added' }));
    } catch {
      setAddedRecs((prev) => ({ ...prev, [idx]: 'error' }));
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard unavailable
    }
  };

  const handleVote = async (helpful) => {
    if (!message.id || message.isLocalOnly || feedbackSent !== null) return;
    setFeedbackSent(helpful);
    if (onFeedback) {
      await onFeedback(message.id, helpful);
    }
  };

  return (
    <div className={`d-flex flex-column ${isUser ? 'align-items-end' : 'align-items-start'} mb-3`}>
      <div
        className={`card ${isUser ? 'bg-primary text-white' : 'bg-white border'}`}
        style={{ maxWidth: '88%' }}
      >
        <div className="card-body py-2 px-3">
          <div className="d-flex justify-content-between align-items-center gap-3 mb-1">
            <small className={isUser ? 'text-white-50' : 'text-muted fw-semibold'}>
              {isUser ? 'You' : 'AirWise AI'}
            </small>
            {message.created_at && (
              <small className={isUser ? 'text-white-50' : 'text-muted'}>
                {new Date(message.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </small>
            )}
          </div>

          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>

          {!isUser && message.data_context && (
            <div className="small text-muted mt-2">
              <i className="bi bi-clock-history me-1" aria-hidden="true" />
              Context: {message.data_context.location || 'No location'}
              {message.data_context.aqi_value !== null &&
              message.data_context.aqi_value !== undefined
                ? ` · AQI ${message.data_context.aqi_value} (${message.data_context.aqi_standard}) observed ${new Date(
                    message.data_context.air_quality_observed_at,
                  ).toLocaleString()}`
                : ' · No live AQI available'}
            </div>
          )}

          {!isUser && message.recommendations?.length > 0 && (
            <div className="mt-3">
              <div className="small fw-semibold mb-2">
                <i className="bi bi-lightbulb me-1" aria-hidden="true" />
                Recommended Actions
              </div>
              <div className="d-flex flex-column gap-2">
                {message.recommendations.map((rec, idx) => (
                  <div key={idx} className="border rounded p-2 bg-light small">
                    <div className="d-flex justify-content-between align-items-center gap-2 mb-1">
                      <strong>{rec.title}</strong>
                      <span className={`badge ${PRIORITY_BADGE[rec.priority] || 'text-bg-secondary'}`}>
                        {rec.priority}
                      </span>
                    </div>
                    <div>{rec.action}</div>
                    <div className="text-muted mt-1">Why: {rec.why}</div>
                    {rec.expected_benefit && (
                      <div className="text-success mt-1">Benefit: {rec.expected_benefit}</div>
                    )}
                    <div className="mt-2">
                      <button
                        type="button"
                        className={`btn btn-sm py-0 px-2 ${
                          addedRecs[idx] === 'added' ? 'btn-success' : 'btn-outline-primary'
                        }`}
                        onClick={() => handleAddRecToPlanner(rec, idx)}
                        disabled={addedRecs[idx] === 'saving' || addedRecs[idx] === 'added'}
                      >
                        <i className="bi bi-calendar-plus me-1" aria-hidden="true" />
                        {addedRecs[idx] === 'added'
                          ? 'Added to Planner'
                          : addedRecs[idx] === 'saving'
                          ? 'Adding...'
                          : 'Add to Planner'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!isUser && message.limitations?.length > 0 && (
            <div className="alert alert-warning py-2 px-3 mt-3 mb-0 small">
              <strong>Note / Limitations:</strong>
              <ul className="mb-0 ps-3 mt-1">
                {message.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </div>
          )}

          {!isUser && <SourceCitationList sources={message.sources} />}

          {!isUser && (
            <div className="d-flex align-items-center gap-2 mt-2 pt-2 border-top">
              <button
                type="button"
                className="btn btn-outline-secondary btn-sm py-0 px-2"
                onClick={handleCopy}
              >
                <i className={`bi ${copied ? 'bi-check' : 'bi-clipboard'} me-1`} aria-hidden="true" />
                {copied ? 'Copied' : 'Copy'}
              </button>
              {!message.isLocalOnly && (
                <>
                  <button
                    type="button"
                    className={`btn btn-sm py-0 px-2 ${
                      feedbackSent === true ? 'btn-success' : 'btn-outline-secondary'
                    }`}
                    onClick={() => handleVote(true)}
                    disabled={feedbackSent !== null}
                    aria-label="Helpful"
                  >
                    <i className="bi bi-hand-thumbs-up" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    className={`btn btn-sm py-0 px-2 ${
                      feedbackSent === false ? 'btn-danger' : 'btn-outline-secondary'
                    }`}
                    onClick={() => handleVote(false)}
                    disabled={feedbackSent !== null}
                    aria-label="Not helpful"
                  >
                    <i className="bi bi-hand-thumbs-down" aria-hidden="true" />
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

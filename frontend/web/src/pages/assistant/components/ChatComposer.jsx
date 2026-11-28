/**
 * Message input composer with context toggle and send button (Phase 5).
 */
export default function ChatComposer({
  value,
  onChange,
  includeContext,
  onToggleContext,
  onSubmit,
  disabled,
}) {
  return (
    <form className="card shadow-sm mt-3" onSubmit={onSubmit}>
      <div className="card-body">
        <div className="d-flex gap-2">
          <input
            type="text"
            className="form-control"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Ask AirWise about air quality, health guidance, or cleaner choices..."
            aria-label="Ask the AI assistant"
            disabled={disabled}
            maxLength={2000}
          />
          <button
            type="submit"
            className="btn btn-primary flex-shrink-0"
            disabled={disabled || !value.trim()}
          >
            <i className="bi bi-send me-1" aria-hidden="true" />
            Send
          </button>
        </div>
        <div className="form-check mt-2 mb-0">
          <input
            id="assistant-include-context"
            type="checkbox"
            className="form-check-input"
            checked={includeContext}
            onChange={(e) => onToggleContext(e.target.checked)}
            disabled={disabled}
          />
          <label className="form-check-label small text-supporting" htmlFor="assistant-include-context">
            Include my saved location, live AQI/weather, and health sensitivities
          </label>
        </div>
      </div>
    </form>
  );
}

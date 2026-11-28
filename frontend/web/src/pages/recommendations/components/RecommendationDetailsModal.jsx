/**
 * Modal displaying full reasoning and metadata for a recommendation (Phase 6).
 */
export default function RecommendationDetailsModal({ rec, onClose }) {
  if (!rec) return null;

  return (
    <div
      className="modal show d-block"
      tabIndex="-1"
      role="dialog"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{rec.title}</h5>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>
          <div className="modal-body">
            <div className="mb-2 d-flex gap-2">
              <span className="badge text-bg-primary">{rec.category}</span>
              <span className="badge text-bg-secondary">{rec.status}</span>
            </div>
            <p>{rec.description}</p>
            {rec.reasoning && (
              <div className="alert alert-light border small">
                <strong>Why this was suggested:</strong> {rec.reasoning}
              </div>
            )}
            <div className="small text-muted">
              <div>Created: {new Date(rec.created_at).toLocaleString()}</div>
              {rec.expires_at && (
                <div>Valid until: {new Date(rec.expires_at).toLocaleString()}</div>
              )}
              <div>
                Knowledge-base source IDs:{' '}
                {rec.source_document_ids?.length > 0
                  ? rec.source_document_ids.join(', ')
                  : 'Deterministic safety/eco rule (no external document ID linked)'}
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

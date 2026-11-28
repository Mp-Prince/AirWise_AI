const CATEGORY_BADGE = {
  health: 'text-bg-danger',
  lifestyle: 'text-bg-info',
  eco: 'text-bg-success',
};

const STATUS_BADGE = {
  pending: 'text-bg-primary',
  accepted: 'text-bg-success',
  dismissed: 'text-bg-secondary',
  expired: 'text-bg-warning',
};

/**
 * Recommendation card with reasoning, source count, Mark Done, Add to Planner, and Dismiss.
 */
export default function RecommendationCard({
  rec,
  busyId,
  onAccept,
  onDismiss,
  onAddToPlanner,
  onViewDetails,
}) {
  const busy = busyId === rec.id;

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body d-flex flex-column">
        <div className="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-2">
          <div className="d-flex gap-1">
            <span className={`badge ${CATEGORY_BADGE[rec.category] || 'text-bg-secondary'}`}>
              {rec.category}
            </span>
            <span className={`badge ${STATUS_BADGE[rec.status] || 'text-bg-secondary'}`}>
              {rec.status}
            </span>
          </div>
          {rec.source_document_ids?.length > 0 && (
            <small className="text-muted">
              <i className="bi bi-journal-text me-1" aria-hidden="true" />
              {rec.source_document_ids.length} source(s)
            </small>
          )}
        </div>

        <h5 className="card-title h6 mb-2">{rec.title}</h5>
        <p className="card-text small text-body-secondary flex-grow-1">{rec.description}</p>

        {rec.reasoning && (
          <div className="small text-muted mb-3">
            <strong>Why:</strong> {rec.reasoning}
          </div>
        )}

        <div className="d-flex flex-wrap gap-1 pt-2 border-top">
          {rec.status === 'pending' && (
            <>
              <button
                type="button"
                className="btn btn-outline-success btn-sm"
                onClick={() => onAccept(rec)}
                disabled={busy}
              >
                <i className="bi bi-check2 me-1" aria-hidden="true" />
                Mark Done
              </button>
              <button
                type="button"
                className="btn btn-outline-primary btn-sm"
                onClick={() => onAddToPlanner(rec)}
                disabled={busy}
              >
                <i className="bi bi-calendar-plus me-1" aria-hidden="true" />
                Add to Planner
              </button>
              <button
                type="button"
                className="btn btn-outline-secondary btn-sm"
                onClick={() => onDismiss(rec)}
                disabled={busy}
              >
                Dismiss
              </button>
            </>
          )}
          <button
            type="button"
            className="btn btn-link btn-sm text-decoration-none ms-auto p-0"
            onClick={() => onViewDetails(rec)}
          >
            Details
          </button>
        </div>
      </div>
    </div>
  );
}

import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Filter bar and Generate button for Recommendations page (Phase 6).
 */
export default function RecommendationFilters({
  category,
  status,
  onCategoryChange,
  onStatusChange,
  onGenerate,
  generating,
}) {
  return (
    <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <div className="d-flex flex-wrap gap-2">
        <select
          className="form-select form-select-sm"
          style={{ width: 'auto' }}
          aria-label="Filter by category"
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="">All categories</option>
          <option value="health">Health</option>
          <option value="lifestyle">Lifestyle</option>
          <option value="eco">Eco / Sustainable</option>
        </select>

        <select
          className="form-select form-select-sm"
          style={{ width: 'auto' }}
          aria-label="Filter by status"
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted / Done</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>

      <button
        type="button"
        className="btn btn-primary btn-sm"
        onClick={onGenerate}
        disabled={generating}
      >
        {generating ? (
          <>
            <LoadingSpinner size="sm" className="me-1" /> Refreshing...
          </>
        ) : (
          <>
            <i className="bi bi-stars me-1" aria-hidden="true" />
            Refresh Suggestions
          </>
        )}
      </button>
    </div>
  );
}

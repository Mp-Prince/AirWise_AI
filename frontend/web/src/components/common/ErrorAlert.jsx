/** Error message alert (UI/UX spec: errors are explicit, with a retry path). */
export default function ErrorAlert({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="alert alert-danger d-flex align-items-start gap-2" role="alert">
      <i className="bi bi-exclamation-triangle-fill flex-shrink-0 mt-1" aria-hidden="true" />
      <div>
        <strong className="d-block">Error</strong>
        <span>{message}</span>
        {onRetry ? (
          <button type="button" className="btn btn-danger btn-sm ms-2" onClick={onRetry}>
            Retry
          </button>
        ) : null}
      </div>
    </div>
  );
}

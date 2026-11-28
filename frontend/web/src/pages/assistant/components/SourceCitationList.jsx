/**
 * Source citation list displayed beneath assistant answers (Phase 5).
 */
export default function SourceCitationList({ sources }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-2 border-top">
      <div className="small fw-semibold text-supporting mb-2">
        <i className="bi bi-journal-check me-1" aria-hidden="true" />
        Supporting Sources ({sources.length})
      </div>
      <div className="d-flex flex-column gap-2">
        {sources.map((src, idx) => (
          <div
            key={`${src.document_id}-${src.chunk_index}-${idx}`}
            className="bg-light rounded p-2 small"
          >
            <div className="d-flex justify-content-between align-items-center gap-2">
              <strong className="text-truncate">
                {src.document_title || `Document ${String(src.document_id).slice(0, 8)}`}
              </strong>
              <span className="badge text-bg-secondary flex-shrink-0">
                {Math.round((src.confidence || 0) * 100)}% match
              </span>
            </div>
            {src.snippet && <p className="mb-1 mt-1 text-body-secondary">{src.snippet}</p>}
            <div className="text-muted">
              {src.source_type || 'doc'} • Chunk #{src.chunk_index}
              {src.page_number ? ` • Page ${src.page_number}` : ''}
              {src.source_url && (
                <>
                  {' • '}
                  <a href={src.source_url} target="_blank" rel="noreferrer">
                    View Source
                  </a>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

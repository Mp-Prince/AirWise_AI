import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Semantic retrieval query test panel with source & page citations (Phase 4).
 */
export default function KnowledgeQueryPanel({ query, onQueryChange, onSubmit, querying, results }) {
  return (
    <div>
      <form onSubmit={onSubmit}>
        <div className="mb-3">
          <label className="form-label" htmlFor="rag-query-input">Ask a Question</label>
          <textarea
            id="rag-query-input"
            className="form-control"
            rows={3}
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="e.g., What are the WHO guidelines for PM2.5 exposure?"
            required
          />
        </div>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={querying || !query.trim()}
        >
          {querying ? (
            <>
              <LoadingSpinner size="sm" className="me-2" />
              Searching...
            </>
          ) : (
            'Search Knowledge Base'
          )}
        </button>
      </form>

      {results && (
        <div className="mt-4">
          <h5 className="mb-1">Retrieved Passages ({results.sources_used} found)</h5>
          <p className="text-muted small mb-3">
            Query took {results.processing_time_ms.toFixed(0)} ms
          </p>

          {!results.is_grounded || results.citations.length === 0 ? (
            <div className="alert alert-warning mb-0">
              {results.answer || 'No relevant documents found for this query.'}
            </div>
          ) : (
            results.citations.map((citation) => (
              <div
                key={`${citation.document_id}-${citation.chunk_index}`}
                className="card mb-2"
              >
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2 gap-2">
                    <strong className="text-truncate">
                      {citation.document_title || `Document ${citation.document_id.slice(0, 8)}`}
                    </strong>
                    <span className="badge text-bg-primary flex-shrink-0">
                      {Math.round(citation.confidence * 100)}% match
                    </span>
                  </div>
                  {citation.snippet && (
                    <p className="small text-body-secondary mb-2">{citation.snippet}</p>
                  )}
                  <small className="text-muted d-block">
                    Type: {citation.source_type || 'unknown'} • Chunk #{citation.chunk_index}
                    {citation.page_number ? ` • Page ${citation.page_number}` : ''}
                    {citation.source_url && (
                      <>
                        {' • '}
                        <a href={citation.source_url} target="_blank" rel="noreferrer">
                          Source
                        </a>
                      </>
                    )}
                  </small>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

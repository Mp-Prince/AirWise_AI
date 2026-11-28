/**
 * Document browse & status management table (Phase 4).
 */
export default function DocumentList({ documents, busyDocId, onToggleActive, onDelete }) {
  if (!documents || documents.length === 0) {
    return (
      <p className="text-supporting text-center py-5 mb-0">
        No documents in the knowledge base yet.
        <br />
        Use the <strong>Ingest</strong> tab to add trusted environmental guidelines.
      </p>
    );
  }

  return (
    <div className="table-responsive">
      <table className="table table-hover align-middle mb-0">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Status</th>
            <th>Chunks</th>
            <th>Created</th>
            <th className="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const isBusy = busyDocId === doc.id;
            return (
              <tr key={doc.id}>
                <td>
                  <strong>{doc.title}</strong>
                  {doc.source_url && (
                    <div className="small text-truncate" style={{ maxWidth: '320px' }}>
                      <a href={doc.source_url} target="_blank" rel="noreferrer">
                        {doc.source_url}
                      </a>
                    </div>
                  )}
                </td>
                <td>
                  <span className="badge text-bg-secondary">{doc.source_type}</span>
                </td>
                <td>
                  {doc.is_active ? (
                    <span className="badge text-bg-success">Active</span>
                  ) : (
                    <span className="badge text-bg-warning">Disabled</span>
                  )}
                </td>
                <td>{doc.chunk_count}</td>
                <td className="text-muted small">
                  {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '—'}
                </td>
                <td className="text-end">
                  <div className="btn-group btn-group-sm">
                    <button
                      type="button"
                      className={`btn ${doc.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                      onClick={() => onToggleActive(doc)}
                      disabled={isBusy}
                    >
                      {doc.is_active ? 'Disable' : 'Enable'}
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline-danger"
                      onClick={() => onDelete(doc)}
                      disabled={isBusy}
                      aria-label={`Delete ${doc.title}`}
                    >
                      <i className="bi bi-trash" aria-hidden="true" />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

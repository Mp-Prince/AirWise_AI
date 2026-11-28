/**
 * Overview cards for Knowledge Base statistics (Phase 4).
 */
export default function KnowledgeStats({ stats }) {
  if (!stats) return null;

  return (
    <div className="row g-3 mb-4">
      <div className="col-6 col-md-3">
        <div className="card text-center h-100">
          <div className="card-body">
            <h3 className="text-primary mb-0">{stats.total_documents}</h3>
            <small className="text-muted">Total Documents</small>
          </div>
        </div>
      </div>
      <div className="col-6 col-md-3">
        <div className="card text-center h-100">
          <div className="card-body">
            <h3 className="text-success mb-0">{stats.total_chunks}</h3>
            <small className="text-muted">Total Chunks</small>
          </div>
        </div>
      </div>
      <div className="col-6 col-md-3">
        <div className="card text-center h-100">
          <div className="card-body">
            <h3 className="text-info mb-0">{stats.active_documents}</h3>
            <small className="text-muted">Active Documents</small>
          </div>
        </div>
      </div>
      <div className="col-6 col-md-3">
        <div className="card text-center h-100">
          <div className="card-body">
            <small className="text-muted d-block mb-1">Embedding Model</small>
            <div className="small text-body-secondary text-break">{stats.embedding_model}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

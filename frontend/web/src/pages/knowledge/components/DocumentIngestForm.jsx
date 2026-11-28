import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Document ingestion form supporting manual text, PDF upload, and web URLs (Phase 4).
 */
export default function DocumentIngestForm({ form, onChange, onSubmit, ingesting }) {
  return (
    <form onSubmit={onSubmit}>
      <div className="mb-3">
        <label className="form-label" htmlFor="ingest-source-type">Source Type</label>
        <select
          id="ingest-source-type"
          className="form-select"
          value={form.source_type}
          onChange={(e) => onChange('source_type', e.target.value)}
        >
          <option value="manual">Manual Text Entry</option>
          <option value="pdf">PDF File</option>
          <option value="web">Web URL</option>
        </select>
      </div>

      <div className="mb-3">
        <label className="form-label" htmlFor="ingest-title">Title</label>
        <input
          id="ingest-title"
          type="text"
          className="form-control"
          value={form.title}
          onChange={(e) => onChange('title', e.target.value)}
          placeholder="Document title (e.g., WHO Global Air Quality Guidelines 2021)"
          required
        />
      </div>

      {form.source_type === 'manual' && (
        <div className="mb-3">
          <label className="form-label" htmlFor="ingest-content">Content</label>
          <textarea
            id="ingest-content"
            className="form-control"
            rows={8}
            value={form.content}
            onChange={(e) => onChange('content', e.target.value)}
            placeholder="Paste or type document content here..."
            required
          />
        </div>
      )}

      {form.source_type === 'pdf' && (
        <div className="mb-3">
          <label className="form-label" htmlFor="ingest-pdf">PDF File</label>
          <input
            id="ingest-pdf"
            type="file"
            className="form-control"
            accept=".pdf"
            onChange={(e) => onChange('file', e.target.files?.[0] || null)}
            required
          />
        </div>
      )}

      {(form.source_type === 'pdf' || form.source_type === 'web') && (
        <div className="mb-3">
          <label className="form-label" htmlFor="ingest-url">
            {form.source_type === 'web' ? 'Web URL' : 'Source URL (optional)'}
          </label>
          <input
            id="ingest-url"
            type="url"
            className="form-control"
            value={form.source_url}
            onChange={(e) => onChange('source_url', e.target.value)}
            placeholder="https://example.com/document"
            required={form.source_type === 'web'}
          />
        </div>
      )}

      <div className="mb-3">
        <label className="form-label" htmlFor="ingest-metadata">Metadata (JSON)</label>
        <textarea
          id="ingest-metadata"
          className="form-control font-monospace small"
          rows={3}
          value={form.metadata_json}
          onChange={(e) => onChange('metadata_json', e.target.value)}
          placeholder='{"author": "WHO", "year": 2021, "category": "guidelines"}'
        />
        <div className="form-text">Optional JSON metadata (source, publication year, category).</div>
      </div>

      <div className="d-grid gap-2 d-md-flex justify-content-md-end">
        <button type="submit" className="btn btn-primary" disabled={ingesting}>
          {ingesting ? (
            <>
              <LoadingSpinner size="sm" className="me-2" />
              Ingesting...
            </>
          ) : (
            'Ingest Document'
          )}
        </button>
      </div>
    </form>
  );
}

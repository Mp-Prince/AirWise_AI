/**
 * Modal showing stored factor snapshot, method version, formula, and assumptions (Phase 7).
 */
export default function CalculationDetailsModal({ record, onClose }) {
  if (!record) return null;
  const snap = record.factor_snapshot || {};

  return (
    <div
      className="modal show d-block"
      tabIndex="-1"
      role="dialog"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Calculation Details & Provenance</h5>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
          </div>
          <div className="modal-body">
            <div className="d-flex flex-wrap gap-2 mb-3">
              <span className="badge text-bg-info">
                {record.is_estimated ? 'Estimated Value' : 'Measured Value'}
              </span>
              <span className="badge text-bg-secondary">Method: {record.method_version}</span>
            </div>

            <p className="mb-2">
              <strong>Activity:</strong> {record.description || '—'}
            </p>
            <div className="row g-2 mb-3">
              <div className="col-4">
                <div className="bg-light rounded p-2 text-center">
                  <div className="small text-muted">Baseline</div>
                  <div className="fw-bold">{Number(record.baseline_co2e_kg || 0).toFixed(4)} kg CO2e</div>
                </div>
              </div>
              <div className="col-4">
                <div className="bg-light rounded p-2 text-center">
                  <div className="small text-muted">Alternative</div>
                  <div className="fw-bold">{Number(record.alternative_co2e_kg || 0).toFixed(4)} kg CO2e</div>
                </div>
              </div>
              <div className="col-4">
                <div className="bg-success-subtle rounded p-2 text-center">
                  <div className="small text-muted">Estimated Avoided</div>
                  <div className="fw-bold text-success">{Number(record.co2e_kg).toFixed(4)} kg CO2e</div>
                </div>
              </div>
            </div>

            <h6 className="small fw-semibold text-uppercase text-muted">Factor Snapshot</h6>
            <ul className="small mb-3">
              {snap.baseline_source && <li><strong>Baseline source:</strong> {snap.baseline_source} ({snap.baseline_factor_kg_per_unit} {snap.baseline_unit})</li>}
              {snap.alternative_source && <li><strong>Alternative source:</strong> {snap.alternative_source} ({snap.alternative_factor_kg_per_unit} {snap.alternative_unit})</li>}
              {snap.source && <li><strong>Source:</strong> {snap.source} ({snap.baseline_factor_kg_per_unit} {snap.unit})</li>}
              {snap.boundary && <li><strong>Boundary:</strong> {snap.boundary}</li>}
              {snap.region && <li><strong>Region:</strong> {snap.region}</li>}
            </ul>

            {snap.assumptions?.length > 0 && (
              <>
                <h6 className="small fw-semibold text-uppercase text-muted">Assumptions</h6>
                <ul className="small mb-3">
                  {snap.assumptions.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </>
            )}

            <div className="alert alert-warning py-2 small mb-0">
              All values are reproducible CO2e estimates derived from average emission factors.
              AirWise AI makes no unsupported PM2.5 or direct health-benefit claim from these figures.
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

/**
 * Breakdown by activity mode and logged impact records list (Phase 7).
 */
export default function ImpactBreakdown({ breakdown, records, onViewCalculation, onDeleteRecord, busyId }) {
  return (
    <div className="row g-3 mt-1">
      <div className="col-12 col-lg-4">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="section-heading mb-3">Mode Breakdown (Estimated)</h2>
            {!breakdown || breakdown.length === 0 ? (
              <p className="text-supporting small mb-0">No activities in this period.</p>
            ) : (
              <ul className="list-group list-group-flush">
                {breakdown.map((item) => (
                  <li
                    key={item.label}
                    className="list-group-item px-0 d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <div className="small fw-semibold">{item.label}</div>
                      <div className="small text-muted">{item.count} activity(ies)</div>
                    </div>
                    <span className="badge text-bg-success">{item.co2e_kg.toFixed(2)} kg CO2e</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="col-12 col-lg-8">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="section-heading mb-3">Activity Log</h2>
            {!records || records.length === 0 ? (
              <p className="text-supporting small mb-0">
                No logged impact records in this date range.
              </p>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm table-hover align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Activity</th>
                      <th>CO2e Avoided</th>
                      <th>Status</th>
                      <th className="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((rec) => (
                      <tr key={rec.id}>
                        <td className="small text-muted">
                          {new Date(rec.recorded_at).toLocaleDateString()}
                        </td>
                        <td className="small">{rec.description || 'Sustainable activity'}</td>
                        <td className="fw-semibold small">{Number(rec.co2e_kg).toFixed(3)} kg</td>
                        <td>
                          <span className="badge text-bg-light border">
                            {rec.is_estimated ? 'Estimated' : 'Measured'}
                          </span>
                        </td>
                        <td className="text-end">
                          <div className="btn-group btn-group-sm">
                            <button
                              type="button"
                              className="btn btn-outline-primary"
                              onClick={() => onViewCalculation(rec)}
                            >
                              View Calculation
                            </button>
                            <button
                              type="button"
                              className="btn btn-outline-danger"
                              onClick={() => onDeleteRecord(rec)}
                              disabled={busyId === rec.id}
                              aria-label="Delete record"
                            >
                              <i className="bi bi-trash" aria-hidden="true" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

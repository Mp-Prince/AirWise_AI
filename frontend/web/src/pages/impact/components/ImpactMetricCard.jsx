/**
 * Summary metric card clearly labelling estimated vs measured status (Phase 7).
 */
export default function ImpactMetricCard({ label, value, unit, hint, badgeText = 'Estimated' }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center gap-2 mb-1">
          <span className="text-supporting small text-uppercase">{label}</span>
          {badgeText && <span className="badge text-bg-light border">{badgeText}</span>}
        </div>
        <div className="fs-3 fw-semibold">
          {value}
          {unit ? <span className="fs-6 fw-normal text-muted ms-1">{unit}</span> : null}
        </div>
        {hint && <div className="text-supporting small mt-1">{hint}</div>}
      </div>
    </div>
  );
}

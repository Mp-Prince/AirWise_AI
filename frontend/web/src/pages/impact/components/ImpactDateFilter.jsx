/**
 * Date range selector for Impact Tracker (Today, 7 Days, 30 Days, Custom Range).
 */
export default function ImpactDateFilter({
  period,
  customFrom,
  customTo,
  onPeriodChange,
  onCustomFromChange,
  onCustomToChange,
}) {
  return (
    <div className="d-flex flex-wrap align-items-center gap-2 mb-3">
      <div className="btn-group btn-group-sm" role="group" aria-label="Reporting period">
        {[
          { id: 'today', label: 'Today' },
          { id: 'week', label: '7 Days' },
          { id: '30d', label: '30 Days' },
          { id: 'custom', label: 'Custom Range' },
        ].map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`btn ${period === opt.id ? 'btn-primary' : 'btn-outline-secondary'}`}
            onClick={() => onPeriodChange(opt.id)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {period === 'custom' && (
        <div className="d-flex align-items-center gap-2">
          <input
            type="date"
            className="form-control form-control-sm"
            value={customFrom}
            onChange={(e) => onCustomFromChange(e.target.value)}
            aria-label="From date"
          />
          <span className="text-muted small">to</span>
          <input
            type="date"
            className="form-control form-control-sm"
            value={customTo}
            onChange={(e) => onCustomToChange(e.target.value)}
            aria-label="To date"
          />
        </div>
      )}
    </div>
  );
}

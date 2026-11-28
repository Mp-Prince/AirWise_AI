/**
 * Toolbar for navigating dates/weeks and opening Add Event modal (Phase 6).
 */
export default function PlannerToolbar({
  selectedDate,
  viewMode,
  onViewModeChange,
  onPrev,
  onNext,
  onToday,
  onAddEvent,
}) {
  const formatted = new Date(`${selectedDate}T00:00:00`).toLocaleDateString(undefined, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <div className="d-flex align-items-center gap-2">
        <div className="btn-group btn-group-sm" role="group" aria-label="Period navigation">
          <button type="button" className="btn btn-outline-secondary" onClick={onPrev}>
            <i className="bi bi-chevron-left" aria-hidden="true" /> Previous
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={onToday}>
            Today
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={onNext}>
            Next <i className="bi bi-chevron-right" aria-hidden="true" />
          </button>
        </div>
        <span className="fw-semibold ms-1">{formatted}</span>
      </div>

      <div className="d-flex align-items-center gap-2">
        <div className="btn-group btn-group-sm d-none d-md-inline-flex" role="group" aria-label="View mode">
          <button
            type="button"
            className={`btn ${viewMode === 'week' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => onViewModeChange('week')}
          >
            Week
          </button>
          <button
            type="button"
            className={`btn ${viewMode === 'agenda' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => onViewModeChange('agenda')}
          >
            Agenda
          </button>
        </div>

        <button type="button" className="btn btn-primary btn-sm" onClick={onAddEvent}>
          <i className="bi bi-plus-lg me-1" aria-hidden="true" />
          Add Event
        </button>
      </div>
    </div>
  );
}

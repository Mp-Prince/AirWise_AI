import { addDaysIso, parseLocalIsoDate, toLocalIsoDate } from '../../../utils/dateUtils.js';

const SAFETY_COLOR = {
  safe: 'border-success',
  caution: 'border-warning',
  avoid: 'border-danger',
  unknown: 'border-secondary',
};

/**
 * 7-day calendar week grid for desktop/tablet screens (Phase 6).
 */
export default function PlannerCalendar({
  weekStart,
  events,
  onSelectDate,
  onEdit,
  onDelete,
  onToggleComplete,
}) {
  const days = Array.from({ length: 7 }, (_, i) => addDaysIso(weekStart, i));
  const todayStr = toLocalIsoDate();

  return (
    <div className="row g-2">
      {days.map((dayStr) => {
        const dateObj = parseLocalIsoDate(dayStr);
        const weekdayIdx = (dateObj.getDay() + 6) % 7; // 0=Mon..6=Sun
        const isToday = dayStr === todayStr;
        const dayEvents = events.filter(
          (ev) =>
            ev.routine_date === dayStr ||
            (!ev.routine_date && (ev.days_of_week?.length === 0 || ev.days_of_week?.includes(weekdayIdx))),
        );

        return (
          <div className="col-12 col-md-6 col-xl" key={dayStr}>
            <div className={`card h-100 ${isToday ? 'border-primary' : ''}`}>
              <div className={`card-header py-2 d-flex justify-content-between align-items-center ${isToday ? 'bg-primary-subtle' : ''}`}>
                <button
                  type="button"
                  className="btn btn-link btn-sm p-0 text-decoration-none fw-semibold"
                  onClick={() => onSelectDate(dayStr)}
                >
                  {dateObj.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                </button>
                <span className="badge text-bg-light border">{dayEvents.length}</span>
              </div>
              <div className="card-body p-2">
                {dayEvents.length === 0 ? (
                  <div className="text-muted small text-center py-3">Free</div>
                ) : (
                  dayEvents.map((ev) => (
                    <div
                      key={`${dayStr}-${ev.id}`}
                      className={`border-start border-3 ${SAFETY_COLOR[ev.safety_band] || 'border-secondary'} bg-light rounded p-2 mb-2 small`}
                    >
                      <div
                        className={`fw-semibold text-truncate ${
                          ev.status === 'completed' ? 'text-decoration-line-through text-muted' : ''
                        }`}
                      >
                        {ev.name}
                      </div>
                      <div className="text-muted">
                        {String(ev.start_time).slice(0, 5)}–{String(ev.end_time).slice(0, 5)}
                      </div>
                      <div className="d-flex gap-1 mt-1">
                        <button
                          type="button"
                          className="btn btn-outline-success btn-sm py-0 px-1"
                          onClick={() => onToggleComplete(ev)}
                          title="Toggle complete"
                        >
                          <i className="bi bi-check2" aria-hidden="true" />
                        </button>
                        <button
                          type="button"
                          className="btn btn-outline-primary btn-sm py-0 px-1"
                          onClick={() => onEdit(ev)}
                          title="Edit"
                        >
                          <i className="bi bi-pencil" aria-hidden="true" />
                        </button>
                        {onDelete && (
                          <button
                            type="button"
                            className="btn btn-outline-danger btn-sm py-0 px-1"
                            onClick={() => onDelete(ev)}
                            title="Delete"
                          >
                            <i className="bi bi-trash" aria-hidden="true" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

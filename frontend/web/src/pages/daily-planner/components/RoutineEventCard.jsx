const SAFETY_BADGE = {
  safe: { cls: 'text-bg-success', label: 'Safe' },
  caution: { cls: 'text-bg-warning', label: 'Caution' },
  avoid: { cls: 'text-bg-danger', label: 'Avoid Outdoors' },
  unknown: { cls: 'text-bg-secondary', label: 'AQI Unknown' },
};

const STATUS_BADGE = {
  planned: 'text-bg-primary',
  completed: 'text-bg-success',
  skipped: 'text-bg-secondary',
};

function formatTime(t) {
  return String(t || '').slice(0, 5);
}

/**
 * Planner event card showing time window, safety band, completion toggle, Edit, and Delete.
 */
export default function RoutineEventCard({
  event,
  onEdit,
  onDelete,
  onToggleComplete,
  busyId,
}) {
  const safety = SAFETY_BADGE[event.safety_band] || SAFETY_BADGE.unknown;
  const isCompleted = event.status === 'completed';
  const busy = busyId === event.id;

  return (
    <div className={`card mb-2 ${isCompleted ? 'border-success bg-light' : ''}`}>
      <div className="card-body py-2 px-3">
        <div className="d-flex flex-column flex-sm-row justify-content-between align-items-start gap-2">
          <div>
            <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
              <strong className={isCompleted ? 'text-decoration-line-through text-muted' : ''}>
                {event.name}
              </strong>
              <span className={`badge ${safety.cls}`} title={event.safety_note}>
                {safety.label}
              </span>
              <span className="badge text-bg-light border">{event.routine_type.replace('_', ' ')}</span>
              <span className={`badge ${STATUS_BADGE[event.status] || 'text-bg-secondary'}`}>
                {event.status}
              </span>
            </div>
            <div className="small text-supporting">
              <i className="bi bi-clock me-1" aria-hidden="true" />
              {formatTime(event.start_time)} – {formatTime(event.end_time)}
              {event.routine_date ? ` · ${event.routine_date}` : ' · Recurring'}
              {event.reminder_minutes !== null && event.reminder_minutes !== undefined
                ? ` · Reminder ${event.reminder_minutes}m before`
                : ''}
            </div>
            {event.description && (
              <p className="small text-body-secondary mb-1 mt-1">{event.description}</p>
            )}
            <div className="small text-muted">{event.safety_note}</div>
          </div>

          <div className="d-flex flex-wrap gap-1 flex-shrink-0">
            <button
              type="button"
              className={`btn btn-sm ${isCompleted ? 'btn-outline-secondary' : 'btn-outline-success'}`}
              onClick={() => onToggleComplete(event)}
              disabled={busy}
            >
              <i className={`bi ${isCompleted ? 'bi-arrow-counterclockwise' : 'bi-check2'} me-1`} aria-hidden="true" />
              {isCompleted ? 'Reopen' : 'Mark Complete'}
            </button>
            <button
              type="button"
              className="btn btn-outline-primary btn-sm"
              onClick={() => onEdit(event)}
              disabled={busy}
            >
              <i className="bi bi-pencil" aria-hidden="true" />
            </button>
            <button
              type="button"
              className="btn btn-outline-danger btn-sm"
              onClick={() => onDelete(event)}
              disabled={busy}
              aria-label={`Delete ${event.name}`}
            >
              <i className="bi bi-trash" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Add / Edit Event modal for Daily Planner (Phase 6).
 */
export default function EventFormModal({ show, initialEvent, defaultDate, onClose, onSave, saving }) {
  const [form, setForm] = useState({
    name: '',
    routine_date: defaultDate,
    start_time: '07:00',
    end_time: '08:00',
    routine_type: 'exercise',
    description: '',
    reminder_minutes: 15,
  });
  const [validationError, setValidationError] = useState(null);

  useEffect(() => {
    if (initialEvent) {
      setForm({
        name: initialEvent.name || '',
        routine_date: initialEvent.routine_date || defaultDate,
        start_time: String(initialEvent.start_time || '07:00').slice(0, 5),
        end_time: String(initialEvent.end_time || '08:00').slice(0, 5),
        routine_type: initialEvent.routine_type || 'other',
        description: initialEvent.description || '',
        reminder_minutes:
          initialEvent.reminder_minutes !== null && initialEvent.reminder_minutes !== undefined
            ? initialEvent.reminder_minutes
            : 15,
      });
    } else {
      setForm({
        name: '',
        routine_date: defaultDate,
        start_time: '07:00',
        end_time: '08:00',
        routine_type: 'exercise',
        description: '',
        reminder_minutes: 15,
      });
    }
    setValidationError(null);
  }, [initialEvent, defaultDate, show]);

  if (!show) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setValidationError('Title is required.');
      return;
    }
    if (form.end_time <= form.start_time) {
      setValidationError('End time must be after start time.');
      return;
    }
    setValidationError(null);
    await onSave({
      name: form.name.trim(),
      routine_date: form.routine_date || null,
      start_time: `${form.start_time}:00`,
      end_time: `${form.end_time}:00`,
      routine_type: form.routine_type,
      description: form.description.trim() || null,
      reminder_minutes:
        form.reminder_minutes === '' ? null : parseInt(form.reminder_minutes, 10),
    });
  };

  return (
    <div
      className="modal show d-block"
      tabIndex="-1"
      role="dialog"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
    >
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <form onSubmit={handleSubmit}>
            <div className="modal-header">
              <h5 className="modal-title">{initialEvent ? 'Edit Event' : 'Add Event'}</h5>
              <button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
            </div>
            <div className="modal-body">
              {validationError && (
                <div className="alert alert-danger py-2 small">{validationError}</div>
              )}
              <div className="mb-3">
                <label className="form-label" htmlFor="event-title">Title *</label>
                <input
                  id="event-title"
                  type="text"
                  className="form-control"
                  value={form.name}
                  onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                  placeholder="e.g., Morning walk, Metro commute"
                  required
                />
              </div>
              <div className="row g-2 mb-3">
                <div className="col-12 col-sm-6">
                  <label className="form-label" htmlFor="event-date">Date *</label>
                  <input
                    id="event-date"
                    type="date"
                    className="form-control"
                    value={form.routine_date}
                    onChange={(e) => setForm((p) => ({ ...p, routine_date: e.target.value }))}
                    required
                  />
                </div>
                <div className="col-12 col-sm-6">
                  <label className="form-label" htmlFor="event-category">Category *</label>
                  <select
                    id="event-category"
                    className="form-select"
                    value={form.routine_type}
                    onChange={(e) => setForm((p) => ({ ...p, routine_type: e.target.value }))}
                  >
                    <option value="commute">Commute</option>
                    <option value="exercise">Exercise</option>
                    <option value="outdoor_work">Outdoor Work</option>
                    <option value="indoor_air">Indoor Air</option>
                    <option value="energy">Energy</option>
                    <option value="waste">Waste</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="row g-2 mb-3">
                <div className="col-6">
                  <label className="form-label" htmlFor="event-start">Start time</label>
                  <input
                    id="event-start"
                    type="time"
                    className="form-control"
                    value={form.start_time}
                    onChange={(e) => setForm((p) => ({ ...p, start_time: e.target.value }))}
                    required
                  />
                </div>
                <div className="col-6">
                  <label className="form-label" htmlFor="event-end">End time</label>
                  <input
                    id="event-end"
                    type="time"
                    className="form-control"
                    value={form.end_time}
                    onChange={(e) => setForm((p) => ({ ...p, end_time: e.target.value }))}
                    required
                  />
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="event-reminder">Reminder</label>
                <select
                  id="event-reminder"
                  className="form-select"
                  value={form.reminder_minutes}
                  onChange={(e) => setForm((p) => ({ ...p, reminder_minutes: e.target.value }))}
                >
                  <option value="">No reminder</option>
                  <option value="10">10 minutes before</option>
                  <option value="15">15 minutes before</option>
                  <option value="30">30 minutes before</option>
                  <option value="60">1 hour before</option>
                </select>
              </div>
              <div className="mb-0">
                <label className="form-label" htmlFor="event-desc">Description</label>
                <textarea
                  id="event-desc"
                  className="form-control"
                  rows={2}
                  value={form.description}
                  onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                  placeholder="Optional notes..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-outline-secondary" onClick={onClose} disabled={saving}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? (
                  <>
                    <LoadingSpinner size="sm" className="me-1" /> Saving...
                  </>
                ) : (
                  'Save'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

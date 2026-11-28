import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import routineService from '../../services/routineService.js';
import PlannerToolbar from './components/PlannerToolbar.jsx';
import PlannerFilters from './components/PlannerFilters.jsx';
import PlannerCalendar from './components/PlannerCalendar.jsx';
import PlannerAgenda from './components/PlannerAgenda.jsx';
import EventFormModal from './components/EventFormModal.jsx';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function getMonday(isoDate) {
  const d = new Date(`${isoDate}T00:00:00`);
  const day = (d.getDay() + 6) % 7;
  d.setDate(d.getDate() - day);
  return d.toISOString().slice(0, 10);
}

function addDays(isoDate, offset) {
  const d = new Date(`${isoDate}T00:00:00`);
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}

/**
 * Daily planner (page workflows doc, section 5): calendar/agenda with
 * deterministic AQI safety bands and event management.
 */
export default function DailyPlannerPage() {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState(todayIso);
  const [viewMode, setViewMode] = useState('week');
  const [category, setCategory] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [events, setEvents] = useState([]);
  const [aqiContext, setAqiContext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);

  const weekStart = getMonday(selectedDate);
  const weekEnd = addDays(weekStart, 6);

  const loadRoutines = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params =
        viewMode === 'week'
          ? { from: weekStart, to: weekEnd }
          : { date: selectedDate };
      if (category) params.category = category;
      if (statusFilter) params.status = statusFilter;

      const res = await routineService.listRoutines(params);
      setEvents(res.routines || []);
      setAqiContext(
        res.aqi_value !== null && res.aqi_value !== undefined
          ? { value: res.aqi_value, standard: res.aqi_standard }
          : null,
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load daily planner');
    } finally {
      setLoading(false);
    }
  }, [user, viewMode, weekStart, weekEnd, selectedDate, category, statusFilter]);

  useEffect(() => {
    loadRoutines();
  }, [loadRoutines]);

  const handleSave = async (payload) => {
    setSaving(true);
    setError(null);
    try {
      if (editingEvent) {
        await routineService.updateRoutine(editingEvent.id, payload);
      } else {
        await routineService.createRoutine(payload);
      }
      setModalOpen(false);
      setEditingEvent(null);
      await loadRoutines();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save event');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleComplete = async (ev) => {
    setBusyId(ev.id);
    setError(null);
    try {
      const nextStatus = ev.status === 'completed' ? 'planned' : 'completed';
      await routineService.updateStatus(ev.id, nextStatus);
      await loadRoutines();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update event status');
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (ev) => {
    if (!window.confirm(`Delete "${ev.name}"?`)) return;
    setBusyId(ev.id);
    setError(null);
    try {
      await routineService.deleteRoutine(ev.id);
      await loadRoutines();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete event');
    } finally {
      setBusyId(null);
    }
  };

  const stepDays = viewMode === 'week' ? 7 : 1;

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Daily Planner"
        subtitle="Plan outdoor activities for the cleanest hours of the day."
        actions={
          aqiContext ? (
            <span className="badge text-bg-light border">
              Local AQI: {aqiContext.value} ({aqiContext.standard})
            </span>
          ) : (
            <span className="badge text-bg-secondary">AQI unavailable</span>
          )
        }
      />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

      <div className="card shadow-sm">
        <div className="card-body">
          <PlannerToolbar
            selectedDate={selectedDate}
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            onPrev={() => setSelectedDate((d) => addDays(d, -stepDays))}
            onNext={() => setSelectedDate((d) => addDays(d, stepDays))}
            onToday={() => setSelectedDate(todayIso())}
            onAddEvent={() => {
              setEditingEvent(null);
              setModalOpen(true);
            }}
          />

          <PlannerFilters
            category={category}
            status={statusFilter}
            onCategoryChange={setCategory}
            onStatusChange={setStatusFilter}
          />

          {loading ? (
            <div className="text-center py-5">
              <LoadingSpinner size="lg" />
              <p className="text-supporting mt-2 mb-0">Loading schedule...</p>
            </div>
          ) : (
            <>
              {viewMode === 'week' && (
                <div className="d-none d-md-block">
                  <PlannerCalendar
                    weekStart={weekStart}
                    events={events}
                    onSelectDate={(d) => {
                      setSelectedDate(d);
                      setViewMode('agenda');
                    }}
                    onEdit={(ev) => {
                      setEditingEvent(ev);
                      setModalOpen(true);
                    }}
                    onToggleComplete={handleToggleComplete}
                  />
                </div>
              )}

              {/* Always show readable agenda on mobile, or on desktop when Agenda view selected */}
              <div className={viewMode === 'week' ? 'd-md-none' : ''}>
                <PlannerAgenda
                  events={events}
                  onEdit={(ev) => {
                    setEditingEvent(ev);
                    setModalOpen(true);
                  }}
                  onDelete={handleDelete}
                  onToggleComplete={handleToggleComplete}
                  busyId={busyId}
                />
              </div>
            </>
          )}
        </div>
      </div>

      <EventFormModal
        show={modalOpen}
        initialEvent={editingEvent}
        defaultDate={selectedDate}
        onClose={() => {
          setModalOpen(false);
          setEditingEvent(null);
        }}
        onSave={handleSave}
        saving={saving}
      />
    </div>
  );
}

import RoutineEventCard from './RoutineEventCard.jsx';

/**
 * Mobile-friendly chronological agenda list (Phase 6).
 */
export default function PlannerAgenda({ events, onEdit, onDelete, onToggleComplete, busyId }) {
  if (!events || events.length === 0) {
    return (
      <div className="text-center py-4 text-supporting">
        No scheduled activities for this period. Click <strong>Add Event</strong> to plan your day.
      </div>
    );
  }

  return (
    <div>
      {events.map((ev) => (
        <RoutineEventCard
          key={ev.id}
          event={ev}
          onEdit={onEdit}
          onDelete={onDelete}
          onToggleComplete={onToggleComplete}
          busyId={busyId}
        />
      ))}
    </div>
  );
}

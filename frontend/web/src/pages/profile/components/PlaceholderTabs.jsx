/**
 * Placeholder tab component for Profile page.
 * Used for tabs that are not yet implemented (routine, notifications).
 */
export default function PlaceholderTabs({ tabId, tabs }) {
  return (
    <div className="text-center py-5">
      <svg className="bi text-muted mb-3" width="64" height="64"><use xlinkHref="#clock-history" /></svg>
      <h5 className="text-body-secondary">Coming Soon</h5>
      <p className="text-supporting">
        {tabId === 'routine'
          ? 'Daily routine planner will be available in Phase 6.'
          : 'Notification preferences will be available in Phase 9.'}
      </p>
    </div>
  );
}
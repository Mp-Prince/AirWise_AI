/**
 * Empty-state block shown when a section has no data yet.
 * Per UI/UX spec: explain what is missing and offer the next action.
 */
export default function EmptyState({ icon = 'bi-inbox', title, message, action }) {
  return (
    <div className="text-center py-5">
      <i className={`bi ${icon} d-block mb-2`} style={{ fontSize: '2rem' }} aria-hidden="true" />
      <h2 className="section-heading h5">{title}</h2>
      <p className="text-supporting mb-3">{message}</p>
      {action ?? null}
    </div>
  );
}

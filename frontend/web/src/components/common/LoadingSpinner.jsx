/** Accessible loading indicator with a text label (never colour-only). */
export default function LoadingSpinner({ label = 'Loading…' }) {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center py-5" role="status">
      <div className="spinner-border text-primary" aria-hidden="true" />
      <span className="text-supporting mt-2">{label}</span>
    </div>
  );
}

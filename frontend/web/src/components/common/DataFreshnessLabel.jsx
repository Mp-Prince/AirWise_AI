/**
 * Shows how old the displayed environmental data is.
 * Pages must label freshness and source (docs 02/03); missing data is
 * shown as "unavailable", never as zero.
 */
export default function DataFreshnessLabel({ fetchedAt, source }) {
  if (!fetchedAt) {
    return (
      <span className="badge text-bg-secondary">
        <i className="bi bi-clock me-1" aria-hidden="true" />
        Data unavailable
      </span>
    );
  }

  const minutes = Math.max(0, Math.round((Date.now() - new Date(fetchedAt).getTime()) / 60000));
  const age = minutes < 60 ? `${minutes} min ago` : `${Math.round(minutes / 60)} h ago`;

  return (
    <span className="badge text-bg-light border">
      <i className="bi bi-clock me-1" aria-hidden="true" />
      Updated {age}
      {source ? ` · ${source}` : ''}
    </span>
  );
}

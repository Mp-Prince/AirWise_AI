/**
 * Standard page heading: title, optional subtitle, optional right-side
 * actions slot (UI/UX spec section 5 — every page starts with a clear
 * title and one primary action).
 */
export default function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="d-flex flex-wrap align-items-start justify-content-between gap-2 mb-3">
      <div>
        <h1 className="page-title mb-0">{title}</h1>
        {subtitle ? <p className="text-supporting mb-0 mt-1">{subtitle}</p> : null}
      </div>
      {actions ? <div className="d-flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}

/**
 * Category & status filters for Daily Planner (Phase 6).
 */
export default function PlannerFilters({ category, status, onCategoryChange, onStatusChange }) {
  return (
    <div className="row g-2 mb-3">
      <div className="col-12 col-sm-6 col-md-4">
        <select
          className="form-select form-select-sm"
          aria-label="Filter by category"
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="">All categories</option>
          <option value="commute">Commute</option>
          <option value="exercise">Exercise</option>
          <option value="outdoor_work">Outdoor Work</option>
          <option value="indoor_air">Indoor Air</option>
          <option value="energy">Energy</option>
          <option value="waste">Waste</option>
          <option value="other">Other</option>
        </select>
      </div>
      <div className="col-12 col-sm-6 col-md-4">
        <select
          className="form-select form-select-sm"
          aria-label="Filter by status"
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="planned">Planned</option>
          <option value="completed">Completed</option>
          <option value="skipped">Skipped</option>
        </select>
      </div>
    </div>
  );
}

import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';

/**
 * Daily planner (page workflows doc, section 5): hour-by-hour safety
 * bands for outdoor activities based on AQI + weather.
 * Phase 0: structural shell; activity blocks + hourly bands arrive in Phase 3.
 */
export default function DailyPlannerPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Daily Planner"
        subtitle="Plan outdoor activities for the cleanest hours of the day."
        actions={
          <button type="button" className="btn btn-primary" disabled>
            <i className="bi bi-plus-lg me-1" aria-hidden="true" />
            Add activity
          </button>
        }
      />
      <div className="card shadow-sm">
        <div className="card-body">
          <EmptyState
            icon="bi-calendar3"
            title="Nothing planned yet"
            message="Add commute, exercise or outdoor-work blocks and AirWise will mark each hour safe, caution or avoid once live air-quality data is connected in Phase 3."
            action={
              <button type="button" className="btn btn-outline-primary" disabled>
                Add your first activity
              </button>
            }
          />
        </div>
      </div>
    </div>
  );
}

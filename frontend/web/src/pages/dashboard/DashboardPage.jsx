import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import DataFreshnessLabel from '../../components/common/DataFreshnessLabel.jsx';

/**
 * Dashboard (page workflows doc, section 4): AQI hero, health advisory,
 * trend chart, today's plan, recommendations, impact summary.
 * Phase 0: layout grid with empty states — no fabricated measurements.
 * Real data arrives with Phase 3 (air quality + weather APIs).
 */
export default function DashboardPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Dashboard"
        subtitle="Air quality and health guidance for today."
        actions={<DataFreshnessLabel fetchedAt={null} />}
      />

      <div className="row g-3 g-lg-4">
        <div className="col-12 col-lg-8">
          <div className="card shadow-sm mb-3 mb-lg-4">
            <div className="card-body">
              <h2 className="section-heading">Current air quality</h2>
              <EmptyState
                icon="bi-wind"
                title="No location set yet"
                message="Once you set your city in onboarding, live AQI and weather will appear here — always labelled with source and update time."
              />
            </div>
          </div>
          <div className="card shadow-sm">
            <div className="card-body">
              <h2 className="section-heading">24-hour trend</h2>
              <EmptyState
                icon="bi-graph-up"
                title="Chart appears with live data"
                message="AQI over the last 24 hours will render here (Chart.js), never estimated when the provider has no reading."
              />
            </div>
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm mb-3">
            <div className="card-body">
              <h2 className="section-heading">Health advisory</h2>
              <p className="text-supporting mb-0">
                Advisory cards appear here when AQI crosses standard bands for your
                profile’s sensitivities.
              </p>
            </div>
          </div>
          <div className="card shadow-sm">
            <div className="card-body">
              <h2 className="section-heading">Today’s plan</h2>
              <p className="text-supporting mb-0">
                Your routine hours marked safe / caution / avoid — from the Daily Planner.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

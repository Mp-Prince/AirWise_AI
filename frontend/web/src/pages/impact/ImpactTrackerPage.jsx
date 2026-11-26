import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';

/**
 * Impact tracker (page workflows doc, section 8): CO2e saved over time
 * from accepted green actions. Values come from emission-factor records
 * and are always shown as estimated vs measured — never fabricated.
 * Phase 0: summary tiles + chart placeholder.
 */
export default function ImpactTrackerPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Impact Tracker"
        subtitle="The cleaner-air and lower-carbon effect of your choices."
      />
      <div className="row g-3 mb-3">
        {[
          { label: 'CO2e avoided (30 days)', hint: 'estimated' },
          { label: 'Low-AQI hours avoided', hint: 'from your plan' },
          { label: 'Streak', hint: 'active days' },
        ].map((tile) => (
          <div className="col-12 col-md-4" key={tile.label}>
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <div className="text-supporting small text-uppercase">{tile.label}</div>
                <div className="fs-2 fw-semibold">—</div>
                <div className="text-supporting small">{tile.hint}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="card shadow-sm">
        <div className="card-body">
          <EmptyState
            icon="bi-graph-up-arrow"
            title="No impact records yet"
            message="When you accept low-emission alternatives in the planner, the savings are calculated from published emission factors and charted here."
          />
        </div>
      </div>
    </div>
  );
}

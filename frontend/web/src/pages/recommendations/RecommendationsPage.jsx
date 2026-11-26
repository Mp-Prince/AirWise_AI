import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';

/**
 * Recommendations feed (page workflows doc, section 7): health,
 * lifestyle and eco suggestions with accept / dismiss actions.
 * Phase 0: shell; engine + user_actions wiring arrives in Phase 5/6.
 */
export default function RecommendationsPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Recommendations"
        subtitle="Personalised, evidence-backed suggestions for cleaner air days."
      />
      <div className="card shadow-sm">
        <div className="card-body">
          <EmptyState
            icon="bi-lightbulb"
            title="No recommendations yet"
            message="Once your profile, routine and location data are set up, suggestions will appear here with the reason behind each one — and you can accept or dismiss them."
          />
        </div>
      </div>
    </div>
  );
}

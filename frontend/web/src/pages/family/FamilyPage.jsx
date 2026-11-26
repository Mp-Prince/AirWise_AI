import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';

/**
 * Family hub (page workflows doc, section 9): members, shared alerts,
 * per-member sensitivities. Phase 0: shell; families/family_members
 * APIs arrive in Phase 2.
 */
export default function FamilyPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Family"
        subtitle="Shared air-quality alerts and guidance for the people you look after."
        actions={
          <button type="button" className="btn btn-primary" disabled>
            <i className="bi bi-person-plus me-1" aria-hidden="true" />
            Invite member
          </button>
        }
      />
      <div className="card shadow-sm">
        <div className="card-body">
          <EmptyState
            icon="bi-people"
            title="No family yet"
            message="Add members so alerts and recommendations account for children, older adults, or anyone with asthma or heart conditions."
          />
        </div>
      </div>
    </div>
  );
}

import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Profile & settings (page workflows doc, section 10): account details,
 * location, health profile, routine, notifications, privacy, units.
 * Phase 0: tabbed section shell; wired to user APIs in Phase 2.
 */
export default function ProfilePage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader title="Profile / Settings" subtitle="Your account, health profile and preferences." />
      <div className="mb-3" role="alert">
        <ErrorAlert message="Settings become editable in Phase 2 — this shows the section layout." />
      </div>
      <div className="card shadow-sm">
        <div className="card-header">
          <ul
            className="nav nav-tabs card-header-tabs"
            role="tablist"
          >
            {['Account', 'Location', 'Health', 'Routine', 'Notifications', 'Privacy'].map(
              (tab, i) => (
                <li className="nav-item" key={tab}>
                  <button
                    className={'nav-link' + (i === 0 ? ' active' : '')}
                    type="button"
                    role="tab"
                    aria-selected={i === 0}
                  >
                    {tab}
                  </button>
                </li>
              ),
            )}
          </ul>
        </div>
        <div className="card-body">
          <p className="text-supporting mb-0">
            Tab content is placeholder-only in Phase 0. Each section maps to its own API
            module on the backend (users, locations, user_profiles, daily_routines).
          </p>
        </div>
      </div>
    </div>
  );
}

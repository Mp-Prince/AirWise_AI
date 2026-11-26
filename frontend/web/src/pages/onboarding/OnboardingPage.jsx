import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Post-signup onboarding (page workflows doc, section 3): location,
 * health sensitivities, daily routine, family, notification prefs.
 * Phase 0: step overview. Phase 1/2 implement the wizard with the
 * user_profiles + locations + daily_routines APIs.
 */
const STEPS = [
  { title: 'Location', text: 'Set your home city or drop a pin on the map.' },
  { title: 'Health & sensitivity', text: 'Asthma, heart condition, children, pregnancy — tunes caution levels.' },
  { title: 'Daily routine', text: 'Commute, exercise and outdoor work windows.' },
  { title: 'Family', text: 'Add members so recommendations cover them too.' },
  { title: 'Notifications', text: 'Choose when AirWise should alert you.' },
];

export default function OnboardingPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Set up AirWise"
        subtitle="A few details so recommendations fit your day and your health."
      />
      <div className="mb-3" role="alert">
        <ErrorAlert message="Onboarding steps activate in Phase 2 — this is the structural shell." />
      </div>
      <ol className="list-group mb-4">
        {STEPS.map((s, i) => (
          <li className="list-group-item d-flex gap-3 align-items-start" key={s.title}>
            <span
              className="badge rounded-pill text-bg-primary flex-shrink-0"
              style={{ width: '2rem', height: '2rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}
            >
              {i + 1}
            </span>
            <div>
              <strong>{s.title}</strong>
              <div className="text-supporting">{s.text}</div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

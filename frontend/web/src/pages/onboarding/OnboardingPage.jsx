import { useState } from 'react';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LocationSearch from './components/LocationSearch.jsx';

/**
 * Post-signup onboarding (page workflows doc, section 3): location,
 * health sensitivities, daily routine, family, notification prefs.
 * Phase 3: Location search now uses Nominatim geocoding via backend.
 */
const STEPS = [
  { title: 'Location', text: 'Set your home city or drop a pin on the map.' },
  { title: 'Health & sensitivity', text: 'Asthma, heart condition, children, pregnancy — tunes caution levels.' },
  { title: 'Daily routine', text: 'Commute, exercise and outdoor work windows.' },
  { title: 'Family', text: 'Add members so recommendations cover them too.' },
  { title: 'Notifications', text: 'Choose when AirWise should alert you.' },
];

export default function OnboardingPage() {
  const [selectedLocation, setSelectedLocation] = useState(null);

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Set up AirWise"
        subtitle="A few details so recommendations fit your day and your health."
      />
      <div className="row g-4">
        <div className="col-12 col-lg-8">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Step 1 of 5: Location</h5>
              <p className="text-supporting mb-4">
                Search for your city or address. We use OpenStreetMap Nominatim to find coordinates
                for accurate air quality and weather data.
              </p>
              <LocationSearch
                onLocationSelect={setSelectedLocation}
                selectedLocation={selectedLocation}
              />
              {selectedLocation && (
                <div className="alert alert-success mt-3 mb-0 small">
                  <svg className="bi me-1" width="16" height="16"><use xlinkHref="#check-circle" /></svg>
                  Selected: <strong>{selectedLocation.display_name}</strong>
                  <div className="text-muted mt-1">
                    Coordinates: {selectedLocation.lat?.toFixed(4)}, {selectedLocation.lon?.toFixed(4)}
                    {selectedLocation.type && ` • Type: ${selectedLocation.type}`}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <h5 className="card-title mb-3">Steps 2–5: Coming Soon</h5>
              <div className="row g-3">
                {STEPS.slice(1).map((s, i) => (
                  <div className="col-12 col-md-6" key={s.title}>
                    <div className="border rounded p-3 bg-light">
                      <div className="d-flex gap-2 align-items-start">
                        <span className="badge rounded-pill text-bg-secondary flex-shrink-0">
                          {i + 2}
                        </span>
                        <div>
                          <strong className="d-block">{s.title}</strong>
                          <small className="text-supporting">{s.text}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">Why location matters</h5>
              <ul className="list-unstyled small">
                <li className="mb-2">• Live AQI from <strong>OpenAQ</strong> monitors near you</li>
                <li className="mb-2">• Weather from <strong>OpenWeatherMap</strong> for your exact coordinates</li>
                <li className="mb-2">• Health advisories tuned to local conditions</li>
                <li className="mb-2">• Daily planner with hour-by-hour guidance</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import LocationSearch from './components/LocationSearch.jsx';
import profileApi from '../../services/profileApi.js';
import environmentalApi from '../../services/environmentalApi.js';

/**
 * Post-signup onboarding (page workflows doc, section 3): location,
 * health sensitivities, daily routine, family, notification prefs.
 * Phase 2/3: Profile creation with city/state selection via Nominatim geocoding.
 */
const STEPS = [
  { title: 'Location', text: 'Set your home city or drop a pin on the map.' },
  { title: 'Health & sensitivity', text: 'Asthma, heart condition, children, pregnancy — tunes caution levels.' },
  { title: 'Daily routine', text: 'Commute, exercise and outdoor work windows.' },
  { title: 'Family', text: 'Add members so recommendations cover them too.' },
  { title: 'Notifications', text: 'Choose when AirWise should alert you.' },
];

export default function OnboardingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    date_of_birth: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    health_conditions: [],
    sensitivities: [],
    preferred_units: 'metric',
    language: 'en',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    setError(null);
  };

  const handleProfileFieldChange = (field, value) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
  };

  const handleHealthConditionToggle = (condition) => {
    setProfileData(prev => ({
      ...prev,
      health_conditions: prev.health_conditions.includes(condition)
        ? prev.health_conditions.filter(c => c !== condition)
        : [...prev.health_conditions, condition]
    }));
  };

  const handleSensitivityToggle = (sensitivity) => {
    setProfileData(prev => ({
      ...prev,
      sensitivities: prev.sensitivities.includes(sensitivity)
        ? prev.sensitivities.filter(s => s !== sensitivity)
        : [...prev.sensitivities, sensitivity]
    }));
  };

  const saveProfile = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const resolvedName =
        profileData.full_name.trim() ||
        user?.full_name ||
        user?.email?.split('@')[0] ||
        'AirWise User';

      // Build profile data for API
      const apiData = {
        full_name: resolvedName,
        date_of_birth: profileData.date_of_birth ? `${profileData.date_of_birth}T00:00:00Z` : null,
        gender: profileData.gender || null,
        height_cm: profileData.height_cm ? parseInt(profileData.height_cm, 10) : null,
        weight_kg: profileData.weight_kg ? parseFloat(profileData.weight_kg) : null,
        health_conditions: profileData.health_conditions,
        sensitivities: profileData.sensitivities,
        preferred_units: profileData.preferred_units,
        language: profileData.language,
        timezone: profileData.timezone,
      };

      await profileApi.upsertProfile(apiData);

      // If location selected and not already saved, create it (backend auto-syncs AQI + weather)
      if (selectedLocation && !selectedLocation.is_saved) {
        const rawName = selectedLocation.name || selectedLocation.display_name || 'Saved Location';
        const locationData = {
          name: rawName.slice(0, 100),
          lat: selectedLocation.lat,
          lon: selectedLocation.lon,
          city: selectedLocation.city,
          state: selectedLocation.state,
          country: selectedLocation.country,
          is_default: true,
        };
        await environmentalApi.createLocation(locationData);
      } else if (selectedLocation?.id && !selectedLocation.is_default) {
        await environmentalApi.setDefaultLocation(selectedLocation.id);
      }

      setSuccess(true);
      // Navigate to dashboard after short delay
      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        Array.isArray(detail)
          ? detail.map((d) => d.msg).join(', ')
          : detail || 'Failed to save profile. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep === 1) {
      if (!selectedLocation) {
        setError('Please select a location to continue.');
        return;
      }
      setCurrentStep(2);
      setError(null);
    } else if (currentStep === 2) {
      setCurrentStep(3);
    } else if (currentStep === 3) {
      setCurrentStep(4);
    } else if (currentStep === 4) {
      setCurrentStep(5);
    } else if (currentStep === 5) {
      saveProfile();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError(null);
    }
  };

  // Step 1: Location
  const renderStep1 = () => (
    <div className="card shadow-sm">
      <div className="card-body">
        <h5 className="card-title mb-3">Step 1 of 5: Location</h5>
        <p className="text-supporting mb-4">
          Search for your city or address. We use OpenStreetMap Nominatim to find coordinates
          for accurate air quality and weather data.
        </p>
        <LocationSearch
          onLocationSelect={handleLocationSelect}
          selectedLocation={selectedLocation}
        />
        {selectedLocation && (
          <div className="alert alert-success mt-3 mb-0 small">
            <i className="bi bi-check-circle me-1" aria-hidden="true" />
            Selected: <strong>{selectedLocation.display_name || selectedLocation.name}</strong>
            <div className="text-muted mt-1">
              Coordinates: {selectedLocation.lat?.toFixed(4)}, {selectedLocation.lon?.toFixed(4)}
              {selectedLocation.city && ` • City: ${selectedLocation.city}`}
              {selectedLocation.state && ` • State: ${selectedLocation.state}`}
              {selectedLocation.country && ` • Country: ${selectedLocation.country}`}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Step 2: Health & Sensitivity
  const renderStep2 = () => {
    const commonConditions = ['Asthma', 'COPD', 'Heart disease', 'Diabetes', 'Allergies', 'Pregnancy', 'None'];
    const commonSensitivities = ['Air pollution', 'Pollen', 'Heat', 'Cold', 'Humidity', 'None'];

    return (
      <div className="card shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">Step 2 of 5: Health & Sensitivity</h5>
          <p className="text-supporting mb-4">
            Select any conditions or sensitivities so we can tailor health advisories for you.
          </p>

          <div className="mb-4">
            <label className="form-label fw-medium">Health Conditions</label>
            <div className="row g-2">
              {commonConditions.map(condition => (
                <div key={condition} className="col-12 col-md-6 col-lg-4">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      value={condition}
                      checked={profileData.health_conditions.includes(condition)}
                      onChange={() => handleHealthConditionToggle(condition)}
                      id={`health-${condition}`}
                    />
                    <label className="form-check-label" htmlFor={`health-${condition}`}>
                      {condition}
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label fw-medium">Sensitivities</label>
            <div className="row g-2">
              {commonSensitivities.map(sensitivity => (
                <div key={sensitivity} className="col-12 col-md-6 col-lg-4">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      value={sensitivity}
                      checked={profileData.sensitivities.includes(sensitivity)}
                      onChange={() => handleSensitivityToggle(sensitivity)}
                      id={`sens-${sensitivity}`}
                    />
                    <label className="form-check-label" htmlFor={`sens-${sensitivity}`}>
                      {sensitivity}
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Step 3: Daily Routine (placeholder)
  const renderStep3 = () => (
    <div className="card shadow-sm">
      <div className="card-body">
        <h5 className="card-title mb-3">Step 3 of 5: Daily Routine</h5>
        <p className="text-supporting mb-4">
          Set your typical commute, exercise, and outdoor work hours for personalized daily planning.
        </p>
        <div className="alert alert-info">
          <svg className="bi me-1" width="16" height="16"><use xlinkHref="#info-circle" /></svg>
          Daily routine planner coming in Phase 6.
        </div>
      </div>
    </div>
  );

  // Step 4: Family (placeholder)
  const renderStep4 = () => (
    <div className="card shadow-sm">
      <div className="card-body">
        <h5 className="card-title mb-3">Step 4 of 5: Family</h5>
        <p className="text-supporting mb-4">
          Add family members so recommendations cover them too.
        </p>
        <div className="alert alert-info">
          <svg className="bi me-1" width="16" height="16"><use xlinkHref="#info-circle" /></svg>
          Family setup coming in Phase 8.
        </div>
      </div>
    </div>
  );

  // Step 5: Notifications (placeholder)
  const renderStep5 = () => (
    <div className="card shadow-sm">
      <div className="card-body">
        <h5 className="card-title mb-3">Step 5 of 5: Notifications</h5>
        <p className="text-supporting mb-4">
          Choose when AirWise should alert you about air quality changes.
        </p>
        <div className="alert alert-info">
          <svg className="bi me-1" width="16" height="16"><use xlinkHref="#info-circle" /></svg>
          Notification preferences coming in Phase 9.
        </div>
        <div className="d-grid gap-2 mt-3">
          <button
            className="btn btn-primary btn-lg"
            onClick={handleNext}
            disabled={loading}
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="me-2" />
                Saving...
              </>
            ) : (
              'Complete Setup'
            )}
          </button>
        </div>
        {success && (
          <div className="alert alert-success mt-3">
            <svg className="bi me-1" width="16" height="16"><use xlinkHref="#check-circle" /></svg>
            Profile saved! Redirecting to dashboard...
          </div>
        )}
      </div>
    </div>
  );

  // Profile basics form (shown on all steps)
  const renderProfileBasics = () => (
    <div className="card shadow-sm mb-3">
      <div className="card-body">
        <h5 className="card-title mb-3">Your Profile</h5>
        <div className="row g-3">
          <div className="col-12 col-md-6">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-control"
              value={profileData.full_name}
              onChange={(e) => handleProfileFieldChange('full_name', e.target.value)}
              placeholder="Enter your full name"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label">Date of Birth</label>
            <input
              type="date"
              className="form-control"
              value={profileData.date_of_birth}
              onChange={(e) => handleProfileFieldChange('date_of_birth', e.target.value)}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label">Gender</label>
            <select
              className="form-select"
              value={profileData.gender}
              onChange={(e) => handleProfileFieldChange('gender', e.target.value)}
            >
              <option value="">Select...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non_binary">Non-binary</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
          </div>
          <div className="col-12 col-md-3">
            <label className="form-label">Height (cm)</label>
            <input
              type="number"
              className="form-control"
              value={profileData.height_cm}
              onChange={(e) => handleProfileFieldChange('height_cm', e.target.value)}
              placeholder="170"
              min="30"
              max="300"
            />
          </div>
          <div className="col-12 col-md-3">
            <label className="form-label">Weight (kg)</label>
            <input
              type="number"
              className="form-control"
              value={profileData.weight_kg}
              onChange={(e) => handleProfileFieldChange('weight_kg', e.target.value)}
              placeholder="70"
              min="1"
              max="500"
              step="0.1"
            />
          </div>
          <div className="col-12 col-md-4">
            <label className="form-label">Preferred Units</label>
            <select
              className="form-select"
              value={profileData.preferred_units}
              onChange={(e) => handleProfileFieldChange('preferred_units', e.target.value)}
            >
              <option value="metric">Metric (°C, km, m/s)</option>
              <option value="imperial">Imperial (°F, mi, mph)</option>
            </select>
          </div>
          <div className="col-12 col-md-4">
            <label className="form-label">Language</label>
            <select
              className="form-select"
              value={profileData.language}
              onChange={(e) => handleProfileFieldChange('language', e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
              <option value="bn">Bengali</option>
            </select>
          </div>
          <div className="col-12 col-md-4">
            <label className="form-label">Timezone</label>
            <select
              className="form-select"
              value={profileData.timezone}
              onChange={(e) => handleProfileFieldChange('timezone', e.target.value)}
            >
              <option value="UTC">UTC</option>
              <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
              <option value="America/New_York">America/New_York (EST)</option>
              <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
              <option value="Europe/London">Europe/London (GMT)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      default: return renderStep1();
    }
  };

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Set up AirWise"
        subtitle="A few details so recommendations fit your day and your health."
      />

      {/* Progress indicator */}
      <div className="mb-4">
        <nav aria-label="Onboarding progress">
          <ol className="breadcrumb mb-0">
            {STEPS.map((step, index) => (
              <li key={step.title} className={`breadcrumb-item ${index + 1 < currentStep ? 'text-success' : index + 1 === currentStep ? 'active text-primary' : 'text-secondary'}`}>
                <span className={index + 1 === currentStep ? 'fw-bold' : ''}>{index + 1}. {step.title}</span>
              </li>
            ))}
          </ol>
        </nav>
        <div className="progress mt-2" style={{ height: '6px' }}>
          <div
            className="progress-bar bg-primary"
            role="progressbar"
            style={{ width: `${(currentStep / STEPS.length) * 100}%` }}
            aria-valuenow={currentStep}
            aria-valuemin={1}
            aria-valuemax={STEPS.length}
          />
        </div>
      </div>

      {error && (
        <ErrorAlert message={error} onDismiss={() => setError(null)} />
      )}

      <div className="row g-4">
        <div className="col-12 col-lg-8">
          {renderProfileBasics()}
          {renderStep()}

          {/* Navigation buttons (hidden on step 5 which has its own button) */}
          {currentStep < 5 && (
            <div className="d-flex justify-content-between mt-3">
              <button
                className="btn btn-outline-secondary"
                onClick={handleBack}
                disabled={currentStep === 1}
              >
                <svg className="bi me-1" width="16" height="16"><use xlinkHref="#chevron-left" /></svg>
                Back
              </button>
              <button
                className="btn btn-primary"
                onClick={handleNext}
                disabled={loading}
              >
                Next
                <svg className="bi ms-1" width="16" height="16"><use xlinkHref="#chevron-right" /></svg>
              </button>
            </div>
          )}
        </div>
        <div className="col-12 col-lg-4">
          <div className="card shadow-sm sticky-top" style={{ top: '100px' }}>
            <div className="card-body">
              <h5 className="card-title">Why this matters</h5>
              <ul className="list-unstyled small">
                <li className="mb-2">• <strong>Location</strong> → Live AQI from <strong>OpenAQ</strong> monitors near you</li>
                <li className="mb-2">• <strong>Location</strong> → Weather from <strong>OpenWeatherMap</strong> for your exact coordinates</li>
                <li className="mb-2">• <strong>Health conditions</strong> → Tuned caution levels for advisories</li>
                <li className="mb-2">• <strong>Sensitivities</strong> → Personalized alerts for triggers</li>
                <li className="mb-2">• <strong>Daily routine</strong> → Hour-by-hour guidance in planner</li>
                <li className="mb-2">• <strong>Family</strong> → Shared recommendations and alerts</li>
                <li className="mb-2">• <strong>Notifications</strong> → Timely air quality warnings</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

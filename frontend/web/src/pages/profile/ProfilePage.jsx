import { useState, useEffect } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import LocationSearch from '../onboarding/components/LocationSearch.jsx';
import profileApi from '../../services/profileApi.js';
import environmentalApi from '../../services/environmentalApi.js';

/**
 * Profile & settings (page workflows doc, section 10): account details,
 * location, health profile, routine, notifications, privacy, units.
 * Phase 2/3: Wired to user profile APIs and location APIs.
 */
export default function ProfilePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [profile, setProfile] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    // Account
    email: '',
    full_name: '',
    // Profile
    date_of_birth: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    health_conditions: [],
    sensitivities: [],
    preferred_units: 'metric',
    language: 'en',
    timezone: 'UTC',
  });

  const loadData = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      // Load profile
      const profileRes = await profileApi.getProfile();
      setProfile(profileRes);
      setFormData(prev => ({
        ...prev,
        full_name: profileRes.full_name || '',
        date_of_birth: profileRes.date_of_birth ? profileRes.date_of_birth.split('T')[0] : '',
        gender: profileRes.gender || '',
        height_cm: profileRes.height_cm || '',
        weight_kg: profileRes.weight_kg || '',
        health_conditions: profileRes.health_conditions || [],
        sensitivities: profileRes.sensitivities || [],
        preferred_units: profileRes.preferred_units || 'metric',
        language: profileRes.language || 'en',
        timezone: profileRes.timezone || 'UTC',
      }));

      // Load locations
      const locRes = await environmentalApi.getLocations();
      setLocations(locRes.locations || []);
      const defaultLoc = locRes.locations?.find(l => l.is_default);
      if (defaultLoc) {
        setSelectedLocation(defaultLoc);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        // Profile doesn't exist yet - that's OK for new users
        setProfile(null);
      } else {
        setError(err.response?.data?.detail || 'Failed to load profile data');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCheckboxToggle = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(v => v !== value)
        : [...prev[field], value]
    }));
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const apiData = {
        full_name: formData.full_name,
        date_of_birth: formData.date_of_birth || null,
        gender: formData.gender || null,
        height_cm: formData.height_cm ? parseInt(formData.height_cm) : null,
        weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : null,
        health_conditions: formData.health_conditions,
        sensitivities: formData.sensitivities,
        preferred_units: formData.preferred_units,
        language: formData.language,
        timezone: formData.timezone,
      };

      if (profile) {
        await profileApi.updateProfile(apiData);
      } else {
        await profileApi.createProfile(apiData);
      }
      setSuccess(true);
      await loadData(); // Reload to get updated data
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    setError(null);
  };

  const handleSaveLocation = async () => {
    if (!selectedLocation) {
      setError('Please select a location');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const locationData = {
        name: selectedLocation.name || selectedLocation.display_name,
        lat: selectedLocation.lat,
        lon: selectedLocation.lon,
        city: selectedLocation.city,
        state: selectedLocation.state,
        country: selectedLocation.country,
        is_default: true,
      };
      await environmentalApi.createLocation(locationData);
      await loadData();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save location');
    } finally {
      setSaving(false);
    }
  };

  const handleSetDefaultLocation = async (locationId) => {
    setSaving(true);
    setError(null);
    try {
      await environmentalApi.setDefaultLocation(locationId);
      await loadData();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to set default location');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteLocation = async (locationId) => {
    if (!window.confirm('Are you sure you want to delete this location?')) return;
    setSaving(true);
    setError(null);
    try {
      await environmentalApi.deleteLocation(locationId);
      await loadData();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete location');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container-fluid px-3 px-lg-4">
        <PageHeader title="Profile / Settings" subtitle="Your account, health profile and preferences." />
        <div className="text-center py-5">
          <LoadingSpinner size="lg" />
          <p className="text-supporting mt-2">Loading profile...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'account', label: 'Account', icon: 'person-circle' },
    { id: 'location', label: 'Location', icon: 'geo-alt' },
    { id: 'health', label: 'Health', icon: 'heart-pulse' },
    { id: 'preferences', label: 'Preferences', icon: 'gear' },
  ];

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader title="Profile / Settings" subtitle="Your account, health profile and preferences." />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
      {success && (
        <div className="alert alert-success alert-dismissible fade show mb-3" role="alert">
          <svg className="bi me-1" width="16" height="16"><use xlinkHref="#check-circle" /></svg>
          Saved successfully!
          <button type="button" className="btn-close" onClick={() => setSuccess(false)} aria-label="Close" />
        </div>
      )}

      <div className="card shadow-sm">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs" role="tablist">
            {tabs.map((tab, i) => (
              <li className="nav-item" key={tab.id}>
                <button
                  className={'nav-link' + (activeTab === tab.id ? ' active' : '')}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <svg className="bi me-1" width="16" height="16"><use xlinkHref={`#${tab.icon}`} /></svg>
                  {tab.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="card-body">
          {/* Account Tab */}
          {activeTab === 'account' && (
            <form onSubmit={(e) => { e.preventDefault(); handleSaveProfile(); }}>
              <h5 className="card-title mb-3">Account Information</h5>
              <div className="row g-3">
                <div className="col-12 col-md-6">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={user?.email || ''}
                    disabled
                  />
                  <div className="form-text">Email cannot be changed. Contact support if needed.</div>
                </div>
                <div className="col-12 col-md-6">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.full_name}
                    onChange={(e) => handleInputChange('full_name', e.target.value)}
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
              <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <LoadingSpinner size="sm" className="me-2" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Location Tab */}
          {activeTab === 'location' && (
            <div>
              <h5 className="card-title mb-3">Saved Locations</h5>

              {locations.length > 0 ? (
                <div className="table-responsive mb-4">
                  <table className="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>City / State</th>
                        <th>Coordinates</th>
                        <th>Default</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {locations.map(loc => (
                        <tr key={loc.id}>
                          <td>{loc.name}</td>
                          <td>
                            {loc.city && <span>{loc.city}</span>}
                            {loc.city && loc.state && <span className="text-muted">, </span>}
                            {loc.state && <span>{loc.state}</span>}
                            {loc.country && <span className="text-muted ms-1">({loc.country})</span>}
                          </td>
                          <td className="text-muted small">
                            {loc.lat?.toFixed(4)}, {loc.lon?.toFixed(4)}
                          </td>
                          <td>
                            {loc.is_default ? (
                              <span className="badge text-bg-success">Default</span>
                            ) : (
                              <button
                                className="btn btn-outline-primary btn-sm"
                                onClick={() => handleSetDefaultLocation(loc.id)}
                                disabled={saving}
                              >
                                Set Default
                              </button>
                            )}
                          </td>
                          <td>
                            {!loc.is_default && (
                              <button
                                className="btn btn-outline-danger btn-sm"
                                onClick={() => handleDeleteLocation(loc.id)}
                                disabled={saving}
                              >
                                <svg className="bi" width="16" height="16"><use xlinkHref="#trash" /></svg>
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-supporting">No locations saved yet.</p>
              )}

              <hr className="my-4" />
              <h5 className="card-title mb-3">Add New Location</h5>
              <p className="text-supporting mb-4">
                Search for a city or address to save as a location for air quality and weather monitoring.
              </p>
              <LocationSearch
                onLocationSelect={handleLocationSelect}
                selectedLocation={selectedLocation}
              />
              {selectedLocation && (
                <div className="alert alert-success mt-3 mb-0 small">
                  <svg className="bi me-1" width="16" height="16"><use xlinkHref="#check-circle" /></svg>
                  Selected: <strong>{selectedLocation.display_name}</strong>
                  <div className="text-muted mt-1">
                    Coordinates: {selectedLocation.lat?.toFixed(4)}, {selectedLocation.lon?.toFixed(4)}
                    {selectedLocation.city && ` • City: ${selectedLocation.city}`}
                    {selectedLocation.state && ` • State: ${selectedLocation.state}`}
                    {selectedLocation.country && ` • Country: ${selectedLocation.country}`}
                  </div>
                </div>
              )}
              <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-3">
                <button
                  className="btn btn-primary"
                  onClick={handleSaveLocation}
                  disabled={saving || !selectedLocation}
                >
                  {saving ? (
                    <>
                      <LoadingSpinner size="sm" className="me-2" />
                      Saving...
                    </>
                  ) : (
                    'Save Location'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Health Tab */}
          {activeTab === 'health' && (
            <form onSubmit={(e) => { e.preventDefault(); handleSaveProfile(); }}>
              <h5 className="card-title mb-3">Health Profile</h5>
              <p className="text-supporting mb-4">
                This information helps us tailor air quality advisories and health recommendations for you.
              </p>

              <div className="row g-3 mb-4">
                <div className="col-12 col-md-6">
                  <label className="form-label">Date of Birth</label>
                  <input
                    type="date"
                    className="form-control"
                    value={formData.date_of_birth}
                    onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                    max={new Date().toISOString().split('T')[0]}
                  />
                </div>
                <div className="col-12 col-md-6">
                  <label className="form-label">Gender</label>
                  <select
                    className="form-select"
                    value={formData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                  >
                    <option value="">Select...</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non_binary">Non-binary</option>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                  </select>
                </div>
                <div className="col-12 col-md-6">
                  <label className="form-label">Height (cm)</label>
                  <input
                    type="number"
                    className="form-control"
                    value={formData.height_cm}
                    onChange={(e) => handleInputChange('height_cm', e.target.value)}
                    placeholder="170"
                    min="30"
                    max="300"
                  />
                </div>
                <div className="col-12 col-md-6">
                  <label className="form-label">Weight (kg)</label>
                  <input
                    type="number"
                    className="form-control"
                    value={formData.weight_kg}
                    onChange={(e) => handleInputChange('weight_kg', e.target.value)}
                    placeholder="70"
                    min="1"
                    max="500"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="form-label fw-medium">Health Conditions</label>
                <div className="row g-2">
                  {['Asthma', 'COPD', 'Heart disease', 'Diabetes', 'Allergies', 'Pregnancy', 'None'].map(condition => (
                    <div key={condition} className="col-12 col-md-6 col-lg-4">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          value={condition}
                          checked={formData.health_conditions.includes(condition)}
                          onChange={() => handleCheckboxToggle('health_conditions', condition)}
                          id={`profile-health-${condition}`}
                        />
                        <label className="form-check-label" htmlFor={`profile-health-${condition}`}>
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
                  {['Air pollution', 'Pollen', 'Heat', 'Cold', 'Humidity', 'None'].map(sensitivity => (
                    <div key={sensitivity} className="col-12 col-md-6 col-lg-4">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          value={sensitivity}
                          checked={formData.sensitivities.includes(sensitivity)}
                          onChange={() => handleCheckboxToggle('sensitivities', sensitivity)}
                          id={`profile-sens-${sensitivity}`}
                        />
                        <label className="form-check-label" htmlFor={`profile-sens-${sensitivity}`}>
                          {sensitivity}
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="d-grid gap-2 d-md-flex justify-content-md-end">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <LoadingSpinner size="sm" className="me-2" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <form onSubmit={(e) => { e.preventDefault(); handleSaveProfile(); }}>
              <h5 className="card-title mb-3">Preferences</h5>
              <div className="row g-3">
                <div className="col-12 col-md-4">
                  <label className="form-label">Preferred Units</label>
                  <select
                    className="form-select"
                    value={formData.preferred_units}
                    onChange={(e) => handleInputChange('preferred_units', e.target.value)}
                  >
                    <option value="metric">Metric (°C, km, m/s)</option>
                    <option value="imperial">Imperial (°F, mi, mph)</option>
                  </select>
                </div>
                <div className="col-12 col-md-4">
                  <label className="form-label">Language</label>
                  <select
                    className="form-select"
                    value={formData.language}
                    onChange={(e) => handleInputChange('language', e.target.value)}
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
                    value={formData.timezone}
                    onChange={(e) => handleInputChange('timezone', e.target.value)}
                  >
                    <option value="UTC">UTC</option>
                    <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                    <option value="America/New_York">America/New_York (EST)</option>
                    <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
                    <option value="Europe/London">Europe/London (GMT)</option>
                  </select>
                </div>
              </div>
              <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <LoadingSpinner size="sm" className="me-2" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Routine & Notifications tabs - placeholders */}
          {['routine', 'notifications'].includes(activeTab) && (
            <div className="text-center py-5">
              <svg className="bi text-muted mb-3" width="64" height="64"><use xlinkHref="#clock-history" /></svg>
              <h5 className="text-body-secondary">Coming Soon</h5>
              <p className="text-supporting">
                {activeTab === 'routine'
                  ? 'Daily routine planner will be available in Phase 6.'
                  : 'Notification preferences will be available in Phase 9.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

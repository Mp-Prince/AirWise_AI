import { useState, useEffect } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';

// Components
import AccountTab from './components/AccountTab.jsx';
import LocationTab from './components/LocationTab.jsx';
import HealthTab from './components/HealthTab.jsx';
import PreferencesTab from './components/PreferencesTab.jsx';
import PlaceholderTabs from './components/PlaceholderTabs.jsx';

// APIs
import profileApi from '../../services/profileApi.js';
import environmentalApi from '../../services/environmentalApi.js';

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

  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
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

      const locRes = await environmentalApi.getLocations();
      setLocations(locRes.locations || []);
      const defaultLoc = locRes.locations?.find(l => l.is_default);
      if (defaultLoc) {
        setSelectedLocation(defaultLoc);
      }
    } catch (err) {
      if (err.response?.status === 404) {
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
      await loadData();
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
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
            {tabs.map((tab) => (
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
          {activeTab === 'account' && (
            <AccountTab user={user} profile={profile} formData={formData} handleInputChange={handleInputChange} handleSaveProfile={handleSaveProfile} saving={saving} success={success} setSuccess={setSuccess} />
          )}
          {activeTab === 'location' && (
            <LocationTab
              locations={locations}
              loading={loading}
              selectedLocation={selectedLocation}
              handleLocationSelect={setSelectedLocation}
              handleSaveLocation={handleSaveLocation}
              handleSetDefaultLocation={handleSetDefaultLocation}
              handleDeleteLocation={handleDeleteLocation}
              saving={saving}
            />
          )}
          {activeTab === 'health' && (
            <HealthTab formData={formData} handleInputChange={handleInputChange} handleCheckboxToggle={handleCheckboxToggle} handleSaveProfile={handleSaveProfile} saving={saving} />
          )}
          {activeTab === 'preferences' && (
            <PreferencesTab formData={formData} handleInputChange={handleInputChange} handleSaveProfile={handleSaveProfile} saving={saving} />
          )}
          {['routine', 'notifications'].includes(activeTab) && (
            <PlaceholderTabs tabId={activeTab} />
          )}
        </div>
      </div>
    </div>
  );
}
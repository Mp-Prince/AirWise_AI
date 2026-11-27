import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Preferences tab component for Profile page.
 * Handles user preferences (units, language, timezone).
 */
export default function PreferencesTab({ formData, handleInputChange, handleSaveProfile, saving }) {
  return (
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
  );
}
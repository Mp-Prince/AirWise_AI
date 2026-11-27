import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Health tab component for Profile page.
 * Handles health profile information (DOB, gender, height, weight, conditions, sensitivities).
 */
export default function HealthTab({ formData, handleInputChange, handleCheckboxToggle, handleSaveProfile, saving }) {
  return (
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
  );
}
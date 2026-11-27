import { useState } from 'react';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Account tab component for Profile page.
 * Handles account information (email, full name).
 */
export default function AccountTab({ user, profile, formData, handleInputChange, handleSaveProfile, saving, success, setSuccess }) {
  return (
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
  );
}
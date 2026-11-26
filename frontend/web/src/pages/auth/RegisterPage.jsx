import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Registration screen (page workflows doc, section 2).
 * Phase 2: wires POST /api/v1/auth/register.
 */
export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, loading, error } = useAuth();
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(true);

    try {
      await register(formData.full_name, formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by auth provider
    }
  };

  return (
    <div className="aw-auth-wrap">
      <div className="aw-auth-card card shadow-sm">
        <div className="card-body p-4 p-md-5">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <Link
              to="/"
              className="btn btn-link text-decoration-none p-0"
              aria-label="Back to home page"
            >
              <i className="bi bi-arrow-left me-1" aria-hidden="true" />
              Home
            </Link>
            <img src="/favicon.svg" alt="" width="28" height="28" />
          </div>
          <h1 className="page-title">Create your account</h1>
          <p className="text-supporting">
            AirWise AI uses your location and routine to give cleaner-air guidance.
          </p>
          {error && (
            <div className="mb-3" role="alert">
              <ErrorAlert message={error} />
            </div>
          )}
          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-name">
                Full name
              </label>
              <input
                id="register-name"
                name="full_name"
                type="text"
                className="form-control"
                value={formData.full_name}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-email">
                Email
              </label>
              <input
                id="register-email"
                name="email"
                type="email"
                className="form-control"
                value={formData.email}
                onChange={handleChange}
                autoComplete="email"
                required
                disabled={loading}
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-password">
                Password
              </label>
              <input
                id="register-password"
                name="password"
                type="password"
                className="form-control"
                value={formData.password}
                onChange={handleChange}
                autoComplete="new-password"
                required
                disabled={loading}
              />
              <div className="form-text">
                At least 8 characters, with one number and one letter.
              </div>
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>
          <p className="text-center mt-4 mb-0">
            Already registered? <Link to="/login">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
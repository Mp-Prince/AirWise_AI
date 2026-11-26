import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Login screen (page workflows doc, section 1).
 * Phase 2: wires POST /api/v1/auth/login and token storage.
 */
export default function LoginPage() {
  const navigate = useNavigate();
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(true);

    try {
      await login(formData.email, formData.password);
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
          <h1 className="page-title">Welcome back</h1>
          <p className="text-supporting">Log in to see today's air quality and plan ahead.</p>
          {error && (
            <div className="mb-3" role="alert">
              <ErrorAlert message={error} />
            </div>
          )}
          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                name="email"
                type="email"
                className="form-control"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                autoComplete="email"
                required
                disabled={loading}
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="login-password">
                Password
              </label>
              <input
                id="login-password"
                name="password"
                type="password"
                className="form-control"
                value={formData.password}
                onChange={handleChange}
                autoComplete="current-password"
                required
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? 'Logging in...' : 'Log in'}
            </button>
          </form>
          {submitted && !loading && !error && (
            <p className="text-supporting small mt-3 mb-0">
              Form validated locally; the API call will be added in Phase 2.
            </p>
          )}
          <p className="text-center mt-4 mb-0">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
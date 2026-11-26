import { useState } from 'react';
import { Link } from 'react-router-dom';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Login screen (page workflows doc, section 1).
 * Phase 0: responsive form shell with client-side validation states.
 * Phase 2 wires POST /api/v1/auth/login and token storage.
 */
export default function LoginPage() {
  const [submitted, setSubmitted] = useState(false);

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
          <p className="text-supporting">Log in to see today’s air quality and plan ahead.</p>
          <div className="mb-3" role="alert">
            <ErrorAlert message="Login is not available yet — backend auth arrives in Phase 2." />
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setSubmitted(true);
            }}
            noValidate
          >
            <div className="mb-3">
              <label className="form-label" htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                type="email"
                className="form-control"
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="login-password">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                className="form-control"
                autoComplete="current-password"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary w-100">
              Log in
            </button>
          </form>
          {submitted ? (
            <p className="text-supporting small mt-3 mb-0">
              Form validated locally; the API call will be added in Phase 2.
            </p>
          ) : null}
          <p className="text-center mt-4 mb-0">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

import { Link } from 'react-router-dom';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';

/**
 * Registration screen (page workflows doc, section 2).
 * Phase 0: form shell + password-requirements copy.
 * Phase 2 wires POST /api/v1/auth/register.
 */
export default function RegisterPage() {
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
          <div className="mb-3" role="alert">
            <ErrorAlert message="Registration is not available yet — backend auth arrives in Phase 2." />
          </div>
          <form onSubmit={(e) => e.preventDefault()} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-name">
                Full name
              </label>
              <input id="register-name" type="text" className="form-control" required />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-email">
                Email
              </label>
              <input
                id="register-email"
                type="email"
                className="form-control"
                autoComplete="email"
                required
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="register-password">
                Password
              </label>
              <input
                id="register-password"
                type="password"
                className="form-control"
                autoComplete="new-password"
                required
              />
              <div className="form-text">
                At least 8 characters, with one number and one letter.
              </div>
            </div>
            <button type="submit" className="btn btn-primary w-100">
              Create account
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

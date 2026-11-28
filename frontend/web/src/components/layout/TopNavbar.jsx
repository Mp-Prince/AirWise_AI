import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import environmentalApi from '../../services/environmentalApi.js';
import NAV_ITEMS from './navItems.js';

/**
 * Mobile/tablet top navbar.
 * Global header displays: selected city, notifications, profile menu.
 */
export default function TopNavbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [defaultLocation, setDefaultLocation] = useState(null);

  const currentLabel =
    NAV_ITEMS.find((i) => pathname.startsWith(i.to))?.label ?? 'AirWise AI';

  useEffect(() => {
    let active = true;
    if (!user) {
      setDefaultLocation(null);
      return undefined;
    }
    environmentalApi
      .getLocations()
      .then((res) => {
        if (!active) return;
        const locs = res?.locations || [];
        setDefaultLocation(locs.find((l) => l.is_default) || locs[0] || null);
      })
      .catch(() => {
        if (active) setDefaultLocation(null);
      });
    return () => {
      active = false;
    };
  }, [user, pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="aw-topbar navbar sticky-top px-3 py-2">
      <div className="d-flex align-items-center gap-2 w-100">
        <button
          className="btn btn-outline-secondary aw-topbar-toggle"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#awMobileMenu"
          aria-controls="awMobileMenu"
          aria-label="Open navigation menu"
        >
          <i className="bi bi-list" aria-hidden="true" />
        </button>

        <span className="navbar-brand mb-0 h1 d-lg-none">AirWise AI</span>
        <span className="text-supporting d-none d-lg-inline ms-2">{currentLabel}</span>

        <div className="ms-auto d-flex align-items-center gap-2">
          <Link
            to="/profile"
            className="badge text-bg-light border text-decoration-none d-none d-sm-inline"
            title="Manage saved locations"
          >
            <i className="bi bi-geo-alt me-1" aria-hidden="true" />
            {defaultLocation ? (defaultLocation.city || defaultLocation.name) : 'Location not set'}
          </Link>
          <button className="btn btn-light position-relative" aria-label="Notifications">
            <i className="bi bi-bell" aria-hidden="true" />
          </button>
          <div className="dropdown">
            <button
              className="btn btn-light d-flex align-items-center gap-1"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              aria-label="Profile menu"
            >
              <i className="bi bi-person-circle fs-5" aria-hidden="true" />
            </button>
            <ul className="dropdown-menu dropdown-menu-end">
              <li>
                <Link className="dropdown-item" to="/profile">
                  Profile / Settings
                </Link>
              </li>
              <li>
                <hr className="dropdown-divider" />
              </li>
              {user ? (
                <li>
                  <button type="button" className="dropdown-item text-danger" onClick={handleLogout}>
                    Log out
                  </button>
                </li>
              ) : (
                <li>
                  <Link className="dropdown-item" to="/login">
                    Log in
                  </Link>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </header>
  );
}

import { Link, useLocation } from 'react-router-dom';
import NAV_ITEMS from './navItems.js';

/**
 * Mobile/tablet top navbar.
 * Global header displays: selected city, data freshness, notifications,
 * profile menu (UI/UX spec section 5). Location/freshness become real
 * once Phase 3 wires environmental data; placeholders are labelled.
 */
export default function TopNavbar() {
  const { pathname } = useLocation();
  const currentLabel =
    NAV_ITEMS.find((i) => pathname.startsWith(i.to))?.label ?? 'AirWise AI';

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
          <span className="badge text-bg-light border d-none d-sm-inline">
            <i className="bi bi-geo-alt me-1" aria-hidden="true" />
            Location not set
          </span>
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
              <li>
                <Link className="dropdown-item" to="/login">
                  Log in
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </header>
  );
}

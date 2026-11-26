import { NavLink } from 'react-router-dom';
import NAV_ITEMS from './navItems.js';

/** Offcanvas navigation for small screens (Bootstrap 5.3 offcanvas). */
export default function MobileOffcanvasMenu() {
  return (
    <div
      className="offcanvas offcanvas-start"
      tabIndex={-1}
      id="awMobileMenu"
      aria-labelledby="awMobileMenuLabel"
    >
      <div className="offcanvas-header border-bottom">
        <h2 className="offcanvas-title" id="awMobileMenuLabel">
          AirWise AI
        </h2>
        <button
          type="button"
          className="btn-close"
          data-bs-dismiss="offcanvas"
          aria-label="Close navigation menu"
        />
      </div>
      <div className="offcanvas-body">
        <nav className="aw-nav" aria-label="Mobile navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => 'aw-nav-link' + (isActive ? ' active' : '')}
            >
              <i className={`bi ${item.icon}`} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}

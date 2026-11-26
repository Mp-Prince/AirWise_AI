import { NavLink } from 'react-router-dom';
import NAV_ITEMS from './navItems.js';

/** Desktop sidebar navigation (>= lg breakpoint). */
export default function Sidebar() {
  return (
    <nav className="aw-sidebar" aria-label="Main navigation">
      <NavLink to="/dashboard" className="aw-brand">
        <img src="/favicon.svg" alt="" width="30" height="30" />
        <span>AirWise AI</span>
      </NavLink>
      <div className="aw-nav">
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
      </div>
    </nav>
  );
}

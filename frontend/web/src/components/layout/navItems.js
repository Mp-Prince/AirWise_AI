/**
 * Single source of truth for navigation destinations, shared by the
 * desktop sidebar and the mobile offcanvas menu (UI/UX spec section 5).
 * Icons are Bootstrap Icons class names.
 */
const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: 'bi-speedometer2' },
  { to: '/planner', label: 'Daily Planner', icon: 'bi-calendar3' },
  { to: '/assistant', label: 'AI Assistant', icon: 'bi-chat-dots' },
  { to: '/recommendations', label: 'Recommendations', icon: 'bi-lightbulb' },
  { to: '/impact', label: 'Impact Tracker', icon: 'bi-graph-up-arrow' },
  { to: '/family', label: 'Family', icon: 'bi-people' },
  { to: '/profile', label: 'Profile / Settings', icon: 'bi-person-gear' },
];

export default NAV_ITEMS;

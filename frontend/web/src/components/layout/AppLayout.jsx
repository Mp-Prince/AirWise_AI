import { Outlet } from 'react-router-dom';

import Sidebar from './Sidebar.jsx';
import TopNavbar from './TopNavbar.jsx';
import MobileOffcanvasMenu from './MobileOffcanvasMenu.jsx';
import Footer from './Footer.jsx';

/**
 * Shared shell for all authenticated pages.
 * Desktop: persistent Sidebar. Mobile/tablet: TopNavbar + Offcanvas menu.
 * Nested routes render inside <Outlet/>.
 */
export default function AppLayout() {
  return (
    <div className="aw-shell">
      <Sidebar />
      <div className="aw-main">
        <TopNavbar />
        <MobileOffcanvasMenu />
        <main className="aw-content" id="main-content">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}

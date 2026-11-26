import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './providers/AuthProvider.jsx';

import AppLayout from '../components/layout/AppLayout.jsx';
import LandingPage from '../pages/LandingPage.jsx';
import LoginPage from '../pages/auth/LoginPage.jsx';
import RegisterPage from '../pages/auth/RegisterPage.jsx';
import OnboardingPage from '../pages/onboarding/OnboardingPage.jsx';
import DashboardPage from '../pages/dashboard/DashboardPage.jsx';
import DailyPlannerPage from '../pages/daily-planner/DailyPlannerPage.jsx';
import AssistantPage from '../pages/assistant/AssistantPage.jsx';
import RecommendationsPage from '../pages/recommendations/RecommendationsPage.jsx';
import ImpactTrackerPage from '../pages/impact/ImpactTrackerPage.jsx';
import FamilyPage from '../pages/family/FamilyPage.jsx';
import ProfilePage from '../pages/profile/ProfilePage.jsx';

/**
 * Auth guard component - redirects to login if not authenticated.
 * Shows loading state while auth is initializing.
 */
function RequireAuth({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: window.location.pathname }} />;
  }

  return children;
}

/**
 * Routes per .md/06_Frontend_Structure.md section 10.
 * Auth guard (RequireAuth) protects authenticated routes.
 */
export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />

      {/* Authenticated area shares the app layout */}
      <Route element={<AppLayout />}>
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/planner"
          element={
            <RequireAuth>
              <DailyPlannerPage />
            </RequireAuth>
          }
        />
        <Route
          path="/assistant"
          element={
            <RequireAuth>
              <AssistantPage />
            </RequireAuth>
          }
        />
        <Route
          path="/recommendations"
          element={
            <RequireAuth>
              <RecommendationsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/impact"
          element={
            <RequireAuth>
              <ImpactTrackerPage />
            </RequireAuth>
          }
        />
        <Route
          path="/family"
          element={
            <RequireAuth>
              <FamilyPage />
            </RequireAuth>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
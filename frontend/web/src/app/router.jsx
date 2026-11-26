import { Navigate, Route, Routes } from 'react-router-dom';

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
 * Routes per .md/06_Frontend_Structure.md section 10.
 * Auth guard (RequireAuth) becomes real in Phase 2 once login exists;
 * for Phase 0 every protected route renders its shell directly.
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
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/planner" element={<DailyPlannerPage />} />
        <Route path="/assistant" element={<AssistantPage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/impact" element={<ImpactTrackerPage />} />
        <Route path="/family" element={<FamilyPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

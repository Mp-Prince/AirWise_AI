# AirWise AI — Frontend Structure

**Framework:** React.js  
**UI:** Bootstrap 5.3  
**Icons:** Bootstrap Icons  
**Charts:** Chart.js with react-chartjs-2 (recommended)  
**Routing:** React Router  
**API client:** Axios  
**State/data fetching:** TanStack Query; local component state where sufficient  
**Mobile strategy:** Responsive mobile-first web application, optionally installable as a PWA

> This document defines only the frontend structure. The backend folder structure is intentionally left undecided, as requested.

## 1. Frontend architecture principles

- Organize by pages and reusable components.
- Keep API calls out of visual components.
- Use shared layout components.
- Use Bootstrap grid and responsive utilities.
- Use feature-specific components for complex pages.
- Keep forms, schemas and API services organized.
- Use a single shared backend for web and mobile browser access.
- Do not place API secrets in frontend environment variables.

## 2. Proposed folder structure

```text
frontend/
└── web/
    ├── public/
    │   ├── favicon.svg
    │   ├── manifest.json
    │   └── images/
    │
    ├── src/
    │   ├── app/
    │   │   ├── App.jsx
    │   │   ├── router.jsx
    │   │   └── providers/
    │   │       ├── QueryProvider.jsx
    │   │       └── AuthProvider.jsx
    │   │
    │   ├── assets/
    │   │   ├── images/
    │   │   ├── icons/
    │   │   └── fonts/
    │   │
    │   ├── components/
    │   │   ├── common/
    │   │   │   ├── PageHeader.jsx
    │   │   │   ├── LoadingSpinner.jsx
    │   │   │   ├── EmptyState.jsx
    │   │   │   ├── ErrorAlert.jsx
    │   │   │   ├── ConfirmDialog.jsx
    │   │   │   └── DataFreshnessLabel.jsx
    │   │   │
    │   │   ├── layout/
    │   │   │   ├── AppLayout.jsx
    │   │   │   ├── Sidebar.jsx
    │   │   │   ├── TopNavbar.jsx
    │   │   │   ├── MobileOffcanvasMenu.jsx
    │   │   │   └── Footer.jsx
    │   │   │
    │   │   └── charts/
    │   │       ├── AQITrendChart.jsx
    │   │       ├── ImpactTrendChart.jsx
    │   │       └── ActivityBreakdownChart.jsx
    │   │
    │   ├── pages/
    │   │   ├── auth/
    │   │   │   ├── LoginPage.jsx
    │   │   │   ├── RegisterPage.jsx
    │   │   │   └── ForgotPasswordPage.jsx
    │   │   │
    │   │   ├── onboarding/
    │   │   │   └── OnboardingPage.jsx
    │   │   │
    │   │   ├── dashboard/
    │   │   │   ├── DashboardPage.jsx
    │   │   │   └── components/
    │   │   │       ├── WelcomeSection.jsx
    │   │   │       ├── LocationSelector.jsx
    │   │   │       ├── AQIOverviewCard.jsx
    │   │   │       ├── PollutantSummary.jsx
    │   │   │       ├── WeatherSummaryCard.jsx
    │   │   │       ├── TodayRecommendations.jsx
    │   │   │       ├── TodayRoutinePreview.jsx
    │   │   │       ├── WeeklyImpactSummary.jsx
    │   │   │       └── AQITrendSection.jsx
    │   │   │
    │   │   ├── daily-planner/
    │   │   │   ├── DailyPlannerPage.jsx
    │   │   │   └── components/
    │   │   │       ├── PlannerToolbar.jsx
    │   │   │       ├── PlannerCalendar.jsx
    │   │   │       ├── PlannerAgenda.jsx
    │   │   │       ├── PlannerFilters.jsx
    │   │   │       ├── RoutineEventCard.jsx
    │   │   │       ├── AddEventModal.jsx
    │   │   │       └── EditEventModal.jsx
    │   │   │
    │   │   ├── assistant/
    │   │   │   ├── AssistantPage.jsx
    │   │   │   └── components/
    │   │   │       ├── ConversationSidebar.jsx
    │   │   │       ├── ChatWindow.jsx
    │   │   │       ├── ChatMessage.jsx
    │   │   │       ├── ChatComposer.jsx
    │   │   │       ├── SuggestedPrompts.jsx
    │   │   │       └── SourceCitationList.jsx
    │   │   │
    │   │   ├── recommendations/
    │   │   │   ├── RecommendationsPage.jsx
    │   │   │   └── components/
    │   │   │       ├── RecommendationCard.jsx
    │   │   │       ├── RecommendationFilters.jsx
    │   │   │       └── RecommendationDetailsModal.jsx
    │   │   │
    │   │   ├── impact/
    │   │   │   ├── ImpactTrackerPage.jsx
    │   │   │   └── components/
    │   │   │       ├── ImpactMetricCard.jsx
    │   │   │       ├── ImpactDateFilter.jsx
    │   │   │       ├── ImpactBreakdown.jsx
    │   │   │       └── CalculationDetailsModal.jsx
    │   │   │
    │   │   ├── family/
    │   │   │   ├── FamilyPage.jsx
    │   │   │   └── components/
    │   │   │       ├── FamilyOverview.jsx
    │   │   │       ├── FamilyMemberList.jsx
    │   │   │       ├── InviteMemberModal.jsx
    │   │   │       ├── FamilyGoalCard.jsx
    │   │   │       └── FamilyProgress.jsx
    │   │   │
    │   │   └── profile/
    │   │       ├── ProfilePage.jsx
    │   │       └── components/
    │   │           ├── ProfileForm.jsx
    │   │           ├── LocationPreferences.jsx
    │   │           ├── LifestylePreferences.jsx
    │   │           ├── NotificationSettings.jsx
    │   │           └── PrivacySettings.jsx
    │   │
    │   ├── services/
    │   │   ├── apiClient.js
    │   │   ├── authService.js
    │   │   ├── userService.js
    │   │   ├── locationService.js
    │   │   ├── airQualityService.js
    │   │   ├── weatherService.js
    │   │   ├── routineService.js
    │   │   ├── assistantService.js
    │   │   ├── recommendationService.js
    │   │   ├── impactService.js
    │   │   └── familyService.js
    │   │
    │   ├── hooks/
    │   │   ├── useAuth.js
    │   │   ├── useCurrentLocation.js
    │   │   ├── useAirQuality.js
    │   │   ├── useDailyRoutines.js
    │   │   └── useImpactSummary.js
    │   │
    │   ├── utils/
    │   │   ├── dateUtils.js
    │   │   ├── numberFormatters.js
    │   │   ├── validators.js
    │   │   └── aqiLabels.js
    │   │
    │   ├── styles/
    │   │   ├── variables.css
    │   │   ├── global.css
    │   │   ├── layout.css
    │   │   └── responsive.css
    │   │
    │   └── main.jsx
    │
    ├── .env.example
    ├── package.json
    └── README.md
```

## 3. Dashboard page — component breakdown

`DashboardPage.jsx` composes the following components:

| Component | Displays | Actions |
|---|---|---|
| `WelcomeSection` | Greeting and date | None |
| `LocationSelector` | Selected city/area | Change location |
| `AQIOverviewCard` | AQI, category, standard and timestamp | View details, refresh |
| `PollutantSummary` | PM2.5, PM10 and available pollutants | View pollutant details |
| `WeatherSummaryCard` | Temperature, humidity and wind | None |
| `TodayRecommendations` | Top recommendations | View all, add to planner |
| `TodayRoutinePreview` | Today's scheduled events | Open planner, mark complete |
| `WeeklyImpactSummary` | Estimated CO2e and other metrics | Open impact tracker |
| `AQITrendSection` | Historical AQI chart | Change time range |

Suggested responsive grid:
- Top row: AQI overview, weather and weekly impact.
- Middle row: recommendations and today's routines.
- Bottom row: AQI trend.

Use Bootstrap classes such as `row g-3`, `col-12 col-xl-5`, `col-12 col-md-6 col-xl-3` and `col-12 col-xl-4`.

## 4. Daily Planner page — component breakdown

`DailyPlannerPage.jsx`:

| Component | Responsibility |
|---|---|
| `PlannerToolbar` | Date navigation, Today and Add Event |
| `PlannerCalendar` | Month/week/day calendar on suitable screens |
| `PlannerAgenda` | Mobile-friendly event list |
| `PlannerFilters` | Filter by event category/status |
| `RoutineEventCard` | Show event details and completion |
| `AddEventModal` | Create an event |
| `EditEventModal` | Update an existing event |

### Add Event modal fields

- Event title.
- Date.
- Start time.
- End time.
- Category.
- Description.
- Reminder preference.

### Event actions

- Save Event.
- Cancel.
- Edit.
- Delete.
- Mark Complete.
- Add to AI-generated routine.

Use a calendar library only if needed. Evaluate FullCalendar's React integration and its licence for the required features: https://fullcalendar.io/docs/react. For a small MVP, a custom Bootstrap agenda plus a date picker may be sufficient.

## 5. AI Assistant page — component breakdown

`AssistantPage.jsx`:

- `ConversationSidebar`: previous conversations and New Chat.
- `ChatWindow`: message history.
- `ChatMessage`: user/assistant message display.
- `ChatComposer`: text input and Send.
- `SuggestedPrompts`: example questions.
- `SourceCitationList`: supporting documents and links.

The page should show a data timestamp when live AQI context is used. If no current data was retrieved, make that clear.

## 6. Impact Tracker page — component breakdown

`ImpactTrackerPage.jsx`:

- `ImpactMetricCard`: CO2e, fuel, electricity or waste metrics.
- `ImpactDateFilter`: date range.
- `ImpactTrendChart`: historical trend.
- `ImpactBreakdown`: activity categories.
- `CalculationDetailsModal`: factors, units and assumptions.

## 7. Recommendations page — component breakdown

`RecommendationsPage.jsx`:

- `RecommendationFilters`
- `RecommendationCard`
- `RecommendationDetailsModal`

Each card should contain:
- Title.
- Category.
- Priority.
- Suggested action.
- Why it is relevant.
- Expected benefit.
- Source references.
- Add to Planner and Mark Done actions.

## 8. Family page — component breakdown

`FamilyPage.jsx`:

- `FamilyOverview`
- `FamilyMemberList`
- `InviteMemberModal`
- `FamilyGoalCard`
- `FamilyProgress`

Display only information the signed-in user is authorized to see.

## 9. Shared layout

`AppLayout.jsx` should contain:
- `TopNavbar`
- `Sidebar` for desktop.
- `MobileOffcanvasMenu` for small screens.
- Main page outlet.
- Optional footer.

Use React Router nested routes so authenticated pages share the same layout.

## 10. Suggested routes

| Route | Page |
|---|---|
| `/login` | Login |
| `/register` | Register |
| `/onboarding` | Onboarding |
| `/dashboard` | Dashboard |
| `/planner` | Daily Planner |
| `/assistant` | AI Assistant |
| `/recommendations` | Recommendations |
| `/impact` | Impact Tracker |
| `/family` | Family |
| `/profile` | Profile and Settings |

## 11. Frontend packages

Suggested dependencies:

```bash
npm install react-router-dom axios
npm install bootstrap bootstrap-icons
npm install @tanstack/react-query
npm install chart.js react-chartjs-2
npm install react-hook-form
```

Optional:
- `zod` for schema validation.
- `date-fns` for date formatting.
- FullCalendar React packages if a full calendar UI is required.
- A PWA plugin such as `vite-plugin-pwa` if the app uses Vite.

## 12. Bootstrap setup

In `main.jsx`:

```javascript
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './styles/global.css';
```

Use Bootstrap components and classes consistently. Avoid mixing Tailwind CSS into the application.

## 13. Responsive design behaviour

| Screen width | Layout behaviour |
|---|---|
| Small mobile | One-column cards, offcanvas menu, agenda planner |
| Large mobile | One-column or compact two-column cards |
| Tablet | Two-column dashboard where suitable |
| Desktop | Sidebar and multi-column dashboard |
| Wide desktop | Wider content with readable maximum widths |

Use Bootstrap breakpoints (`sm`, `md`, `lg`, `xl`, `xxl`) rather than fixed pixel positioning.

## 14. Frontend completion criteria

- Every page has loading, empty and error states.
- Every visible button performs a real action.
- All forms have validation.
- All protected routes require authentication.
- API calls are handled through service modules.
- Layout works on mobile, tablet and desktop.
- AQI data freshness is visible.
- Impact figures show their units and estimated/measured status.
- Family-only information is protected by backend authorization.

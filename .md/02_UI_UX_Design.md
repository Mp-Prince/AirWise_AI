# AirWise AI — UI/UX Design Specification

**Frontend:** React.js + Bootstrap 5  
**Responsive targets:** Mobile, tablet and desktop  
**Design approach:** Mobile-first, accessible, simple and action-oriented

## 1. Product design goals

1. Show the air-quality situation clearly without overwhelming users.
2. Turn environmental information into practical next steps.
3. Make sustainable actions easy to discover and record.
4. Explain why recommendations are shown and what impact they may have.
5. Support individual use first, with optional family collaboration.
6. Work well on narrow mobile screens using Bootstrap responsive utilities.

## 2. Visual identity

### Suggested product identity

**AirWise AI**  
*Smarter choices for cleaner air.*

### Colour palette

| Token | Suggested colour | Use |
|---|---|---|
| Primary | `#176B5B` | Main actions, navigation highlights |
| Primary dark | `#104B41` | Hover and emphasis |
| Secondary | `#2F6F9F` | Information and links |
| Accent | `#E5A93D` | Highlights and progress |
| Background | `#F5F8F7` | Page background |
| Surface | `#FFFFFF` | Cards and panels |
| Text | `#1F2933` | Main text |
| Muted text | `#64748B` | Supporting text |
| Danger | `#B42318` | Severe warnings |
| Warning | `#A15C00` | Caution |
| Success | `#18794E` | Completed actions |

Do not communicate AQI severity through colour alone. Always include a text category, number and accessible icon/label.

## 3. Typography and spacing

- Use Bootstrap's system font stack or a readable web font such as Inter.
- Page title: approximately 1.5–2rem depending on viewport.
- Section heading: approximately 1.1–1.25rem.
- Body text: 16px default.
- Supporting text: no smaller than 13–14px where practical.
- Use Bootstrap spacing utilities consistently: `p-3`, `p-4`, `mb-3`, `g-3`.
- Cards should have consistent padding, subtle borders and modest corner radius.

## 4. Responsive layout rules

### Desktop (large screens)
- Sidebar navigation: approximately 240–260px.
- Main content uses a Bootstrap `.container-fluid`.
- Dashboard cards use a 12-column grid.
- Two-column layouts for planner and impact details.

### Tablet
- Sidebar collapses to an offcanvas menu.
- Dashboard cards use two columns where space allows.
- Forms and charts use full available width.

### Mobile
- Use a top navbar with a menu button.
- Use Bootstrap Offcanvas for navigation.
- Stack cards in one column.
- Make primary buttons full width when useful.
- Use a bottom navigation bar only for the most frequent destinations if usability testing supports it.
- Calendars should switch to agenda/list mode on narrow screens.
- Tables should become responsive cards or use `.table-responsive`.

## 5. Global application shell

### Main navigation

Desktop sidebar:
- Dashboard
- Daily Planner
- AI Assistant
- Recommendations
- Impact Tracker
- Family
- Profile / Settings

Mobile:
- Brand and menu button in top navbar.
- Offcanvas navigation containing the same destinations.
- Persistent, easy-to-reach primary action for the AI assistant if appropriate.

### Global header

Display:
- Current selected city/area.
- Data freshness or last updated time.
- Notification icon.
- User profile menu.

Do not imply precise location access unless the user has granted permission.

## 6. Screen-by-screen UI specification

### 6.1 Login and registration

**Layout**
- Centered responsive authentication card.
- AirWise AI logo and short value proposition.
- Email and password fields.
- Primary sign-in button.
- Link to registration and password recovery.

**Registration fields**
- Full name.
- Email.
- Password.
- Confirm password.
- Consent checkbox for terms/privacy.

Do not ask for precise location during account creation. Ask for a city or location preference during onboarding.

### 6.2 Onboarding

Use a short stepper:

1. Basic profile.
2. City/state selection.
3. Lifestyle and travel habits.
4. Sustainability goal.
5. Optional family group setup.

Show a skip option for optional questions. Explain why each requested detail improves recommendations.

### 6.3 Dashboard

**Top section**
- Greeting and selected location.
- Current AQI card with category and standard.
- Observation timestamp and data source.
- Weather summary.

**Main components**
- AQI overview card.
- Pollutant cards: PM2.5, PM10 and available pollutants.
- Today's recommended actions.
- Daily planner preview.
- Weekly estimated impact summary.
- Air-quality trend chart.
- Quick actions: Ask AI, Add activity, View planner.

Suggested Bootstrap layout:
- AQI overview: `col-12 col-xl-5`
- Weather: `col-12 col-md-6 col-xl-3`
- Weekly impact: `col-12 col-md-6 col-xl-4`
- Recommendations and charts: responsive `col-12 col-lg-6`

### 6.4 Daily Planner

**Main components**
- Calendar with month/week/day or agenda view.
- Date navigation.
- Add Event button.
- Today's event list.
- Routine category filters.
- Completion checkboxes.
- Edit and delete actions.

Event categories:
- Low-emission travel.
- Indoor air quality.
- Energy saving.
- Waste reduction.
- Personal routine.

Add Event form:
- Event title.
- Date.
- Start and end time.
- Category.
- Description.
- Optional reminder.
- Save and Cancel buttons.

On mobile, default to an agenda/list view; do not force a tiny month calendar.

### 6.5 AI Assistant

**Layout**
- Conversation history panel on desktop.
- Chat message area.
- Input field and Send button.
- Suggested question chips.
- Source citations beneath relevant answers.
- Optional "Add to planner" action for suitable recommendations.

The assistant should show:
- Whether live AQI data was available.
- Data timestamp.
- Source documents used.
- Estimated versus measured impact labels.

### 6.6 Recommendations

Components:
- Recommendation cards.
- Category filter.
- Priority label.
- Why this is recommended.
- Expected benefit and assumptions.
- Source references.
- Mark as done.
- Add to planner.
- Dismiss or save for later.

### 6.7 Impact Tracker

Components:
- Date-range filter.
- CO2e avoided summary.
- Fuel saved, electricity saved and waste reduced where available.
- Daily/weekly/monthly chart.
- Activity breakdown.
- Calculation method and assumptions.
- Estimated/measured status.

Never combine unrelated metrics into a single unqualified "pollution reduced" number.

### 6.8 Family Dashboard

Components:
- Family name and member list.
- Invite member action.
- Family goal cards.
- Shared completed activities.
- Family progress chart.
- Member permissions.

Personal conversations and private profile details must not be shown to family members by default.

### 6.9 Profile and Settings

Sections:
- Personal information.
- City and location preferences.
- Travel and lifestyle preferences.
- Sustainability goals.
- Notification settings.
- Privacy and consent.
- Family memberships.
- Account deletion/export options.

## 7. Reusable UI components

- `AQIStatusCard`
- `PollutantCard`
- `WeatherSummaryCard`
- `RecommendationCard`
- `RoutineCalendar`
- `RoutineEventCard`
- `AddEventModal`
- `ChatMessage`
- `ChatComposer`
- `SourceCitationList`
- `ImpactMetricCard`
- `ImpactTrendChart`
- `FamilyMemberCard`
- `EmptyState`
- `LoadingSkeleton`
- `DataFreshnessLabel`
- `ErrorAlert`

## 8. UX states required on every data-driven screen

Design all of the following:
- Loading state.
- Empty state.
- API error state.
- Partial data state.
- Stale data state.
- Permission denied state.
- Offline state where applicable.
- Successful save/update state.

## 9. Accessibility

- Use semantic HTML and correct heading order.
- Ensure keyboard navigation and visible focus.
- Add labels to all form controls.
- Provide text labels alongside status colours.
- Use sufficient colour contrast.
- Give charts text summaries or accessible data tables.
- Ensure touch targets are comfortably usable on mobile.
- Respect reduced-motion preferences.

## 10. Bootstrap implementation conventions

Use Bootstrap 5.3:
- Grid: `.container-fluid`, `.row`, `.col-*`, `.g-*`.
- Navigation: Navbar, Offcanvas, Nav.
- Forms: Form Control, Form Select, Form Check.
- Dialogs: Modal.
- Feedback: Alert, Toast, Spinner, Placeholder.
- Layout: Card, Accordion, Dropdown, Tabs.
- Tables: `.table-responsive`.

Use Bootstrap Icons if an icon library is needed. Avoid mixing multiple UI frameworks.

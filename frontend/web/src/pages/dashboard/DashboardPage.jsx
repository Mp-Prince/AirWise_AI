import PageHeader from '../../components/common/PageHeader.jsx';
import DataFreshnessLabel from '../../components/common/DataFreshnessLabel.jsx';
import AQIHero from './components/AQIHero.jsx';
import WeatherCard from './components/WeatherCard.jsx';

/**
 * Dashboard (page workflows doc, section 4): AQI hero, health advisory,
 * trend chart, today's plan, recommendations, impact summary.
 * Phase 3: Real data from OpenAQ and OpenWeatherMap via backend.
 */
export default function DashboardPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Dashboard"
        subtitle="Air quality and health guidance for today."
        actions={<DataFreshnessLabel fetchedAt={null} />}
      />

      <div className="row g-3 g-lg-4">
        <div className="col-12 col-lg-8">
          <AQIHero />
          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <h2 className="section-heading">24-hour trend</h2>
              <p className="text-supporting mb-0">
                AQI over the last 24 hours will render here (Chart.js), never estimated when the provider has no reading.
              </p>
            </div>
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <WeatherCard />
          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <h2 className="section-heading">Today's plan</h2>
              <p className="text-supporting mb-0">
                Your routine hours marked safe / caution / avoid — from the Daily Planner.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

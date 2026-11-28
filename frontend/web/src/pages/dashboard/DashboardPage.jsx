import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import DataFreshnessLabel from '../../components/common/DataFreshnessLabel.jsx';
import routineService from '../../services/routineService.js';
import recommendationService from '../../services/recommendationService.js';
import AQIHero from './components/AQIHero.jsx';
import WeatherCard from './components/WeatherCard.jsx';

const BAND_BADGE = {
  safe: 'text-bg-success',
  caution: 'text-bg-warning',
  avoid: 'text-bg-danger',
  unknown: 'text-bg-secondary',
};

/**
 * Dashboard (page workflows doc, section 4): AQI hero, health advisory,
 * today's plan preview, today's recommendations, and weather card.
 */
export default function DashboardPage() {
  const { user } = useAuth();
  const [freshness, setFreshness] = useState({ fetchedAt: null, source: null });
  const [todayRoutines, setTodayRoutines] = useState([]);
  const [todayRecs, setTodayRecs] = useState([]);

  const handleDataLoaded = useCallback(({ reading }) => {
    if (reading) {
      setFreshness({ fetchedAt: reading.measured_at, source: reading.provider });
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    const today = new Date().toISOString().slice(0, 10);
    Promise.allSettled([
      routineService.listRoutines({ date: today }),
      recommendationService.getTodayRecommendations(),
    ]).then(([routineRes, recRes]) => {
      if (routineRes.status === 'fulfilled') {
        setTodayRoutines(routineRes.value.routines || []);
      }
      if (recRes.status === 'fulfilled') {
        setTodayRecs((recRes.value.recommendations || []).slice(0, 3));
      }
    });
  }, [user]);

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Dashboard"
        subtitle="Air quality and health guidance for today."
        actions={<DataFreshnessLabel fetchedAt={freshness.fetchedAt} source={freshness.source} />}
      />

      <div className="row g-3 g-lg-4">
        <div className="col-12 col-lg-8">
          <AQIHero onDataLoaded={handleDataLoaded} />
          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="section-heading mb-0">Today's recommendations</h2>
                <Link to="/recommendations" className="small text-decoration-none">
                  View all
                </Link>
              </div>
              {todayRecs.length === 0 ? (
                <p className="text-supporting mb-0">
                  Open Recommendations to generate tailored health and eco actions.
                </p>
              ) : (
                <ul className="list-group list-group-flush">
                  {todayRecs.map((rec) => (
                    <li key={rec.id} className="list-group-item px-0">
                      <div className="d-flex justify-content-between align-items-center gap-2">
                        <strong className="small">{rec.title}</strong>
                        <span className="badge text-bg-light border">{rec.category}</span>
                      </div>
                      <div className="small text-supporting">{rec.description}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <WeatherCard />
          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="section-heading mb-0">Today's plan</h2>
                <Link to="/planner" className="small text-decoration-none">
                  Open planner
                </Link>
              </div>
              {todayRoutines.length === 0 ? (
                <p className="text-supporting mb-0">
                  No activities scheduled for today yet. Add commute or exercise blocks in Daily Planner.
                </p>
              ) : (
                <ul className="list-group list-group-flush">
                  {todayRoutines.slice(0, 4).map((ev) => (
                    <li key={ev.id} className="list-group-item px-0 d-flex justify-content-between align-items-center gap-2">
                      <div className="text-truncate">
                        <div className="small fw-semibold text-truncate">{ev.name}</div>
                        <div className="small text-muted">
                          {String(ev.start_time).slice(0, 5)}–{String(ev.end_time).slice(0, 5)}
                        </div>
                      </div>
                      <span className={`badge ${BAND_BADGE[ev.safety_band] || 'text-bg-secondary'}`}>
                        {ev.safety_band}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

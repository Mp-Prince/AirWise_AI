import { useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider.jsx';
import environmentalApi from '../../../services/environmentalApi';
import DataFreshnessLabel from '../../../components/common/DataFreshnessLabel.jsx';

/**
 * AQI Hero card - shows current AQI with category, color, and health advisory.
 * Fetches real data from backend via environmentalApi.
 */
export default function AQIHero() {
  const { user } = useAuth();
  const [aqiData, setAqiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAQI = async () => {
    if (!user) return;
    try {
      setLoading(true);
      // First get default location
      const locations = await environmentalApi.getLocations();
      const defaultLocation = locations.locations.find(l => l.is_default) || locations.locations[0];

      if (!defaultLocation) {
        setAqiData(null);
        return;
      }

      // Fetch AQI info
      const aqiInfo = await environmentalApi.getCurrentAQIInfo(defaultLocation.id);
      setAqiData(aqiInfo);
      setError(null);
    } catch (err) {
      setError('Failed to load air quality data');
      setAqiData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAQI();
  }, [user]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAQI();
  };

  if (loading) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading AQI...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !aqiData) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-5">
          <svg className="bi text-muted mb-3" width="48" height="48"><use xlinkHref="#exclamation-triangle" /></svg>
          <h5 className="text-body-secondary">No air quality data yet</h5>
          <p className="text-supporting small mb-3">
            {error || 'Add a location in onboarding to see live AQI from OpenAQ.'}
          </p>
          <button
            className="btn btn-outline-primary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Retry'}
          </button>
        </div>
      </div>
    );
  }

  const { reading, aqi_info, data_age_minutes, is_stale } = aqiData;
  const { category, color, health_advisory } = aqi_info;

  return (
    <div className="card shadow-sm">
      <div className="card-body">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-3">
          <div>
            <h2 className="section-heading mb-1">Current Air Quality</h2>
            <DataFreshnessLabel fetchedAt={reading?.measured_at} />
          </div>
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
            ) : (
              'Refresh'
            )}
          </button>
        </div>

        <div className="row align-items-center g-3">
          <div className="col-12 col-md-4 text-center text-md-start">
            <div
              className="aqi-value d-inline-flex align-items-center justify-content-center rounded-circle"
              style={{
                width: '120px',
                height: '120px',
                backgroundColor: color,
                color: '#fff',
                fontSize: '3rem',
                fontWeight: 700,
                boxShadow: `0 4px 12px ${color}66`,
              }}
              role="img"
              aria-label={`AQI ${reading.aqi_value}, ${category}`}
            >
              {reading.aqi_value}
            </div>
            <div className="mt-2">
              <span
                className="badge fs-6 px-3 py-2"
                style={{ backgroundColor: color }}
              >
                {category}
              </span>
              <div className="text-supporting small mt-1">
                {reading.aqi_standard} • {reading.provider}
              </div>
            </div>
          </div>

          <div className="col-12 col-md-8">
            <h5 className="mb-2">Health Advisory</h5>
            <div className="alert" style={{ backgroundColor: `${color}15`, borderLeft: `4px solid ${color}` }}>
              <p className="mb-0">{health_advisory}</p>
            </div>

            <div className="row g-3 mt-3">
              {reading.pm25 !== null && reading.pm25 !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <div className="text-supporting small">PM2.5</div>
                    <div className="fw-bold">{reading.pm25} µg/m³</div>
                  </div>
                </div>
              )}
              {reading.pm10 !== null && reading.pm10 !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <div className="text-supporting small">PM10</div>
                    <div className="fw-bold">{reading.pm10} µg/m³</div>
                  </div>
                </div>
              )}
              {reading.o3 !== null && reading.o3 !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <div className="text-supporting small">O₃</div>
                    <div className="fw-bold">{reading.o3} µg/m³</div>
                  </div>
                </div>
              )}
              {reading.no2 !== null && reading.no2 !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <div className="text-supporting small">NO₂</div>
                    <div className="fw-bold">{reading.no2} µg/m³</div>
                  </div>
                </div>
              )}
            </div>

            {is_stale && (
              <div className="alert alert-warning mt-3 mb-0 small">
                <svg className="bi me-1" width="16" height="16"><use xlinkHref="#exclamation-triangle" /></svg>
                Data is {data_age_minutes} minutes old — consider refreshing for latest readings.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
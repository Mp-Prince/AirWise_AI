import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider.jsx';
import environmentalApi from '../../../services/environmentalApi';
import DataFreshnessLabel from '../../../components/common/DataFreshnessLabel.jsx';

/**
 * AQI Hero card - shows current AQI with category, color, and health advisory.
 * Fetches real data from backend via environmentalApi and triggers OpenAQ sync on refresh.
 */
export default function AQIHero({ onDataLoaded }) {
  const { user } = useAuth();
  const [location, setLocation] = useState(null);
  const [aqiData, setAqiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAQI = useCallback(async (forceSync = false) => {
    if (!user) return;
    try {
      if (!forceSync) setLoading(true);
      const locations = await environmentalApi.getLocations();
      const defaultLocation =
        locations.locations.find((l) => l.is_default) || locations.locations[0];

      if (!defaultLocation) {
        setLocation(null);
        setAqiData(null);
        setError(null);
        return;
      }

      setLocation(defaultLocation);

      if (forceSync) {
        await environmentalApi.syncAQIData(defaultLocation.id);
      }

      const aqiInfo = await environmentalApi.getCurrentAQIInfo(defaultLocation.id);
      setAqiData(aqiInfo);
      setError(null);
      if (onDataLoaded) {
        onDataLoaded({ location: defaultLocation, reading: aqiInfo.reading });
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to load air quality data. Try refreshing.',
      );
      setAqiData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user, onDataLoaded]);

  useEffect(() => {
    fetchAQI(false);
  }, [fetchAQI]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAQI(true);
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

  if (!location) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-5">
          <i className="bi bi-geo-alt text-muted fs-1 d-block mb-2" aria-hidden="true" />
          <h5 className="text-body-secondary">No location selected</h5>
          <p className="text-supporting small mb-3">
            Add a home city to see live air quality readings from OpenAQ.
          </p>
          <Link to="/profile" className="btn btn-primary btn-sm">
            Set location
          </Link>
        </div>
      </div>
    );
  }

  if (error || !aqiData) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-5">
          <i className="bi bi-exclamation-triangle text-warning fs-1 d-block mb-2" aria-hidden="true" />
          <h5 className="text-body-secondary">Air quality data unavailable</h5>
          <p className="text-supporting small mb-1">
            Location: <strong>{location.name}</strong>
          </p>
          <p className="text-supporting small mb-3">
            {error || 'No recent OpenAQ readings found near this location.'}
          </p>
          <button
            className="btn btn-outline-primary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Syncing...' : 'Sync OpenAQ Now'}
          </button>
        </div>
      </div>
    );
  }

  const { reading, aqi_info, data_age_minutes, is_stale } = aqiData;
  const { category, color, health_advisory } = aqi_info;

  const pollutants = [
    { label: 'PM2.5', value: reading.pm25, unit: 'µg/m³' },
    { label: 'PM10', value: reading.pm10, unit: 'µg/m³' },
    { label: 'O₃', value: reading.o3, unit: 'µg/m³' },
    { label: 'NO₂', value: reading.no2, unit: 'µg/m³' },
    { label: 'SO₂', value: reading.so2, unit: 'µg/m³' },
    { label: 'CO', value: reading.co, unit: 'mg/m³' },
  ].filter((p) => p.value !== null && p.value !== undefined);

  return (
    <div className="card shadow-sm">
      <div className="card-body">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-3">
          <div>
            <h2 className="section-heading mb-1">
              Current Air Quality · <span className="text-primary">{location.city || location.name}</span>
            </h2>
            <DataFreshnessLabel fetchedAt={reading?.measured_at} source={reading?.provider} />
          </div>
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <>
                <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
                Syncing...
              </>
            ) : (
              <>
                <i className="bi bi-arrow-clockwise me-1" aria-hidden="true" />
                Refresh
              </>
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

            {pollutants.length > 0 && (
              <div className="row g-2 mt-2">
                {pollutants.map((p) => (
                  <div className="col-6 col-lg-4" key={p.label}>
                    <div className="bg-light rounded p-2 text-center">
                      <div className="text-supporting small">{p.label}</div>
                      <div className="fw-bold">{p.value} {p.unit}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {is_stale && (
              <div className="alert alert-warning mt-3 mb-0 small">
                <i className="bi bi-exclamation-triangle me-1" aria-hidden="true" />
                Data is {data_age_minutes} minutes old — click Refresh to check for newer readings.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
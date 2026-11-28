import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider.jsx';
import environmentalApi from '../../../services/environmentalApi';
import DataFreshnessLabel from '../../../components/common/DataFreshnessLabel.jsx';

/**
 * Weather card - shows current weather with description and UV advisory.
 * Fetches real data from backend via environmentalApi and triggers sync on refresh.
 */
export default function WeatherCard() {
  const { user } = useAuth();
  const [location, setLocation] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchWeather = useCallback(async (forceSync = false) => {
    if (!user) return;
    try {
      if (!forceSync) setLoading(true);
      const locations = await environmentalApi.getLocations();
      const defaultLocation =
        locations.locations.find((l) => l.is_default) || locations.locations[0];

      if (!defaultLocation) {
        setLocation(null);
        setWeatherData(null);
        setError(null);
        return;
      }

      setLocation(defaultLocation);

      if (forceSync) {
        await environmentalApi.syncWeatherData(defaultLocation.id);
      }

      const weatherInfo = await environmentalApi.getCurrentWeatherInfo(defaultLocation.id);
      setWeatherData(weatherInfo);
      setError(null);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to load weather data. Try refreshing.',
      );
      setWeatherData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user]);

  useEffect(() => {
    fetchWeather(false);
  }, [fetchWeather]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchWeather(true);
  };

  if (loading) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-4">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading weather...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!location) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-4">
          <i className="bi bi-cloud-slash text-muted fs-2 d-block mb-2" aria-hidden="true" />
          <h6 className="text-body-secondary">No location selected</h6>
          <p className="text-supporting small mb-2">
            Add a location to see live weather conditions.
          </p>
          <Link to="/profile" className="btn btn-outline-primary btn-sm">
            Set location
          </Link>
        </div>
      </div>
    );
  }

  if (error || !weatherData) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-4">
          <i className="bi bi-cloud-slash text-muted fs-2 d-block mb-2" aria-hidden="true" />
          <h6 className="text-body-secondary">Weather data unavailable</h6>
          <p className="text-supporting small mb-2">
            {error || 'No weather readings available yet.'}
          </p>
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Syncing...' : 'Sync Weather'}
          </button>
        </div>
      </div>
    );
  }

  const { reading, weather_info, data_age_minutes, is_stale } = weatherData;
  const { description, uv_advisory } = weather_info;

  const getWeatherIcon = (code) => {
    const icons = {
      0: 'bi-sun',
      1: 'bi-sun-fill',
      2: 'bi-cloud-sun',
      3: 'bi-clouds',
      45: 'bi-cloud-fog',
      48: 'bi-cloud-fog2',
      51: 'bi-cloud-drizzle',
      53: 'bi-cloud-drizzle',
      55: 'bi-cloud-drizzle',
      61: 'bi-cloud-rain',
      63: 'bi-cloud-rain',
      65: 'bi-cloud-rain',
      71: 'bi-cloud-snow',
      73: 'bi-cloud-snow',
      75: 'bi-cloud-snow',
      95: 'bi-cloud-lightning',
    };
    return icons[code] || 'bi-cloud';
  };

  return (
    <div className="card shadow-sm">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start gap-2 mb-3">
          <div>
            <h2 className="section-heading mb-1">Current Weather</h2>
            <DataFreshnessLabel fetchedAt={reading?.measured_at} source={reading?.provider} />
          </div>
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
            ) : (
              <i className="bi bi-arrow-clockwise" aria-hidden="true" />
            )}
          </button>
        </div>

        <div className="d-flex align-items-center gap-3 mb-3">
          <i
            className={`bi ${getWeatherIcon(reading.weather_code)} text-primary`}
            style={{ fontSize: '2.5rem' }}
            aria-label={description}
          />
          <div>
            <div className="fs-3 fw-bold lh-1">
              {reading.temperature_c !== null && reading.temperature_c !== undefined
                ? `${Math.round(reading.temperature_c)}°C`
                : '—'}
            </div>
            <div className="text-supporting small">{description}</div>
          </div>
        </div>

        <div className="row g-2">
          {reading.humidity_pct !== null && reading.humidity_pct !== undefined && (
            <div className="col-6">
              <div className="bg-light rounded p-2 text-center">
                <i className="bi bi-droplet text-secondary me-1" aria-hidden="true" />
                <span className="fw-bold">{reading.humidity_pct}%</span>
                <div className="text-supporting small">Humidity</div>
              </div>
            </div>
          )}
          {reading.wind_speed_ms !== null && reading.wind_speed_ms !== undefined && (
            <div className="col-6">
              <div className="bg-light rounded p-2 text-center">
                <i className="bi bi-wind text-secondary me-1" aria-hidden="true" />
                <span className="fw-bold">{reading.wind_speed_ms} m/s</span>
                <div className="text-supporting small">Wind</div>
              </div>
            </div>
          )}
          {reading.pressure_hpa !== null && reading.pressure_hpa !== undefined && (
            <div className="col-6">
              <div className="bg-light rounded p-2 text-center">
                <i className="bi bi-speedometer2 text-secondary me-1" aria-hidden="true" />
                <span className="fw-bold">{reading.pressure_hpa} hPa</span>
                <div className="text-supporting small">Pressure</div>
              </div>
            </div>
          )}
          {reading.uv_index !== null && reading.uv_index !== undefined && (
            <div className="col-6">
              <div className="bg-light rounded p-2 text-center">
                <i className="bi bi-sun text-secondary me-1" aria-hidden="true" />
                <span className="fw-bold">{reading.uv_index}</span>
                <div className="text-supporting small">UV Index</div>
              </div>
            </div>
          )}
        </div>

        {uv_advisory && reading.uv_index !== null && reading.uv_index !== undefined && (
          <div className="alert alert-info mt-3 mb-0 small">
            <i className="bi bi-info-circle me-1" aria-hidden="true" />
            <strong>UV Advisory:</strong> {uv_advisory}
          </div>
        )}

        {is_stale && (
          <div className="alert alert-warning mt-3 mb-0 small">
            <i className="bi bi-exclamation-triangle me-1" aria-hidden="true" />
            Data is {data_age_minutes} minutes old — click refresh for latest readings.
          </div>
        )}
      </div>
    </div>
  );
}
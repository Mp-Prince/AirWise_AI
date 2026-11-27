import { useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider.jsx';
import environmentalApi from '../../../services/environmentalApi';
import DataFreshnessLabel from '../../../components/common/DataFreshnessLabel.jsx';

/**
 * Weather card - shows current weather with description and UV advisory.
 * Fetches real data from backend via environmentalApi.
 */
export default function WeatherCard() {
  const { user } = useAuth();
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchWeather = async () => {
    if (!user) return;
    try {
      setLoading(true);
      // First get default location
      const locations = await environmentalApi.getLocations();
      const defaultLocation = locations.locations.find(l => l.is_default) || locations.locations[0];

      if (!defaultLocation) {
        setWeatherData(null);
        return;
      }

      // Fetch weather info
      const weatherInfo = await environmentalApi.getCurrentWeatherInfo(defaultLocation.id);
      setWeatherData(weatherInfo);
      setError(null);
    } catch (err) {
      setError('Failed to load weather data');
      setWeatherData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchWeather();
  }, [user]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchWeather();
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

  if (error || !weatherData) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-4">
          <svg className="bi text-muted mb-2" width="32" height="32"><use xlinkHref="#cloud-slash" /></svg>
          <h6 className="text-body-secondary">No weather data yet</h6>
          <p className="text-supporting small mb-2">
            {error || 'Add a location in onboarding to see live weather from OpenWeatherMap.'}
          </p>
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Retry'}
          </button>
        </div>
      </div>
    );
  }

  const { reading, weather_info, data_age_minutes, is_stale } = weatherData;
  const { description, uv_advisory } = weather_info;

  // Weather icon mapping
  const getWeatherIcon = (code) => {
    const icons = {
      0: 'bi-sun',           // Clear sky
      1: 'bi-sun-fill',      // Mainly clear
      2: 'bi-cloud-sun',     // Partly cloudy
      3: 'bi-clouds',        // Overcast
      45: 'bi-cloud-fog',    // Fog
      48: 'bi-cloud-fog2',   // Depositing rime fog
      51: 'bi-cloud-drizzle', // Light drizzle
      53: 'bi-cloud-drizzle', // Moderate drizzle
      55: 'bi-cloud-drizzle', // Dense drizzle
      61: 'bi-cloud-rain',   // Slight rain
      63: 'bi-cloud-rain',   // Moderate rain
      65: 'bi-cloud-rain',   // Heavy rain
      71: 'bi-cloud-snow',   // Slight snow
      73: 'bi-cloud-snow',   // Moderate snow
      75: 'bi-cloud-snow',   // Heavy snow
      95: 'bi-cloud-lightning', // Thunderstorm
    };
    return icons[code] || 'bi-cloud';
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-3">
          <div>
            <h2 className="section-heading mb-1">Current Weather</h2>
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
            <div className="d-inline-flex align-items-center justify-content-center">
              <svg className="bi text-primary" width="64" height="64" role="img" aria-label={description}>
                <use xlinkHref={`#${getWeatherIcon(reading.weather_code)}`} />
              </svg>
            </div>
            <div className="mt-2">
              <h5 className="mb-1">
                {reading.temperature_c !== null && reading.temperature_c !== undefined
                  ? `${Math.round(reading.temperature_c)}°C`
                  : '—'}
              </h5>
              <div className="text-supporting small">{description}</div>
            </div>
          </div>

          <div className="col-12 col-md-8">
            <div className="row g-3">
              {reading.humidity_pct !== null && reading.humidity_pct !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <svg className="bi text-secondary mb-1" width="20" height="20"><use xlinkHref="#droplet" /></svg>
                    <div className="fw-bold">{reading.humidity_pct}%</div>
                    <div className="text-supporting small">Humidity</div>
                  </div>
                </div>
              )}
              {reading.wind_speed_ms !== null && reading.wind_speed_ms !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <svg className="bi text-secondary mb-1" width="20" height="20"><use xlinkHref="#wind" /></svg>
                    <div className="fw-bold">{reading.wind_speed_ms} m/s</div>
                    <div className="text-supporting small">Wind</div>
                  </div>
                </div>
              )}
              {reading.pressure_hpa !== null && reading.pressure_hpa !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <svg className="bi text-secondary mb-1" width="20" height="20"><use xlinkHref="#gauge" /></svg>
                    <div className="fw-bold">{reading.pressure_hpa} hPa</div>
                    <div className="text-supporting small">Pressure</div>
                  </div>
                </div>
              )}
              {reading.uv_index !== null && reading.uv_index !== undefined && (
                <div className="col-6 col-lg-3">
                  <div className="bg-light rounded p-2 text-center">
                    <svg className="bi text-secondary mb-1" width="20" height="20"><use xlinkHref="#sun" /></svg>
                    <div className="fw-bold">{reading.uv_index}</div>
                    <div className="text-supporting small">UV Index</div>
                  </div>
                </div>
              )}
            </div>

            {uv_advisory && (
              <div className="alert alert-info mt-3 mb-0 small">
                <svg className="bi me-1" width="16" height="16"><use xlinkHref="#info-circle" /></svg>
                <strong>UV Advisory:</strong> {uv_advisory}
              </div>
            )}

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
import apiClient from './apiClient';

/**
 * Environmental data API calls (Phase 3).
 * All calls go through the backend which proxies to external providers.
 */

export const environmentalApi = {
  // Locations
  async getLocations() {
    const response = await apiClient.get('/locations');
    return response.data;
  },

  async getDefaultLocation() {
    const response = await apiClient.get('/locations/default');
    return response.data;
  },

  async searchLocations(query) {
    const response = await apiClient.get('/locations/search', {
      params: { q: query },
    });
    return response.data;
  },

  async createLocation(data) {
    const response = await apiClient.post('/locations', data);
    return response.data;
  },

  async updateLocation(locationId, data) {
    const response = await apiClient.patch(`/locations/${locationId}`, data);
    return response.data;
  },

  async deleteLocation(locationId) {
    const response = await apiClient.delete(`/locations/${locationId}`);
    return response.data;
  },

  async setDefaultLocation(locationId) {
    const response = await apiClient.post(`/locations/${locationId}/set-default`);
    return response.data;
  },

  async getLocationWithEnvironmentalData(locationId) {
    const response = await apiClient.get(`/locations/${locationId}`);
    return response.data;
  },

  // Air Quality
  async getLatestAQI(locationId, provider = null) {
    const params = provider ? { provider } : {};
    const response = await apiClient.get(`/air-quality/locations/${locationId}/latest`, { params });
    return response.data;
  },

  async getAQIHistory(locationId, params = {}) {
    const response = await apiClient.get(`/air-quality/locations/${locationId}`, { params });
    return response.data;
  },

  async syncAQIData(locationId, radiusKm = 25) {
    const response = await apiClient.post(`/air-quality/locations/${locationId}/sync`, null, {
      params: { radius_km: radiusKm },
    });
    return response.data;
  },

  async getCurrentAQIInfo(locationId, provider = null) {
    const params = provider ? { provider } : {};
    const response = await apiClient.get(`/air-quality/locations/${locationId}/current-aqi-info`, { params });
    return response.data;
  },

  // Weather
  async getLatestWeather(locationId, provider = null) {
    const params = provider ? { provider } : {};
    const response = await apiClient.get(`/weather/locations/${locationId}/latest`, { params });
    return response.data;
  },

  async getWeatherHistory(locationId, params = {}) {
    const response = await apiClient.get(`/weather/locations/${locationId}`, { params });
    return response.data;
  },

  async syncWeatherData(locationId) {
    const response = await apiClient.post(`/weather/locations/${locationId}/sync`);
    return response.data;
  },

  async getCurrentWeatherInfo(locationId, provider = null) {
    const params = provider ? { provider } : {};
    const response = await apiClient.get(`/weather/locations/${locationId}/current-weather-info`, { params });
    return response.data;
  },
};

export default environmentalApi;
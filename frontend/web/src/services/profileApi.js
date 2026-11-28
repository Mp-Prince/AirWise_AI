import apiClient from './apiClient';

/**
 * Profile API module (Phase 2/3).
 * Consolidates all profile-related API calls.
 *
 * API Endpoints:
 * - GET  /api/v1/profile          - Get current user's profile
 * - POST /api/v1/profile          - Create user profile
 * - PATCH /api/v1/profile         - Update user profile
 * - GET  /api/v1/profile/locations - Get user's locations
 * - POST /api/v1/profile/locations - Create location
 * - PATCH /api/v1/profile/locations/{id} - Update location
 * - DELETE /api/v1/profile/locations/{id} - Delete location
 */

export const profileApi = {
  // Profile operations
  async getProfile() {
    const response = await apiClient.get('/profile');
    return response.data;
  },

  async createProfile(data) {
    const response = await apiClient.post('/profile', data);
    return response.data;
  },

  async updateProfile(data) {
    const response = await apiClient.patch('/profile', data);
    return response.data;
  },

  async upsertProfile(data) {
    const response = await apiClient.post('/profile/upsert', data);
    return response.data;
  },

  // Location operations (consolidated with environmentalApi)
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
};

// Also export as default
export default profileApi;
import apiClient from './apiClient';

/**
 * User profile API calls (Phase 2).
 * Handles profile creation, retrieval, and updates.
 */

export const profileApi = {
  /**
   * Get current user's profile
   * GET /api/v1/profile
   */
  async getProfile() {
    const response = await apiClient.get('/profile');
    return response.data;
  },

  /**
   * Create current user's profile
   * POST /api/v1/profile
   */
  async createProfile(data) {
    const response = await apiClient.post('/profile', data);
    return response.data;
  },

  /**
   * Update current user's profile
   * PATCH /api/v1/profile
   */
  async updateProfile(data) {
    const response = await apiClient.patch('/profile', data);
    return response.data;
  },

  /**
   * Create or update current user's profile (upsert)
   * POST /api/v1/profile/upsert
   */
  async upsertProfile(data) {
    const response = await apiClient.post('/profile/upsert', data);
    return response.data;
  },
};

export default profileApi;
import apiClient from './apiClient';

/**
 * Personalized Recommendations API service (Phase 6).
 */
export const recommendationService = {
  async listRecommendations(params = {}) {
    const response = await apiClient.get('/recommendations', { params });
    return response.data;
  },

  async getTodayRecommendations() {
    const response = await apiClient.get('/recommendations/today');
    return response.data;
  },

  async generateRecommendations() {
    const response = await apiClient.post('/recommendations/generate');
    return response.data;
  },

  async acceptRecommendation(recId) {
    const response = await apiClient.patch(`/recommendations/${recId}/accept`);
    return response.data;
  },

  async dismissRecommendation(recId) {
    const response = await apiClient.patch(`/recommendations/${recId}/dismiss`);
    return response.data;
  },

  async addToPlanner(recId, payload) {
    const response = await apiClient.post(`/recommendations/${recId}/add-to-planner`, payload);
    return response.data;
  },
};

export default recommendationService;

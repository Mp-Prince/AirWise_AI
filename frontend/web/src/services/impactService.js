import apiClient from './apiClient';

/**
 * Environmental Impact & Emission Factors API service (Phase 7).
 */
export const impactService = {
  async getFactors() {
    const response = await apiClient.get('/impact/factors');
    return response.data;
  },

  async calculatePreview(payload) {
    const response = await apiClient.post('/impact/calculate', payload);
    return response.data;
  },

  async logActivity(payload) {
    const response = await apiClient.post('/impact/activities', payload);
    return response.data;
  },

  async getSummary(params = {}) {
    const response = await apiClient.get('/impact/summary', { params });
    return response.data;
  },

  async getRecords(params = {}) {
    const response = await apiClient.get('/impact/records', { params });
    return response.data;
  },

  async getRecordDetail(recordId) {
    const response = await apiClient.get(`/impact/records/${recordId}`);
    return response.data;
  },

  async deleteRecord(recordId) {
    await apiClient.delete(`/impact/records/${recordId}`);
  },
};

export default impactService;

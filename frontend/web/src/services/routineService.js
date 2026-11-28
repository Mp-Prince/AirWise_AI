import apiClient from './apiClient';

/**
 * Daily Planner / Routines API service (Phase 6).
 */
export const routineService = {
  async listRoutines(params = {}) {
    const response = await apiClient.get('/routines', { params });
    return response.data;
  },

  async createRoutine(data) {
    const response = await apiClient.post('/routines', data);
    return response.data;
  },

  async updateRoutine(routineId, data) {
    const response = await apiClient.put(`/routines/${routineId}`, data);
    return response.data;
  },

  async updateStatus(routineId, status) {
    const response = await apiClient.patch(`/routines/${routineId}/status`, { status });
    return response.data;
  },

  async deleteRoutine(routineId) {
    await apiClient.delete(`/routines/${routineId}`);
  },
};

export default routineService;

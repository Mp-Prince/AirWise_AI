import axios from 'axios';

/**
 * Shared Axios instance for all API calls.
 * Base URL comes from VITE_API_BASE_URL (see .env.example) — never
 * hard-code hosts, and never put API keys here: authentication and
 * third-party provider keys stay on the backend.
 */
const ACCESS_TOKEN_KEY = 'aw_access_token';
const REFRESH_TOKEN_KEY = 'aw_refresh_token';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
});

// Attach access token from storage when not already present on the request
apiClient.interceptors.request.use((config) => {
  if (!config.headers.Authorization) {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

let refreshPromise = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh') &&
      !originalRequest.url?.includes('/auth/register')
    ) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${apiClient.defaults.baseURL}/auth/refresh`, {
              refresh_token: refreshToken,
            })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const refreshRes = await refreshPromise;
        const { access_token, refresh_token: newRefreshToken } = refreshRes.data;
        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        delete apiClient.defaults.headers.common.Authorization;
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;

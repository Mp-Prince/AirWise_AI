import axios from 'axios';

/**
 * Shared Axios instance for all API calls.
 * Base URL comes from VITE_API_BASE_URL (see .env.example) — never
 * hard-code hosts, and never put API keys here: authentication and
 * third-party provider keys stay on the backend.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Phase 2 will attach the access token here once auth is implemented.
apiClient.interceptors.request.use((config) => config);

export default apiClient;

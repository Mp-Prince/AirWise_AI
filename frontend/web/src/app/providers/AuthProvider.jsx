import { createContext, useContext, useMemo, useState, useEffect, useCallback } from 'react';
import apiClient from '../../services/apiClient';

/**
 * Auth context with real login/token handling (Phase 2).
 *
 * Tokens are stored in memory (access) + localStorage (refresh) for this phase.
 * The backend enforces access control; this provider only tracks client-side state
 * so routes can react to it.
 */
const AuthContext = createContext(null);

const REFRESH_TOKEN_KEY = 'aw_refresh_token';
const ACCESS_TOKEN_KEY = 'aw_access_token';

export function AuthProvider({ children }) {
  // null = unknown, false = signed out, object = signed-in user summary
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);

      if (refreshToken) {
        // Try to refresh the access token
        const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
        const { access_token, refresh_token: newRefreshToken } = response.data;

        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
        apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;

        // Fetch user profile
        const userResponse = await apiClient.get('/auth/me');
        setUser(userResponse.data);
      } else if (accessToken) {
        // Try with existing access token
        apiClient.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
        try {
          const userResponse = await apiClient.get('/auth/me');
          setUser(userResponse.data);
        } catch {
          // Access token expired, clear and show as signed out
          clearAuth();
        }
      }
    } catch (err) {
      // Refresh failed, clear auth state
      clearAuth();
    } finally {
      setLoading(false);
    }
  };

  const clearAuth = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    delete apiClient.defaults.headers.common.Authorization;
    setUser(false);
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      // OAuth2PasswordRequestForm expects form-encoded data
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const { access_token, refresh_token } = response.data;

      localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
      apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;

      const userResponse = await apiClient.get('/auth/me');
      setUser(userResponse.data);

      return userResponse.data;
    } catch (err) {
      // Handle different error response formats
      let message = 'Login failed. Please check your credentials.';
      if (err.response?.data?.detail) {
        // FastAPI validation errors are arrays of objects with 'msg' field
        if (Array.isArray(err.response.data.detail)) {
          message = err.response.data.detail.map(e => e.msg).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        } else if (err.response.data.detail.msg) {
          message = err.response.data.detail.msg;
        }
      }
      setError(message);
      throw err;
    }
  }, []);

  const register = useCallback(async (name, email, password) => {
    setError(null);
    try {
      const response = await apiClient.post('/auth/register', {
        full_name: name,
        email,
        password,
      });

      // After registration, log in automatically
      return await login(email, password);
    } catch (err) {
      // Handle different error response formats
      let message = 'Registration failed. Please try again.';
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          message = err.response.data.detail.map(e => e.msg).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        } else if (err.response.data.detail.msg) {
          message = err.response.data.detail.msg;
        }
      }
      setError(message);
      throw err;
    }
  }, [login]);

  const logout = useCallback(async () => {
    clearAuth();
  }, [clearAuth]);

  const refreshAccessToken = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      clearAuth();
      return false;
    }

    try {
      const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
      const { access_token, refresh_token: newRefreshToken } = response.data;

      localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
      apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;

      return true;
    } catch {
      clearAuth();
      return false;
    }
  }, [clearAuth]);

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshAccessToken,
      setError,
    }),
    [user, loading, error, login, register, logout, refreshAccessToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Access the auth context. Must be used inside AuthProvider. */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
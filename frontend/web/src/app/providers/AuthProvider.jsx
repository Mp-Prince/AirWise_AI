import { createContext, useContext, useMemo, useState } from 'react';

/**
 * Auth context scaffold (Phase 2 will implement real login/token handling).
 *
 * In Phase 2 the token strategy (httpOnly cookie vs bearer in memory) will be
 * decided with the backend; nothing here is authorization — the backend
 * enforces access control. This provider only tracks client-side state so
 * routes can react to it.
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // null = unknown, false = signed out, object = signed-in user summary
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      setUser,
      setLoading,
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Access the auth context. Must be used inside AuthProvider. */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}

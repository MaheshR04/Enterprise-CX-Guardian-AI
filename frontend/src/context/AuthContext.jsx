import { useEffect, useMemo, useState } from 'react';
import { AuthContext } from './auth-context.js';
import {
  getCurrentUserRequest,
  loginRequest,
  logoutRequest,
  signupRequest,
  updateGuardianContactsRequest,
} from '../services/authService.js';
import { AUTH_TOKEN_KEY } from '../utils/constants.js';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(AUTH_TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(Boolean(token));

  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      if (!token) {
        setInitializing(false);
        return;
      }

      try {
        const response = await getCurrentUserRequest();

        if (isMounted) {
          setUser(response.user);
        }
      } catch {
        localStorage.removeItem(AUTH_TOKEN_KEY);

        if (isMounted) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setInitializing(false);
        }
      }
    }

    restoreSession();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      initializing,
      isAuthenticated: Boolean(token && user),
      signup: async (payload) => {
        const response = await signupRequest(payload);
        localStorage.setItem(AUTH_TOKEN_KEY, response.token);
        setToken(response.token);
        setUser(response.user);
        return response.user;
      },
      login: async (payload) => {
        const response = await loginRequest(payload);
        localStorage.setItem(AUTH_TOKEN_KEY, response.token);
        setToken(response.token);
        setUser(response.user);
        return response.user;
      },
      updateGuardianContacts: async (guardianContacts) => {
        const response = await updateGuardianContactsRequest(guardianContacts);
        setUser(response.user);
        return response.user;
      },
      logout: async () => {
        try {
          await logoutRequest();
        } finally {
          localStorage.removeItem(AUTH_TOKEN_KEY);
          setUser(null);
          setToken(null);
        }
      },
      clearSession: () => {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        setUser(null);
        setToken(null);
      },
    }),
    [initializing, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { User } from './types';
import { login as apiLogin, logout as apiLogout } from './api';

interface AuthState {
  user: User | null;
  token: string | null;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem('demo_token');
    const userStr = localStorage.getItem('demo_user');
    return {
      token,
      user: userStr ? JSON.parse(userStr) : null,
    };
  });

  const login = useCallback(async (username: string, password: string) => {
    const resp = await apiLogin(username, password);
    localStorage.setItem('demo_token', resp.access_token);
    localStorage.setItem('demo_user', JSON.stringify(resp.user));
    setState({ token: resp.access_token, user: resp.user });
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      localStorage.removeItem('demo_token');
      localStorage.removeItem('demo_user');
      setState({ token: null, user: null });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

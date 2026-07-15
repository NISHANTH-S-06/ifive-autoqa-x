import { createContext, useContext } from 'react';
import type { Operator } from './types/auth';
export const AuthContext = createContext<{ operator: Operator; logout: () => Promise<void> } | null>(null);
export const useAuth = () => { const value = useContext(AuthContext); if (!value) throw new Error('Authentication context unavailable.'); return value; };

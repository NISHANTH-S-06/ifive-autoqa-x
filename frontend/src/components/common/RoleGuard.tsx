import React from 'react';
import type { OperatorRole } from '../../types/auth';
import { ShieldAlert } from 'lucide-react';

interface RoleGuardProps {
  userRole?: OperatorRole | string;
  allowedRoles: (OperatorRole | string)[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({ userRole, allowedRoles, children, fallback }: RoleGuardProps) {
  const normUserRole = String(userRole || '').toLowerCase();
  const isAllowed = allowedRoles.some(r => String(r).toLowerCase() === normUserRole || normUserRole === 'admin');

  if (!isAllowed) {
    if (fallback) return <>{fallback}</>;
    return (
      <div className="card" style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'var(--bg-card-subtle)' }}>
        <ShieldAlert size={32} style={{ color: 'var(--color-warning)', margin: '0 auto 0.5rem' }} />
        <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>Restricted Access</h4>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Your current role (<strong>{userRole || 'Guest'}</strong>) does not have permission to access this module.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}

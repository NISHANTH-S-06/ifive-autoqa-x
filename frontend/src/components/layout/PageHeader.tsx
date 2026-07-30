import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

interface PageHeaderProps {
  breadcrumbs?: { label: string; href?: string }[];
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function PageHeader({
  breadcrumbs = [],
  title,
  description,
  actions
}: PageHeaderProps) {
  return (
    <div style={{ marginBottom: '1.5rem' }}>
      {/* Breadcrumb Trail */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
        <Home size={12} style={{ color: 'var(--text-subtle)' }} />
        <span>AutoQA</span>
        {breadcrumbs.map((crumb, i) => (
          <React.Fragment key={i}>
            <ChevronRight size={12} style={{ color: 'var(--text-subtle)' }} />
            <span style={{ color: i === breadcrumbs.length - 1 ? 'var(--text-main)' : 'var(--text-muted)', fontWeight: i === breadcrumbs.length - 1 ? 600 : 400 }}>
              {crumb.label}
            </span>
          </React.Fragment>
        ))}
      </nav>

      {/* Title & Action Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            {title}
          </h1>
          {description && (
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              {description}
            </p>
          )}
        </div>

        {actions && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

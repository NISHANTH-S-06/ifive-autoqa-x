import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string;
  };
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  loading?: boolean;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
  loading = false
}: StatCardProps) {
  if (loading) {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div className="skeleton" style={{ height: '0.875rem', width: '40%' }}></div>
        <div className="skeleton" style={{ height: '2rem', width: '60%' }}></div>
        <div className="skeleton" style={{ height: '0.75rem', width: '50%' }}></div>
      </div>
    );
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary': return { accent: 'var(--color-primary)', bg: 'rgba(37, 99, 235, 0.08)' };
      case 'success': return { accent: 'var(--color-success)', bg: 'rgba(16, 185, 129, 0.08)' };
      case 'warning': return { accent: 'var(--color-warning)', bg: 'rgba(245, 158, 11, 0.08)' };
      case 'danger': return { accent: 'var(--color-danger)', bg: 'rgba(239, 68, 68, 0.08)' };
      case 'info': return { accent: 'var(--color-info)', bg: 'rgba(14, 165, 233, 0.08)' };
      default: return { accent: 'var(--text-muted)', bg: 'var(--bg-card-subtle)' };
    }
  };

  const style = getVariantStyles();

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{ padding: '0.4rem', borderRadius: 'var(--radius-md)', backgroundColor: style.bg, color: style.accent }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.2 }}>
        {value}
      </div>

      {(subtitle || trend) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {trend && (
            <span style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '0.2rem', 
              fontWeight: 600, 
              color: trend.direction === 'up' ? 'var(--color-success)' : trend.direction === 'down' ? 'var(--color-danger)' : 'var(--text-muted)' 
            }}>
              {trend.direction === 'up' ? <TrendingUp size={12} /> : trend.direction === 'down' ? <TrendingDown size={12} /> : null}
              {trend.value}
            </span>
          )}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}

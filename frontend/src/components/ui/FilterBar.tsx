import React from 'react';
import { Search, X, Filter } from 'lucide-react';

export interface FilterOption {
  key: string;
  label: string;
  options: { label: string; value: string }[];
  value: string;
}

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  filters?: FilterOption[];
  onFilterChange?: (key: string, value: string) => void;
  onClearFilters?: () => void;
  placeholder?: string;
  actions?: React.ReactNode;
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  filters = [],
  onFilterChange,
  onClearFilters,
  placeholder = 'Search records...',
  actions
}: FilterBarProps) {
  const hasActiveFilters = searchQuery.trim() !== '' || filters.some(f => f.value !== '' && f.value !== 'ALL');

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', marginBottom: '1rem' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
        <div style={{ position: 'relative', minWidth: '240px', maxWidth: '360px', flex: 1 }}>
          <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-subtle)' }} />
          <input
            type="text"
            className="input"
            style={{ paddingLeft: '2.25rem' }}
            placeholder={placeholder}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer' }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        {filters.map(f => (
          <select
            key={f.key}
            className="select"
            style={{ width: 'auto', minWidth: '130px' }}
            value={f.value}
            onChange={(e) => onFilterChange && onFilterChange(f.key, e.target.value)}
          >
            <option value="">All {f.label}</option>
            {f.options.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        ))}

        {hasActiveFilters && onClearFilters && (
          <button className="btn btn-ghost btn-sm" onClick={onClearFilters}>
            <X size={14} />
            Clear
          </button>
        )}
      </div>

      {actions && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {actions}
        </div>
      )}
    </div>
  );
}

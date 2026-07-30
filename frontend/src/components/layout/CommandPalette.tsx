import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  LayoutDashboard, FileInput, FileCode, CheckSquare, PlayCircle,
  ShieldCheck, Image, Bug, BarChart3, CalendarClock, FolderGit2,
  FileCheck2, Settings, Search, CornerDownLeft, ArrowUp, ArrowDown
} from 'lucide-react';
import type { ModuleKey } from './Sidebar';

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onSelectModule: (module: ModuleKey) => void;
  pendingApprovalsCount?: number;
}

interface PaletteItem {
  key: ModuleKey;
  label: string;
  group: string;
  icon: React.ElementType;
  keywords?: string;
}

const ITEMS: PaletteItem[] = [
  { key: 'dashboard', label: 'Dashboard', group: 'Navigate', icon: LayoutDashboard, keywords: 'home overview kpi' },
  { key: 'task-imports', label: 'Task Imports', group: 'Navigate', icon: FileInput, keywords: 'testing l2 sync connector' },
  { key: 'test-plans', label: 'Test Plans', group: 'Navigate', icon: FileCode, keywords: 'scenarios steps ai plan' },
  { key: 'approval-queue', label: 'Approval Queue', group: 'Navigate', icon: CheckSquare, keywords: 'review approve reject' },
  { key: 'automated-runs', label: 'Automated Runs', group: 'Navigate', icon: PlayCircle, keywords: 'execution playwright worker queue' },
  { key: 'advanced-validation', label: 'Advanced Validation', group: 'Navigate', icon: ShieldCheck, keywords: 'accessibility performance api database' },
  { key: 'evidence', label: 'Evidence', group: 'Navigate', icon: Image, keywords: 'screenshot video trace logs' },
  { key: 'defects', label: 'Defects', group: 'Navigate', icon: Bug, keywords: 'bugs rework retest' },
  { key: 'reports', label: 'Reports', group: 'Navigate', icon: BarChart3, keywords: 'analytics export pdf csv' },
  { key: 'schedules', label: 'Local Schedules', group: 'Navigate', icon: CalendarClock, keywords: 'cron recurring' },
  { key: 'projects', label: 'Projects', group: 'Navigate', icon: FolderGit2, keywords: 'workspace modules suites' },
  { key: 'audit-logs', label: 'Audit Logs', group: 'Navigate', icon: FileCheck2, keywords: 'security integrity hash' },
  { key: 'settings', label: 'Settings', group: 'Navigate', icon: Settings, keywords: 'preferences account' }
];

export function CommandPalette({ open, onClose, onSelectModule, pendingApprovalsCount = 0 }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [highlighted, setHighlighted] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return ITEMS;
    return ITEMS.filter(
      (item) => item.label.toLowerCase().includes(q) || item.keywords?.toLowerCase().includes(q)
    );
  }, [query]);

  useEffect(() => {
    if (open) {
      setQuery('');
      setHighlighted(0);
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open]);

  useEffect(() => {
    setHighlighted(0);
  }, [query]);

  const commit = (item: PaletteItem | undefined) => {
    if (!item) return;
    onSelectModule(item.key);
    onClose();
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlighted((h) => Math.min(h + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlighted((h) => Math.max(h - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      commit(results[highlighted]);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={onClose}
          style={{
            position: 'fixed', inset: 0, zIndex: 'var(--z-command-palette, 900)' as unknown as number,
            backgroundColor: 'rgba(6, 10, 18, 0.55)',
            backdropFilter: 'blur(3px)',
            display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
            paddingTop: '12vh'
          }}
          data-testid="command-palette-overlay"
        >
          <motion.div
            initial={{ opacity: 0, y: -12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
            onClick={(e) => e.stopPropagation()}
            className="card"
            style={{
              width: '560px', maxWidth: '92vw', maxHeight: '60vh',
              display: 'flex', flexDirection: 'column',
              boxShadow: 'var(--shadow-xl)', overflow: 'hidden', padding: 0
            }}
            data-testid="command-palette"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', padding: '0.85rem 1rem', borderBottom: '1px solid var(--border-color)' }}>
              <Search size={17} style={{ color: 'var(--text-subtle)', flexShrink: 0 }} />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Jump to a module... (Task Imports, Defects, Reports)"
                data-testid="command-palette-input"
                style={{
                  flex: 1, border: 'none', outline: 'none', background: 'transparent',
                  fontSize: '0.9rem', color: 'var(--text-main)'
                }}
              />
              <kbd style={{
                fontSize: '0.7rem', color: 'var(--text-subtle)', border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)', padding: '0.1rem 0.4rem'
              }}>Esc</kbd>
            </div>

            <div style={{ overflowY: 'auto', padding: '0.5rem' }}>
              {results.length === 0 && (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No matching modules.
                </div>
              )}
              {results.map((item, index) => {
                const Icon = item.icon;
                const active = index === highlighted;
                return (
                  <div
                    key={item.key}
                    onMouseEnter={() => setHighlighted(index)}
                    onClick={() => commit(item)}
                    data-testid={`command-palette-item-${item.key}`}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '0.7rem',
                      padding: '0.6rem 0.7rem', borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      backgroundColor: active ? 'var(--bg-surface-hover)' : 'transparent',
                      transition: 'background-color 0.1s ease'
                    }}
                  >
                    <Icon size={16} style={{ color: active ? 'var(--color-primary)' : 'var(--text-subtle)', flexShrink: 0 }} />
                    <span style={{ flex: 1, fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: active ? 600 : 500 }}>
                      {item.label}
                    </span>
                    {item.key === 'approval-queue' && pendingApprovalsCount > 0 && (
                      <span className="badge" style={{ backgroundColor: 'var(--color-warning)', color: '#fff' }}>
                        {pendingApprovalsCount}
                      </span>
                    )}
                    {active && <CornerDownLeft size={13} style={{ color: 'var(--text-subtle)' }} />}
                  </div>
                );
              })}
            </div>

            <div style={{
              display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.5rem 1rem',
              borderTop: '1px solid var(--border-color)', fontSize: '0.7rem', color: 'var(--text-subtle)'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><ArrowUp size={11} /><ArrowDown size={11} /> Navigate</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><CornerDownLeft size={11} /> Select</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

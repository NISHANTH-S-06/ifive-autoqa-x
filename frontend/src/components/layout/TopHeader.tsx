import React, { useState } from 'react';
import { useProject } from '../../stores/projectStore';
import { useTheme } from '../../stores/themeStore';
import type { Operator } from '../../types/auth';
import { 
  FolderGit2, Search, Bell, Sun, Moon, User, Key, 
  LogOut, Shield, Check, X, Layers 
} from 'lucide-react';

interface TopHeaderProps {
  operator: Operator | null;
  onLogout: () => void;
  onChangePassword?: () => void;
  globalSearch: string;
  onGlobalSearchChange: (q: string) => void;
  onOpenCommandPalette?: () => void;
}

export function TopHeader({
  operator,
  onLogout,
  onChangePassword,
  globalSearch,
  onGlobalSearchChange,
  onOpenCommandPalette
}: TopHeaderProps) {
  const { activeProject, projects, setActiveProject } = useProject();
  const { theme, toggleTheme } = useTheme();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const notifications = [
    { id: 1, title: 'Execution Completed', message: 'Automated Run #104 passed 14/14 steps.', time: '5m ago', unread: true },
    { id: 2, title: 'Plan Review Needed', message: 'Test Plan #12 awaiting manager review.', time: '20m ago', unread: true },
    { id: 3, title: 'Defect Created', message: 'Defect #45 logged from execution failure.', time: '1h ago', unread: false }
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header style={{
      height: '60px',
      backgroundColor: 'var(--bg-header)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1.5rem',
      zIndex: 90
    }}>
      {/* Left: Project Selector & Environment */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: '220px' }}>
          <FolderGit2 size={18} style={{ color: 'var(--color-primary)' }} />
          <select
            className="select"
            style={{ padding: '0.35rem 0.6rem', fontSize: '0.85rem', fontWeight: 600 }}
            value={activeProject?.id || ''}
            onChange={(e) => {
              const selected = projects.find(p => String(p.id) === e.target.value);
              if (selected) setActiveProject(selected);
            }}
            data-testid="project-selector"
          >
            {projects.length === 0 ? (
              <option value="">No Projects</option>
            ) : (
              projects.map(p => (
                <option key={p.id} value={p.id}>{p.code} - {p.name}</option>
              ))
            )}
          </select>
        </div>

        <span className="badge" style={{ backgroundColor: 'var(--bg-card-subtle)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
          <Layers size={11} />
          <span>STAGE: LOCAL</span>
        </span>
      </div>

      {/* Center: Global Search */}
      <div style={{ position: 'relative', width: '320px' }} onClick={() => onOpenCommandPalette?.()}>
        <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-subtle)' }} />
        <input
          type="text"
          className="input"
          style={{ paddingLeft: '2.25rem', paddingRight: '2.75rem', height: '34px', fontSize: '0.825rem', cursor: 'pointer' }}
          placeholder="Search or jump to..."
          value={globalSearch}
          onFocus={() => onOpenCommandPalette?.()}
          onChange={(e) => onGlobalSearchChange(e.target.value)}
          data-testid="global-search-input"
          readOnly
        />
        <kbd style={{
          position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)',
          fontSize: '0.65rem', color: 'var(--text-subtle)', border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)', padding: '0.05rem 0.35rem', pointerEvents: 'none'
        }}>Ctrl K</kbd>
      </div>

      {/* Right Actions: Theme Toggle, Notifications, User Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="btn btn-ghost btn-sm"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          style={{ padding: '0.4rem' }}
          data-testid="theme-toggle"
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* Notification Center */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => { setShowNotifications(!showNotifications); setShowUserMenu(false); }}
            className="btn btn-ghost btn-sm"
            style={{ padding: '0.4rem', position: 'relative' }}
            title="Notifications"
            data-testid="notification-button"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '2px',
                right: '2px',
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-danger)'
              }} />
            )}
          </button>

          {showNotifications && (
            <div className="card" style={{
              position: 'absolute',
              right: 0,
              top: '42px',
              width: '320px',
              padding: '0.75rem',
              boxShadow: 'var(--shadow-xl)',
              zIndex: 200
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Notifications</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{unreadCount} unread</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '240px', overflowY: 'auto' }}>
                {notifications.map(n => (
                  <div key={n.id} style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)', backgroundColor: n.unread ? 'var(--bg-surface-hover)' : 'transparent' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-main)' }}>{n.title}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-subtle)' }}>{n.time}</span>
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{n.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => { setShowUserMenu(!showUserMenu); setShowNotifications(false); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '0.25rem 0.5rem',
              borderRadius: 'var(--radius-md)'
            }}
            data-testid="user-menu-button"
          >
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--color-primary-light)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              {(operator?.display_name || operator?.username || 'U')[0].toUpperCase()}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.2 }}>
                {operator?.display_name || operator?.username || 'Operator'}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {operator?.role ? String(operator.role).toUpperCase() : 'TESTER'}
              </span>
            </div>
          </button>

          {showUserMenu && (
            <div className="card" style={{
              position: 'absolute',
              right: 0,
              top: '42px',
              width: '220px',
              padding: '0.5rem',
              boxShadow: 'var(--shadow-xl)',
              zIndex: 200
            }}>
              <div style={{ padding: '0.5rem', borderBottom: '1px solid var(--border-color)', marginBottom: '0.25rem' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-main)' }}>{operator?.display_name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>@{operator?.username}</div>
              </div>

              {onChangePassword && (
                <button
                  onClick={() => { setShowUserMenu(false); onChangePassword(); }}
                  className="btn btn-ghost btn-sm"
                  style={{ width: '100%', justifyContent: 'flex-start' }}
                >
                  <Key size={14} />
                  Change Password
                </button>
              )}

              <button
                onClick={() => { setShowUserMenu(false); onLogout(); }}
                className="btn btn-ghost btn-sm"
                style={{ width: '100%', justifyContent: 'flex-start', color: 'var(--color-danger)' }}
                data-testid="logout-button"
              >
                <LogOut size={14} />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar, ModuleKey } from '../components/layout/Sidebar';
import { TopHeader } from '../components/layout/TopHeader';
import { CommandPalette } from '../components/layout/CommandPalette';
import { ToastSystem } from '../components/ui/ToastSystem';
import type { Operator } from '../types/auth';

interface AppShellProps {
  operator: Operator | null;
  onLogout: () => void;
  onChangePassword?: () => void;
  activeModule: ModuleKey;
  onSelectModule: (module: ModuleKey) => void;
  children: React.ReactNode;
  pendingApprovalsCount?: number;
}

export function AppShell({
  operator,
  onLogout,
  onChangePassword,
  activeModule,
  onSelectModule,
  children,
  pendingApprovalsCount = 0
}: AppShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [globalSearch, setGlobalSearch] = useState('');
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((open) => !open);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-app)' }}>
      {/* Collapsible Left Sidebar */}
      <Sidebar
        activeModule={activeModule}
        onSelectModule={onSelectModule}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        pendingApprovalsCount={pendingApprovalsCount}
        operatorRole={operator?.role}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        {/* Top Header */}
        <TopHeader
          operator={operator}
          onLogout={onLogout}
          onChangePassword={onChangePassword}
          globalSearch={globalSearch}
          onGlobalSearchChange={setGlobalSearch}
          onOpenCommandPalette={() => setPaletteOpen(true)}
        />

        {/* Dynamic Page Container */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 2rem' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeModule}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Global Toast System */}
      <ToastSystem />

      {/* Command Palette (Ctrl+K / Cmd+K) */}
      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onSelectModule={onSelectModule}
        pendingApprovalsCount={pendingApprovalsCount}
      />
    </div>
  );
}

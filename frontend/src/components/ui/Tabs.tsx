import React from 'react';
import { motion } from 'framer-motion';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
}

export function Tabs({ tabs, activeTab, onChange }: TabsProps) {
  return (
    <div style={{
      display: 'flex',
      gap: '1rem',
      borderBottom: '1px solid var(--border-color)',
      marginBottom: '1.5rem',
      paddingBottom: '0.5rem'
    }}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            style={{
              background: 'transparent',
              border: 'none',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              fontWeight: isActive ? 600 : 500,
              color: isActive ? 'var(--color-primary)' : 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              position: 'relative',
              fontSize: '0.9rem',
              transition: 'color 0.2s ease'
            }}
          >
            {tab.icon}
            {tab.label}
            {isActive && (
              <motion.div
                layoutId="activeTabIndicator"
                style={{
                  position: 'absolute',
                  bottom: '-0.5rem',
                  left: 0,
                  right: 0,
                  height: '2px',
                  backgroundColor: 'var(--color-primary)',
                  borderRadius: '2px 2px 0 0'
                }}
                initial={false}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

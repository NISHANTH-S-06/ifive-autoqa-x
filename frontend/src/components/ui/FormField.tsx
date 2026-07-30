import React from 'react';

export interface FormFieldProps {
  label?: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: React.ReactNode;
  htmlFor?: string;
}

export function FormField({ label, required, error, hint, children, htmlFor }: FormFieldProps) {
  return (
    <div style={{ marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
      {label && (
        <label
          htmlFor={htmlFor}
          style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}
        >
          {label}
          {required && <span style={{ color: 'var(--color-danger)', marginLeft: '0.25rem' }}>*</span>}
        </label>
      )}
      {children}
      {hint && !error && (
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{hint}</span>
      )}
      {error && (
        <span style={{ fontSize: '0.75rem', color: 'var(--color-danger)', fontWeight: 500 }} role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

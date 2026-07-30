import React, { type InputHTMLAttributes, forwardRef } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  icon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', error, icon, ...props }, ref) => {
    return (
      <div style={{ position: 'relative', width: '100%' }}>
        {icon && (
          <div style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
            {icon}
          </div>
        )}
        <input
          ref={ref}
          className={`input ${error ? 'border-danger' : ''} ${className}`}
          style={{
            paddingLeft: icon ? '2.35rem' : '0.75rem',
            borderColor: error ? 'var(--color-danger)' : undefined,
          }}
          {...props}
        />
      </div>
    );
  }
);

Input.displayName = 'Input';

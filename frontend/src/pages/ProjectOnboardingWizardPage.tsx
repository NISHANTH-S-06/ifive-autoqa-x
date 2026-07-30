import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { FormField } from '../components/ui/FormField';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  Building2, Package, Globe, Lock, Monitor, Layers, ShieldCheck,
  ChevronRight, ChevronLeft, CheckCircle2, Loader2
} from 'lucide-react';
import { apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

const STEPS = [
  { id: 1, label: 'Company', icon: Building2 },
  { id: 2, label: 'Product', icon: Package },
  { id: 3, label: 'App URL', icon: Globe },
  { id: 4, label: 'Auth Type', icon: Lock },
  { id: 5, label: 'Browser', icon: Monitor },
  { id: 6, label: 'Environment', icon: Layers },
  { id: 7, label: 'Validation', icon: ShieldCheck },
];

const AUTH_TYPES = ['USERNAME_PASSWORD', 'OTP', 'GOOGLE', 'MICROSOFT', 'SSO', 'BEARER_TOKEN', 'COOKIE', 'MANUAL'];
const BROWSERS = ['CHROMIUM', 'CHROME', 'FIREFOX', 'EDGE', 'WEBKIT'];
const ENVIRONMENTS = ['DEV', 'QA', 'UAT', 'PRODUCTION'];

export function ProjectOnboardingWizardPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    company_name: '',
    product_name: '',
    application_url: '',
    auth_type: 'USERNAME_PASSWORD',
    browser_selection: 'CHROMIUM',
    environment: 'QA',
  });

  const update = (key: string, value: string) => setForm(f => ({ ...f, [key]: value }));

  const handleStartSession = async () => {
    setLoading(true);
    try {
      const res = await apiPost<any>('/api/onboarding/start', form);
      setSessionId(res.session_id);
      setCurrentStep(7);
      toast.success('Onboarding session created. Proceeding to AI validation...');
    } catch (err: any) {
      toast.error(err.message || 'Failed to start onboarding session');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!sessionId) return;
    setValidating(true);
    try {
      const res = await apiPost<any>(`/api/onboarding/validate/${sessionId}`, {});
      setValidationResult(res);
      toast.success('AI Connection Validation complete!');
    } catch (err: any) {
      toast.error(err.message || 'Validation failed');
    } finally {
      setValidating(false);
    }
  };

  const canProceed = () => {
    if (currentStep === 1) return form.company_name.trim().length > 0;
    if (currentStep === 2) return form.product_name.trim().length > 0;
    if (currentStep === 3) return form.application_url.trim().length > 0;
    return true;
  };

  const progressPct = (currentStep / 7) * 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Zero-Code Ecosystem' }, { label: 'Project Onboarding Wizard' }]}
        title="Zero-Code Project Onboarding Wizard"
        description="Connect any enterprise web application in 7 guided steps. No code required."
      />

      {/* Step Progress Bar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', gap: '0.5rem', flexWrap: 'wrap' }}>
          {STEPS.map(step => {
            const Icon = step.icon;
            const isActive = currentStep === step.id;
            const isDone = currentStep > step.id;
            return (
              <div
                key={step.id}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.35rem',
                  flex: 1, minWidth: '80px',
                }}
              >
                <div style={{
                  width: 42, height: 42, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: isDone ? '#10b981' : isActive ? 'var(--color-primary)' : 'var(--bg-muted)',
                  border: `2px solid ${isActive ? 'var(--color-primary)' : isDone ? '#10b981' : 'var(--border-color)'}`,
                  transition: 'all 0.25s',
                }}>
                  {isDone ? <CheckCircle2 size={20} color="#fff" /> : <Icon size={18} color={isActive ? '#fff' : 'var(--text-muted)'} />}
                </div>
                <span style={{ fontSize: '0.7rem', fontWeight: isActive ? 700 : 500, color: isActive ? 'var(--color-primary)' : 'var(--text-muted)' }}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
        <div style={{ height: 6, background: 'var(--bg-muted)', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${progressPct}%`, background: 'var(--color-primary)', borderRadius: 3, transition: 'width 0.4s ease' }} />
        </div>
      </div>

      {/* Step Content */}
      <div className="card" style={{ padding: '2rem', minHeight: 280 }}>
        {currentStep === 1 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 1 – Company Information</h3>
            <FormField label="Company Name" required>
              <Input placeholder="e.g. Acme Corporation" value={form.company_name} onChange={e => update('company_name', e.target.value)} />
            </FormField>
          </div>
        )}
        {currentStep === 2 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 2 – Product Information</h3>
            <FormField label="Product Name" required>
              <Input placeholder="e.g. ERP Suite v3.2" value={form.product_name} onChange={e => update('product_name', e.target.value)} />
            </FormField>
          </div>
        )}
        {currentStep === 3 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 3 – Application URL</h3>
            <FormField label="Application URL" required>
              <Input placeholder="https://app.yourcompany.com" value={form.application_url} onChange={e => update('application_url', e.target.value)} />
            </FormField>
          </div>
        )}
        {currentStep === 4 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 4 – Authentication Type</h3>
            <div className="grid grid-cols-4" style={{ gap: '0.75rem' }}>
              {AUTH_TYPES.map(at => (
                <div
                  key={at}
                  onClick={() => update('auth_type', at)}
                  style={{
                    padding: '0.85rem 1rem', borderRadius: 8, cursor: 'pointer', textAlign: 'center',
                    border: `2px solid ${form.auth_type === at ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    background: form.auth_type === at ? 'rgba(var(--color-primary-rgb, 99,102,241),0.08)' : 'var(--bg-muted)',
                    fontWeight: form.auth_type === at ? 700 : 500, fontSize: '0.8rem',
                    transition: 'all 0.2s',
                  }}
                >
                  {at.replace('_', ' ')}
                </div>
              ))}
            </div>
          </div>
        )}
        {currentStep === 5 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 5 – Browser Selection</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {BROWSERS.map(br => (
                <div
                  key={br}
                  onClick={() => update('browser_selection', br)}
                  style={{
                    padding: '0.85rem 1.5rem', borderRadius: 8, cursor: 'pointer',
                    border: `2px solid ${form.browser_selection === br ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    background: form.browser_selection === br ? 'rgba(var(--color-primary-rgb, 99,102,241),0.08)' : 'var(--bg-muted)',
                    fontWeight: form.browser_selection === br ? 700 : 500,
                    transition: 'all 0.2s',
                  }}
                >
                  {br}
                </div>
              ))}
            </div>
          </div>
        )}
        {currentStep === 6 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 6 – Target Environment</h3>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {ENVIRONMENTS.map(env => (
                <div
                  key={env}
                  onClick={() => update('environment', env)}
                  style={{
                    padding: '1rem 2rem', borderRadius: 8, cursor: 'pointer',
                    border: `2px solid ${form.environment === env ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    background: form.environment === env ? 'rgba(var(--color-primary-rgb, 99,102,241),0.08)' : 'var(--bg-muted)',
                    fontWeight: form.environment === env ? 700 : 500, fontSize: '0.95rem',
                    transition: 'all 0.2s',
                  }}
                >
                  {env}
                </div>
              ))}
            </div>
          </div>
        )}
        {currentStep === 7 && (
          <div>
            <h3 style={{ margin: '0 0 1.5rem 0' }}>Step 7 – AI Connection Validation</h3>
            {!sessionId ? (
              <div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                  Review your configuration and submit to start the AI-powered connection validation.
                </p>
                <div className="grid grid-cols-3" style={{ gap: '1rem', marginBottom: '1.5rem' }}>
                  {[
                    ['Company', form.company_name], ['Product', form.product_name],
                    ['URL', form.application_url], ['Auth', form.auth_type],
                    ['Browser', form.browser_selection], ['Environment', form.environment],
                  ].map(([label, val]) => (
                    <div key={label} style={{ background: 'var(--bg-muted)', padding: '0.75rem 1rem', borderRadius: 8 }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{label}</div>
                      <div style={{ fontWeight: 600, marginTop: '0.2rem', wordBreak: 'break-all' }}>{val}</div>
                    </div>
                  ))}
                </div>
                <Button variant="primary" onClick={() => void handleStartSession()} isLoading={loading}>
                  Start Onboarding Session
                </Button>
              </div>
            ) : validationResult ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                  <StatusBadge
                    status={validationResult.validation_status === 'PASSED' ? 'APPROVED' : 'CRITICAL'}
                    label={validationResult.validation_status}
                  />
                  <span style={{ fontWeight: 600 }}>{validationResult.validation_results.recommendation}</span>
                </div>
                <div className="grid grid-cols-3" style={{ gap: '0.75rem' }}>
                  {Object.entries(validationResult.validation_results.checks || {}).map(([key, val]) => (
                    <div key={key} style={{ background: 'var(--bg-muted)', padding: '0.75rem 1rem', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{key.replace('_', ' ')}</span>
                      <CheckCircle2 size={16} color="#10b981" />
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ color: 'var(--text-muted)' }}>
                  Session ID: <strong>#{sessionId}</strong> created. Click below to run AI connection validation.
                </p>
                <Button variant="primary" onClick={() => void handleValidate()} isLoading={validating} leftIcon={<ShieldCheck size={16} />}>
                  {validating ? 'Validating...' : 'Run AI Connection Validation'}
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="secondary" onClick={() => setCurrentStep(s => Math.max(1, s - 1))} disabled={currentStep === 1} leftIcon={<ChevronLeft size={16} />}>
          Back
        </Button>
        {currentStep < 7 && (
          <Button variant="primary" onClick={() => setCurrentStep(s => s + 1)} disabled={!canProceed()} rightIcon={<ChevronRight size={16} />}>
            Next Step
          </Button>
        )}
      </div>
    </div>
  );
}

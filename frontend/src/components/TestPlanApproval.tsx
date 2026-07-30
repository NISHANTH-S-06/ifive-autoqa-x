import React, { useState, useEffect, useContext } from 'react';
import { TestPlanService } from '../services/testPlans';
import { AuthContext } from '../authContext';
import { Drawer } from './ui/Drawer';
import { Button } from './ui/Button';
import { StatusBadge } from './ui/StatusBadge';
import { FormField } from './ui/FormField';
import { JSONViewer } from './ui/JSONViewer';
import { ShieldAlert, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

interface Props {
  planId: number;
  onClose: () => void;
  onRefresh: () => void;
}

export function TestPlanApproval({ planId, onClose, onRefresh }: Props) {
  const auth = useContext(AuthContext);
  const currentUserId = auth?.operator?.id || 1;

  const [plan, setPlan] = useState<any>(null);
  const [reason, setReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlan();
  }, [planId]);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const data = await TestPlanService.getTestPlan(planId);
      setPlan(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load test plan details');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setSaving(true);
    setError('');
    try {
      await TestPlanService.approveTestPlan(planId);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Approval failed');
    } finally {
      setSaving(false);
    }
  };

  const handleReject = async () => {
    if (!reason.trim()) {
      setError('A mandatory rejection reason is required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await TestPlanService.rejectTestPlan(planId, reason);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Rejection failed');
    } finally {
      setSaving(false);
    }
  };

  const isCreator = plan && plan.created_by === currentUserId;

  return (
    <Drawer
      isOpen={true}
      onClose={onClose}
      title={plan ? `Review Test Plan: ${plan.title}` : 'Review Test Plan'}
      subtitle={plan ? `Plan Key: ${plan.plan_key || `PLAN-${plan.id}`} • Version v${plan.current_version}` : undefined}
      width="680px"
      footer={(
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleReject}
            isLoading={saving}
            leftIcon={<XCircle size={15} />}
          >
            Reject Plan
          </Button>
          <Button
            variant="primary"
            onClick={handleApprove}
            isLoading={saving}
            disabled={isCreator}
            leftIcon={<CheckCircle2 size={15} />}
            title={isCreator ? 'You authored this plan. Self-approval is strictly blocked.' : undefined}
          >
            Approve Plan
          </Button>
        </>
      )}
    >
      {loading && <div className="skeleton" style={{ height: '300px' }} />}

      {error && (
        <div className="state-panel state-error" style={{ marginBottom: '1rem' }} role="alert">
          {error}
        </div>
      )}

      {plan && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {isCreator && (
            <div style={{ padding: '0.75rem 1rem', background: 'var(--status-rejected-bg)', color: 'var(--status-rejected-text)', border: '1px solid var(--status-rejected-border)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.85rem' }}>
              <ShieldAlert size={18} style={{ flexShrink: 0 }} />
              <span>
                <strong>Self-Approval Blocked:</strong> You are the author of this plan. Another qualified reviewer or administrator must perform approval.
              </span>
            </div>
          )}

          {/* Plan Summary Card */}
          <div className="card" style={{ padding: '1rem', background: 'var(--bg-card-subtle)' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Governance & Version Details
            </h4>
            <div className="grid grid-cols-2" style={{ fontSize: '0.8rem', gap: '0.75rem' }}>
              <div><span style={{ color: 'var(--text-muted)' }}>Status:</span> <StatusBadge status={plan.status} size="sm" /></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Current Version:</span> <strong>v{plan.current_version}</strong></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Plan Hash:</span> <code style={{ fontSize: '0.75rem' }}>{plan.plan_hash?.slice(0, 16) || '—'}</code></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Author ID:</span> Operator #{plan.created_by}</div>
            </div>
          </div>

          {/* Scenario Overview */}
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Scenarios & Step Definitions ({plan.scenarios?.length || 0})
            </h4>
            <JSONViewer data={plan.scenarios || []} title="Plan Scenarios JSON Payload" maxHeight="240px" />
          </div>

          {/* Mandatory Rejection Reason */}
          <FormField
            label="Rejection Reason"
            hint="Mandatory if rejecting this test plan for revisions"
          >
            <textarea
              className="textarea"
              style={{ minHeight: '80px', fontSize: '0.85rem' }}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why this test plan requires revision or fails review criteria..."
            />
          </FormField>
        </div>
      )}
    </Drawer>
  );
}

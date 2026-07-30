import React, { useState, useEffect, useContext } from 'react';
import { TestPlan, TestScenario, TestStep } from '../types/testPlan';
import { TestPlanService } from '../services/testPlans';
import { AuthContext } from '../authContext';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { StatusBadge } from './ui/StatusBadge';
import { Plus, Trash2, ArrowUp, ArrowDown, Save, Send } from 'lucide-react';

interface Props {
  planId: number;
  onClose: () => void;
  onRefresh: () => void;
}

export function TestPlanEditor({ planId, onClose, onRefresh }: Props) {
  const auth = useContext(AuthContext);

  const [plan, setPlan] = useState<TestPlan | null>(null);
  const [scenarios, setScenarios] = useState<TestScenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlan();
  }, [planId]);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const data = await TestPlanService.getTestPlan(planId);
      setPlan(data);
      if (data.versions && data.versions.length > 0) {
        const latestVersion = data.versions.find(v => v.version_number === data.current_version) || data.versions[data.versions.length - 1];
        setScenarios(JSON.parse(JSON.stringify(latestVersion.scenarios)));
      } else {
        setScenarios([]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load plan');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      await TestPlanService.updateTestPlan(planId, { scenarios });
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save plan');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    setSaving(true);
    setError('');
    try {
      await TestPlanService.updateTestPlan(planId, { scenarios });
      await TestPlanService.submitTestPlan(planId);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit plan');
    } finally {
      setSaving(false);
    }
  };

  const updateStep = (sIdx: number, stIdx: number, field: keyof TestStep, value: any) => {
    const updated = [...scenarios];
    updated[sIdx].steps[stIdx] = { ...updated[sIdx].steps[stIdx], [field]: value };
    setScenarios(updated);
  };

  const addStep = (sIdx: number) => {
    const updated = [...scenarios];
    const steps = updated[sIdx].steps;
    steps.push({
      step_order: steps.length + 1,
      action: 'CLICK',
      locator_json: '',
      input_value_reference: '',
      expected_value: '',
      timeout_ms: 5000,
      continue_on_failure: false,
    });
    setScenarios(updated);
  };

  const removeStep = (sIdx: number, stIdx: number) => {
    const updated = [...scenarios];
    updated[sIdx].steps.splice(stIdx, 1);
    updated[sIdx].steps.forEach((step, idx) => { step.step_order = idx + 1; });
    setScenarios(updated);
  };

  const moveStep = (sIdx: number, stIdx: number, delta: number) => {
    const updated = [...scenarios];
    const steps = updated[sIdx].steps;
    const target = stIdx + delta;
    if (target < 0 || target >= steps.length) return;
    [steps[stIdx], steps[target]] = [steps[target], steps[stIdx]];
    steps.forEach((step, idx) => { step.step_order = idx + 1; });
    setScenarios(updated);
  };

  if (loading || !plan) {
    return (
      <Modal isOpen={true} onClose={onClose} title="Edit Test Plan">
        <div className="skeleton" style={{ height: '200px' }} />
      </Modal>
    );
  }

  const isReadOnly = plan.status === 'APPROVED';
  const planHash = plan.versions?.[0]?.plan_hash || 'Draft';

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={`Visual Editor: ${plan.title}`}
      subtitle={`Plan Hash: ${planHash} • Status: ${plan.status}`}
      maxWidth="960px"
      footer={(
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="secondary"
            onClick={handleSave}
            isLoading={saving}
            disabled={plan.status === 'REJECTED'}
            leftIcon={<Save size={15} />}
          >
            {isReadOnly ? 'Edit & Create Draft' : 'Save Draft'}
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            isLoading={saving}
            disabled={plan.status !== 'DRAFT'}
            leftIcon={<Send size={15} />}
          >
            Submit for Approval
          </Button>
        </>
      )}
    >
      {error && (
        <div className="state-panel state-error" style={{ marginBottom: '1rem' }} role="alert">
          {error}
        </div>
      )}

      {isReadOnly && (
        <div className="state-panel" style={{ marginBottom: '1rem', borderLeft: '4px solid var(--color-info)' }}>
          Approved versions are read-only. Saving modifications will generate a new draft version.
        </div>
      )}

      <div style={{ maxHeight: '65vh', overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {scenarios.map((scenario, sIdx) => (
          <div
            key={sIdx}
            className="card"
            style={{ padding: '1rem', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {scenario.title}
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{scenario.description}</p>
              </div>
              <StatusBadge status={scenario.scenario_type || 'PRIMARY'} size="sm" />
            </div>

            <div className="table-container" style={{ marginTop: '0.75rem' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: '50px' }}>Step</th>
                    <th style={{ width: '160px' }}>Action</th>
                    <th>Locator / Selector</th>
                    <th>Value Reference</th>
                    <th>Expected Result</th>
                    <th style={{ width: '90px', textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {scenario.steps.map((step, stIdx) => (
                    <tr key={stIdx}>
                      <td style={{ fontWeight: 600, textAlign: 'center' }}>{step.step_order}</td>
                      <td>
                        <Select
                          disabled={isReadOnly}
                          value={step.action}
                          onChange={(e) => updateStep(sIdx, stIdx, 'action', e.target.value)}
                        >
                          <option value="NAVIGATE">NAVIGATE</option>
                          <option value="CLICK">CLICK</option>
                          <option value="FILL">FILL</option>
                          <option value="ASSERT_VISIBLE">ASSERT_VISIBLE</option>
                          <option value="ASSERT_TEXT">ASSERT_TEXT</option>
                          <option value="SCREENSHOT">SCREENSHOT</option>
                        </Select>
                      </td>
                      <td>
                        <Input
                          disabled={isReadOnly}
                          value={step.locator_json || ''}
                          onChange={(e) => updateStep(sIdx, stIdx, 'locator_json', e.target.value)}
                          placeholder="#element-id or xpath"
                        />
                      </td>
                      <td>
                        <Input
                          disabled={isReadOnly}
                          value={step.input_value_reference || ''}
                          onChange={(e) => updateStep(sIdx, stIdx, 'input_value_reference', e.target.value)}
                          placeholder="input test data"
                        />
                      </td>
                      <td>
                        <Input
                          disabled={isReadOnly}
                          value={step.expected_value || ''}
                          onChange={(e) => updateStep(sIdx, stIdx, 'expected_value', e.target.value)}
                          placeholder="expected text / state"
                        />
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '0.25rem', justifyContent: 'center' }}>
                          <button
                            type="button"
                            className="btn btn-ghost btn-sm"
                            disabled={isReadOnly || stIdx === 0}
                            onClick={() => moveStep(sIdx, stIdx, -1)}
                          >
                            <ArrowUp size={13} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-ghost btn-sm"
                            disabled={isReadOnly || stIdx === scenario.steps.length - 1}
                            onClick={() => moveStep(sIdx, stIdx, 1)}
                          >
                            <ArrowDown size={13} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-ghost btn-sm"
                            disabled={isReadOnly || scenario.steps.length <= 1}
                            onClick={() => removeStep(sIdx, stIdx)}
                            style={{ color: 'var(--color-danger)' }}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {!isReadOnly && (
              <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'flex-end' }}>
                <Button size="sm" variant="secondary" onClick={() => addStep(sIdx)} leftIcon={<Plus size={14} />}>
                  Add Step
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </Modal>
  );
}

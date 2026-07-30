import React, { useState, useEffect } from 'react';
import { LiveExecutionMonitor, PipelineStage } from './LiveExecutionMonitor';
import { ContextViewer } from './ContextViewer';
import { ValidationTimeline } from './ValidationTimeline';
import { AIDecisionPanel } from './AIDecisionPanel';
import { SelfHealingPanel } from './SelfHealingPanel';

// Simulated data fetching for Live Pipeline View based on latest run
export function AutoQAPipeline() {
  const [stage, setStage] = useState<PipelineStage>('DISCOVERY');
  const [status, setStatus] = useState<'RUNNING'|'FAILED'|'SUCCESS'>('RUNNING');
  
  // Mock contexts for demonstration
  const [contextData, setContextData] = useState<any>(null);
  const [validationPlan, setValidationPlan] = useState<any>(null);
  const [decisionData, setDecisionData] = useState<any>(null);
  const [healingData, setHealingData] = useState<any>(null);

  useEffect(() => {
    // In a real application, this would poll the /api/automated-runs/{id} endpoint
    // and /api/ai/dashboard/live to update these states.
    // For this Phase 7 implementation, we simulate the live pipeline progression.
    
    let timer1 = setTimeout(() => {
      setStage('CONTEXT');
      setContextData({
        url: 'https://demo.ifive.io/login',
        buttons: [{text: 'Sign In', id: 'btn-signin'}, {text: 'Forgot Password'}],
        links: [{text: 'Create Account', href: '/register'}],
        inputs: [{id: 'username', type: 'text'}, {id: 'password', type: 'password'}]
      });
    }, 2000);

    let timer2 = setTimeout(() => {
      setStage('VALIDATION');
      setValidationPlan({
        plan_title: 'Dynamic Execution Plan',
        steps: [
          { step_number: 1, action: 'NAVIGATE', validations: ['URL Validation', 'HTTP 200'] },
          { step_number: 2, action: 'FILL', selector: '#username', validations: ['Element Visible', 'Text Validation'] },
          { step_number: 3, action: 'CLICK', selector: '#btn-login-v2', validations: ['Element Clickable', 'URL Changed'] }
        ]
      });
    }, 4000);

    let timer3 = setTimeout(() => {
      setStage('EXECUTION');
    }, 6000);

    let timer4 = setTimeout(() => {
      setStage('DECISION');
      setStatus('FAILED'); // Simulate a failure on step 3
      setDecisionData({
        decision: 'HEAL',
        confidenceScore: 92,
        riskLevel: 'LOW',
        healingAttempts: 1,
        reason: "Locator '#btn-login-v2' timed out. Initiating heuristic self-healing."
      });
      setHealingData({
        originalLocator: '#btn-login-v2',
        recoveredLocator: '#btn-signin',
        recoveryMethod: 'PARTIAL_ID_MATCH',
        success: true,
        confidence: 85
      });
    }, 8000);

    return () => {
      clearTimeout(timer1); clearTimeout(timer2); clearTimeout(timer3); clearTimeout(timer4);
    };
  }, []);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <LiveExecutionMonitor currentStage={stage} status={status} />
      
      <div className="grid grid-cols-2" style={{ gap: '1.5rem' }}>
        <div>
          {contextData && <ContextViewer contextData={contextData} />}
          {validationPlan && <ValidationTimeline planTitle={validationPlan.plan_title} steps={validationPlan.steps} />}
        </div>
        <div>
          {decisionData && <AIDecisionPanel {...decisionData} />}
          {healingData && <SelfHealingPanel {...healingData} />}
        </div>
      </div>
    </div>
  );
}

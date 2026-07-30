import React, { useState } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Bot, Send, Sparkles, HelpCircle, ShieldAlert, Cpu, CheckCircle } from 'lucide-react';
import { apiPost } from '../services/api';
import { toast } from '../stores/toastStore';

interface ChatMessage {
  sender: 'user' | 'copilot';
  text: string;
  confidence?: number;
  timestamp: string;
}

export function EnterpriseCopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'copilot',
      text: 'Hello! I am your **AutoQA Enterprise AI Copilot**. Ask me anything about test failures, root cause analysis, release predictions, visual regression diffs, or executive summaries.',
      confidence: 0.99,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    'Why did this test fail?',
    'Explain root cause for recent defect',
    'Predict release quality for v1.0.0',
    'Explain visual regression diffs',
    'Generate executive summary'
  ];

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend || !textToSend.trim()) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await apiPost<{ query: string; answer: string; confidence_score: number }>('/api/copilot/query', {
        query: textToSend
      });

      const copilotMsg: ChatMessage = {
        sender: 'copilot',
        text: res.answer,
        confidence: res.confidence_score,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, copilotMsg]);
    } catch (err: any) {
      toast.error(err.message || 'Copilot query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', height: 'calc(100vh - 120px)' }}>
      <PageHeader
        breadcrumbs={[{ label: 'AI Autonomous QA' }, { label: 'AI Copilot' }]}
        title="Enterprise AI Copilot"
        description="Natural language Q&A reasoning engine synthesizing platform data, root cause tracebacks, and release quality predictions."
      />

      {/* Main Chat Container */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0 }}>
        {/* Chat Messages Log */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '0.75rem',
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%'
              }}
            >
              {msg.sender === 'copilot' && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #2563eb, #0ea5e9)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', flexShrink: 0 }}>
                  <Bot size={20} />
                </div>
              )}
              <div
                style={{
                  background: msg.sender === 'user' ? 'var(--color-primary)' : 'var(--bg-muted)',
                  color: msg.sender === 'user' ? '#ffffff' : 'var(--text-main)',
                  padding: '1rem 1.25rem',
                  borderRadius: '12px',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem', gap: '1rem' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.8rem', opacity: 0.9 }}>
                    {msg.sender === 'user' ? 'Operator' : 'AutoQA AI Copilot'}
                  </span>
                  {msg.confidence && (
                    <StatusBadge status="APPROVED" label={`Confidence: ${Math.round(msg.confidence * 100)}%`} size="sm" />
                  )}
                </div>
                <div style={{ fontSize: '0.9rem', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: '0.4rem', textAlign: 'right' }}>
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Sample Prompts Bar */}
        <div style={{ padding: '0.75rem 1.25rem', background: 'var(--bg-app)', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem', overflowX: 'auto' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem', whiteSpace: 'nowrap' }}>
            <Sparkles size={13} /> Suggested Queries:
          </span>
          {samplePrompts.map((prompt, pIdx) => (
            <button
              key={pIdx}
              onClick={() => void handleSend(prompt)}
              className="btn btn-ghost btn-sm"
              style={{ fontSize: '0.75rem', whiteSpace: 'nowrap', border: '1px solid var(--border-color)', padding: '0.2rem 0.6rem' }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Query Input Footer */}
        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.75rem' }}>
          <Input
            placeholder="Ask AI Copilot (e.g. Why did test fail? Predict release readiness score...)"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') void handleSend(); }}
            style={{ flex: 1 }}
          />
          <Button variant="primary" onClick={() => void handleSend()} isLoading={loading} leftIcon={<Send size={16} />}>
            Ask Copilot
          </Button>
        </div>
      </div>
    </div>
  );
}

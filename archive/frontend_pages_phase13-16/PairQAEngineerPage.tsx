import React, { useState } from 'react';
import { assistPairQA } from '../services/phase15Service';

const card = { background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', padding: '20px' };

const QUICK_PROMPTS = [
  'Generate Playwright TypeScript checkout test',
  'Improve locator for submit button',
  'Explain database pool timeout RCA',
  'Suggest regression suite optimization',
  'Review release readiness for v5.0.0',
];

export const PairQAEngineerPage: React.FC = () => {
  const [inputIntent, setInputIntent] = useState('');
  const [messages, setMessages] = useState<any[]>([
    {
      sender: 'AI Pair Engineer',
      text: 'Hello! I am your Enterprise AI Pair QA Engineer. Ask me to generate tests, improve locators, analyze test failure RCAs, or review release readiness.',
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text: string) => {
    if (!text) return;
    const userMsg = { sender: 'You', text };
    setMessages(prev => [...prev, userMsg]);
    setInputIntent('');
    setLoading(true);

    try {
      const res: any = await assistPairQA(text);
      const aiMsg = {
        sender: 'AI Pair Engineer',
        text: res.suggestion,
        code: res.code_snippet,
        intent: res.intent,
        confidence: res.confidence,
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err: any) { alert(err.message); } finally { setLoading(false); }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 900, margin: 0, background: 'linear-gradient(90deg, #38bdf8, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🤖 Enterprise AI Pair QA Engineer
          </h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>Interactive Pair Programming Assistant — Test Generation · Locator Optimization · RCA · Code Review</p>
        </div>
      </div>

      {/* Quick Prompts */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {QUICK_PROMPTS.map(p => (
          <button key={p} onClick={() => handleSend(p)} style={{ padding: '6px 14px', borderRadius: '16px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', fontSize: '12px', cursor: 'pointer' }}>
            💡 {p}
          </button>
        ))}
      </div>

      {/* Chat Stream */}
      <div style={{ ...card, marginBottom: '20px', minHeight: '400px', maxHeight: '550px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{ alignSelf: m.sender === 'You' ? 'flex-end' : 'flex-start', maxWidth: '80%', background: m.sender === 'You' ? '#38bdf822' : '#0f172a', border: `1px solid ${m.sender === 'You' ? '#38bdf844' : '#334155'}`, borderRadius: '12px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: m.sender === 'You' ? '#38bdf8' : '#a78bfa', fontWeight: 800, marginBottom: '4px' }}>{m.sender}</div>
            <div style={{ fontSize: '14px', color: '#fff', lineHeight: '1.5' }}>{m.text}</div>
            {m.code && (
              <pre style={{ background: '#1e293b', padding: '10px', borderRadius: '6px', fontSize: '12px', marginTop: '10px', overflowX: 'auto', color: '#38bdf8' }}>
                <code>{m.code}</code>
              </pre>
            )}
          </div>
        ))}
      </div>

      {/* Input Bar */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(inputIntent); }} style={{ display: 'flex', gap: '12px' }}>
        <input
          value={inputIntent}
          onChange={e => setInputIntent(e.target.value)}
          placeholder="Ask the AI Pair QA Engineer anything (e.g. improve locator for checkout submit button)..."
          style={{ flex: 1, padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff', fontSize: '14px' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '12px 24px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #38bdf8, #0284c7)', color: '#fff', fontWeight: 700, cursor: 'pointer' }}>
          {loading ? 'Thinking...' : '💬 Send'}
        </button>
      </form>
    </div>
  );
};

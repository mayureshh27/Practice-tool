import {useState} from 'react';

type Slot = { id: string; name: string; tokens: number; enabled: boolean; };

const INITIAL_SLOTS: Slot[] = [
  {id: 'sys', name: 'system_prompt', tokens: 850, enabled: true},
  {id: 'src', name: 'source_chunks', tokens: 2100, enabled: true},
  {id: 'hist', name: 'user_history', tokens: 1300, enabled: true},
  {id: 'graph', name: 'concept_graph', tokens: 400, enabled: false},
  {id: 'mem', name: 'memory_events', tokens: 350, enabled: false},
];

const BUDGET_MAX = 8000;

function ContextPanel() {
  const [slots, setSlots] = useState<Slot[]>(INITIAL_SLOTS);
  const [budgetMax, setBudgetMax] = useState(BUDGET_MAX);

  const usedTokens = slots.filter(s => s.enabled).reduce((sum, s) => sum + s.tokens, 0);
  const pct = Math.min(100, Math.round((usedTokens / budgetMax) * 100));
  const overBudget = usedTokens > budgetMax;

  const toggleSlot = (id: string) => {
    setSlots(prev => prev.map(s => s.id === id ? {...s, enabled: !s.enabled} : s));
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <p className="text-ws-muted text-sm m-0">Context assembly and token usage.</p>
      
      <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
        <div className="text-ws-ink font-medium">Token Budget</div>
        <div className="flex items-center justify-between text-ws-muted text-sm">
          <span style={{color: overBudget ? "#ef4444" : "#10b981", fontWeight: 600}}>
            {usedTokens.toLocaleString()} / {budgetMax.toLocaleString()}
          </span>
          <span style={{color: overBudget ? "#ef4444" : "#71717a"}}>{pct}%</span>
        </div>
        <div style={{
          height: 6, borderRadius: 999, background: "#27272a", overflow: 'hidden', marginTop: 6,
        }}>
          <div style={{
            height: '100%', width: pct + '%', borderRadius: 'inherit',
            background: overBudget ? "#ef4444" : 'linear-gradient(90deg, var(--ws-glow), var(--ws-accent-2))',
            transition: 'width 300ms ease',
          }} />
        </div>
        <div style={{marginTop: 8}}>
          <label style={{display: 'flex', alignItems: 'center', gap: 8, fontSize: 'var(--ws-type-xs)', color: "#71717a"}}>
            Max budget:
            <input
              type="range"
              min={2000}
              max={16000}
              step={500}
              value={budgetMax}
              onChange={e => setBudgetMax(Number(e.target.value))}
              style={{flex: 1, accentColor: "#10b981"}}
            />
            <span style={{minWidth: 48, textAlign: 'right', fontFamily: 'var(--ws-font-mono)', color: "#a1a1aa"}}>{budgetMax.toLocaleString()}</span>
          </label>
        </div>
      </div>
      
      <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
        <div className="text-ws-ink font-medium">Context Slots</div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 2}}>
          {slots.map(slot => (
            <label
              key={slot.id}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0',
                cursor: 'pointer', borderBottom: '1px solid var(--ws-edge-soft)',
              }}
            >
              <input
                type="checkbox"
                checked={slot.enabled}
                onChange={() => toggleSlot(slot.id)}
                style={{accentColor: "#10b981"}}
              />
              <span style={{
                flex: 1, color: slot.enabled ? "#a1a1aa" : "#71717a",
                fontFamily: 'var(--ws-font-mono)', fontSize: '11px',
                textDecoration: slot.enabled ? 'none' : 'line-through',
              }}>
                {slot.name}
              </span>
              <span style={{
                color: slot.enabled ? "#a1a1aa" : "#71717a",
                fontFamily: 'var(--ws-font-mono)', fontSize: 'var(--ws-type-xs)',
              }}>
                {slot.tokens}t
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ContextPanel;

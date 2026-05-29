import {RefreshCw, ChevronDown, ChevronRight, Clock} from 'lucide-react';
import {useState} from 'react';

type EvalCheck = {
  id: string;
  name: string;
  status: 'pass' | 'warn' | 'fail';
  latency: string;
  log: string;
};

type WorkflowRun = {
  id: string;
  template: string;
  latency: string;
  timestamp: string;
  checks: EvalCheck[];
};

const INITIAL_RUN: WorkflowRun = {
  id: 'wf_892b1a',
  template: 'create_exercises',
  latency: '4.2s',
  timestamp: new Date().toLocaleTimeString(),
  checks: [
    {id: 'e1', name: 'Schema Validation', status: 'pass', latency: '0.3s', log: '✓ Output matches PracticeArtifact schema\n✓ All required fields present\n✓ 5 exercises generated\n✓ difficulty field valid'},
    {id: 'e2', name: 'Sandbox Execution', status: 'pass', latency: '1.8s', log: '✓ Exercise 1: code compiles and runs\n✓ Exercise 2: code compiles and runs\n✓ Exercise 3: code compiles and runs\n✓ Exercise 4: expected output matches\n✓ Exercise 5: expected output matches'},
    {id: 'e3', name: 'Source Grounding', status: 'warn', latency: '2.1s', log: '✓ Exercise 1: grounded in chunk c1\n✓ Exercise 2: grounded in chunk c3\n⚠ Exercise 3: no direct source match found\n✓ Exercise 4: grounded in chunk c2\n✓ Exercise 5: grounded in chunk c1'},
  ],
};

function InspectorPanel() {
  const [run, setRun] = useState<WorkflowRun>(INITIAL_RUN);
  const [expandedCheck, setExpandedCheck] = useState<string | null>(null);
  const [rerunning, setRerunning] = useState(false);

  const handleRerun = () => {
    setRerunning(true);
    setTimeout(() => {
      setRun(prev => ({
        ...prev,
        id: 'wf_' + Math.random().toString(36).slice(2, 8),
        timestamp: new Date().toLocaleTimeString(),
        latency: (3 + Math.random() * 3).toFixed(1) + 's',
        checks: prev.checks.map(c => ({
          ...c,
          latency: (Math.random() * 3).toFixed(1) + 's',
          status: Math.random() > 0.15 ? 'pass' : 'warn' as 'pass' | 'warn' | 'fail',
        })),
      }));
      setRerunning(false);
    }, 2000);
  };

  const statusColor = (s: string) => s === 'pass' ? "#10b981" : s === 'warn' ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <p className="text-ws-muted text-sm m-0">Debug metadata and eval results.</p>
        <button
          type="button"
          onClick={handleRerun}
          disabled={rerunning}
          style={{
            display: 'flex', alignItems: 'center', gap: 4, padding: '3px 8px',
            background: 'none', border: '1px solid var(--ws-edge-soft)', borderRadius: "4px",
            color: rerunning ? "#71717a" : "#10b981", cursor: rerunning ? 'wait' : 'pointer',
            fontSize: 'var(--ws-type-xs)', fontWeight: 600,
          }}
        >
          <RefreshCw size={10} className={rerunning ? 'animate-spin' : ''} />
          {rerunning ? 'Running...' : 'Re-run Evals'}
        </button>
      </div>

      <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
        <div className="text-ws-ink font-medium">Workflow Run</div>
        <div className="flex items-center justify-between py-1">
          <span style={{color: 'var(--ws-muted)'}}>ID</span>
          <span style={{fontFamily: 'var(--ws-font-mono)', color: "#71717a"}}>{run.id}</span>
        </div>
        <div className="flex items-center justify-between py-1">
          <span style={{color: 'var(--ws-muted)'}}>Template</span>
          <span style={{color: "#71717a"}}>{run.template}</span>
        </div>
        <div className="flex items-center justify-between py-1">
          <span style={{color: 'var(--ws-muted)'}}>Latency</span>
          <span style={{color: "#71717a"}}>{run.latency}</span>
        </div>
        <div className="flex items-center justify-between py-1">
          <span style={{color: 'var(--ws-muted)'}}>Ran at</span>
          <span style={{color: "#71717a", display: 'flex', alignItems: 'center', gap: 4}}>
            <Clock size={10} /> {run.timestamp}
          </span>
        </div>
      </div>
      
      <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
        <div className="text-ws-ink font-medium">Eval Checks</div>
        {run.checks.map(check => (
          <div key={check.id}>
            <button
              type="button"
              onClick={() => setExpandedCheck(expandedCheck === check.id ? null : check.id)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%',
                padding: '6px 0', background: 'none', border: 'none', borderBottom: '1px solid var(--ws-edge-soft)',
                cursor: 'pointer', color: "#a1a1aa",
              }}
            >
              <span style={{display: 'flex', alignItems: 'center', gap: 6}}>
                {expandedCheck === check.id ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                <span style={{fontSize: '11px'}}>{check.name}</span>
              </span>
              <span style={{display: 'flex', alignItems: 'center', gap: 6}}>
                <span style={{fontSize: 'var(--ws-type-xs)', color: "#71717a"}}>{check.latency}</span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ${check.status}`} style={{textTransform: 'uppercase', fontSize: 10}}>{check.status}</span>
              </span>
            </button>
            {expandedCheck === check.id && (
              <pre style={{
                margin: '4px 0 8px 18px', padding: 8,
                background: "#0a0a0b", border: '1px solid var(--ws-edge-soft)',
                borderRadius: "4px", fontSize: 'var(--ws-type-xs)',
                color: "#a1a1aa", lineHeight: 1.6,
                whiteSpace: 'pre-wrap', fontFamily: 'var(--ws-font-mono)',
                borderLeft: `2px solid ${statusColor(check.status)}`,
              }}>
                {check.log}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default InspectorPanel;

import {X, Terminal, FlaskConical, Play, FileText, ScrollText, TestTubeDiagonal, Send, Power} from 'lucide-react';
import {useState, useRef, useEffect} from 'react';
import type {BottomDockTab} from '../workspaceTypes';

import { useUIStore } from '../stores/uiStore';

type Props = {
  outputContent?: string;
  verdictLabel?: string;
};

const TABS: {id: BottomDockTab; label: string; icon: typeof Terminal}[] = [
  {id: 'output',   label: 'Output',   icon: Play},
  {id: 'tests',    label: 'Tests',    icon: TestTubeDiagonal},
  {id: 'terminal', label: 'Terminal', icon: Terminal},
  {id: 'sandbox',  label: 'Sandbox',  icon: FlaskConical},
  {id: 'evals',    label: 'Evals',    icon: FileText},
  {id: 'logs',     label: 'Logs',     icon: ScrollText},
];

/* ── Test Results ────────────────────────── */
const TEST_RESULTS = [
  {id: 1, name: 'test_basic_input',     status: 'pass', time: '0.02s', detail: 'Expected: [1,2,3] → Got: [1,2,3]'},
  {id: 2, name: 'test_edge_case_empty', status: 'pass', time: '0.01s', detail: 'Expected: [] → Got: []'},
  {id: 3, name: 'test_large_input',     status: 'pass', time: '0.15s', detail: 'Expected: 1000 elements → Got: 1000 elements'},
  {id: 4, name: 'test_negative_values', status: 'fail', time: '0.03s', detail: 'Expected: [-1,-2,-3] → Got: [-1,-2,3]'},
  {id: 5, name: 'test_boundary',        status: 'pass', time: '0.01s', detail: 'Expected: [0] → Got: [0]'},
];

/* ── Eval Results ────────────────────────── */
const EVAL_RESULTS = [
  {id: 1, gate: 'Schema Validation',  status: 'pass', detail: 'Output matches PracticeArtifact JSON schema.'},
  {id: 2, gate: 'Sandbox Execution',  status: 'pass', detail: 'All generated code compiles and produces expected output.'},
  {id: 3, gate: 'Source Grounding',   status: 'warn', detail: 'Exercise 3 has no direct source chunk match.'},
  {id: 4, gate: 'Difficulty Calibration', status: 'pass', detail: 'Exercises correctly match requested difficulty level.'},
];

/* ── Log Entries ─────────────────────────── */
function generateLogs() {
  const now = new Date();
  return [
    {id: 1, time: new Date(now.getTime() - 120000).toLocaleTimeString(), level: 'INFO',  msg: 'Workspace session started'},
    {id: 2, time: new Date(now.getTime() - 90000).toLocaleTimeString(),  level: 'INFO',  msg: 'Loaded 14 source chunks from Modern Robotics V2'},
    {id: 3, time: new Date(now.getTime() - 60000).toLocaleTimeString(),  level: 'INFO',  msg: 'Context assembled: 4250 tokens across 3 slots'},
    {id: 4, time: new Date(now.getTime() - 45000).toLocaleTimeString(),  level: 'DEBUG', msg: 'Workflow create_exercises triggered with 2 sources'},
    {id: 5, time: new Date(now.getTime() - 30000).toLocaleTimeString(),  level: 'INFO',  msg: 'Workflow completed in 4.2s — 5 exercises generated'},
    {id: 6, time: new Date(now.getTime() - 15000).toLocaleTimeString(),  level: 'WARN',  msg: 'Source grounding check: exercise 3 ungrounded'},
    {id: 7, time: now.toLocaleTimeString(),                              level: 'INFO',  msg: 'Artifact "Kinematics Basics Quiz" approved'},
  ];
}

/* ── Terminal Commands ───────────────────── */
const TERMINAL_RESPONSES: Record<string, string> = {
  'help': 'Available commands: help, status, clear, sources, budget, whoami, ls',
  'status': 'Workspace: active\nProject: Robotics Learning\nSources loaded: 3\nArtifacts generated: 5\nBlind spots detected: 2',
  'sources': '1. Modern Robotics V2 (PDF, 14 chunks)\n2. Kinematics Lecture (Transcript, 8 chunks)\n3. Chapter 2 Notes (Note, 3 chunks)',
  'budget': 'Token budget: 4,250 / 8,000 (53%)\nSlots: system_prompt(850), source_chunks(2100), user_history(1300)',
  'whoami': 'Learner: Practice Workspace User\nProject: Robotics Learning\nSession: active since page load',
  'ls': 'artifacts/\n  kinematics_quiz.json\n  chapter2_flashcards.json\n  cspace_mindmap.json\nsources/\n  modern_robotics_v2.pdf\n  kinematics_lecture.txt\n  ch2_notes.md',
};

function TerminalTab() {
  const [history, setHistory] = useState<{type: 'cmd' | 'out'; text: string}[]>([
    {type: 'out', text: 'Practice Workspace Terminal v1.0\nType "help" for available commands.\n'},
  ]);
  const [cmd, setCmd] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [history]);

  const handleSubmit = () => {
    if (!cmd.trim()) return;
    const command = cmd.trim().toLowerCase();
    const response = command === 'clear'
      ? null
      : TERMINAL_RESPONSES[command] || `Command not found: ${cmd.trim()}\nType "help" for available commands.`;

    if (command === 'clear') {
      setHistory([{type: 'out', text: 'Terminal cleared.\n'}]);
    } else {
      setHistory(prev => [...prev, {type: 'cmd', text: cmd.trim()}, {type: 'out', text: response!}]);
    }
    setCmd('');
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: '100%'}}>
      <div ref={scrollRef} style={{flex: 1, overflow: 'auto', fontFamily: "'JetBrains Mono', monospace", fontSize: 12, lineHeight: 1.6}}>
        {history.map((entry, i) => (
          <div key={i} style={{color: entry.type === 'cmd' ? "var(--ws-accent)" : "var(--ws-soft)", whiteSpace: 'pre-wrap'}}>
            {entry.type === 'cmd' ? `$ ${entry.text}` : entry.text}
          </div>
        ))}
      </div>
      <div style={{display: 'flex', gap: 6, alignItems: 'center', marginTop: 8}}>
        <span style={{color: "var(--ws-accent)", fontFamily: "'JetBrains Mono', monospace", fontSize: 12}}>$</span>
        <input
          type="text"
          value={cmd}
          onChange={e => setCmd(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); }}
          style={{
            flex: 1, background: 'transparent', border: 'none', outline: 'none',
            color: "var(--ws-ink)", fontFamily: "'JetBrains Mono', monospace", fontSize: 12,
          }}
          placeholder="Type a command..."
          autoFocus
        />
        <button type="button" onClick={handleSubmit} style={{background: 'none', border: 'none', cursor: 'pointer', color: "var(--ws-accent)", display: 'flex'}}>
          <Send size={12} />
        </button>
      </div>
    </div>
  );
}

function SandboxTab() {
  const [running, setRunning] = useState(false);
  const [output, setOutput] = useState<string[]>(['Sandbox environment ready. Click "Start" to launch.']);

  const toggleSandbox = () => {
    if (running) {
      setRunning(false);
      setOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Sandbox stopped.`]);
    } else {
      setRunning(true);
      setOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Sandbox starting...`]);
      setTimeout(() => {
        setOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Python 3.11 environment ready.`, `[${new Date().toLocaleTimeString()}] numpy, scipy, sympy loaded.`, `[${new Date().toLocaleTimeString()}] Sandbox running. Waiting for code execution...`]);
      }, 1200);
    }
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: '100%', gap: 8}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
        <button
          type="button"
          onClick={toggleSandbox}
          style={{
            display: 'flex', alignItems: 'center', gap: 4, padding: '4px 10px',
            background: running ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
            border: `1px solid ${running ? "#ef4444" : "var(--ws-accent)"}`,
            borderRadius: "4px", cursor: 'pointer',
            color: running ? "#ef4444" : "var(--ws-accent)",
            fontSize: 11, fontWeight: 600,
          }}
        >
          <Power size={12} /> {running ? 'Stop' : 'Start'}
        </button>
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: "var(--ws-muted)",
        }}>
          <span style={{width: 6, height: 6, borderRadius: '50%', background: running ? "var(--ws-accent)" : "var(--ws-muted)"}} />
          {running ? 'Running' : 'Stopped'}
        </span>
      </div>
      <div style={{flex: 1, overflow: 'auto', fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--ws-soft)", whiteSpace: 'pre-wrap', lineHeight: 1.6}}>
        {output.map((line, i) => <div key={i}>{line}</div>)}
      </div>
    </div>
  );
}

function BottomDock({outputContent, verdictLabel}: Props) {
  const [logs] = useState(generateLogs);
  const open = useUIStore(s => s.bottomOpen);
  const activeTab = useUIStore(s => s.bottomTab);
  const onTabChange = useUIStore(s => s.setBottomTab);
  const onClose = () => useUIStore.getState().setBottomOpen(false);

  return (
    <div className={`flex flex-col bg-ws-bg border-t border-ws-line transition-[height] duration-200 ease-out overflow-hidden ${open ? 'h-[300px]' : 'h-0 border-t-0'}`}>
      <div className="flex items-center gap-1 px-2 border-b border-ws-line bg-ws-bg shrink-0 h-9 overflow-x-auto scrollbar-none">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              type="button"
              className={`flex items-center gap-2 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider rounded transition-colors whitespace-nowrap ${activeTab === tab.id ? 'text-ws-success bg-ws-surface-2/50' : 'text-ws-muted hover:bg-ws-surface-2 hover:text-ws-soft'}`}
              onClick={() => onTabChange(tab.id)}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}

        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 ml-auto text-ws-muted hover:text-red-500 hover:bg-ws-surface-2 rounded transition-colors shrink-0"
          onClick={onClose}
          title="Close dock"
          aria-label="Close dock"
        >
          <X size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 bg-ws-bg">
        {activeTab === 'output' && (
          <div style={{fontSize: 12, color: "var(--ws-soft)", fontFamily: "'JetBrains Mono', monospace", whiteSpace: 'pre-wrap', lineHeight: 1.6}}>
            {verdictLabel && (
              <span style={{
                display: 'inline-block', marginBottom: 8, padding: '2px 8px', fontSize: 11, fontWeight: 700,
                color: verdictLabel === 'Accepted' ? "var(--ws-accent)" : verdictLabel === 'Error' ? "#ef4444" : "var(--ws-soft)",
                background: "var(--ws-bg)", border: '1px solid var(--ws-edge)', borderRadius: "4px",
              }}>
                {verdictLabel}
              </span>
            )}
            {outputContent || 'Run or submit code to see output here.'}
          </div>
        )}

        {activeTab === 'tests' && (
          <div style={{fontSize: 12}}>
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead>
                <tr style={{borderBottom: '1px solid var(--ws-edge-soft)', color: "var(--ws-muted)", fontSize: 11, textAlign: 'left'}}>
                  <th style={{padding: '4px 8px', fontWeight: 600}}>Test</th>
                  <th style={{padding: '4px 8px', fontWeight: 600}}>Status</th>
                  <th style={{padding: '4px 8px', fontWeight: 600}}>Time</th>
                  <th style={{padding: '4px 8px', fontWeight: 600}}>Detail</th>
                </tr>
              </thead>
              <tbody>
                {TEST_RESULTS.map(t => (
                  <tr key={t.id} style={{borderBottom: '1px solid var(--ws-edge-soft)'}}>
                    <td style={{padding: '6px 8px', color: "var(--ws-soft)", fontFamily: "'JetBrains Mono', monospace"}}>{t.name}</td>
                    <td style={{padding: '6px 8px'}}>
                      <span style={{
                        padding: '2px 6px', fontSize: 10, fontWeight: 700, borderRadius: "4px",
                        color: t.status === 'pass' ? "var(--ws-accent)" : "#ef4444",
                        background: t.status === 'pass' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                        border: `1px solid ${t.status === 'pass' ? "var(--ws-accent)" : "#ef4444"}`,
                        textTransform: 'uppercase',
                      }}>
                        {t.status}
                      </span>
                    </td>
                    <td style={{padding: '6px 8px', color: "var(--ws-muted)", fontFamily: "'JetBrains Mono', monospace"}}>{t.time}</td>
                    <td style={{padding: '6px 8px', color: "var(--ws-muted)", fontSize: 11}}>{t.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{marginTop: 8, color: "var(--ws-muted)", fontSize: 11}}>
              {TEST_RESULTS.filter(t => t.status === 'pass').length}/{TEST_RESULTS.length} tests passing
            </div>
          </div>
        )}

        {activeTab === 'terminal' && <TerminalTab />}
        {activeTab === 'sandbox' && <SandboxTab />}

        {activeTab === 'evals' && (
          <div style={{fontSize: 12, display: 'flex', flexDirection: 'column', gap: 6}}>
            {EVAL_RESULTS.map(ev => (
              <div key={ev.id} style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '6px 8px',
                background: "var(--ws-bg)", border: '1px solid var(--ws-edge-soft)', borderRadius: "4px",
              }}>
                <span style={{flex: 1, color: "var(--ws-soft)"}}>{ev.gate}</span>
                <span style={{
                  padding: '2px 6px', fontSize: 10, fontWeight: 700, borderRadius: "4px",
                  textTransform: 'uppercase',
                  color: ev.status === 'pass' ? "var(--ws-accent)" : ev.status === 'warn' ? "#f59e0b" : "#ef4444",
                  background: ev.status === 'pass' ? 'rgba(16,185,129,0.1)' : ev.status === 'warn' ? 'rgba(217,119,6,0.1)' : 'rgba(239,68,68,0.1)',
                  border: `1px solid ${ev.status === 'pass' ? "var(--ws-accent)" : ev.status === 'warn' ? "#f59e0b" : "#ef4444"}`,
                }}>
                  {ev.status}
                </span>
                <span style={{color: "var(--ws-muted)", fontSize: 11, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                  {ev.detail}
                </span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'logs' && (
          <div style={{fontFamily: "'JetBrains Mono', monospace", fontSize: 11, lineHeight: 1.8, color: "var(--ws-soft)"}}>
            {logs.map(log => (
              <div key={log.id} style={{display: 'flex', gap: 8}}>
                <span style={{color: "var(--ws-muted)", flexShrink: 0}}>{log.time}</span>
                <span style={{
                  flexShrink: 0, fontWeight: 700, width: 40,
                  color: log.level === 'WARN' ? "#f59e0b" : log.level === 'DEBUG' ? "var(--ws-muted)" : "var(--ws-accent)",
                }}>
                  {log.level}
                </span>
                <span>{log.msg}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BottomDock;

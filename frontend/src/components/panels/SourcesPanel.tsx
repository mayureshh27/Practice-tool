import {FileText, Search, ChevronDown, ChevronRight, ToggleLeft, ToggleRight} from 'lucide-react';
import {useState} from 'react';

type ChunkPreview = { id: string; text: string; };
type Source = { id: string; title: string; type: string; chunkCount: number; inContext: boolean; chunks: ChunkPreview[]; };

const INITIAL_SOURCES: Source[] = [
  {id: '1', title: 'Modern Robotics V2', type: 'PDF', chunkCount: 14, inContext: true, chunks: [
    {id: 'c1', text: 'The configuration of a robot is a complete specification of the position of every point of the robot...'},
    {id: 'c2', text: 'The minimum number n of real-valued coordinates needed to represent the configuration is the number of degrees of freedom (dof)...'},
    {id: 'c3', text: 'The n-dimensional space containing all possible configurations of the robot is called the configuration space (C-space)...'},
  ]},
  {id: '2', title: 'Kinematics Lecture', type: 'Transcript', chunkCount: 8, inContext: true, chunks: [
    {id: 'c4', text: 'Forward kinematics maps joint angles to end-effector position using the product of exponentials formula...'},
    {id: 'c5', text: 'The Jacobian matrix relates joint velocities to end-effector twist velocities...'},
  ]},
  {id: '3', title: 'Chapter 2 Notes', type: 'Note', chunkCount: 3, inContext: false, chunks: [
    {id: 'c6', text: 'Topology of C-space: S¹ for revolute joints, ℝ for prismatic joints...'},
  ]},
];

function SourcesPanel() {
  const [sources, setSources] = useState<Source[]>(INITIAL_SOURCES);
  const [filter, setFilter] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = sources.filter(s => s.title.toLowerCase().includes(filter.toLowerCase()) || s.type.toLowerCase().includes(filter.toLowerCase()));

  const toggleContext = (id: string) => {
    setSources(prev => prev.map(s => s.id === id ? {...s, inContext: !s.inContext} : s));
  };

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  const contextCount = sources.filter(s => s.inContext).length;
  const totalChunks = sources.filter(s => s.inContext).reduce((sum, s) => sum + s.chunkCount, 0);

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <p className="text-ws-muted text-sm m-0">{contextCount} sources · {totalChunks} chunks active</p>
      </div>

      <div style={{position: 'relative'}}>
        <Search size={12} style={{position: 'absolute', left: 8, top: 9, color: "#71717a"}} />
        <input
          type="text"
          className="flex-1 bg-ws-surface border border-ws-line rounded px-3 py-2 text-ws-ink outline-none focus:border-ws-success transition-colors"
          style={{paddingLeft: 28, width: '100%'}}
          placeholder="Filter sources..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
      </div>
      
      <div className="flex flex-col gap-3 overflow-y-auto flex-1">
        {filtered.map(source => (
          <div key={source.id} className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => toggleExpand(source.id)}
                style={{background: 'none', border: 'none', padding: 0, color: "#71717a", cursor: 'pointer', display: 'flex'}}
              >
                {expandedId === source.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </button>
              <FileText size={14} className="text-ws-muted" />
              <span className="text-ws-ink font-medium">{source.title}</span>
              <button
                type="button"
                onClick={() => toggleContext(source.id)}
                style={{background: 'none', border: 'none', padding: 0, cursor: 'pointer', marginLeft: 'auto', display: 'flex', color: source.inContext ? "#10b981" : "#71717a"}}
                title={source.inContext ? 'Remove from context' : 'Add to context'}
              >
                {source.inContext ? <ToggleRight size={18} /> : <ToggleLeft size={18} />}
              </button>
            </div>
            <div className="flex items-center justify-between text-ws-muted text-sm">
              <span>{source.type}</span>
              <span>{source.chunkCount} chunks</span>
            </div>
            {expandedId === source.id && (
              <div style={{marginTop: 4, display: 'flex', flexDirection: 'column', gap: 6}}>
                {source.chunks.map(chunk => (
                  <div key={chunk.id} style={{
                    padding: '6px 8px',
                    background: "#0a0a0b",
                    borderRadius: "4px",
                    border: '1px solid var(--ws-edge-soft)',
                    fontSize: 'var(--ws-type-xs)',
                    color: "#a1a1aa",
                    lineHeight: 1.4,
                  }}>
                    {chunk.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {filtered.length === 0 && (
          <div style={{color: "#71717a", fontSize: '11px', textAlign: 'center', padding: 'var(--ws-sp-6) 0'}}>
            No sources match "{filter}"
          </div>
        )}
      </div>
    </div>
  );
}

export default SourcesPanel;

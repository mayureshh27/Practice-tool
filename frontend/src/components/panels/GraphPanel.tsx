import {useState} from 'react';

type ConceptNode = { id: string; label: string; mastery: 'mastered' | 'practiced' | 'unseen'; x: number; y: number; };
type ConceptEdge = { from: string; to: string; };

const NODES: ConceptNode[] = [
  {id: 'cspace', label: 'C-Space', mastery: 'mastered', x: 80, y: 20},
  {id: 'dof', label: 'DOF', mastery: 'practiced', x: 20, y: 80},
  {id: 'topology', label: 'Topology', mastery: 'practiced', x: 140, y: 80},
  {id: 'rigid', label: 'Rigid Bodies', mastery: 'mastered', x: 80, y: 140},
  {id: 'fk', label: 'Forward Kin.', mastery: 'unseen', x: 20, y: 200},
  {id: 'ik', label: 'Inverse Kin.', mastery: 'unseen', x: 140, y: 200},
  {id: 'jacobian', label: 'Jacobian', mastery: 'unseen', x: 80, y: 260},
];

const EDGES: ConceptEdge[] = [
  {from: 'cspace', to: 'dof'},
  {from: 'cspace', to: 'topology'},
  {from: 'dof', to: 'rigid'},
  {from: 'topology', to: 'rigid'},
  {from: 'rigid', to: 'fk'},
  {from: 'rigid', to: 'ik'},
  {from: 'fk', to: 'jacobian'},
  {from: 'ik', to: 'jacobian'},
];

const MASTERY_COLORS: Record<string, string> = {
  mastered: "var(--ws-accent)",
  practiced: "#f59e0b",
  unseen: "var(--ws-muted)",
};

function GraphPanel() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const selected = NODES.find(n => n.id === selectedNode);

  const getNodePos = (id: string) => {
    const node = NODES.find(n => n.id === id);
    return node ? {x: node.x + 40, y: node.y + 12} : {x: 0, y: 0};
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <p className="text-ws-muted text-sm m-0">Concept prerequisite map. Click a node for details.</p>

      <div style={{
        position: 'relative',
        height: 300,
        background: "var(--ws-bg)",
        border: '1px solid var(--ws-edge-soft)',
        borderRadius: "6px",
        overflow: 'hidden',
      }}>
        <svg width="100%" height="100%" style={{position: 'absolute', top: 0, left: 0}}>
          {EDGES.map(edge => {
            const from = getNodePos(edge.from);
            const to = getNodePos(edge.to);
            return (
              <line
                key={`${edge.from}-${edge.to}`}
                x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                stroke="var(--ws-line)" strokeWidth={1.5}
              />
            );
          })}
        </svg>
        {NODES.map(node => (
          <button
            key={node.id}
            type="button"
            onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
            style={{
              position: 'absolute',
              left: node.x, top: node.y,
              width: 80, height: 24,
              background: selectedNode === node.id ? "rgba(16,185,129,0.1)" : "var(--ws-bg)",
              border: `1.5px solid ${selectedNode === node.id ? "var(--ws-accent)" : MASTERY_COLORS[node.mastery]}`,
              borderRadius: "4px",
              color: "var(--ws-ink)",
              fontSize: 10,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
              transition: 'all 150ms ease',
            }}
          >
            {node.label}
          </button>
        ))}
      </div>

      {selected && (
        <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2" style={{marginTop: 8}}>
          <div className="text-ws-ink font-medium">{selected.label}</div>
          <div className="flex items-center justify-between text-ws-muted text-sm">
            <span className={`ws-tag mastery-${selected.mastery}`} style={{textTransform: 'capitalize'}}>{selected.mastery}</span>
          </div>
          <div style={{fontSize: '11px', color: "var(--ws-soft)", marginTop: 4}}>
            {selected.mastery === 'mastered' && 'You have demonstrated consistent understanding of this concept.'}
            {selected.mastery === 'practiced' && 'You have practiced this concept but may still have gaps.'}
            {selected.mastery === 'unseen' && 'You have not yet encountered exercises on this concept.'}
          </div>
          <div style={{fontSize: 'var(--ws-type-xs)', color: "var(--ws-muted)", marginTop: 4}}>
            Prerequisites: {EDGES.filter(e => e.to === selected.id).map(e => NODES.find(n => n.id === e.from)?.label).filter(Boolean).join(', ') || 'None'}
          </div>
        </div>
      )}

      {!selected && (
        <div className="flex flex-col gap-3 overflow-y-auto flex-1" style={{marginTop: 4}}>
          <div className="bg-ws-surface border border-ws-line rounded-md p-3 flex flex-col gap-2">
            <div className="text-ws-ink font-medium">Legend</div>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-bold tracking-wider bg-ws-success/10 text-ws-success border border-ws-success/30">Mastered</span>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold tracking-wider bg-ws-accent/10 text-ws-accent border border-ws-accent/30">Practiced</span>
              <span className="px-2 py-0.5 rounded text-[11px] font-bold tracking-wider bg-ws-surface text-ws-muted border border-ws-line">Unseen</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GraphPanel;

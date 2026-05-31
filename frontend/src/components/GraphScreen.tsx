import {Filter, GitBranch} from 'lucide-react';
import {useState, useCallback} from 'react';
import { CustomSelect } from './ui/CustomSelect';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from '@xyflow/react';
import type { Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 50, y: 125 }, data: { label: 'Topology', status: 'mastered' }, type: 'default', className: 'ws-graph-node mastered' },
  { id: '2', position: { x: 250, y: 125 }, data: { label: 'Configuration Space', status: 'practiced' }, type: 'default', className: 'ws-graph-node practiced' },
  { id: '3', position: { x: 450, y: 125 }, data: { label: 'Rigid Body', status: 'unseen' }, type: 'default', className: 'ws-graph-node unseen' },
  { id: '4', position: { x: 250, y: 250 }, data: { label: 'Degrees of Freedom', status: 'blind-spot' }, type: 'default', className: 'ws-graph-node blind-spot' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: 'var(--ws-edge-strong)' }, markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--ws-edge-strong)' } },
  { id: 'e2-3', source: '2', target: '3', style: { stroke: 'var(--ws-edge-strong)' }, markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--ws-edge-strong)' } },
  { id: 'e2-4', source: '2', target: '4', style: { stroke: 'var(--ws-edge-strong)' }, markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--ws-edge-strong)' } },
];

function GraphScreen() {
  const [nodes, _, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNodeId(node.id);
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="flex flex-col w-full h-full bg-ws-floor relative">
      <style>{`
        .ws-graph-node {
          background: var(--ws-bench);
          border: 1px solid var(--ws-edge-soft);
          border-radius: var(--ws-radius-md);
          padding: 8px 16px;
          color: var(--ws-ink);
          font-weight: 500;
          font-size: 14px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .ws-graph-node::before {
          content: '';
          display: block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        .ws-graph-node.mastered { border-color: var(--ws-signal-pass); }
        .ws-graph-node.mastered::before { background: var(--ws-signal-pass); }
        .ws-graph-node.practiced { border-color: var(--ws-glow); box-shadow: 0 0 0 2px var(--ws-glow-ring); }
        .ws-graph-node.practiced::before { background: var(--ws-glow); }
        .ws-graph-node.unseen { opacity: 0.7; }
        .ws-graph-node.unseen::before { background: var(--ws-ink-muted); }
        .ws-graph-node.blind-spot { border-color: var(--ws-signal-warn); }
        .ws-graph-node.blind-spot::before { background: var(--ws-signal-warn); }
        
        /* React Flow Dark Theme Overrides */
        .react-flow__pane { background: var(--ws-floor); }
        .react-flow__background { fill: var(--ws-edge-strong); opacity: 0.2; }
        .react-flow__controls { background: var(--ws-bench); border: 1px solid var(--ws-edge-soft); box-shadow: none; border-radius: var(--ws-radius-md); overflow: hidden; }
        .react-flow__controls-button { background: transparent; border-bottom: 1px solid var(--ws-edge-soft); fill: var(--ws-ink-secondary); }
        .react-flow__controls-button:hover { background: var(--ws-floor); fill: var(--ws-ink); }
        .react-flow__controls-button:last-child { border-bottom: none; }
      `}</style>

      {/* Filters Overlay */}
      <div className="absolute top-6 left-6 z-10 bg-ws-bench border border-ws-edge-soft rounded-lg p-4 shadow-md w-80">
        <h3 className="font-medium text-ws-ink mb-4 flex items-center gap-2"><Filter size={16} /> Graph Filters</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-ws-type-sm text-ws-ink-tertiary mb-1">Domain</label>
            <CustomSelect 
              value="Robotics Learning"
              onChange={() => {}}
              options={[
                { value: 'Robotics Learning', label: 'Robotics Learning' },
                { value: 'CMU MRSD Prep', label: 'CMU MRSD Prep' }
              ]}
              style={{ width: '100%', padding: '6px' }}
            />
          </div>
          
          <div>
            <label className="block text-ws-type-sm text-ws-ink-tertiary mb-1">Subject</label>
            <CustomSelect 
              value="Modern Robotics"
              onChange={() => {}}
              options={[
                { value: 'Modern Robotics', label: 'Modern Robotics' },
                { value: 'All Subjects', label: 'All Subjects' }
              ]}
              style={{ width: '100%', padding: '6px' }}
            />
          </div>

          <div>
            <label className="block text-ws-type-sm text-ws-ink-tertiary mb-2">Show Elements</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm text-ws-ink-secondary cursor-pointer">
                <input type="checkbox" defaultChecked /> Concepts
              </label>
              <label className="flex items-center gap-2 text-sm text-ws-ink-secondary cursor-pointer">
                <input type="checkbox" defaultChecked /> Prerequisites
              </label>
              <label className="flex items-center gap-2 text-sm text-ws-ink-secondary cursor-pointer">
                <input type="checkbox" /> Sources
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Graph Canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="var(--ws-edge-strong)" gap={24} size={2} />
          <Controls showInteractive={false} position="top-right" style={{margin: '24px'}} />
        </ReactFlow>
      </div>

      {/* Node Detail */}
      <div className="h-48 border-t border-ws-edge bg-ws-bench p-6 flex gap-6 transition-opacity duration-300">
        {selectedNode ? (
          <>
            <div className="w-1/3 border-r border-ws-edge-soft pr-6 flex flex-col justify-center">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-3 h-3 rounded-full ${selectedNode.data.status === 'mastered' ? 'bg-ws-signal-pass' : selectedNode.data.status === 'practiced' ? 'bg-ws-glow' : selectedNode.data.status === 'blind-spot' ? 'bg-ws-signal-warn' : 'bg-ws-ink-muted'}`}></div>
                <h2 className="text-xl font-bold text-ws-ink">{selectedNode.data.label as string}</h2>
              </div>
              <div className="text-ws-ink-secondary text-sm mb-4">Chapter 2 · {Math.floor(Math.random() * 5) + 1} exercises</div>
              <div className="flex gap-2">
                <button type="button" className="bg-ws-glow text-ws-floor font-medium rounded-md py-1.5 px-4 text-sm hover:brightness-110 transition-all">Practice</button>
                <button type="button" className="ws-home-recent-item !w-auto py-1.5 px-3 text-sm">Sources</button>
              </div>
            </div>
            
            <div className="flex-1 flex flex-col justify-center">
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="text-ws-type-sm text-ws-ink-tertiary uppercase tracking-wider mb-1">Status</div>
                  <div className="text-ws-ink font-medium capitalize">{selectedNode.data.status as string}</div>
                </div>
                <div>
                  <div className="text-ws-type-sm text-ws-ink-tertiary uppercase tracking-wider mb-1">Attempts</div>
                  <div className="text-ws-ink font-medium">{Math.floor(Math.random() * 10)} attempts</div>
                </div>
                <div>
                  <div className="text-ws-type-sm text-ws-ink-tertiary uppercase tracking-wider mb-1">Last Practiced</div>
                  <div className="text-ws-ink font-medium">{Math.floor(Math.random() * 5) + 1} days ago</div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-ws-ink-muted">
            <span className="flex items-center gap-2"><GitBranch size={20} /> Select a node in the graph to view details.</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default GraphScreen;

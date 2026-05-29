import {X} from 'lucide-react';
import type {RightDockPanel as RightDockPanelType} from '../workspaceTypes';
import TutorPanel from './panels/TutorPanel';
import SourcesPanel from './panels/SourcesPanel';
import ArtifactsPanel from './panels/ArtifactsPanel';
import MemoryPanel from './panels/MemoryPanel';
import GraphPanel from './panels/GraphPanel';
import ContextPanel from './panels/ContextPanel';
import InspectorPanel from './panels/InspectorPanel';

import { useUIStore } from '../stores/uiStore';

// No props needed since we use Zustand

const PANEL_TITLES: Record<Exclude<RightDockPanelType, null>, string> = {
  sources:   'Source Chunks',
  tutor:     'Tutor Chat',
  artifacts: 'Generated Artifacts',
  memory:    'Learning Memory',
  graph:     'Related Concepts',
  context:   'Context Slots',
  inspector: 'Debug Inspector',
};

function renderPanelContent(activePanel: Exclude<RightDockPanelType, null>) {
  switch (activePanel) {
    case 'sources':   return <SourcesPanel />;
    case 'tutor':     return <TutorPanel />;
    case 'artifacts': return <ArtifactsPanel />;
    case 'memory':    return <MemoryPanel />;
    case 'graph':     return <GraphPanel />;
    case 'context':   return <ContextPanel />;
    case 'inspector': return <InspectorPanel />;
    default: return null;
  }
}

/** Slide-in panel that overlays from the right side of ws-main. Rendered inside ws-main so positioning is correct. */
function RightDockPanel() {
  const activePanel = useUIStore(s => s.rightPanel);
  const onClose = () => useUIStore.getState().setRightPanel(null);

  return (
    <div className={`absolute right-[42px] top-0 bottom-0 z-20 bg-white dark:bg-ws-bg transition-[width,border] duration-200 ease-out overflow-hidden ${activePanel ? 'w-[360px] border-l border-zinc-200 dark:border-ws-line' : 'w-0 border-l-0 border-transparent'}`}>
      {activePanel && (
        <div className="flex flex-col w-[360px] h-full">
          <div className="flex items-center justify-between px-4 h-11 shrink-0 border-b border-zinc-200 dark:border-ws-line bg-ws-bg">
            <span className="font-bold text-[13px] text-ws-ink">{PANEL_TITLES[activePanel]}</span>
            <button
              type="button"
              className="flex items-center justify-center w-7 h-7 rounded text-ws-muted hover:bg-zinc-200 hover:text-ws-ink dark:hover:bg-ws-surface-2 dark:hover:text-ws-ink transition-colors"
              onClick={onClose}
              title="Close panel"
              aria-label="Close panel"
            >
              <X size={14} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">
            {renderPanelContent(activePanel)}
          </div>
        </div>
      )}
    </div>
  );
}

export default RightDockPanel;

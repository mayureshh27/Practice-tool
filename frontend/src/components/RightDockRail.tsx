import {FileText,MessageCircle,LayoutGrid,Brain,GitBranch,Sliders,Bug} from 'lucide-react';
import type {RightDockPanel} from '../workspaceTypes';

import { useUIStore } from '../stores/uiStore';

// No props needed

const RAIL_ITEMS: {id: Exclude<RightDockPanel, null>; label: string; icon: typeof FileText; group: 'study' | 'debug'}[] = [
  {id: 'sources',   label: 'Sources',   icon: FileText,      group: 'study'},
  {id: 'tutor',     label: 'Tutor',     icon: MessageCircle, group: 'study'},
  {id: 'artifacts', label: 'Artifacts', icon: LayoutGrid,    group: 'study'},
  {id: 'memory',    label: 'Memory',    icon: Brain,         group: 'study'},
  {id: 'graph',     label: 'Graph',     icon: GitBranch,     group: 'study'},
  {id: 'context',   label: 'Context',   icon: Sliders,       group: 'debug'},
  {id: 'inspector', label: 'Inspector', icon: Bug,           group: 'debug'},
];

/** Just the vertical icon rail — the slide-in panel is rendered separately via RightDockPanel. */
function RightDockRail() {
  const activePanel = useUIStore(s => s.rightPanel);
  const onTogglePanel = useUIStore(s => s.setRightPanel);
  const studyItems = RAIL_ITEMS.filter(i => i.group === 'study');
  const debugItems = RAIL_ITEMS.filter(i => i.group === 'debug');

  return (
    <aside className="flex flex-col items-center gap-2 py-4 w-[42px] bg-white dark:bg-ws-bg border-l border-zinc-200 dark:border-ws-line shrink-0" aria-label="Right dock toggle rail">
      {studyItems.map(item => {
        const Icon = item.icon;
        return (
          <button
            key={item.id}
            type="button"
            className={`flex items-center justify-center w-7 h-7 rounded transition-colors ${activePanel === item.id ? 'text-ws-success bg-ws-surface-2' : 'text-ws-muted hover:text-ws-ink hover:bg-zinc-100 dark:hover:text-ws-ink dark:hover:bg-ws-surface-2'}`}
            onClick={() => onTogglePanel(activePanel === item.id ? null : item.id)}
            title={item.label}
            aria-label={item.label}
          >
            <Icon size={16} />
          </button>
        );
      })}

      <div className="w-5 h-px bg-zinc-200 dark:bg-ws-surface-2 my-2" />

      {debugItems.map(item => {
        const Icon = item.icon;
        return (
          <button
            key={item.id}
            type="button"
            className={`flex items-center justify-center w-7 h-7 rounded transition-colors ${activePanel === item.id ? 'text-ws-success bg-ws-surface-2' : 'text-ws-muted hover:text-ws-ink hover:bg-zinc-100 dark:hover:text-ws-ink dark:hover:bg-ws-surface-2'}`}
            onClick={() => onTogglePanel(activePanel === item.id ? null : item.id)}
            title={item.label}
            aria-label={item.label}
          >
            <Icon size={16} />
          </button>
        );
      })}
    </aside>
  );
}

export default RightDockRail;

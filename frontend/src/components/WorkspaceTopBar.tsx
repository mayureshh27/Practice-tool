import { PanelLeftClose, PanelLeftOpen, Search, Settings, Moon, Sun, ChevronLeft, ChevronRight } from 'lucide-react';
import { Link, useRouter, useMatches, useRouterState } from '@tanstack/react-router';
import { useUIStore } from '../stores/uiStore';
import { useWorkspaceStore } from '../stores/workspaceStore';

function WorkspaceTopBar() {
  const theme = useUIStore(s => s.theme);
  const leftCollapsed = useUIStore(s => s.leftCollapsed);
  const toggleTheme = useUIStore(s => s.toggleTheme);
  const toggleLeftCollapsed = useUIStore(s => s.toggleLeftCollapsed);
  const setSearchModalOpen = useUIStore(s => s.setSearchModalOpen);

  // Getting domains is needed if breadcrumbs need domain names, but TanStack Router's route loader can provide them in route context!
  // For now, let's just grab domains from our Zustand store.
  const domains = useWorkspaceStore(s => s.domains);
  
  const router = useRouter();
  const routerState = useRouterState();
  const matches = useMatches();

  // We can build breadcrumbs from `matches` since it's an array of active routes!
  // We can define static titles in route `meta` or `staticData`, or dynamically.
  // For now, let's fall back to parsing `routerState.location.pathname` or extracting from `matches`.
  const crumbs = matches
    .filter(match => match.routeId !== '__root__' && match.routeId !== '/')
    .map(match => {
      // In a real TanStack Router app, we'd use `match.loaderData` or `match.staticData.title`.
      // For this migration step, let's try to infer from params.
      const params = match.params as any;
      let label = match.routeId;

      if (match.routeId === '/domain/$domainId' && params.domainId) {
        label = domains.find(d => d.id === params.domainId)?.name || 'Domain';
      } else if (match.routeId === '/domain/$domainId/subject/$subjectId' && params.subjectId) {
        label = domains.find(d => d.id === params.domainId)?.subjects.find(s => s.id === params.subjectId)?.name || 'Subject';
      } else if (label.includes('workflows')) {
        label = 'Workflows';
      } else if (label.includes('artifacts')) {
        label = 'Artifacts';
      } else if (label.includes('graph')) {
        label = 'Knowledge Graph';
      }
      return { label, to: match.pathname };
    });

  // Always prepend Root
  const allCrumbs = [{ label: 'Domains', to: '/' }, ...crumbs];

  return (
    <header className="flex items-center justify-between gap-4 h-11 px-4 bg-ws-bg border-b border-ws-line z-30 min-w-0">
      <div className="flex items-center gap-3 min-w-0 shrink-0">
        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 text-ws-muted rounded hover:text-ws-ink hover:bg-ws-surface-2 shrink-0 transition-colors"
          onClick={toggleLeftCollapsed}
          title={leftCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={leftCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {leftCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
        </button>

        <div className="flex items-center gap-2 min-w-0">
          <span className="text-[14px] font-bold text-ws-ink whitespace-nowrap tracking-tight">Practice Workspace</span>
          <span className="text-[11px] font-semibold text-ws-muted uppercase tracking-wide whitespace-nowrap hidden sm:inline-block">Adaptive Learning</span>
        </div>
      </div>

      {/* Breadcrumb navigation */}
      <div className="flex-1 flex items-center gap-1 min-w-0 overflow-x-auto pr-4 flex-nowrap scrollbar-none [mask-image:linear-gradient(to_right,black_85%,transparent_100%)]">
        {allCrumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1 shrink-0">
            {i > 0 && <span className="text-ws-faint text-[11px] shrink-0">›</span>}
            <Link
              to={crumb.to}
              className={`text-[12px] font-medium hover:bg-ws-surface-2 hover:text-ws-ink px-1.5 py-0.5 rounded transition-colors ${i === allCrumbs.length - 1 ? 'text-ws-ink' : 'text-ws-muted'}`}
              activeProps={{ className: 'text-ws-ink bg-ws-surface-2' }}
            >
              {crumb.label}
            </Link>
          </span>
        ))}
      </div>

      <div className="flex items-center justify-end gap-1 min-w-0">
        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 text-ws-muted hover:text-ws-ink hover:bg-ws-surface-2 rounded transition-colors"
          onClick={() => setSearchModalOpen(true)}
          title="Search or command (⌘K)"
        >
          <Search size={15} />
        </button>

        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 text-ws-muted hover:text-ws-ink hover:bg-ws-surface-2 rounded transition-colors"
          onClick={() => router.history.back()}
          title="Back"
        >
          <ChevronLeft size={16} />
        </button>
        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 text-ws-muted hover:text-ws-ink hover:bg-ws-surface-2 rounded transition-colors"
          onClick={() => router.history.forward()}
          title="Forward"
        >
          <ChevronRight size={16} />
        </button>

        <button
          type="button"
          className="flex items-center justify-center w-7 h-7 text-ws-muted hover:text-ws-ink hover:bg-ws-surface-2 rounded transition-colors"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </button>

        <button type="button" className="flex items-center justify-center w-7 h-7 text-ws-muted hover:text-ws-ink hover:bg-ws-surface-2 rounded transition-colors" title="Settings">
          <Settings size={15} />
        </button>
      </div>
    </header>
  );
}

export default WorkspaceTopBar;

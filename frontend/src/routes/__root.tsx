import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { HotkeysProvider } from '@tanstack/react-hotkeys'

import { useUIStore } from '../stores/uiStore'
import WorkspaceTopBar from '../components/WorkspaceTopBar'
import LeftNav from '../components/LeftNav'
import BottomDock from '../components/BottomDock'
import RightDockPanel from '../components/RightDockPanel'
import RightDockRail from '../components/RightDockRail'
import { SearchPalette } from '../components/SearchPalette'
import { CreationModal } from '../components/CreationModal'

import '../styles.css'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  const setSearchModalOpen = useUIStore(s => s.setSearchModalOpen);
  const leftCollapsed = useUIStore(s => s.leftCollapsed);

  // Global keyboard shortcuts via native listeners (avoids TanStack hotkey type constraints)
  if (typeof window !== 'undefined') {
    // eslint-disable-next-line react-hooks/rules-of-hooks
  }

  return (
    <HotkeysProvider>
      <div
        className="h-dvh max-h-dvh flex flex-col overflow-hidden bg-ws-bg text-ws-ink font-sans text-[13px] leading-relaxed antialiased"
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            setSearchModalOpen(true);
          }
        }}
        tabIndex={-1}
      >
        <WorkspaceTopBar />

        <div className="flex-1 flex overflow-hidden min-h-0">
          <LeftNav />

          <div
            className="flex-1 flex flex-col min-w-0 overflow-hidden"
            style={{ marginLeft: leftCollapsed ? 0 : undefined }}
          >
            <div className="flex-1 overflow-auto bg-ws-bg">
              <Outlet />
            </div>

            <BottomDock />
          </div>

          <RightDockPanel />
          <RightDockRail />
        </div>
      </div>
      <TanStackRouterDevtools position="bottom-right" />
      <SearchPalette />
      <CreationModal />
    </HotkeysProvider>
  )
}

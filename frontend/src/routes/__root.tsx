import { Outlet, createRootRouteWithContext } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { HotkeysProvider } from '@tanstack/react-hotkeys'
import type { QueryClient } from '@tanstack/react-query'

import { domainQueries, masteryQueries } from '../api/queries'
import { useUIStore } from '../stores/uiStore'

import WorkspaceTopBar from '../components/WorkspaceTopBar'
import LeftNav from '../components/LeftNav'
import BottomDock from '../components/BottomDock'
import RightDockPanel from '../components/RightDockPanel'
import RightDockRail from '../components/RightDockRail'
import { SearchPalette } from '../components/SearchPalette'
import { CreationModal } from '../components/CreationModal'

import '../styles.css'

interface RouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({
  loader: ({ context: { queryClient } }) => {
    queryClient.ensureQueryData(domainQueries.list())
    queryClient.ensureQueryData(masteryQueries.scores())
    queryClient.ensureQueryData(masteryQueries.blindSpots())
  },
  component: RootComponent,
})

function RootComponent() {
  const setSearchModalOpen = useUIStore(s => s.setSearchModalOpen);

  return (
    <HotkeysProvider>
      <div
        className="h-dvh max-h-dvh flex overflow-hidden bg-ws-bg text-ws-ink font-sans text-[13px] leading-relaxed antialiased"
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            setSearchModalOpen(true);
          }
        }}
        tabIndex={-1}
      >
        <LeftNav />

        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <WorkspaceTopBar />

          <div className="flex-1 overflow-auto bg-ws-bg">
            <Outlet />
          </div>

          <BottomDock />
        </div>

        <RightDockPanel />
        <RightDockRail />
      </div>
      <TanStackRouterDevtools position="bottom-right" />
      <SearchPalette />
      <CreationModal />
    </HotkeysProvider>
  )
}

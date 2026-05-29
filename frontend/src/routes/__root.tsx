import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { HotkeysProvider, useHotkey } from '@tanstack/react-hotkeys'

import { useUIStore } from '../stores/uiStore'
import WorkspaceTopBar from '../components/WorkspaceTopBar'
import LeftNav from '../components/LeftNav'
import BottomDock from '../components/BottomDock'
import RightDockPanel from '../components/RightDockPanel'
import RightDockRail from '../components/RightDockRail'
import { SearchPalette } from '../components/SearchPalette'

import '../styles.css'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  const theme = useUIStore(s => s.theme);
  const leftCollapsed = useUIStore(s => s.leftCollapsed);
  const setSearchModalOpen = useUIStore(s => s.setSearchModalOpen);

  useHotkey('meta+k', (e) => {
    e.preventDefault();
    setSearchModalOpen(true);
  });
  
  useHotkey('ctrl+k', (e) => {
    e.preventDefault();
    setSearchModalOpen(true);
  });

  return (
    <HotkeysProvider>
      <div>
        <div className="h-dvh max-h-dvh flex flex-col overflow-hidden bg-ws-bg text-ws-ink font-sans text-[13px] leading-relaxed antialiased">
          <WorkspaceTopBar />
          
          <div className="flex-1 flex overflow-hidden min-h-0 relative">
            <LeftNav />
            
            <div className="flex-1 flex flex-col min-w-0">
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
      </div>
    </HotkeysProvider>
  )
}

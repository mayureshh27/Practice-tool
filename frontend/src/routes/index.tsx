import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { RootScreen } from '../components/ExplorerScreens'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/workspaceApi'
import { useWorkspaceStore } from '../stores/workspaceStore'

export const Route = createFileRoute('/')({
  component: IndexScreen,
})

function IndexScreen() {
  const { data: domains = [], isLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: api.getDomains,
  })
  const renameDomain = useWorkspaceStore(s => s.renameDomain);
  const deleteDomain = useWorkspaceStore(s => s.deleteDomain);
  const togglePinDomain = useWorkspaceStore(s => s.togglePinDomain);
  const toggleArchiveDomain = useWorkspaceStore(s => s.toggleArchiveDomain);
  const navigate = useNavigate();

  if (isLoading) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Loading domains...</div>
  }

  return (
    <RootScreen
      domains={domains}
      onNavigate={(loc: any) => {
        if (loc.level === 'domain') {
          navigate({ to: `/domain/${loc.domainId}` });
        }
      }}
      onOpenCreateModal={() => {}}
      onRenameDomain={renameDomain}
      onDeleteDomain={deleteDomain}
      onTogglePinDomain={togglePinDomain}
      onToggleArchiveDomain={toggleArchiveDomain}
    />
  );
}
